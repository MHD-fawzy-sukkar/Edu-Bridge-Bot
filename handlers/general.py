from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType, ChatMemberStatus

from services.banned import banned_users

router = Router()

# --- Stop Command ---
@router.message(Command("stop"))
async def cmd_stop(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("🛑 لا توجد عملية جارية. يمكنك البدء باستخدام /start")
        return

    # Clear FSM state
    await state.clear()
    await message.answer("🛑 تم إلغاء العملية. يمكنك البدء من جديد باستخدام\n/start")

# --- Help Command ---
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📘 <b>دليل استخدام بوت Edu Bridge</b>\n\n"
        "🤖 هذا البوت مخصص لتسهيل التواصل بين المتبرعين والمستفيدين.\n\n"
        "🛠️ <b>الأوامر المتاحة</b>:\n"
        "/start - بدء إرسال رسالة جديدة\n"
        "/stop - إلغاء العملية الحالية\n"
        "/help - عرض هذه التعليمات\n"
        "/info - شرح فكرة البوت وكيفية استخدامه بالتفصيل\n\n"
        "📌 <b>خطوات الاستخدام</b>:\n"
        "1️⃣ استخدم /start لاختيار <b>متبرع</b>، <b>مستفيد</b>، أو <b>الدعم</b>.\n"
        "2️⃣ أدخل معلوماتك (الاسم، العنوان، المحتوى) إذا كنت متبرعًا أو مستفيدًا.\n"
        "3️⃣ للدعم، اكتب رسالتك مباشرة.\n\n"
        "✍️ <b>نصيحة</b>: اكتب رسالتك بوضوح لنتمكن من مساعدتك.\n"
        "📧 لأي استفسار، أرسل رسالة دعم باستخدام /start واختيار 'الدعم'."
    )
    await message.answer(help_text)

# --- Info Command ---
@router.message(Command("info"))
async def cmd_info(message: types.Message):
    info_text = (
        "📚 <b>فكرة بوت Edu Bridge وكيفية استخدامه</b> 📚\n\n"
        "🎯 <b>الهدف:</b>\n"
        "بوت خيري لتسهيل التبرع بـ (كتب، دفاتر، نوط، قرطاسية) للطلاب المحتاجين، وربط المتبرعين بالمستفيدين بطريقة منظمة، مع إمكانية إرسال استفسارات الدعم.\n\n"
        "---\n"
        "<b>🛠️ كيف يعمل البوت؟</b>\n"
        "البوت مقسم إلى ثلاثة أقسام: <b>متبرعين</b>، <b>مستفيدين</b>، و<b>الدعم</b>. إليك الخطوات:\n\n"
        "1️⃣ <b>ابدأ بالأمر /start</b>\n"
        "اختر إذا كنت <b>متبرعًا</b>، <b>مستفيدًا</b>، أو تريد <b>الدعم</b>.\n\n"
        "2️⃣ <b>أدخل معلوماتك</b>\n"
        "- للمتبرعين والمستفيدين: أدخل الاسم الكامل، العنوان، ومحتوى الرسالة.\n"
        "- للدعم: أدخل رسالة الدعم مباشرة.\n\n"
        "3️⃣ <b>اكتب محتوى رسالتك</b>\n"
        "- <b>للمتبرعين</b>: اذكر تفاصيل التبرع (مثال: دفتر عربي للأستاذ رامي، بحالة جيدة).\n"
        "- <b>للمستفيدين</b>: اذكر ما تحتاجه بدقة (مثال: نوطة رياضيات للأستاذ محمد).\n"
        "- <b>للدعم</b>: اكتب استفسارك أو مشكلتك بوضوح.\n"
        "📝 <b>كن دقيقًا</b>: اذكر التفاصيل بوضوح لتسهيل الربط أو الرد.\n\n"
        "4️⃣ <b>الربط أو الرد</b>\n"
        "- <b>للمتبرعين</b>: سنرسل لك معرف المستفيد المناسب عند توفر طلب مطابق.\n"
        "- <b>للمستفيدين</b>: انتظر حتى نجد متبرعًا قريبًا منك.\n"
        "- <b>للدعم</b>: سنرد عليك عبر البوت.\n"
        "📬 سنتولى عملية الربط أو الرد، تواصل معنا عبر البوت.\n\n"
        "---\n"
        "<b>📋 ملاحظات هامة لضمان نجاح العملية</b>\n"
        "- <b>للمتبرعين</b>:\n"
        "  - لا تتبرع بمواد تالفة جدًا أو ناقصة، تأكد أن تكون مفيدة فعلاً.\n"
        "  - إذا كان المصدر بجودة عالية، قم بتحويله إلى PDF قبل التبرع.\n"
        "- <b>للجميع</b>:\n"
        "  - اكتب رسالة المحتوى دفعة واحدة مع كل التفاصيل.\n"
        "  - إذا تلقيت معرف مستخدم، تواصل معه مباشرة، ولا ترد على البوت.\n\n"
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
@router.message(F.text, ~F.text.startswith("/"))
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
            print(f"Failed to check admin status: {e}")

    # Check if the user is in an active FSM state
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("⚠️ لم تبدأ عملية بعد! استخدم /start للبدء.")