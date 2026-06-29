from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states import SupportForm
from config import GROUP_ID, SUPPORT_TOPIC

router = Router()

@router.message(SupportForm.waiting_for_content)
async def process_support_content(message: types.Message, state: FSMContext):
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
        await message.answer("✅ تم إرسال الرسالة بنجاح. شكراً لتواصلك معنا.")
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ أثناء إرسال الرسالة.\n"
            "📧 أرسل رسالة دعم باستخدام /start واختيار 'الدعم'."
        )
        print(f"Error sending support message: {e}")
    
    # Clear FSM state
    await state.clear()