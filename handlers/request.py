import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from states import RequestForm
from config import GROUP_ID, DONOR_TOPIC_ID, BENEFICIARY_TOPIC_ID
from keyboards import *
from services.notify import notify_admin

router = Router()

@router.message(RequestForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    # Validation: Ensure name is not too short
    if len(message.text.strip()) < 3:
        await message.answer("⚠️ عذراً، يرجى إدخال اسم حقيقي (أكثر من حرفين).", reply_markup=get_cancel_keyboard())
        return

    # Save name and move to address state
    await state.update_data(name=message.text)
    await state.set_state(RequestForm.waiting_for_governorate)
    await message.answer("📍 الرجاء اختيار محافظتك من القائمة أدناه:", reply_markup=get_governorates_keyboard())
    
@router.message(RequestForm.waiting_for_governorate)
async def process_governorate(message: types.Message, state: FSMContext):
    # Validation: Ensure the user selected a valid Syrian governorate (Optional but recommended)
    valid_govs = [
        "دمشق", "ريف دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس", 
        "إدلب", "درعا", "السويداء", "القنيطرة", "دير الزور", "الرقة", "الحسكة"
    ]
    
    if message.text not in valid_govs:
        await message.answer("⚠️ يرجى اختيار المحافظة من الأزرار المتاحة فقط.", reply_markup=get_governorates_keyboard())
        return

    # Save governorate and ask for specific address
    await state.update_data(governorate=message.text)
    await state.set_state(RequestForm.waiting_for_address)
    await message.answer("🏠 أين بالضبط؟ (مثال: المزة - جانب جامع الأكرم)", reply_markup=get_cancel_keyboard())

@router.message(RequestForm.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    # Validation: Ensure address is not too short
    if len(message.text.strip()) < 3:
        await message.answer("⚠️ عذراً، العنوان قصير جداً. يرجى كتابة عنوان أوضح.", reply_markup=get_cancel_keyboard())
        return

    # Save address and move to content state
    await state.update_data(address=message.text)
    await state.set_state(RequestForm.waiting_for_content)
    await message.answer("✉️ الرجاء كتابة محتوى رسالتك بالتفصيل:", reply_markup=get_cancel_keyboard())

@router.message(RequestForm.waiting_for_content)
async def process_content(message: types.Message, state: FSMContext):
    # Validation: Ensure content is not too short
    if len(message.text.strip()) < 3:
        await message.answer("⚠️ عذراً، المحتوى قصير جداً. يرجى كتابة تفاصيل أكثر.", reply_markup=get_cancel_keyboard())
        return

    # Retrieve all saved data
    data = await state.get_data()
    user_type = data.get("type")
    
    topic_id = DONOR_TOPIC_ID if user_type == "donor" else BENEFICIARY_TOPIC_ID
    type_ar = 'متبرع' if user_type == 'donor' else 'مستفيد'
    
    final_msg = (
        f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"📨 <b>رسالة جديدة من {type_ar}</b>\n\n"
        f"👤 <b>الاسم:</b> {data['name']}\n"
        f"📱 <b>اسم الحساب:</b> {data['telegram_name']}\n"
        f"🔗 <b>Username:</b> {data['username']}\n"
        f"📍 <b>العنوان:</b> {data['address']}\n"
        f"✉️ <b>المحتوى:</b>\n{message.text}"
    )
    
    try:
        # Send message to the target topic
        await message.bot.send_message(chat_id=GROUP_ID, text=final_msg, message_thread_id=topic_id)
        # Restore main keyboard upon success
        await message.answer("✅ تم إرسال رسالتك بنجاح. شكراً لتواصلك معنا.", reply_markup=get_main_keyboard())
        
    except TelegramForbiddenError:
        # User blocked the bot before we could reply, no need to notify admins
        pass 
    except TelegramBadRequest as e:
        # Malformed request (e.g., text too long), log locally but don't crash
        logging.error(f"Bad Request Error: {e}")
    except Exception as e:
        # Critical network or unexpected errors: Notify user and admins
        await message.answer(
            "❌ عذراً، حدث خطأ تقني أثناء إرسال رسالتك.\n"
            "يرجى المحاولة لاحقاً أو التواصل مع الدعم.",
            reply_markup=get_main_keyboard()
        )
        await notify_admin(message.bot, f"فشل إرسال رسالة مستخدم:\n{str(e)}")
    
    # Clear FSM state
    await state.clear()