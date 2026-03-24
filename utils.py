import requests
import json
import logging
from config import QURAN_API_BASE, QURAN_COM_API, RECITERS
import aiohttp
import asyncio
import random

ayah_cache = {}
tafsir_cache = {}

async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None

def get_sura_name(sura_num, lang="ar"):
    try:
        resp = requests.get(f"{QURAN_API_BASE}/surah/{sura_num}")
        if resp.status_code == 200:
            data = resp.json()["data"]
            if lang == "ar":
                return data["name"]
            elif lang == "en":
                return data["englishName"]
            else:
                return data["name"]
    except:
        pass
    return f"سورة {sura_num}"

async def get_ayah_text(sura, ayah, lang="ar"):
    cache_key = f"{sura}:{ayah}:{lang}"
    if cache_key in ayah_cache:
        return ayah_cache[cache_key]

    if lang == "ar":
        url = f"{QURAN_API_BASE}/ayah/{sura}:{ayah}"
        data = await fetch_json(url)
        if data:
            text = data["data"]["text"]
            ayah_cache[cache_key] = text
            return text
    else:
        edition_map = {
            "en": "en.sahih",
            "fr": "fr.hamidullah",
            "id": "id.indonesian",
            "ur": "ur.jalandhry"
        }
        edition = edition_map.get(lang, "en.sahih")
        url = f"{QURAN_API_BASE}/ayah/{sura}:{ayah}/editions/quran-uthmani,{edition}"
        data = await fetch_json(url)
        if data and "data" in data:
            editions = data["data"]
            if len(editions) >= 2:
                arabic = editions[0]["text"]
                translation = editions[1]["text"]
                result = f"{arabic}\n\n{translation}"
                ayah_cache[cache_key] = result
                return result
    return None

async def get_tafsir(sura, ayah, tafsir_type="muyassar"):
    cache_key = f"tafsir:{sura}:{ayah}:{tafsir_type}"
    if cache_key in tafsir_cache:
        return tafsir_cache[cache_key]
    # مؤقتاً نرجع رسالة توضيحية
    result = f"📜 تفسير الآية {sura}:{ayah} (مختصر): سيتم إضافته قريباً إن شاء الله."
    tafsir_cache[cache_key] = result
    return result

async def get_recitation_url(reciter_id, sura, ayah=None):
    if ayah:
        url = f"https://cdn.alquran.cloud/media/audio/ayah/{reciter_id}/{sura:03d}{ayah:03d}.mp3"
    else:
        url = f"https://cdn.alquran.cloud/media/audio/surah/{reciter_id}/{sura:03d}.mp3"
    return url

async def search_quran(keyword, language="ar"):
    url = f"{QURAN_COM_API}/search?q={keyword}&language={language}"
    data = await fetch_json(url)
    if data and "verses" in data:
        results = []
        for verse in data["verses"]:
            results.append({
                "sura": verse["chapter_id"],
                "ayah": verse["verse_number"],
                "text": verse["text"]
            })
        return results
    return []

def get_sura_info(sura_num):
    try:
        resp = requests.get(f"{QURAN_API_BASE}/surah/{sura_num}")
        if resp.status_code == 200:
            data = resp.json()["data"]
            return {
                "name": data["name"],
                "english_name": data["englishName"],
                "ayas": data["numberOfAyahs"],
                "revelation_type": data["revelationType"]
            }
    except:
        pass
    return None

async def get_random_ayah():
    sura = random.randint(1, 114)
    info = get_sura_info(sura)
    if info:
        ayah = random.randint(1, info["ayas"])
        text = await get_ayah_text(sura, ayah, "ar")
        return sura, ayah, text
    return 1, 1, "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"