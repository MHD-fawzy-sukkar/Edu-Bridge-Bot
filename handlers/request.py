import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from states import RequestForm
from config import GROUP_ID, DONOR_TOPIC_ID, BENEFICIARY_TOPIC_ID, UNIVERSITY_TOPIC_ID
from database.requests import add_request_data
from keyboards import (
    get_cancel_keyboard,
    get_main_keyboard,
    get_level_keyboard,
    get_branch_keyboard,
    get_university_specialization_keyboard,
    get_governorates_keyboard
)
from services.notify import notify_admin

router = Router()

def is_cancel(text: str) -> bool:
    if not text:
        return False
    return "إلغاء" in text

# 1. Level state handler
@router.message(RequestForm.waiting_for_level)
async def process_level(message: types.Message, state: FSMContext):
    if is_cancel(message.text):
        await state.clear()
        await message.answer("🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.", reply_markup=get_main_keyboard())
        return

    valid_levels = ["🎒 بكالوريا", "🎓 طالب جامعي"]
    if message.text not in valid_levels:
        await message.answer("⚠️ يرجى اختيار المرحلة الدراسية من الأزرار المتاحة فقط.", reply_markup=get_level_keyboard())
        return

    level_key = "baccalaureate" if "بكالوريا" in message.text else "university"
    level_label = "بكالوريا" if level_key == "baccalaureate" else "طالب جامعي"
    await state.update_data(level=level_key, level_label=level_label)
    
    # Move to branch / specialization state (before name state)
    await state.set_state(RequestForm.waiting_for_branch)
    if level_key == "university":
        await message.answer("🏛️ ما هو تخصصك الجامعي؟", reply_markup=get_university_specialization_keyboard())
    else:
        await message.answer("🎓 ما هو فرعك الدراسي للمرحلة الثانوية؟", reply_markup=get_branch_keyboard())

# 2. Branch / Specialization state handler
@router.message(RequestForm.waiting_for_branch)
async def process_branch(message: types.Message, state: FSMContext):
    if is_cancel(message.text):
        await state.clear()
        await message.answer("🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.", reply_markup=get_main_keyboard())
        return

    data = await state.get_data()
    level = data.get("level", "baccalaureate")

    if level == "baccalaureate":
        valid_branches = ["🔬 علمي", "📖 أدبي", "⚙️ مهني", "🕌 شرعي"]
        if message.text not in valid_branches:
            await message.answer("⚠️ يرجى اختيار الفرع من الأزرار المتاحة فقط.", reply_markup=get_branch_keyboard())
            return
        await state.update_data(branch=message.text)
    else:
        # Check if user wants custom specialization
        if "تخصص آخر" in message.text or "آخر" in message.text:
            await state.set_state(RequestForm.waiting_for_custom_specialization)
            await message.answer("✍️ يرجى كتابة تخصصك الجامعي بالتفصيل:", reply_markup=get_cancel_keyboard())
            return

        if len(message.text.strip()) < 3:
            await message.answer("⚠️ يرجى اختيار التخصص من الأزرار المتاحة أو تحديد (تخصص آخر).", reply_markup=get_university_specialization_keyboard())
            return
        
        await state.update_data(branch=message.text)

    # Move to name state
    await state.set_state(RequestForm.waiting_for_name)
    await message.answer("📝 ما اسمك الكامل؟", reply_markup=get_cancel_keyboard())

# 3. Custom Specialization state handler
@router.message(RequestForm.waiting_for_custom_specialization)
async def process_custom_specialization(message: types.Message, state: FSMContext):
    if is_cancel(message.text):
        await state.clear()
        await message.answer("🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.", reply_markup=get_main_keyboard())
        return

    if len(message.text.strip()) < 2:
        await message.answer("⚠️ يرجى كتابة اسم التخصص بشكل واضح.", reply_markup=get_cancel_keyboard())
        return

    await state.update_data(branch=message.text.strip())
    # Move to name state
    await state.set_state(RequestForm.waiting_for_name)
    await message.answer("📝 ما اسمك الكامل؟", reply_markup=get_cancel_keyboard())

# 4. Name state handler
@router.message(RequestForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    if is_cancel(message.text):
        await state.clear()
        await message.answer("🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.", reply_markup=get_main_keyboard())
        return

    if len(message.text.strip()) < 3:
        await message.answer("⚠️ عذراً، يرجى إدخال اسم حقيقي (أكثر من حرفين).", reply_markup=get_cancel_keyboard())
        return

    await state.update_data(name=message.text)
    # Move to governorate state
    await state.set_state(RequestForm.waiting_for_governorate)
    await message.answer("📍 الرجاء اختيار محافظتك من القائمة أدناه:", reply_markup=get_governorates_keyboard())

# 5. Governorate state handler
@router.message(RequestForm.waiting_for_governorate)
async def process_governorate(message: types.Message, state: FSMContext):
    if is_cancel(message.text):
        await state.clear()
        await message.answer("🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.", reply_markup=get_main_keyboard())
        return

    valid_govs = [
        "دمشق", "ريف دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس", 
        "إدلب", "درعا", "السويداء", "القنيطرة", "دير الزور", "الرقة", "الحسكة"
    ]
    
    if message.text not in valid_govs:
        await message.answer("⚠️ يرجى اختيار المحافظة من الأزرار المتاحة فقط.", reply_markup=get_governorates_keyboard())
        return

    await state.update_data(governorate=message.text)
    await state.set_state(RequestForm.waiting_for_address)
    await message.answer("🏠 أين بالضبط؟ (مثال: المزة - جانب جامع الأكرم)", reply_markup=get_cancel_keyboard())

# 6. Address state handler
@router.message(RequestForm.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    if is_cancel(message.text):
        await state.clear()
        await message.answer("🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.", reply_markup=get_main_keyboard())
        return

    if len(message.text.strip()) < 3:
        await message.answer("⚠️ عذراً، العنوان قصير جداً. يرجى كتابة عنوان أوضح.", reply_markup=get_cancel_keyboard())
        return

    await state.update_data(address=message.text)
    await state.set_state(RequestForm.waiting_for_content)
    data = await state.get_data()
    user_type = data.get("type")
    is_univ = data.get("level") == "university"

    if user_type == "donor":
        if is_univ:
            content_prompt = (
                "✉️ <b>الرجاء كتابة تفاصيل التبرع الجامعي بدقة:</b>\n\n"
                "لنسهل وصول تبرعك، يرجى ذكر:\n"
                "🔸 <b>المحتوى:</b> (كتب جامعية، سلاسل نوط، مراجع...)\n"
                "🔸 <b>الحالة:</b> (جديدة، مخططة، مصورة...)\n\n"
                "📝 <i>مثال: تبرع بمحاضرات الهندسة المعلوماتية السنة الثالثة بحالة ممتازة.</i>\n\n"
            )
        else:
            content_prompt = (
                "✉️ <b>الرجاء كتابة تفاصيل التبرع بدقة:</b>\n\n"
                "لنسهل وصول تبرعك، يرجى ذكر:\n"
                "🔸 <b>المحتوى:</b> (كتب منهاج، نوط، أسئلة دورات...)\n"
                "🔸 <b>الحالة:</b> (جديدة، مخططة، محلولة...)\n\n"
                "📝 <i>مثال: تبرع بكتب بكالوريا نسخة 2026 بحالة ممتازة، مع نوطة رياضيات للأستاذ كذا.</i>\n\n"
            )
    else:
        if is_univ:
            content_prompt = (
                "✉️ <b>الرجاء كتابة تفاصيل طلبك الجامعي بدقة:</b>\n\n"
                "لنسهل العثور على طلبك، يرجى ذكر:\n"
                "🔸 <b>المطلوب:</b> (كتب جامعية محددة، قسم معينة، مراجع...)\n\n"
                "📝 <i>مثال: محتاج كتب الوراثة والتشريح للسنة التحصيرية.</i>"
            )
        else:
            content_prompt = (
                "✉️ <b>الرجاء كتابة تفاصيل طلبك بدقة:</b>\n\n"
                "لنسهل العثور على طلبك، يرجى ذكر:\n"
                "🔸 <b>المطلوب:</b> (كتب محددة، نوطة لأستاذ معين، دورات...)\n\n"
                "📝 <i>مثال: محتاج كتاب الفيزياء والكيمياء، أو نوطة للغة العربية.</i>"
            )
    await message.answer(content_prompt, parse_mode="HTML", reply_markup=get_cancel_keyboard())

# 7. Content state handler
@router.message(RequestForm.waiting_for_content)
async def process_content(message: types.Message, state: FSMContext):
    if is_cancel(message.text):
        await state.clear()
        await message.answer("🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.", reply_markup=get_main_keyboard())
        return

    if len(message.text.strip()) < 20:
        await message.answer("⚠️ عذراً، المحتوى قصير جداً. يرجى كتابة تفاصيل أكثر.", reply_markup=get_cancel_keyboard())
        return

    data = await state.get_data()
    user_type = data.get("type")
    level = data.get("level", "baccalaureate")
    
    # Target topic configuration: University requests go to UNIVERSITY_TOPIC_ID (3053)
    if level == "university":
        topic_id = UNIVERSITY_TOPIC_ID
    else:
        topic_id = DONOR_TOPIC_ID if user_type == "donor" else BENEFICIARY_TOPIC_ID
        
    type_ar = 'متبرع' if user_type == 'donor' else 'مستفيد'
    level_ar = '🎓 طالب جامعي' if level == 'university' else '🎒 بكالوريا'

    await add_request_data(
        tg_id=message.from_user.id,
        data=data,
        username=message.from_user.username,
        content=message.text
    )    

    final_msg = (
        f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        f"📨 <b>رسالة جديدة من {type_ar}</b>\n"
        f"📚 <b>المرحلة الدراسية:</b> {level_ar}\n"
        f"📱 <b>اسم الحساب:</b> {data['telegram_name']}\n"
        f"🔗 <b>Username:</b> {data['username']}\n\n"
        f"👤 <b>الاسم:</b> {data['name']}\n"
        f"🎓 <b>الفرع:</b> {data['branch']}\n"
        f"🌍 <b>المحافظة:</b> {data['governorate']}\n"
        f"📍 <b>العنوان:</b> {data['address']}\n\n"
        f"✉️ <b>المحتوى:</b>\n{message.text}"
    )
    
    try:
        # Send message to target topic
        await message.bot.send_message(chat_id=GROUP_ID, text=final_msg, message_thread_id=topic_id)
        
        if user_type == "donor":
            final_asn = (
                "✅ <b>تم إرسال رسالتك بنجاح!</b>\n\n"
                "شكراً جزيلاً لمبادرتك الطيبة. 🤍\n"
                "سيقوم الفريق بمراجعة التفاصيل، و<b>سنقوم بالتواصل معك مباشرةً فور تأمين الطالب المستحق</b> الذي يحتاج هذه المواد.\n\n"
                "⚠️ <i>ملاحظة: إذا تغير شيء أو قمت بالتبرع بها خارج البوت، يرجى إبلاغنا عبر قسم (📧 الدعم) لنقوم بتحديث القوائم.</i>"
            )
        else: 
            final_asn = (
                "✅ <b>تم إرسال طلبك بنجاح!</b>\n\n"
                "لقد استلمنا تفاصيل المواد التي تحتاجها بنجاح.\n"
                "فريقنا يعمل الآن على مطابقة طلبك، و<b>سنتواصل معك فوراً بمجرد توفر متبرع</b> يملك نفس طلبك.\n\n"
                "⚠️ <i>ملاحظة: في حال قمت بتأمين المواد من مكان آخر، يرجى التواصل معنا عبر قسم (📧 الدعم) لإلغاء الطلب وإتاحة الفرصة لطلاب آخرين.</i>"
            )
            
        await message.answer(final_asn, parse_mode="HTML", reply_markup=get_main_keyboard())
        
    except TelegramForbiddenError:
        pass 
    except TelegramBadRequest as e:
        logging.error(f"Bad Request Error: {e}")
    except Exception as e:
        await message.answer(
            "❌ عذراً، حدث خطأ تقني أثناء إرسال رسالتك.\n"
            "يرجى المحاولة لاحقاً أو التواصل مع الدعم.",
            reply_markup=get_main_keyboard()
        )
        await notify_admin(message.bot, f"فشل إرسال رسالة مستخدم:\n{str(e)}")
    
    await state.clear()