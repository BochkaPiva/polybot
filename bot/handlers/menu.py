from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.repositories.menu import MenuRepository
from db.models import MenuItem
from bot.keyboards.menu import get_menu_keyboard

# Define menu states
class MenuStates(StatesGroup):
    browsing = State()
    asking_question = State()

# Create router
router = Router()

@router.message(Command("menu"))
@router.message(F.text == "📚 Меню справочника")
async def cmd_menu(message: Message, session, is_authenticated: bool, state: FSMContext):
    """Handle menu command"""
    if not is_authenticated:
        await message.answer(
            "Для доступа к меню справочника необходимо авторизоваться.\n"
            "Используйте команду /start для авторизации."
        )
        return
    
    # Get first level menu items
    menu_repo = MenuRepository(session)
    menu_items = await menu_repo.get_menu_items_by_level(level=1)
    
    # Check if menu is empty
    if not menu_items:
        await message.answer(
            "В справочнике пока нет разделов. Пожалуйста, обратитесь к администратору."
        )
        return
    
    # Send menu
    await message.answer(
        "Выберите раздел справочника:",
        reply_markup=get_menu_keyboard(menu_items, level=1)
    )
    
    # Store current level and parent ID in state
    await state.update_data(current_level=1, parent_id=None)
    await state.set_state(MenuStates.browsing)

@router.callback_query(MenuStates.browsing, F.data.startswith("menu:"))
async def menu_navigation(callback: CallbackQuery, state: FSMContext, session):
    """Handle menu navigation"""
    await callback.answer()
    
    # Get menu item ID from callback data
    menu_item_id = callback.data.split(":")[1]
    
    # Handle back button
    if menu_item_id == "back":
        # Get current state data
        data = await state.get_data()
        current_level = data.get("current_level", 1)
        
        if current_level <= 2:
            # Go back to first level
            menu_repo = MenuRepository(session)
            menu_items = await menu_repo.get_menu_items_by_level(level=1)
            
            await callback.message.edit_text(
                "Выберите раздел справочника:",
                reply_markup=get_menu_keyboard(menu_items, level=1)
            )
            
            # Update state
            await state.update_data(current_level=1, parent_id=None)
        else:
            # Go back to parent's parent
            parent_item = await session.get(MenuItem, data.get("parent_id"))
            if parent_item and parent_item.parent_id:
                grandparent_id = parent_item.parent_id
                
                # Get siblings of parent
                menu_repo = MenuRepository(session)
                menu_items = await menu_repo.get_menu_items_by_level(
                    level=current_level-1, 
                    parent_id=grandparent_id
                )
                
                await callback.message.edit_text(
                    f"Раздел: {parent_item.title}",
                    reply_markup=get_menu_keyboard(menu_items, level=current_level-1)
                )
                
                # Update state
                await state.update_data(
                    current_level=current_level-1, 
                    parent_id=grandparent_id
                )
        
        return
    
    # Get menu item
    menu_repo = MenuRepository(session)
    menu_item = await menu_repo.get_menu_item_by_id(int(menu_item_id))
    
    if not menu_item:
        await callback.message.edit_text(
            "Раздел не найден. Пожалуйста, вернитесь в главное меню.",
            reply_markup=get_menu_keyboard([], level=1)
        )
        return
    
    # Check if menu item has children
    children = await menu_repo.get_menu_items_by_level(
        level=menu_item.level + 1, 
        parent_id=menu_item.id
    )
    
    if children:
        # Show submenu
        await callback.message.edit_text(
            f"Раздел: {menu_item.title}",
            reply_markup=get_menu_keyboard(children, level=menu_item.level + 1)
        )
        
        # Update state
        await state.update_data(
            current_level=menu_item.level + 1, 
            parent_id=menu_item.id
        )
    else:
        # Show content
        content = menu_item.content or "Информация отсутствует."
        
        # Check if there are media files
        if menu_item.media_urls:
            # Handle media files (simplified for now)
            media_text = "\n\nМедиа файлы доступны в админ-панели."
            content += media_text
        
        await callback.message.edit_text(
            f"Раздел: {menu_item.title}\n\n{content}",
            reply_markup=get_menu_keyboard([], level=menu_item.level)
        )

@router.callback_query(F.data == "ask_question")
async def ask_question_callback(callback: CallbackQuery, state: FSMContext):
    """Handle ask question button click"""
    await callback.answer()
    
    await callback.message.edit_text(
        "Пожалуйста, введите ваш вопрос, и я постараюсь найти ответ в базе знаний.",
    )
    
    # Set state to asking question
    await state.set_state(MenuStates.asking_question)

@router.message(MenuStates.asking_question)
async def process_question(message: Message, state: FSMContext):
    """Process user question"""
    question = message.text.strip()
    
    # For now, just acknowledge the question
    # Later we'll implement OpenSearch integration
    await message.answer(
        f"Спасибо за ваш вопрос: '{question}'\n\n"
        "В данный момент функция поиска в базе знаний находится в разработке.\n"
        "Скоро вы получите ответ на ваш вопрос."
    )
    
    # Clear state
    await state.clear()
