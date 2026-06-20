"""
Telegram Userbot - Zakaz kuzatuvchi
====================================
Guruhlardan zakaz xabarlarini kuzatib, buyurtma guruhiga yuboradi.

Talablar:
- pip install telethon
"""

import asyncio
import logging
from datetime import datetime

from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageMediaDocument,
    DocumentAttributeSticker,
    MessageEntityCustomEmoji,
)

import config

# ── Logging sozlamalari ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("userbot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ── Client yaratish ──────────────────────────────────────────────────────────
client = TelegramClient(
    config.SESSION_NAME,
    config.API_ID,
    config.API_HASH,
)


# ── Yordamchi funksiyalar ────────────────────────────────────────────────────

def has_sticker(message) -> bool:
    """Xabarda stiker borligini tekshiradi."""
    if not message.media:
        return False
    if isinstance(message.media, MessageMediaDocument):
        doc = message.media.document
        if doc and doc.attributes:
            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeSticker):
                    return True
    return False


def has_emoji(message) -> bool:
    """Xabarda oddiy yoki custom emoji borligini tekshiradi."""
    text = message.raw_text or ""

    # Custom emoji entity tekshiruvi
    if message.entities:
        for entity in message.entities:
            if isinstance(entity, MessageEntityCustomEmoji):
                return True

    # Unicode emoji tekshiruvi
    import unicodedata
    for char in text:
        try:
            cat = unicodedata.category(char)
            # So, Sm, Sk, So kategoriyalari emoji bo'lishi mumkin
            if "EMOJI" in unicodedata.name(char, ""):
                return True
        except (ValueError, TypeError):
            pass

    # Keng tarqalgan emoji range tekshiruvi (UTF-16 surrogate pairs)
    for char in text:
        cp = ord(char)
        if (
            0x1F600 <= cp <= 0x1F64F   # Emoticons
            or 0x1F300 <= cp <= 0x1F5FF  # Misc Symbols and Pictographs
            or 0x1F680 <= cp <= 0x1F6FF  # Transport and Map
            or 0x1F700 <= cp <= 0x1F77F  # Alchemical Symbols
            or 0x1F780 <= cp <= 0x1F7FF  # Geometric Shapes Extended
            or 0x1F800 <= cp <= 0x1F8FF  # Supplemental Arrows-C
            or 0x1F900 <= cp <= 0x1F9FF  # Supplemental Symbols and Pictographs
            or 0x1FA00 <= cp <= 0x1FA6F  # Chess Symbols
            or 0x1FA70 <= cp <= 0x1FAFF  # Symbols and Pictographs Extended-A
            or 0x2600 <= cp <= 0x26FF    # Misc symbols
            or 0x2700 <= cp <= 0x27BF    # Dingbats
            or 0xFE00 <= cp <= 0xFE0F    # Variation Selectors
            or 0x1F1E0 <= cp <= 0x1F1FF  # Flags
        ):
            return True
    return False


async def get_user_info(user_id: int) -> dict:
    """
    Foydalanuvchi ID si bo'yicha to'liq ma'lumot oladi.
    Telefon raqami faqat kontaktlar uchun ko'rinadi.
    """
    info = {
        "id": user_id,
        "full_name": "Noma'lum",
        "username": None,
        "phone": None,
        "profile_url": None,
    }
    try:
        user = await client.get_entity(user_id)
        first = user.first_name or ""
        last = user.last_name or ""
        info["full_name"] = f"{first} {last}".strip() or "Noma'lum"
        info["username"] = user.username
        info["phone"] = getattr(user, "phone", None)
        # Profilga o'tish uchun havola
        if user.username:
            info["profile_url"] = f"https://t.me/{user.username}"
        else:
            info["profile_url"] = f"tg://user?id={user_id}"
    except Exception as e:
        log.warning(f"Foydalanuvchi ma'lumoti olinmadi (ID: {user_id}): {e}")
    return info


async def build_order_message(message, group_title: str, group_username: str, user: dict) -> str:
    """Buyurtma guruhiga yuboriladigan formatlangan xabar."""
    username_str = f"@{user['username']}" if user["username"] else "username yo'q"
    phone_str = user["phone"] if user["phone"] else "telefon ko'rinmaydi"
    profile_link = user["profile_url"] or f"tg://user?id={user['id']}"

    group_link = f"@{group_username}" if group_username else group_title

    text = (
        f"🛒 **YANGI ZAKAZ**\n"
        f"{'─' * 30}\n"
        f"👤 **Ism:** [{user['full_name']}]({profile_link})\n"
        f"🔗 **Username:** {username_str}\n"
        f"📞 **Telefon:** `{phone_str}`\n"
        f"📍 **Guruh:** {group_link}  |  `{group_title}`\n"
        f"🕐 **Vaqt:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{'─' * 30}\n"
        f"💬 **Xabar matni:**\n{message.raw_text}"
    )
    return text


# ── Asosiy handler ───────────────────────────────────────────────────────────

@client.on(events.NewMessage(chats=config.WATCH_GROUPS))
async def order_handler(event):
    """Kuzatiladigan guruhlardagi yangi xabarlarni qayta ishlaydi."""
    message = event.message

    # 1. Matn bo'lmagan xabarlarni o'tkazib yuborish
    text = message.raw_text or ""
    if not text.strip():
        return

    # 2. Stiker bo'lsa o'tkazib yuborish
    if has_sticker(message):
        log.debug(f"Stiker xabar o'tkazildi: {message.id}")
        return

    # 3. Emoji bo'lsa o'tkazib yuborish
    if has_emoji(message):
        log.debug(f"Emoji xabar o'tkazildi: {message.id}")
        return

    # 4. 60 belgidan kam bo'lsa o'tkazib yuborish
    if len(text) < config.MIN_MESSAGE_LENGTH:
        log.debug(f"Qisqa xabar o'tkazildi ({len(text)} belgi): {message.id}")
        return

    # 5. Guruh ma'lumotlarini olish
    try:
        chat = await event.get_chat()
        group_title = getattr(chat, "title", "Noma'lum guruh")
        group_username = getattr(chat, "username", None) or ""
    except Exception as e:
        log.warning(f"Guruh ma'lumoti olinmadi: {e}")
        group_title = "Noma'lum guruh"
        group_username = ""

    # 6. Yuboruvchi ma'lumotlarini olish
    sender_id = message.sender_id
    if not sender_id:
        log.warning("Yuboruvchi ID si yo'q, xabar o'tkazildi.")
        return

    user_info = await get_user_info(sender_id)

    # 7. Formatlangan xabarni tuzish
    order_text = await build_order_message(message, group_title, group_username, user_info)

    # 8. Buyurtma guruhiga yuborish
    try:
        await client.send_message(
            config.ORDER_GROUP,
            order_text,
            parse_mode="markdown",
            link_preview=False,
        )
        log.info(
            f"✅ Zakaz yuborildi | Guruh: {group_title} | "
            f"Foydalanuvchi: {user_info['full_name']} | "
            f"Xabar uzunligi: {len(text)}"
        )
    except Exception as e:
        log.error(f"❌ Zakaz yuborishda xato: {e}")


# ── Ishga tushirish ──────────────────────────────────────────────────────────

async def main():
    log.info("🤖 Userbot ishga tushmoqda...")
    await client.start(phone=config.PHONE_NUMBER)
    log.info("✅ Userbot muvaffaqiyatli ulandi!")
    log.info(f"👁  Kuzatiladigan guruhlar: {config.WATCH_GROUPS}")
    log.info(f"📦 Buyurtma guruhi: {config.ORDER_GROUP}")
    log.info(f"📏 Minimal xabar uzunligi: {config.MIN_MESSAGE_LENGTH} belgi")
    log.info("Xabarlar kutilmoqda... (to'xtatish uchun Ctrl+C)")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
