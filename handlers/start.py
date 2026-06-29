from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import get_main_keyboard
from states import RequestForm, SupportForm
from services.banned import banned_users
from config import GROUP_ID, STOP_TOPIC

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    # Clear any previous FSM state
    await state.clear()

    start_msg = (
        f"✅ المستخدم <b>{message.from_user.full_name}</b> "
        f"(@{message.from_user.username or '❌ لا يوجد'})\n"
        f"ID: <code>{user_id}</code>\n"
        "بدأ تفاعل جديد مع البوت."
    )
    try:
        # Send interaction alert to the admin group
        await message.bot.send_message(chat_id=GROUP_ID, message_thread_id=STOP_TOPIC, text=start_msg)
    except Exception as e:
        print(f"Failed to send start interaction message: {e}")

    await message.answer(
        "👋 مرحباً بك في بوت <b>Edu Bridge</b>!\n"
        "نحن هنا لنوصل رسالتك إلى الجهة المناسبة.\n"
        "استخدم الأمر /help لقراءة دليل الاستخدام\n"
        "أو /info لفهم فكرة البوت وكيفية استخدامه.\n"
        "اختر أحد الخيارات أدناه للمتابعة:",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text.in_(["🤝 أنا متبرع", "📬 أنا مستفيد"]))
async def choose_request_type(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    username = message.from_user.username
    if not username:
        await message.answer(
            "❌ لا يوجد اسم مستخدم (Username) على حسابك.\n\n"
            "لا يمكن متابعة الطلب بدون اسم مستخدم، لأننا نستخدمه لربط المتبرعين بالمستفيدين.\n\n"
            "لإضافة اسم مستخدم:\n"
            "1. افتح تيليغرام.\n"
            "2. ادخل إلى Settings.\n"
            "3. اختر Username.\n"
            "4. أضف اسم مستخدم ثم أرسل /start من جديد.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    # Store user type and username in FSM storage
    user_type = "donor" if "متبرع" in message.text else "beneficiary"
    await state.update_data(type=user_type, username=f"@{username}", telegram_name=message.from_user.full_name)
    
    # Move to the first step of the form
    await state.set_state(RequestForm.waiting_for_name)
    await message.answer("📝 ما اسمك الكامل؟", reply_markup=types.ReplyKeyboardRemove())

# Handle Support Option
@router.message(F.text == "📧 الدعم")
async def choose_support_type(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    username = message.from_user.username
    if not username:
        await message.answer(
            "❌ لا يوجد اسم مستخدم (Username) على حسابك.\n\n"
            "يرجى إضافة Username من إعدادات تيليغرام ثم إعادة المحاولة باستخدام /start.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    # Store support data and move to content state
    await state.update_data(username=f"@{username}", telegram_name=message.from_user.full_name)
    await state.set_state(SupportForm.waiting_for_content)
    await message.answer("📧 اكتب رسالتك:", reply_markup=types.ReplyKeyboardRemove())