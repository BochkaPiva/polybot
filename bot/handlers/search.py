from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from search.searcher import DocumentSearcher
from db.repositories.documents import DocumentRepository

# Define search states
class SearchStates(StatesGroup):
    waiting_for_query = State()

# Create router
router = Router()

@router.callback_query(F.data == "ask_question")
async def ask_question_callback(callback: CallbackQuery, state: FSMContext):
    """Handle ask question button click"""
    await callback.answer()
    
    await callback.message.edit_text(
        "Пожалуйста, введите ваш вопрос, и я постараюсь найти ответ в базе знаний."
    )
    
    # Set state to waiting for query
    await state.set_state(SearchStates.waiting_for_query)

@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext, session: AsyncSession):
    """Process search query"""
    query = message.text.strip()
    
    # Send typing action
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Search for documents
    searcher = DocumentSearcher()
    results = await searcher.search(query)
    await searcher.close()
    
    if not results:
        await message.answer(
            "К сожалению, я не нашел ответа на ваш вопрос в базе знаний.\n"
            "Попробуйте переформулировать вопрос или обратитесь к администратору."
        )
    else:
        # Get document details
        doc_repo = DocumentRepository(session)
        
        # Prepare response
        response = f"По вашему запросу '{query}' найдено {len(results)} результатов:\n\n"
        
        for i, result in enumerate(results, 1):
            document = await doc_repo.get_document_by_id(result['id'])
            if document:
                response += f"{i}. <b>{document.title}</b>\n"
                if document.description:
                    response += f"{document.description}\n"
                
                # Add highlights
                if result['highlights']:
                    response += "\nФрагменты:\n"
                    for highlight in result['highlights'][:2]:  # Limit to 2 highlights
                        response += f"• ...{highlight}...\n"
                
                response += "\n"
        
        await message.answer(response, parse_mode="HTML")
    
    # Clear state
    await state.clear()