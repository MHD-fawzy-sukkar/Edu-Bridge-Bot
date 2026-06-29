import re
import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.enums import ChatType, ChatMemberStatus
from aiogram.fsm.context import FSMContext

from services.banned import banned_users, save_banned_users
from states import AdminReplyForm
from config import GROUP_ID

router = Router()

# Helper function to check if the user is an admin in the group
async def is_admin(message: types.Message) -> bool:
    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        await message.reply("❌ استخدم هذا الأمر داخل القروب.")
        return False

    user_member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("❌ هذا الأمر للمشرفين فقط.")
        return False
    
    return True

# --- Direct Reply via Swipe ---
@router.message(F.chat.id == GROUP_ID, F.reply_to_message, F.text)
async def direct_admin_reply(message: types.Message):
    # لا نرد إذا كان المشرف يكتب أمراً مثل /ban
    if message.text.startswith('/'):
        return

    # التحقق من أن من قام بالرد هو مشرف فعلاً
    if not await is_admin(message): 
        return

    # جلب نص الرسالة التي قام المشرف بالرد عليها
    original_text = message.reply_to_message.text or message.reply_to_message.caption
    if not original_text:
        return

    # استخراج الـ User ID من الرسالة الأصلية باستخدام Regex
    match = re.search(r'User ID:\s*(\d+)', original_text)
    if not match:
        # إذا لم يجد ID (بمعنى أن المشرف رد على رسالة عادية بالجروب)، يتجاهلها البوت بصمت
        return

    target_user_id = int(match.group(1))

    reply_text = (
        f"{message.text}\n"
        "<i>⚠️ ملاحظة: الرد على هذه الرسالة لن يصل إلينا. يرجى التواصل مباشرة مع الشخص المعني، وفي حال واجهت أي مشكلة يمكنك التواصل مع الدعم</i>"
    )
    
    try:
        await message.bot.send_message(chat_id=target_user_id, text=reply_text)
        await message.reply(f"✅ تم إرسال الرسالة بنجاح.\n👤 تمت المعالجة بواسطة المشرف: {message.from_user.full_name}")
    except Exception as e:
        await message.reply(f"❌ فشل إرسال الرسالة: {str(e)}")
        logging.error(f"Error sending reply to user {target_user_id}: {e}")

# --- Ban User ---
@router.message(F.text.regexp(r'^/ban\s+\d+$'))
async def ban_user(message: types.Message):
    if not await is_admin(message): return

    user_to_ban = int(message.text.split()[1])
    if user_to_ban in banned_users:
        await message.reply(f"⚠️ المستخدم <code>{user_to_ban}</code> محظور بالفعل.")
        return
    
    banned_users.add(user_to_ban)
    save_banned_users(banned_users)
    await message.reply(f"🚫 تم حظر المستخدم <code>{user_to_ban}</code> من استخدام البوت.")

# --- Unban User ---
@router.message(F.text.regexp(r'^/unban\s+\d+$'))
async def unban_user(message: types.Message):
    if not await is_admin(message): return

    user_to_unban = int(message.text.split()[1])
    if user_to_unban not in banned_users:
        await message.reply(f"⚠️ المستخدم <code>{user_to_unban}</code> غير محظور.")
        return
    
    banned_users.discard(user_to_unban)
    save_banned_users(banned_users)
    await message.reply(f"✅ تم فك الحظر عن المستخدم <code>{user_to_unban}</code>.")

# --- Reply To Command (Fallback) ---
@router.message(Command("replyto"))
async def start_reply_command(message: types.Message, state: FSMContext):
    if not await is_admin(message): return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("❓ الرجاء إدخال معرف المستخدم (User ID) للرد عليه:")
        await state.set_state(AdminReplyForm.waiting_for_user_id)
    else:
        try:
            target_id = int(args[1])
            await state.update_data(target_user_id=target_id)
            await state.set_state(AdminReplyForm.waiting_for_message)
            await message.reply(f"✍️ اكتب الآن رسالتك للمستخدم <code>{target_id}</code>.")
        except ValueError:
            await message.reply("❌ الرجاء إدخال معرف مستخدم صالح (رقم فقط).")

# --- Process Missing Target ID for Reply ---
@router.message(AdminReplyForm.waiting_for_user_id)
async def process_target_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("❌ الرجاء إدخال معرف مستخدم صالح (رقم فقط).")
        return
    
    target_id = int(message.text)
    await state.update_data(target_user_id=target_id)
    await state.set_state(AdminReplyForm.waiting_for_message)
    await message.reply(f"✍️ اكتب الآن رسالتك للمستخدم <code>{target_id}</code>.")

# --- Process Admin Message ---
@router.message(AdminReplyForm.waiting_for_message)
async def handle_admin_reply_fsm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")

    reply_text = (
        f"{message.text}\n"
        "<i>⚠️ ملاحظة: الرد على هذه الرسالة لن يصل إلينا. يرجى التواصل مباشرة مع الشخص المعني، وفي حال واجهت أي مشكلة يمكنك التواصل مع الدعم</i>"
    )
    try:
        await message.bot.send_message(chat_id=target_user_id, text=reply_text)
        await message.reply(f"✅ تم إرسال الرسالة بنجاح.\n👤 تمت المعالجة بواسطة المشرف: {message.from_user.full_name}")
    except Exception as e:
        await message.reply(f"❌ فشل إرسال الرسالة: {str(e)}")
        logging.error(f"Error sending reply to user {target_user_id}: {e}")
    
    await state.clear()

# --- Handle Incomplete Admin Commands ---
@router.message(F.text.regexp(r'^/(ban|unban)(\s+.*)?$'))
async def handle_incomplete_command(message: types.Message):
    command = message.text.split()[0]
    await message.reply(f"❌ الصيغة: {command} [user_id]")