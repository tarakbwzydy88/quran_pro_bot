from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import RECITERS, LANGUAGES

def main_menu(lang="ar"):
    buttons = [
        [InlineKeyboardButton(text="📖 السور", callback_data="menu_suras"),
         InlineKeyboardButton(text="🎙️ التلاوات", callback_data="menu_reciters")],
        [InlineKeyboardButton(text="🔍 بحث", callback_data="menu_search"),
         InlineKeyboardButton(text="📜 تفسير", callback_data="menu_tafsir")],
        [InlineKeyboardButton(text="⭐ إشاراتي", callback_data="menu_bookmarks"),
         InlineKeyboardButton(text="⚙️ إعدادات", callback_data="menu_settings")],
        [InlineKeyboardButton(text="🎲 آية عشوائية", callback_data="random_ayah"),
         InlineKeyboardButton(text="📅 تذكير يومي", callback_data="menu_reminder")],
        [InlineKeyboardButton(text="ℹ️ معلومات", callback_data="menu_info")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def sura_list_keyboard(page=0, per_page=20):
    start = page * per_page + 1
    end = min((page+1)*per_page, 114)
    buttons = []
    for i in range(start, end+1):
        buttons.append([InlineKeyboardButton(text=str(i), callback_data=f"sura_{i}")])
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ السابق", callback_data=f"sura_page_{page-1}"))
    if end < 114:
        nav_buttons.append(InlineKeyboardButton(text="التالي ➡️", callback_data=f"sura_page_{page+1}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def reciter_list_keyboard():
    buttons = []
    for rec_id, rec_name in RECITERS.items():
        buttons.append([InlineKeyboardButton(text=rec_name, callback_data=f"reciter_{rec_id}")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def language_keyboard():
    buttons = []
    for code, name in LANGUAGES.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"lang_{code}")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def ayah_actions_keyboard(sura, ayah):
    buttons = [
        [InlineKeyboardButton(text="📖 تفسير الآية", callback_data=f"tafsir_{sura}_{ayah}"),
         InlineKeyboardButton(text="🎧 استماع الآية", callback_data=f"listen_ayah_{sura}_{ayah}")],
        [InlineKeyboardButton(text="⭐ أضف إلى الإشارات", callback_data=f"bookmark_{sura}_{ayah}"),
         InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def bookmark_list_keyboard(bookmarks):
    buttons = []
    for b in bookmarks:
        buttons.append([InlineKeyboardButton(text=f"سورة {b['sura']} آية {b['ayah']}",
                                            callback_data=f"goto_{b['sura']}_{b['ayah']}")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def reminder_keyboard():
    buttons = [
        [InlineKeyboardButton(text="⏰ ضبط التذكير", callback_data="set_reminder")],
        [InlineKeyboardButton(text="❌ إلغاء التذكير", callback_data="cancel_reminder")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")]
    ])