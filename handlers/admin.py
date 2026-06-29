import re
import logging
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
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

    try:
        user_member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if user_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await message.reply("❌ هذا الأمر للمشرفين فقط.")
            return False
        return True
    except Exception as e:
        logging.error(f"Failed to check admin status: {e}")
        return False

# --- Direct Reply via Swipe ---
# التعديل هنا: StateFilter(None) لمنع التصادم مع أوامر الـ FSM
@router.message(F.chat.id == GROUP_ID, F.reply_to_message, F.text, ~F.text.startswith('/'), StateFilter(None))
async def direct_admin_reply(message: types.Message):
    if not await is_admin(message): 
        return

    original_text = message.reply_to_message.text or message.reply_to_message.caption
    if not original_text:
        return

    match = re.search(r'User ID:\s*(\d+)', original_text)
    if not match:
        # التعديل هنا: تم إزالة رسالة الخطأ المزعجة. البوت سيتجاهل الرسالة بصمت إذا كانت دردشة عادية بين المشرفين.
        return

    target_user_id = int(match.group(1))

    reply_text = (
        f"{message.text}\n------------------------------------------------------------\n"
        "<i>⚠️ ملاحظة: الرد على هذه الرسالة لن يصل إلينا. يرجى التواصل مباشرة مع الشخص المعني، وفي حال واجهت أي مشكلة يمكنك التواصل مع الدعم</i>"
    )
    
    try:
        await message.bot.send_message(chat_id=target_user_id, text=reply_text)
        await message.reply(f"✅ تم إرسال الرسالة بنجاح.\n👤 تمت المعالجة بواسطة المشرف: {message.from_user.full_name}")
    except Exception as e:
        await message.reply(f"❌ فشل إرسال الرسالة: {str(e)}")
        logging.error(f"Error sending reply to user {target_user_id}: {e}")

# --- Ban User ---
@router.message(Command("ban"), StateFilter("*"))
async def ban_user(message: types.Message):
    if not await is_admin(message): return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("❌ الصيغة الصحيحة: /ban [user_id]")
        return

    user_to_ban = int(args[1])
    if user_to_ban in banned_users:
        await message.reply(f"⚠️ المستخدم <code>{user_to_ban}</code> محظور بالفعل.")
        return
    
    banned_users.add(user_to_ban)
    save_banned_users(banned_users)
    await message.reply(f"🚫 تم حظر المستخدم <code>{user_to_ban}</code> من استخدام البوت.")

# --- Unban User ---
@router.message(Command("unban"), StateFilter("*"))
async def unban_user(message: types.Message):
    if not await is_admin(message): return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("❌ الصيغة الصحيحة: /unban [user_id]")
        return

    user_to_unban = int(args[1])
    if user_to_unban not in banned_users:
        await message.reply(f"⚠️ المستخدم <code>{user_to_unban}</code> غير محظور.")
        return
    
    banned_users.discard(user_to_unban)
    save_banned_users(banned_users)
    await message.reply(f"✅ تم فك الحظر عن المستخدم <code>{user_to_unban}</code>.")

# --- Reply To Command (Supercharged) ---
@router.message(Command("replyto"), StateFilter("*"))
async def start_reply_command(message: types.Message, state: FSMContext):
    if not await is_admin(message): return

    # تقسيم النص إلى 3 أجزاء كحد أقصى (الأمر، الآيدي، محتوى الرسالة إن وُجد)
    args = message.text.split(maxsplit=2)
    
    if len(args) < 2:
        await message.reply("❓ الرجاء إدخال معرف المستخدم (User ID) للرد عليه:\nمثال: <code>/replyto 123456789</code>")
        await state.set_state(AdminReplyForm.waiting_for_user_id)
        
    elif len(args) == 2:
        # إذا أدخل الآيدي فقط، ندخله في الـ FSM
        try:
            target_id = int(args[1])
            await state.update_data(target_user_id=target_id)
            await state.set_state(AdminReplyForm.waiting_for_message)
            await message.reply(f"✍️ اكتب الآن رسالتك للمستخدم User ID <code>{target_id}</code>.")
        except ValueError:
            await message.reply("❌ الرجاء إدخال معرف مستخدم صالح (رقم فقط).")
            
    else:
        # الميزة الجديدة: إذا أدخل الأمر + الآيدي + الرسالة في سطر واحد
        try:
            target_id = int(args[1])
            reply_text_content = args[2]
            
            reply_text = (
                f"{reply_text_content}\n------------------------------------------------------------\n"
                "<i>⚠️ ملاحظة: الرد على هذه الرسالة لن يصل إلينا. يرجى التواصل مباشرة مع الشخص المعني، وفي حال واجهت أي مشكلة يمكنك التواصل مع الدعم</i>"
            )
            
            await message.bot.send_message(chat_id=target_id, text=reply_text)
            await message.reply(f"✅ تم إرسال الرسالة بنجاح.\n👤 تمت المعالجة بواسطة المشرف: {message.from_user.full_name}")
            await state.clear() # تفريغ الحالة للضمان
            
        except ValueError:
            await message.reply("❌ الرجاء إدخال معرف مستخدم صالح (رقم فقط).")
        except Exception as e:
            await message.reply(f"❌ فشل إرسال الرسالة: {str(e)}")
            logging.error(f"Error sending reply to user {target_id}: {e}")

# --- Process Missing Target ID for Reply ---
@router.message(AdminReplyForm.waiting_for_user_id)
async def process_target_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("❌ الرجاء إدخال معرف مستخدم صالح (رقم فقط).")
        return
    
    target_id = int(message.text)
    await state.update_data(target_user_id=target_id)
    await state.set_state(AdminReplyForm.waiting_for_message)
    await message.reply(f"✍️ اكتب الآن رسالتك للمستخدم User ID <code>{target_id}</code>.")

# --- Process Admin Message ---
@router.message(AdminReplyForm.waiting_for_message)
async def handle_admin_reply_fsm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")

    reply_text = (
        f"{message.text}\n-------------------------------------------------------------\n"
        "<i>⚠️ ملاحظة: الرد على هذه الرسالة لن يصل إلينا. يرجى التواصل مباشرة مع الشخص المعني، وفي حال واجهت أي مشكلة يمكنك التواصل مع الدعم</i>"
    )
    try:
        await message.bot.send_message(chat_id=target_user_id, text=reply_text)
        await message.reply(f"✅ تم إرسال الرسالة بنجاح.\n👤 تمت المعالجة بواسطة المشرف: {message.from_user.full_name}")
    except Exception as e:
        await message.reply(f"❌ فشل إرسال الرسالة: {str(e)}")
        logging.error(f"Error sending reply to user {target_user_id}: {e}")
    
    await state.clear()