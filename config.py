import os

# توكن البوت من BotFather - استخدم متغير بيئة أو ضعه مباشرة (للرفع على GitHub يفضل عدم وضعه هنا)
BOT_TOKEN = "8760413618:AAGDu2BU3XB0I8cAXoRqmMxQ61xPRYTg1N8"

# معرف المسؤول (يمكنك الحصول عليه من @userinfobot)
ADMIN_ID = 123456789

# إعدادات قاعدة البيانات
DB_NAME = "quran_bot.db"

# إعدادات API
QURAN_API_BASE = "https://api.alquran.cloud/v1"
QURAN_COM_API = "https://api.quran.com/api/v4"

# قائمة القراء المتاحين للتلاوة (المعرف في API)
RECITERS = {
    "abdulbasit": "عبد الباسط عبد الصمد",
    "afasy": "مشاري العفاسي",
    "ghamdi": "سعد الغامدي",
    "husary": "محمود خليل الحصري",
    "sudais": "عبد الرحمن السديس",
    "shuraym": "سعود الشريم",
    "minshawi": "محمد صديق المنشاوي"
}

# اللغات المدعومة للترجمة
LANGUAGES = {
    "ar": "العربية (النص القرآني)",
    "en": "English (Sahih International)",
    "fr": "Français (Muhammad Hamidullah)",
    "id": "Bahasa Indonesia (Indonesian)",
    "ur": "اردو (Urdu)"
}