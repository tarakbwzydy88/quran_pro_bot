import logging
import asyncio
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, RECITERS
from database import (
    get_user_lang, set_user_lang, get_user_reciter, set_user_reciter,
    get_user_theme, set_user_theme, set_reminder, get_reminder, delete_reminder,
    add_history, get_bookmarks, add_bookmark, delete_bookmark
)
from utils import (
    get_ayah_text, get_tafsir, get_recitation_url, search_quran,
    get_sura_info, get_random_ayah
)
from keyboards import (
    main_menu, sura_list_keyboard, reciter_list_keyboard,
    language_keyboard, ayah_actions_keyboard, bookmark_list_keyboard,
    reminder_keyboard, back_button
)
from states import SearchStates, ReminderStates

router = Router()

# --------------------- الأوامر الرئيسية ---------------------
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    await message.answer(
        "🌟 أهلاً بك في أقوى بوت قرآن على الإطلاق!\nاختر من القائمة:",
        reply_markup=main_menu(lang)
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "يمكنك استخدام الأوامر التالية:\n"
        "/start - بدء البوت\n"
        "/sura <رقم> - عرض السورة\n"
        "/ayah <سورة:آية> - عرض آية محددة\n"
        "/search <كلمة> - بحث في القرآن\n"
        "/random - آية عشوائية\n"
        "/bookmarks - إشاراتي\n"
        "/settings - الإعدادات"
    )

@router.message(Command("sura"))
async def cmd_sura(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("أدخل رقم السورة مثل: /sura 1")
        return
    try:
        sura_num = int(parts[1])
        info = get_sura_info(sura_num)
        if info:
            text = f"*{info['name']}* ({info['english_name']})\n"
            text += f"عدد الآيات: {info['ayas']}\n"
            text += f"نوع السورة: {info['revelation_type']}\n"
            first_ayah = await get_ayah_text(sura_num, 1, "ar")
            text += f"\n{first_ayah}"
            await message.answer(text, parse_mode="Markdown", reply_markup=ayah_actions_keyboard(sura_num, 1))
        else:
            await message.answer("لم أجد السورة المطلوبة.")
    except ValueError:
        await message.answer("الرجاء إدخال رقم صحيح.")

@router.message(Command("ayah"))
async def cmd_ayah(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("أدخل الآية مثل: /ayah 2:255")
        return
    try:
        sura_str, ayah_str = parts[1].split(":")
        sura = int(sura_str)
        ayah = int(ayah_str)
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        text = await get_ayah_text(sura, ayah, lang)
        if text:
            await message.answer(text, parse_mode="Markdown", reply_markup=ayah_actions_keyboard(sura, ayah))
            add_history(user_id, sura, ayah, "read")
        else:
            await message.answer("لم أتمكن من جلب الآية.")
    except:
        await message.answer("الصيغة غير صحيحة. مثال: /ayah 2:255")

@router.message(Command("random"))
async def cmd_random(message: Message):
    sura, ayah, text = await get_random_ayah()
    await message.answer(text, parse_mode="Markdown", reply_markup=ayah_actions_keyboard(sura, ayah))

@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("أدخل كلمة البحث بعد الأمر، مثل: /search رحمن")
        return
    keyword = parts[1]
    await state.update_data(keyword=keyword)
    results = await search_quran(keyword, "ar")
    if results:
        text = f"🔍 نتائج البحث عن '{keyword}':\n"
        for i, res in enumerate(results[:5], 1):
            text += f"{i}. سورة {res['sura']} آية {res['ayah']}: {res['text'][:100]}...\n"
        await message.answer(text)
    else:
        await message.answer("لم يتم العثور على نتائج.")

# --------------------- الاستعلامات (Callback Queries) ---------------------
@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    await callback.message.edit_text("القائمة الرئيسية:", reply_markup=main_menu(lang))
    await callback.answer()

@router.callback_query(F.data == "menu_suras")
async def menu_suras(callback: CallbackQuery):
    await callback.message.edit_text("اختر رقم السورة:", reply_markup=sura_list_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("sura_page_"))
async def sura_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await callback.message.edit_reply_markup(reply_markup=sura_list_keyboard(page))
    await callback.answer()

@router.callback_query(F.data.startswith("sura_"))
async def show_sura(callback: CallbackQuery):
    sura_num = int(callback.data.split("_")[1])
    info = get_sura_info(sura_num)
    if info:
        text = f"*{info['name']}* ({info['english_name']})\n"
        text += f"عدد الآيات: {info['ayas']}\n"
        text += f"نوع السورة: {info['revelation_type']}\n"
        first_ayah = await get_ayah_text(sura_num, 1, "ar")
        text += f"\n{first_ayah}"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=ayah_actions_keyboard(sura_num, 1))
        add_history(callback.from_user.id, sura_num, 1, "read")
    await callback.answer()

@router.callback_query(F.data.startswith("goto_"))
async def goto_ayah(callback: CallbackQuery):
    _, sura_str, ayah_str = callback.data.split("_")
    sura, ayah = int(sura_str), int(ayah_str)
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    text = await get_ayah_text(sura, ayah, lang)
    if text:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=ayah_actions_keyboard(sura, ayah))
        add_history(user_id, sura, ayah, "read")
    else:
        await callback.answer("لم أستطع جلب الآية", show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("tafsir_"))
async def show_tafsir(callback: CallbackQuery):
    _, sura_str, ayah_str = callback.data.split("_")
    sura, ayah = int(sura_str), int(ayah_str)
    tafsir_text = await get_tafsir(sura, ayah)
    text = f"📜 *تفسير الآية {sura}:{ayah}*\n\n{tafsir_text}"
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data.startswith("listen_ayah_"))
async def listen_ayah(callback: CallbackQuery, bot: Bot):
    _, _, sura_str, ayah_str = callback.data.split("_")
    sura, ayah = int(sura_str), int(ayah_str)
    user_id = callback.from_user.id
    reciter_id = get_user_reciter(user_id)
    url = await get_recitation_url(reciter_id, sura, ayah)
    if url:
        await bot.send_audio(callback.message.chat.id, url, caption=f"تلاوة الآية {sura}:{ayah}")
        add_history(user_id, sura, ayah, "listen")
    else:
        await callback.answer("رابط التلاوة غير متوفر", show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("bookmark_"))
async def add_bookmark_callback(callback: CallbackQuery):
    _, sura_str, ayah_str = callback.data.split("_")
    sura, ayah = int(sura_str), int(ayah_str)
    user_id = callback.from_user.id
    add_bookmark(user_id, sura, ayah)
    await callback.answer("تمت إضافة الآية إلى الإشارات ✅", show_alert=True)

@router.callback_query(F.data == "menu_bookmarks")
async def show_bookmarks(callback: CallbackQuery):
    user_id = callback.from_user.id
    bookmarks = get_bookmarks(user_id)
    if bookmarks:
        await callback.message.edit_text("⭐ إشاراتك:", reply_markup=bookmark_list_keyboard(bookmarks))
    else:
        await callback.message.edit_text("لا توجد إشارات بعد.", reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "menu_reciters")
async def menu_reciters(callback: CallbackQuery):
    await callback.message.edit_text("اختر القارئ المفضل:", reply_markup=reciter_list_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("reciter_"))
async def set_reciter(callback: CallbackQuery):
    reciter_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    set_user_reciter(user_id, reciter_id)
    await callback.answer(f"تم اختيار القارئ: {RECITERS[reciter_id]} ✅")
    await back_main(callback)

@router.callback_query(F.data == "menu_settings")
async def settings_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 تغيير اللغة", callback_data="settings_lang")],
        [InlineKeyboardButton(text="🎙️ تغيير القارئ", callback_data="menu_reciters")],
        [InlineKeyboardButton(text="🎨 الوضع (ليلي/نهاري)", callback_data="settings_theme")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")]
    ])
    await callback.message.edit_text("الإعدادات:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "settings_lang")
async def settings_lang(callback: CallbackQuery):
    await callback.message.edit_text("اختر لغتك:", reply_markup=language_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    set_user_lang(user_id, lang_code)
    await callback.answer(f"تم تغيير اللغة ✅")
    await back_main(callback)

@router.callback_query(F.data == "settings_theme")
async def settings_theme(callback: CallbackQuery):
    user_id = callback.from_user.id
    current = get_user_theme(user_id)
    new_theme = "dark" if current == "light" else "light"
    set_user_theme(user_id, new_theme)
    await callback.answer(f"تم تغيير المظهر إلى {new_theme}")

@router.callback_query(F.data == "menu_reminder")
async def menu_reminder(callback: CallbackQuery):
    await callback.message.edit_text("⏰ إعدادات التذكير اليومي:", reply_markup=reminder_keyboard())
    await callback.answer()

@router.callback_query(F.data == "set_reminder")
async def set_reminder_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("أرسل وقت التذكير بصيغة HH:MM (مثال: 06:30)")
    await state.set_state(ReminderStates.waiting_for_time)
    await callback.answer()

@router.message(ReminderStates.waiting_for_time)
async def receive_reminder_time(message: Message, state: FSMContext):
    try:
        time_str = message.text.strip()
        datetime.strptime(time_str, "%H:%M")
        user_id = message.from_user.id
        set_reminder(user_id, time_str, 1)
        await message.answer(f"تم ضبط التذكير اليومي الساعة {time_str} ✅")
        await state.clear()
    except ValueError:
        await message.answer("صيغة غير صحيحة. الرجاء الإرسال بصيغة HH:MM مثل 06:30")

@router.callback_query(F.data == "cancel_reminder")
async def cancel_reminder_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    delete_reminder(user_id)
    await callback.message.edit_text("تم إلغاء التذكير اليومي ❌", reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "random_ayah")
async def random_ayah_callback(callback: CallbackQuery):
    sura, ayah, text = await get_random_ayah()
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=ayah_actions_keyboard(sura, ayah))
    await callback.answer()

@router.callback_query(F.data == "menu_info")
async def menu_info(callback: CallbackQuery):
    info_text = (
        "🤖 *بوت القرآن الاحترافي*\n"
        "إصدار 3.0\n\n"
        "✨ المميزات:\n"
        "• عرض الآيات مع الترجمة والتفسير\n"
        "• تلاوات أشهر القراء\n"
        "• بحث متقدم في القرآن\n"
        "• إشارات مرجعية\n"
        "• تذكير يومي\n"
        "• وأكثر...\n\n"
        "للاستفسار: @support_bot"
    )
    await callback.message.edit_text(info_text, parse_mode="Markdown", reply_markup=back_button())
    await callback.answer()