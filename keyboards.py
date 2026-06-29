from aiogram import types

def get_main_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🤝 أنا متبرع"), types.KeyboardButton(text="📬 أنا مستفيد")],
            [types.KeyboardButton(text="📧 الدعم")]
        ],
        resize_keyboard=True
    )

def get_cancel_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="❌ إلغاء")]
        ],
        resize_keyboard=True
    )