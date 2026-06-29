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

def get_governorates_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="دمشق"), types.KeyboardButton(text="ريف دمشق"), types.KeyboardButton(text="حلب")],
            [types.KeyboardButton(text="حمص"), types.KeyboardButton(text="حماة"), types.KeyboardButton(text="اللاذقية")],
            [types.KeyboardButton(text="طرطوس"), types.KeyboardButton(text="درعا"), types.KeyboardButton(text="السويداء")],
            [types.KeyboardButton(text="إدلب"), types.KeyboardButton(text="القنيطرة"), types.KeyboardButton(text="دير الزور")],
            [types.KeyboardButton(text="الرقة"), types.KeyboardButton(text="الحسكة")],
            [types.KeyboardButton(text="❌ إلغاء")]
        ],
        resize_keyboard=True
    )