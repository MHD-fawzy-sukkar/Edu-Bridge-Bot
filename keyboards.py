from aiogram import types

CANCEL_TEXT = "❌ إلغاء"

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
            [types.KeyboardButton(text=CANCEL_TEXT)]
        ],
        resize_keyboard=True
    )

def get_level_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🎒 بكالوريا"), types.KeyboardButton(text="🎓 طالب جامعي")],
            [types.KeyboardButton(text=CANCEL_TEXT)]
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
            [types.KeyboardButton(text=CANCEL_TEXT)]
        ],
        resize_keyboard=True
    )

def get_branch_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔬 علمي"), types.KeyboardButton(text="📖 أدبي")],
            [types.KeyboardButton(text="⚙️ مهني"), types.KeyboardButton(text="🕌 شرعي")],
            [types.KeyboardButton(text=CANCEL_TEXT)]
        ],
        resize_keyboard=True
    )

def get_university_specialization_keyboard():
    return types.ReplyKeyboardMarkup(
        keyboard=[
            # الكليات الطبية والتحضيرية
            [types.KeyboardButton(text="السنة التحضيرية 🩺"), types.KeyboardButton(text="طب بشري 🩺")],
            [types.KeyboardButton(text="طب أسنان 🦷"), types.KeyboardButton(text="صيدلة 💊")],
            # الهندسات والتكنولوجيا
            [types.KeyboardButton(text="هندسة معلوماتية 💻"), types.KeyboardButton(text="هندسة الحواسيب 🖥️")],
            [types.KeyboardButton(text="هندسة الاتصالات 📡"), types.KeyboardButton(text="هندسة الطاقة الكهربائية ⚡")],
            [types.KeyboardButton(text="هندسة ميكانيكية ⚙️"), types.KeyboardButton(text="هندسة طبية 🩻")],
            [types.KeyboardButton(text="هندسة مدنية 🏗️"), types.KeyboardButton(text="هندسة معمارية 🏛️")],
            [types.KeyboardButton(text="هندسة زراعية 🌾"), types.KeyboardButton(text="علوم صحية 🩹")],
            # العلوم، الاقتصاد، والعلوم الإنسانية
            [types.KeyboardButton(text="كلية العلوم 🔬"), types.KeyboardButton(text="اقتصاد 📊")],
            [types.KeyboardButton(text="حقوق ⚖️"), types.KeyboardButton(text="شريعة 📜")],
            [types.KeyboardButton(text="إعلام 🎙️"), types.KeyboardButton(text="فنون جميلة 🎨")],
            [types.KeyboardButton(text="أدب عربي 📖"), types.KeyboardButton(text="أدب إنكليزي 🔤")],
            # المعاهد التقانية
            [types.KeyboardButton(text="معهد تقاني حاسوب 💻"), types.KeyboardButton(text="معهد تقاني طبي/صحي 🧪")],
            [types.KeyboardButton(text="معهد تقاني هندسي 📐"), types.KeyboardButton(text="📌 تخصص آخر")],
            # خيارات التحكم
            [types.KeyboardButton(text=CANCEL_TEXT)]
        ],
        resize_keyboard=True
    )