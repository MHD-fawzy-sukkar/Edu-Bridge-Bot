import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

TOKEN = "8251440358:AAGRc64aVPY-jgCmCs-uJyiudwaGguPMhr4"
GROUP_ID = -1002555456158
TOPIC_DONOR_ID = 2
TOPIC_BENEFICIARY_ID = 3
TOPIC_STOP = 168
BANNED_USERS_FILE = "banned_users.json"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

user_data = {}
admin_reply_sessions = {}

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
    if message.from_user.id in banned_users:
        return

    await message.answer(
        "👋 مرحباً بك في بوت <b>Edu Bridge</b>!\n"
        "نحن هنا لنوصل رسالتك إلى الجهة المناسبة.\n"
        "استخدم الأمر /help لقراءة دليل الاستخدام\n"
        "اختر أحد الخيارات أدناه للمتابعة:"
    )
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🤝 أنا متبرع")],
            [types.KeyboardButton(text="📬 أنا مستفيد")]
        ],
        resize_keyboard=True
    )
    await message.answer("⬇️ الرجاء اختيار نوع المستخدم:", reply_markup=keyboard)

# === اختيار نوع المستخدم ===
@dp.message(F.text.in_(["📬 أنا مستفيد", "🤝 أنا متبرع"]))
async def choose_user_type(message: Message):
    if message.from_user.id in banned_users:
        return

    user_data[message.from_user.id] = {
        "type": "donor" if "متبرع" in message.text else "beneficiary"
    }
    await message.answer("📝 ما اسمك الكامل؟")

# === جمع البيانات بالتسلسل ===
@dp.message(F.text, F.from_user.id.in_(user_data))
async def collect_user_data(message: Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        return

    data = user_data[user_id]

    if "name" not in data:
        data["name"] = message.text
        await message.answer("🔗 ما هو اسم المستخدم الخاص بك على تيليجرام؟")
    elif "username" not in data:
        data["username"] = message.text.strip() or "❌ لا يوجد"
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
            f"👤 <b>الاسم:</b> {data['name']}\n"
            f"🔗 <b>Username:</b> {data['username']}\n"
            f"📍 <b>العنوان:</b> {data['title']}\n"
            f"✉️ <b>المحتوى:</b>\n{data['content']}"
        )

        try:
            await bot.send_message(GROUP_ID, final_msg, message_thread_id=topic_id)
            await message.answer("✅ تم إرسال رسالتك بنجاح. شكراً لتواصلك معنا.")
        except Exception as e:
            await message.answer("❌ حدث خطأ أثناء إرسال الرسالة.")
            print(f"❌ Error: {e}")

        user_data.pop(user_id, None)

# === /stop ===
@dp.message(Command("stop"))
async def cmd_stop(message: Message):
    user = message.from_user
    user_id = user.id
    full_name = user.full_name
    username = f"@{user.username}" if user.username else "❌ لا يوجد"

    if user_id in user_data:
        user_data.pop(user_id)

    stop_msg = (
        f"🚫 المستخدم <b>{full_name}</b> ({username})\n"
        f"ID: <code>{user_id}</code>\n"
        "قام بإيقاف العملية."
    )
    await bot.send_message(chat_id=GROUP_ID, message_thread_id=TOPIC_STOP, text=stop_msg)
    await message.answer("🛑 تم إلغاء العملية. يمكنك البدء من جديد باستخدام /start.")

# === /help ===
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📘 <b>دليل استخدام بوت Edu Bridge</b>\n\n"
        "🤖 هذا البوت مخصص لتسهيل التواصل بين المتبرعين والمستفيدين.\n\n"
        "🛠️ الأوامر:\n"
        "/start - بدء إرسال رسالة جديدة\n"
        "/stop - إلغاء العملية الحالية\n"
        "/help - عرض هذه الرسالة\n\n"
        "📌 خطوات الاستخدام:\n"
        "1️⃣ اختر <b>متبرع</b> أو <b>مستفيد</b>\n"
        "2️⃣ أدخل معلوماتك بشكل واضح\n"
        "3️⃣ تأكد من أن اسم المستخدم ظاهر في حسابك\n\n"
        "✍️ <b>اجعل رسالتك واضحة ومباشرة لنتمكن من مساعدتك بشكل صحيح.</b>\n\n"
        "📬 سنرد عليك بأقرب وقت، أو يمكنك التواصل مع مشرف البوت: @fawzys"
    )
    await message.answer(help_text)


# === /ban ===
@dp.message(Command("ban"))
async def ban_user(message: Message):
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        await message.reply("❌ استخدم هذا الأمر داخل القروب.")
        return

    user_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("❌ هذا الأمر للمشرفين فقط.")
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply("❌ الصيغة: /ban [user_id]")
        return

    user_to_ban = int(args[1])
    banned_users.add(user_to_ban)
    save_banned_users(banned_users)
    await message.reply(f"🚫 تم حظر المستخدم <code>{user_to_ban}</code> من استخدام البوت.")

# === /unban ===
@dp.message(Command("unban"))
async def unban_user(message: Message):
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        await message.reply("❌ استخدم هذا الأمر داخل القروب.")
        return

    user_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("❌ هذا الأمر للمشرفين فقط.")
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply("❌ الصيغة: /unban [user_id]")
        return

    user_to_unban = int(args[1])
    banned_users.discard(user_to_unban)
    save_banned_users(banned_users)
    await message.reply(f"✅ تم فك الحظر عن المستخدم <code>{user_to_unban}</code>.")

# === /replyto ===
@dp.message(Command("replyto"))
async def start_reply_command(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply("❌ الصيغة: /replyto [user_id]")
        return

    user_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("❌ هذا الأمر للمشرفين فقط.")
        return

    target_id = int(args[1])
    admin_reply_sessions[message.from_user.id] = target_id
    await message.reply(f"✍️ اكتب الآن رسالتك للمستخدم <code>{target_id}</code>.")

# === رد مشرف بعد /replyto ===
@dp.message(F.text)
async def handle_admin_reply(message: Message):
    admin_id = message.from_user.id
    if admin_id in admin_reply_sessions:
        target_user_id = admin_reply_sessions.pop(admin_id)
        try:
            await bot.send_message(chat_id=target_user_id, text=message.text)
            await message.reply("✅ تم إرسال الرسالة.")
        except:
            await message.reply("❌ لم أتمكن من إرسال الرسالة.")

# === set commands
async def set_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command="start", description="بدء الاستخدام"),
        types.BotCommand(command="stop", description="إلغاء العملية الحالية"),
        types.BotCommand(command="help", description="عرض التعليمات")
    ])
    await bot.set_my_commands([
        types.BotCommand(command="start", description="بدء الاستخدام"),
        types.BotCommand(command="stop", description="إلغاء العملية الحالية"),
        types.BotCommand(command="help", description="عرض التعليمات"),
        types.BotCommand(command="ban", description="حظر مستخدم من البوت"),
        types.BotCommand(command="unban", description="إلغاء الحظر"),
        types.BotCommand(command="replyto", description="الرد على مستخدم")
    ], scope=types.BotCommandScopeChatAdministrators(chat_id=GROUP_ID))

# === التشغيل
async def main():
    print("✅ Bot is running...")
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
