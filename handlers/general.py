import logging
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType, ChatMemberStatus
from keyboards import get_cancel_keyboard, get_main_keyboard

from services.banned import banned_users

router = Router()

@router.message(F.text == "❌ إلغاء", StateFilter("*"))
async def cancel_process(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("🛑 لا توجد عملية جارية لإلغائها.", reply_markup=get_main_keyboard())
        return

    await state.clear()
    await message.answer(
        "🛑 تم إلغاء العملية الحالية. يمكنك البدء من جديد متى شئت.",
        reply_markup=get_main_keyboard()
    )

# --- Stop Command ---
@router.message(Command("stop"), StateFilter("*"))
async def cmd_stop(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("🛑 لا توجد عملية جارية. يمكنك البدء باستخدام /start")
        return

    # Clear FSM state
    await state.clear()
    await message.answer("🛑 تم إلغاء العملية. يمكنك البدء من جديد باستخدام\n/start")

# --- Help Command ---
@router.message(Command("help"), StateFilter("*"))
async def cmd_help(message: types.Message):
    help_text = (
        "📘 <b>دليل استخدام بوت Edu Bridge</b>\n\n"
        "🤖 هذا البوت مخصص لتسهيل التواصل بين المتبرعين والمستفيدين (لطلاب البكالوريا والطلاب الجامعيين).\n\n"
        "🛠️ <b>الأوامر المتاحة</b>:\n"
        "/start - بدء إرسال رسالة جديدة\n"
        "/stop - إلغاء العملية الحالية\n"
        "/help - عرض هذه التعليمات\n"
        "/info - شرح فكرة البوت وكيفية استخدامه بالتفصيل\n\n"
        "📌 <b>خطوات الاستخدام</b>:\n"
        "1️⃣ استخدم /start لاختيار <b>متبرع</b>، <b>مستفيد</b>، أو <b>الدعم</b>.\n"
        "2️⃣ حدد مرحلتك الدراسية (<b>بكالوريا</b> أو <b>طالب جامعي</b>).\n"
        "3️⃣ اختر الفرع الدراسي أو التخصص الجامعي.\n"
        "4️⃣ أدخل معلوماتك (الاسم، المحافظة، العنوان، والمحتوى).\n"
        "5️⃣ للتواصل مع الدعم من أجل مشكلة معينة اكتب رسالتك مباشرة.\n\n"
        "✍️ <b>نصيحة</b>: اكتب رسالتك بوضوح لنتمكن من مساعدتك.\n"
    )
    await message.answer(help_text)

# --- Info Command ---
@router.message(Command("info"), StateFilter("*"))
async def cmd_info(message: types.Message):
    info_text = (
        "📚 <b>فكرة بوت Edu Bridge وكيفية استخدامه</b> 📚\n\n"
        "🎯 <b>الهدف:</b>\n"
        "بوت خيري لتسهيل التبرع بـ (كتب، دفاتر، نوط، مراجع جامعية، قرطاسية) لطلاب المرحلة الثانوية (البكالوريا) والجامعية، وربط المتبرعين بالمستفيدين بطريقة منظمة، مع إمكانية إرسال استفسارات لفريق الدعم الخاص بالبوت.\n\n"
        "---\n"
        "<b>🛠️ كيف يعمل البوت؟</b>\n"
        "1️⃣ <b>ابدأ بالأمر /start</b>\n"
        "اختر إذا كنت <b>متبرعًا</b>، <b>مستفيدًا</b>، أو تريد <b>الدعم</b>.\n\n"
        "2️⃣ <b>اختر المرحلة الدراسية والتخصص والمعلومات</b>\n"
        "- اختر بين مرحلة (البكالوريا) أو مرحلة (طالب جامعي).\n"
        "- اختر الفرع الدراسي أو التخصص الجامعي.\n"
        "- أدخل الاسم الكامل، المحافظة، العنوان، ومحتوى الرسالة.\n"
        "- للتواصل مع فريق البوت (الدعم): أدخل رسالة الدعم مباشرة.\n\n"
        "3️⃣ <b>اكتب محتوى رسالتك</b>\n"
        "- <b>للمتبرعين</b>: اذكر تفاصيل التبرع (مثال: دفاتر أو مراجع لفرع معلوماتية/طب، بحالة جيدة).\n"
        "- <b>للمستفيدين</b>: اذكر تفاصيل طلبك (مثال: نوطة رياضيات أو مراجع جامعية لسنة معينة).\n"
        "- <b>للدعم</b>: اكتب استفسارك أو مشكلتك بوضوح.\n"
        "📝 <b>كن دقيقًا</b>: اذكر التفاصيل بوضوح لتسهيل الربط أو الرد.\n\n"
        "4️⃣ <b>الربط أو الرد</b>\n"
        "- <b>للمتبرعين</b>: سنرسل لك معرف المستفيد المناسب عند توفر طلب مطابق.\n"
        "- <b>للمستفيدين</b>: انتظر حتى نجد متبرعًا قريبًا منك.\n"
        "<b>الفريق مسؤول عن ربط المتبرعين بالمستفيدين وسيتواصل معهم في حين تطابق طلب مع تبرع ما</b>\n"
        "- <b>للدعم</b>: سنرد عليك عبر البوت.\n"
        "---\n"
        "<b>📋 ملاحظات هامة لضمان نجاح العملية</b>\n"
        "- <b>للمتبرعين</b>:\n"
        "  - اكتب رسالة المحتوى دفعة واحدة مع كل التفاصيل.\n"
        "  - إذا تلقيت معرف مستخدم، تواصل معه مباشرة، ولا حاجة للرد على البوت.\n\n"
        "---\n"
        "<b>⚠️ تنبيه هام</b>\n"
        "هذا بوت خيري يهدف لخدمة المجتمع. يُرجى استخدامه بمسؤولية:\n"
        "- <b>ممنوع</b> التخريب أو إرسال معلومات مضللة.\n"
        "- يحق لنا حظر أي مستخدم يخالف القواعد.\n"
        "مطور البوت: @fawzys\n\n"
        "🌟 <b>نأمل أن يكون هذا البوت بداية لخير كبير ومستمر!</b> 🌟"
    )
    await message.answer(info_text)

# --- Fallback Handler (No Start) ---
@router.message(F.text, ~F.text.startswith("/"), StateFilter(None))
async def handle_no_start_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    # Ignore messages from admins in the group
    if message.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
        try:
            user_member = await message.bot.get_chat_member(message.chat.id, user_id)
            if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                return
        except Exception as e:
            logging.error(f"Failed to check admin status: {e}")

    await message.answer("⚠️ لم تبدأ عملية بعد! استخدم /start للبدء.")