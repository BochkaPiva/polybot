from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.repositories.users import UserRepository
from db.models import User, Employee
from bot.keyboards.common import get_auth_keyboard, get_main_keyboard
from db.base import get_session
from sqlalchemy import select

# Define authentication states
class AuthStates(StatesGroup):
    waiting_for_name = State()
    confirming_identity = State()

# Create router
router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать! Для начала работы введите ваше ФИО."
    )
    await state.set_state(AuthStates.waiting_for_name)

@router.message(AuthStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка введенного ФИО"""
    async with get_session() as session:
        # Ищем сотрудника по ФИО
        query = select(Employee).where(
            Employee.full_name.ilike(f"%{message.text}%"),
            Employee.is_active == True
        )
        result = await session.execute(query)
        employee = result.scalar_one_or_none()

        if not employee:
            await message.answer(
                "Сотрудник с таким ФИО не найден. Пожалуйста, проверьте правильность ввода и попробуйте снова."
            )
            return

        # Сохраняем найденного сотрудника в состоянии
        await state.update_data(employee_id=employee.id)
        
        # Запрашиваем подтверждение
        await message.answer(
            f"Вы {employee.full_name} из отдела {employee.department or 'не указан'}?\n"
            "Пожалуйста, подтвердите, что это вы."
        )
        await state.set_state(AuthStates.confirming_identity)

@router.message(AuthStates.confirming_identity)
async def process_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения личности"""
    if message.text.lower() not in ["да", "yes", "верно", "правильно"]:
        await message.answer(
            "Пожалуйста, введите ваше ФИО снова."
        )
        await state.set_state(AuthStates.waiting_for_name)
        return

    # Получаем данные из состояния
    data = await state.get_data()
    employee_id = data.get("employee_id")

    async with get_session() as session:
        # Обновляем telegram_id сотрудника
        query = select(Employee).where(Employee.id == employee_id)
        result = await session.execute(query)
        employee = result.scalar_one()

        employee.telegram_id = message.from_user.id
        await session.commit()

        await message.answer(
            "Отлично! Вы успешно авторизованы.\n"
            "Используйте /menu для доступа к основному меню."
        )
        await state.clear()

@router.callback_query(F.data == "auth")
async def auth_callback(callback: CallbackQuery, state: FSMContext):
    """Handle authentication button click"""
    await callback.answer()
    
    await callback.message.answer(
        "Пожалуйста, введите ваше ФИО полностью, как оно указано в базе данных.\n"
        "Например: Иванов Иван Иванович"
    )
    
    # Set state to waiting for full name
    await state.set_state(AuthStates.waiting_for_name)

@router.message(AuthStates.waiting_for_name)
async def process_full_name(message: Message, state: FSMContext, session):
    """Process full name input"""
    full_name = message.text.strip()
    
    # Check if full name exists in database
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_full_name(full_name)
    
    if not user:
        await message.answer(
            "К сожалению, такого пользователя нет в базе данных.\n"
            "Пожалуйста, проверьте правильность написания ФИО и попробуйте снова."
        )
        return
    
    # Store user ID in state
    await state.update_data(user_id=user.id)
    
    # Check if this is a new Telegram user for this full name
    if user.telegram_id != message.from_user.id:
        # Update Telegram ID for this user
        user.telegram_id = message.from_user.id
        await session.commit()
    
    # Ask for authentication code
    await message.answer(
        f"Спасибо, {full_name}!\n"
        "Для подтверждения личности, пожалуйста, введите ваш персональный код.\n"
        "Если у вас его нет, обратитесь к администратору."
    )
    
    # Set state to waiting for auth code
    await state.set_state(AuthStates.confirming_identity)

@router.message(AuthStates.confirming_identity)
async def process_auth_code(message: Message, state: FSMContext, session):
    """Process authentication code input"""
    auth_code = message.text.strip()
    
    # Get user ID from state
    data = await state.get_data()
    user_id = data.get("user_id")
    
    if not user_id:
        await message.answer("Произошла ошибка. Пожалуйста, начните авторизацию заново.")
        await state.clear()
        return
    
    # Get user from database
    user_repo = UserRepository(session)
    user = await session.get(User, user_id)
    
    if not user:
        await message.answer("Произошла ошибка. Пожалуйста, начните авторизацию заново.")
        await state.clear()
        return
    
    # Check authentication code
    if user.auth_code == auth_code:
        # Authenticate user
        await user_repo.authenticate_user(user.id)
        
        await message.answer(
            f"Авторизация успешна! Добро пожаловать, {user.full_name}.",
            reply_markup=get_main_keyboard()
        )
    else:
        # Record failed attempt
        failed_attempts = await user_repo.record_failed_attempt(user.id)
        
        if failed_attempts >= 3:
            await message.answer(
                "Слишком много неудачных попыток. Пожалуйста, обратитесь к администратору."
            )
            await state.clear()
        else:
            await message.answer(
                "Неверный код. Пожалуйста, попробуйте снова или обратитесь к администратору."
            )
            return
    
    # Clear state
    await state.clear()
