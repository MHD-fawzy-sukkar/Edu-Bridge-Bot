import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from states import SupportForm
from config import GROUP_ID, SUPPORT_TOPIC
from keyboards import get_cancel_keyboard, get_main_keyboard
from services.notify import notify_admin

router = Router()

@router.message(SupportForm.waiting_for_content)
async def process_support_content(message: types.Message, state: FSMContext):
    # Validation: Ensure support message is not too short
    if len(message.text.strip()) < 10:
        await message.answer("⚠️ عذراً، محتوى الرسالة قصير جداً. يرجى التوضيح أكثر.", reply_markup=get_cancel_keyboard())
        return

    # Retrieve data saved in start.py
    data = await state.get_data()
    
    final_msg = (
        f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"📱 <b>اسم الحساب:</b> {data['telegram_name']}\n"
        f"🔗 <b>Username:</b> {data['username']}\n"
        f"📧 <b>رسالة الدعم:</b>\n{message.text}"
    )
    
    try:
        # Send support message to the support topic
        await message.bot.send_message(chat_id=GROUP_ID, text=final_msg, message_thread_id=SUPPORT_TOPIC)
        # Restore main keyboard upon success
        await message.answer("✅ تم إرسال رسالتك بنجاح. فريق الدعم سيتواصل معك قريباً.", reply_markup=get_main_keyboard())
        
    except TelegramForbiddenError:
        # User blocked the bot before we could reply
        pass
    except TelegramBadRequest as e:
        # Malformed request
        logging.error(f"Bad Request Error: {e}")
    except Exception as e:
        # Critical network or unexpected errors: Notify user and admins
        await message.answer(
            "❌ عذراً، حدث خطأ تقني أثناء إرسال رسالتك.\n"
            "يرجى المحاولة لاحقاً.",
            reply_markup=get_main_keyboard()
        )
        await notify_admin(message.bot, f"فشل إرسال رسالة دعم:\n{str(e)}")
    
    # Clear FSM state
    await state.clear()