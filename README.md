# Edu Bridge Telegram Bot 🤖🌉

هذا بوت بسيط مصمم لتجميع رسائل المتبرعين والمستفيدين في غروب تيلغرام باستخدام التوبيكات.  
يعتمد على مكتبة `aiogram` (أحد أشهر أطر عمل Bots بلغة Python).

## المتطلبات الأساسية

- Python 3.10+
- مكتبة aiogram v2
- إنشاء بوت من [BotFather](https://t.me/botfather)
- غروب Telegram مفعل عليه Topics (يجب أن يكون Supergroup)

## التشغيل

1. ثبت المكتبات:
```bash
pip install aiogram
```

2. عدّل ملف `main.py`:
- ضع التوكن في `BOT_TOKEN`
- غيّر `GROUP_ID` إلى رقم الغروب
- عدل `TOPIC_DONOR_ID` و `TOPIC_BENEF_ID` إلى أرقام التوبيكات

3. شغل البوت:
```bash
python main.py
```

## التعديل لاحقاً

إذا أردت تعديل الأزرار أو الحقول، يمكنك تعديل الشيفرة مباشرة من داخل ملف `main.py` بكل سهولة.
