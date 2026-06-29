import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand, BotCommandScopeChatAdministrators
from aiogram.enums import ChatMemberStatus
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramConflictError
from aiohttp.client_exceptions import ClientConnectorError

# إعداد المتغيرات
TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002555456158
TOPIC_DONOR_ID = 2
TOPIC_BENEFICIARY_ID = 3
TOPIC_STOP = 168
ERRORS_TOPIC = 574  
SUPPORT_TOPIC = 882  
BANNED_USERS_FILE = "banned_users.json"

# إعداد البوت مع AiohttpSession
session = AiohttpSession()
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML, session=session)
dp = Dispatcher()

user_data = {}
admin_reply_sessions = {}

# دالة لإرسال تنبيهات الأخطاء إلى توبيك ERRORS_TOPIC
async def notify_admin(error_message: str):
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            message_thread_id=ERRORS_TOPIC,
            text=f"⚠️ خطأ في البوت:\n{error_message}"
        )
    except Exception as e:
        print(f"❌ فشل إرسال تنبيه الخطأ: {e}")

# دالة مساعدة لإعادة المحاولة
async def retry(func, max_attempts=3, delay=0.5):
    last_exception = None
    for attempt in range(max_attempts):
        try:
            return await func()
        except ClientConnectorError as e:
            last_exception = e
            print(f"⚠️ محاولة {attempt + 1} فشلت: {e}")
            await notify_admin(f"ClientConnectorError في المحاولة {attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay * (2 ** attempt))  # تأخير متزايد
    raise last_exception

# === الحظر ===
def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        return set()
    with open(BANNED_USERS_FILE, "r") as f:
        return set(json.load(f))

def save_banned_users(banned_users):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(list(banned_users), f)

banned_users = load_banned_users()

# === /start ===
@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    if user_id in user_data:
        await message.answer(
            "⚠️ أنت بالفعل في عملية إرسال رسالة. للبدء من جديد، استخدم /stop لإلغاء العملية الحالية."
        )
        return

    start_msg = (
        f"✅ المستخدم <b>{message.from_user.full_name}</b> "
        f"(@{message.from_user.username or '❌ لا يوجد'})\n"
        f"ID: <code>{user_id}</code>\n"
        "بدأ تفاعل جديد مع البوت."
    )
    try:
        await retry(lambda: bot.send_message(chat_id=GROUP_ID, message_thread_id=TOPIC_STOP, text=start_msg))
    except Exception as e:
        await notify_admin(f"فشل إرسال رسالة بدء التفاعل: {e}")
        print(f"⚠️ فشل إرسال رسالة بدء التفاعل: {e}")

    await message.answer(
        "👋 مرحباً بك في بوت <b>Edu Bridge</b>!\n"
        "نحن هنا لنوصل رسالتك إلى الجهة المناسبة.\n"
        "استخدم الأمر /help لقراءة دليل الاستخدام\n"
        "أو /info لفهم فكرة البوت وكيفية استخدامه.\n"
        "اختر أحد الخيارات أدناه للمتابعة:"
    )
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🤝 أنا متبرع")],
            [types.KeyboardButton(text="📬 أنا مستفيد")],
            [types.KeyboardButton(text="📧 الدعم")]
        ],
        resize_keyboard=True
    )
    await message.answer("⬇️ الرجاء اختيار نوع المستخدم:", reply_markup=keyboard)

# === اختيار نوع المستخدم ===
@dp.message(F.text.in_(["📬 أنا مستفيد", "🤝 أنا متبرع", "📧 الدعم"]))
async def choose_user_type(message: Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    user_data[user_id] = {
        "type": "donor" if "متبرع" in message.text else "beneficiary" if "مستفيد" in message.text else "support"
    }

    if user_data[user_id]["type"] == "support":
        await message.answer(
            "🔗 ما هو اسم المستخدم الخاص بك على تيليغرام؟ (مثال: @Username)",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer("📝 ما اسمك الكامل؟", reply_markup=types.ReplyKeyboardRemove())

# === جمع البيانات بالتسلسل مع فحص الأوامر ===
@dp.message(F.from_user.id.in_(user_data), ~F.text.startswith(("/start", "/stop", "/help", "/info")))
async def collect_user_data(message: Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    data = user_data[user_id]

    if data["type"] in ["donor", "beneficiary"]:
        if "name" not in data:
            data["name"] = message.text
            data["telegram_name"] = message.from_user.full_name

            username = message.from_user.username

            if username is None:
                user_data.pop(user_id, None)
                await message.answer(
                    "❌ لا يوجد اسم مستخدم (Username) على حسابك.\n\n"
                    "لا يمكن متابعة الطلب بدون اسم مستخدم، لأننا نستخدمه لربط المتبرعين بالمستفيدين.\n\n"
                    "لإضافة اسم مستخدم:\n"
                    "1. افتح تيليغرام.\n"
                    "2. ادخل إلى Settings.\n"
                    "3. اختر Username.\n"
                    "4. أضف اسم مستخدم ثم أرسل /start من جديد."
                )
                return
                data["username"] = f"@{username}"
                await message.answer("📍 ما هو عنوانك؟ (مثال: دمشق - باب توما)")
        elif "title" not in data:
            data["title"] = message.text
            await message.answer("✉️ الرجاء كتابة محتوى رسالتك بالتفصيل:")
        elif "content" not in data:
            data["content"] = message.text
            topic_id = TOPIC_DONOR_ID if data["type"] == "donor" else TOPIC_BENEFICIARY_ID
            final_msg = (
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
                f"📨 <b>رسالة جديدة من {'متبرع' if data['type'] == 'donor' else 'مستفيد'}</b>\n\n"
                f"👤 <b>الاسم الذي أدخله:</b> {data['name']}\n"
                f"📱 <b>اسم الحساب:</b> {data['telegram_name']}\n"
                f"🔗 <b>Username:</b> {data['username']}\n"
                f"📍 <b>العنوان:</b> {data['title']}\n"
                f"✉️ <b>المحتوى:</b>\n{data['content']}"
            )
            try:
                await retry(lambda: bot.send_message(GROUP_ID, final_msg, message_thread_id=topic_id))
                await message.answer("✅ تم إرسال رسالتك بنجاح. شكراً لتواصلك معنا.")
            except Exception as e:
                await message.answer(
                    "❌ حدث خطأ أثناء إرسال الرسالة.\n"
                    "📧 أرسل رسالة دعم باستخدام /start واختيار 'الدعم'."
                )
                print(f"❌ Error sending message to group: {e}")
            user_data.pop(user_id, None)
    elif data["type"] == "support":
        if "username" not in data:
            data["telegram_name"] = message.from_user.full_name

            username = message.from_user.username

            if username is None:
                user_data.pop(user_id, None)
                await message.answer(
                    "❌ لا يوجد اسم مستخدم (Username) على حسابك.\n\n"
                    "يرجى إضافة Username من إعدادات تيليغرام ثم إعادة المحاولة باستخدام /start."
                )
                return

            data["username"] = f"@{username}"
            await message.answer("📧 اكتب رسالتك:")
        elif "content" not in data:
            data["content"] = message.text
            final_msg = (
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
                f"📱 <b>اسم الحساب:</b> {data['telegram_name']}\n"
                f"🔗 <b>Username:</b> {data['username']}\n"
                f"📧 <b>رسالة الدعم:</b>\n{data['content']}"
            )
            try:
                await retry(lambda: bot.send_message(GROUP_ID, final_msg, message_thread_id=SUPPORT_TOPIC))
                await message.answer("✅ تم إرسال الرسالة بنجاح. شكراً لتواصلك معنا.")
            except Exception as e:
                await message.answer(
                    "❌ حدث خطأ أثناء إرسال الرسالة.\n"
                    "📧 أرسل رسالة دعم باستخدام /start واختيار 'الدعم'."
                )
                print(f"❌ Error sending support message: {e}")
            user_data.pop(user_id, None)

# === /stop ===
@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data.pop(user_id)
        await message.answer("🛑 تم إلغاء العملية. يمكنك البدء من جديد باستخدام\n/start")
    else:
        await message.answer("🛑 لا توجد عملية جارية. يمكنك البدء باستخدام /start")

# === /help ===
@dp.message(Command("help"))
async def cmd_help(message: Message):
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
        "2️⃣ أدخل اسم المستخدم يدويًا (يبدأ بـ @).\n"
        "3️⃣ أدخل معلوماتك (الاسم، العنوان، المحتوى) إذا كنت متبرعًا أو مستفيدًا.\n"
        "4️⃣ للدعم، اكتب رسالتك مباشرة بعد إدخال اسم المستخدم.\n\n"
        "✍️ <b>نصيحة</b>: اكتب رسالتك بوضوح لنتمكن من مساعدتك.\n"
        "📧 لأي استفسار، أرسل رسالة دعم باستخدام /start واختيار 'الدعم'."
    )
    await message.answer(help_text)

# === /info ===
@dp.message(Command("info"))
async def cmd_info(message: Message):
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
        "- أدخل اسم المستخدم يدويًا (يبدأ بـ @).\n"
        "- للمتبرعين والمستفيدين: أدخل الاسم الكامل، العنوان، ومحتوى الرسالة.\n"
        "- للدعم: أدخل اسم المستخدم ثم رسالة الدعم.\n\n"
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
        "  - إذا كان المصدر (دفتر أو نوطة) بجودة عالية، قم بتحويله إلى PDF قبل التبرع.\n"
        "- <b>للجميع</b>:\n"
        "  - أدخل اسم المستخدم يدويًا وبدقة (يبدأ بـ @).\n"
        "  - اكتب رسالة المحتوى دفعة واحدة مع كل التفاصيل.\n"
        "  - إذا تلقيت معرف مستخدم، تواصل معه مباشرة، ولا ترد على البوت.\n"
        "  - لأي استفسار، أرسل رسالة دعم باستخدام /start واختيار 'الدعم'.\n\n"
        "---\n"
        "<b>⚠️ تنبيه هام</b>\n"
        "هذا بوت خيري يهدف لخدمة المجتمع. يُرجى استخدامه بمسؤولية:\n"
        "- <b>ممنوع</b> التخريب أو إرسال معلومات مضللة.\n"
        "- يحق لنا حظر أي مستخدم يخالف القواعد.\n"
        "- نعمل بجد لضمان سير العملية بسلاسة، ونتمنى منكم التعاون.\n"
        "مطور البوت: @fawzys\n\n"
        "🌟 <b>نأمل أن يكون هذا البوت بداية لخير كبير ومستمر!</b> 🌟"
    )
    await message.answer(info_text)

# === /ban ===
@dp.message(F.text.regexp(r'^/ban\s+\d+$'))
async def ban_user(message: Message):
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        await message.reply("❌ استخدم هذا الأمر داخل القروب.")
        return

    user_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("❌ هذا الأمر للمشرفين فقط.")
        return

    args = message.text.split()
    user_to_ban = int(args[1])
    if user_to_ban in banned_users:
        await message.reply(f"⚠️ المستخدم <code>{user_to_ban}</code> محظور بالفعل.")
        return
    banned_users.add(user_to_ban)
    save_banned_users(banned_users)
    await message.reply(f"🚫 تم حظر المستخدم <code>{user_to_ban}</code> من استخدام البوت.")

# === /unban ===
@dp.message(F.text.regexp(r'^/unban\s+\d+$'))
async def unban_user(message: Message):
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        await message.reply("❌ استخدم هذا الأمر داخل القروب.")
        return

    user_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("❌ هذا الأمر للمشرفين فقط.")
        return

    args = message.text.split()
    user_to_unban = int(args[1])
    if user_to_unban not in banned_users:
        await message.reply(f"⚠️ المستخدم <code>{user_to_unban}</code> غير محظور.")
        return
    banned_users.discard(user_to_unban)
    save_banned_users(banned_users)
    await message.reply(f"✅ تم فك الحظر عن المستخدم <code>{user_to_unban}</code>.")

# === /replyto ===
@dp.message(Command("replyto"))
async def start_reply_command(message: Message):
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        await message.reply("❌ استخدم هذا الأمر داخل القروب.")
        return

    user_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("❌ هذا الأمر للمشرفين فقط.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("❓ الرجاء إدخال معرف المستخدم (User ID) للرد عليه:")
        admin_reply_sessions[message.from_user.id] = None
    else:
        try:
            target_id = int(args[1])
            admin_reply_sessions[message.from_user.id] = target_id
            await message.reply(f"✍️ اكتب الآن رسالتك للمستخدم <code>{target_id}</code>.")
        except ValueError:
            await message.reply("❌ الرجاء إدخال معرف مستخدم صالح (رقم فقط).")

# === رد مشرف بعد /replyto ===
@dp.message(F.text, F.from_user.id.in_(admin_reply_sessions))
async def handle_admin_reply(message: Message):
    admin_id = message.from_user.id
    target_user_id = admin_reply_sessions[admin_id]

    if target_user_id is None:
        if not message.text.isdigit():
            await message.reply("❌ الرجاء إدخال معرف مستخدم صالح (رقم فقط).")
            return
        target_user_id = int(message.text)
        admin_reply_sessions[admin_id] = target_user_id
        await message.reply(f"✍️ اكتب الآن رسالتك للمستخدم <code>{target_user_id}</code>.")
        return

    reply_text = (
        f"{message.text}\n"
        "<i>⚠️ ملاحظة: الرد على هذه الرسالة لن يصل إلينا. يرجى التواصل مباشرة مع الشخص المعني، وفي حال واجهت أي مشكلة يمكنك التواصل مع الدعم</i>"
    )
    try:
        await retry(lambda: bot.send_message(chat_id=target_user_id, text=reply_text))
        await message.reply("✅ تم إرسال الرسالة بنجاح.")
    except Exception as e:
        await message.reply(f"❌ فشل إرسال الرسالة: {str(e)}")
        print(f"❌ Error sending reply to user {target_user_id}: {e}")
    admin_reply_sessions.pop(admin_id, None)

# === معالجة الأوامر الناقصة (/ban, /unban) ===
@dp.message(F.text.regexp(r'^/(ban|unban)(\s+.*)?$'))
async def handle_incomplete_command(message: Message):
    command = message.text.split()[0]
    await message.reply(f"❌ الصيغة: {command} [user_id]")

# === معالجة الرسائل بدون /start ===
@dp.message(F.text, ~F.from_user.id.in_(user_data), ~F.text.startswith(("/start", "/stop", "/help", "/info")))
async def handle_no_start_message(message: Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    # فحص إذا المستخدم مشرف في القروب
    if message.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
        try:
            user_member = await bot.get_chat_member(message.chat.id, user_id)
            if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                return  # لا ترد على المشرفين
        except Exception as e:
            await notify_admin(f"فشل فحص حالة المشرف للمستخدم {user_id}: {e}")
            print(f"⚠️ فشل فحص حالة المشرف: {e}")

    await message.answer("⚠️ لم تبدأ عملية بعد! استخدم /start للبدء.")

# === set commands ===
async def set_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command="start", description="بدء الاستخدام"),
        types.BotCommand(command="stop", description="إلغاء العملية الحالية"),
        types.BotCommand(command="help", description="عرض التعليمات"),
        types.BotCommand(command="info", description="معلومات حول فكرة البوت وكيفية استخدامه")
    ])
    await bot.set_my_commands([
        types.BotCommand(command="start", description="بدء الاستخدام"),
        types.BotCommand(command="stop", description="إلغاء العملية الحالية"),
        types.BotCommand(command="help", description="عرض التعليمات"),
        types.BotCommand(command="info", description="معلومات حول فكرة البوت وكيفية استخدامه"),
        types.BotCommand(command="ban", description="حظر مستخدم من البوت"),
        types.BotCommand(command="unban", description="إلغاء الحظر"),
        types.BotCommand(command="replyto", description="الرد على مستخدم")
    ], scope=types.BotCommandScopeChatAdministrators(chat_id=GROUP_ID))

# === التشغيل ===
async def main():
    print("✅ Bot is running...")
    try:
        await bot.delete_webhook()  # إلغاء أي Webhook موجود
        await set_commands(bot)
        await dp.start_polling(bot)
    except TelegramConflictError as e:
        await notify_admin(f"TelegramConflictError عند بدء البوت: {e}")
        raise
    except Exception as e:
        await notify_admin(f"خطأ عام عند بدء البوت: {e}")
        raise
    finally:
        await bot.session.close()  # إغلاق الـ session بشكل صحيح

if __name__ == "__main__":
    asyncio.run(main())