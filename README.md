# Telegram Zakaz Userbot

Guruhlardan zakaz xabarlarini kuzatib, buyurtma guruhiga yuboruvchi userbot.

## Ishlash prinsipi

- Belgilangan guruhlarni kuzatadi
- Stiker yoki emoji bo'lgan xabarlarni **o'tkazib yuboradi**
- 60 belgidan **kam** xabarlarni o'tkazib yuboradi
- Qolgan xabarlarni zakaz deb qabul qiladi va buyurtma guruhiga yuboradi
- Buyurtmada: **ism** (profilga havola), **username**, **telefon**, **guruh nomi**, **vaqt**, **xabar matni** ko'rsatiladi

## O'rnatish

```bash
pip install -r requirements.txt
```

## Sozlash

`config.py` faylini oching va quyidagilarni to'ldiring:

| Parametr | Tavsif |
|---|---|
| `API_ID` | [my.telegram.org/apps](https://my.telegram.org/apps) dan oling |
| `API_HASH` | [my.telegram.org/apps](https://my.telegram.org/apps) dan oling |
| `PHONE_NUMBER` | Telegram raqamingiz (`+998...`) |
| `WATCH_GROUPS` | Kuzatiladigan guruhlar ro'yxati |
| `ORDER_GROUP` | Zakaz yuboriluvchi guruh |
| `MIN_MESSAGE_LENGTH` | Minimal xabar uzunligi (default: 60) |

## Ishga tushirish

```bash
python userbot.py
```

Birinchi marta ishga tushirganda Telegram SMS kodi so'raydi. Kod kiritilgandan so'ng `userbot_session.session` fayli yaratiladi va keyingi safar kod so'ralmaydi.

## Fayl tuzilmasi

```
├── userbot.py        # Asosiy bot kodi
├── config.py         # Sozlamalar
├── requirements.txt  # Kutubxonalar
├── userbot.log       # Log fayli (avtomatik yaratiladi)
└── userbot_session.session  # Session (avtomatik yaratiladi)
```

## Eslatma

- Telefon raqami faqat kontaktlar uchun ko'rinadi, boshqalar uchun "telefon ko'rinmaydi" chiqadi
- Bot ishlayotganida `userbot.log` faylida barcha harakatlar yozib boriladi
