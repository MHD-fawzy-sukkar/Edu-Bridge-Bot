from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states import RequestForm
from config import GROUP_ID, DONOR_TOPIC_ID, BENEFICIARY_TOPIC_ID

router = Router()

@router.message(RequestForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    # Save name and move to address state
    await state.update_data(name=message.text)
    await state.set_state(RequestForm.waiting_for_address)
    await message.answer("📍 ما هو عنوانك؟ (مثال: دمشق - باب توما)")

@router.message(RequestForm.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    # Save address and move to content state
    await state.update_data(address=message.text)
    await state.set_state(RequestForm.waiting_for_content)
    await message.answer("✉️ الرجاء كتابة محتوى رسالتك بالتفصيل:")

@router.message(RequestForm.waiting_for_content)
async def process_content(message: types.Message, state: FSMContext):
    # Retrieve all saved data from previous steps
    data = await state.get_data()
    user_type = data.get("type")
    
    topic_id = DONOR_TOPIC_ID if user_type == "donor" else BENEFICIARY_TOPIC_ID
    type_ar = 'متبرع' if user_type == 'donor' else 'مستفيد'
    
    final_msg = (
        f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"📨 <b>رسالة جديدة من {type_ar}</b>\n\n"
        f"👤 <b>الاسم الذي أدخله:</b> {data['name']}\n"
        f"📱 <b>اسم الحساب:</b> {data['telegram_name']}\n"
        f"🔗 <b>Username:</b> {data['username']}\n"
        f"📍 <b>العنوان:</b> {data['address']}\n"
        f"✉️ <b>المحتوى:</b>\n{message.text}"
    )
    
    try:
        # Send message to the target topic
        await message.bot.send_message(chat_id=GROUP_ID, text=final_msg, message_thread_id=topic_id)
        await message.answer("✅ تم إرسال رسالتك بنجاح. شكراً لتواصلك معنا.")
    except Exception as e:
        await message.answer(
            "❌ حدث خطأ أثناء إرسال الرسالة.\n"
            "📧 أرسل رسالة دعم باستخدام /start واختيار 'الدعم'."
        )
        print(f"Error sending message: {e}")
    
    # Clear FSM state after completion
    await state.clear()