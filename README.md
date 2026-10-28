# 🌟 AI Telegram Image Enhancer Bot (Xira Rasmlarni Sifatli Qiluvchi Bot)

Ushbu Telegram bot foydalanuvchilar tomonidan yuborilgan xira, sifati past, piksellashgan yoki xiralashgan rasmlarni avtomatik tarzda tahlil qilib, ularni yuqori sifatli (HD / Super Resolution) ko'rinishga keltiradi.

---

## 🚀 Asosiy Imkoniyatlar

1. **🌟 Ultra HD Rejim (Tavsiya etiladi)**:
   - 2x masshtabda kattalashtirish (Lanczos4 Super-Resolution)
   - Shovqin va JPEG siqilish artefaktlarini tozalash (Bilateral Filtering)
   - LAB rang fazosida yorug'lik va kontrastni adaptiv kuchaytirish (CLAHE)
   - Qirralarni keskinlashtirish va mikro-detallarni tiklash (Unsharp Masking)
2. **👤 Portret / Yuz Rejimi**:
   - Yuz terisini silliqlash va ko'z, qosh, lab qirralarini aniqlashtirish.
3. **🔍 4x Super Aniqlik**:
   - Rasmni 4 baravargacha kattalashtirib, chuqur qirra tiklash.
4. **⚡ Tezkor Tiklash**:
   - Kichik hajmli va bir zumda ishlov berish.
5. **📁 Asl Sifatda Yuklash (Hujjat/Fayl ko'rinishida)**:
   - Telegramning siqish algoritmlarisiz, to'liq sifatli tasvirni fayl shaklida olish.

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python 3.10 yoki undan yuqori (Tizimda Python 3.14 mavjud)
- Git

### 2. Kutubxonalarni o'rnatish
Terminalda (PowerShell yoki CMD) quyidagi buyruqni bajaring:
```bash
pip install -r requirements.txt
```

### 3. Telegram Bot Tokenini Olish va Sozlash
1. Telegramda [@BotFather](https://t.me/BotFather) ga kiring.
2. `/newbot` buyrug'ini yuboring va ko'rsatmalarga asosan bot nomi va username bering.
3. BotFather bergan **HTTP API Token**ni nusxalang.
4. Loyiha papkasidagi `.env` faylini ochib, o'z tokeningizni yozing:
```env
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ
```

### 4. Botni Ishga Tushirish
```bash
python bot.py
```

---

## 🐙 GitHub ga Push Qilish (Yuklash)

Loyihangizni o'z GitHub hisobingizga yuklash uchun quyidagi qadamlarni bajaring:

1. [GitHub.com](https://github.com) ga kiring va yangi repozitoriy (New Repository) yarating (masalan, `telegram-image-enhancer-bot`).
2. Terminalda quyidagi buyruqlarni ketma-ket bajaring:

```bash
# Git sozlash (agar avval kiritilmagan bo'lsa):
git config --global user.name "Sizning Ismingiz"
git config --global user.email "sizning_emailingiz@example.com"

# Repozitoriyga yangi o'zgarishlarni qo'shish va commit qilish:
git add .
git commit -m "feat: initial commit - AI Telegram Image Enhancer Bot"

# GitHub repozitoriyangiz manzilini bog'lash (URL ni o'zingiznikiga almashtiring):
git remote add origin https://github.com/SIZNING_USERNAME/telegram-image-enhancer-bot.git

# O'zgarishlarni GitHub ga push qilish:
git branch -M main
git push -u origin main
```

> ⚠️ **Muhim**: `.gitignore` fayli sozlangan, shuning uchun `.env` ichidagi shaxsiy Bot Tokeningiz GitHub ga chiqib ketmaydi va xavfsiz saqlanadi.

---

## 📁 Loyiha Strukturasi

```text
├── bot.py             # Asosiy Telegram bot logikasi (aiogram 3)
├── enhancer.py        # Tasvirlarni qayta ishlash va tiniqlashtirish algoritmlari (OpenCV, PIL)
├── config.py          # Sozlamalar va muhit o'zgaruvchilarini yuklash
├── requirements.txt   # Kerakli Python kutubxonalari ro'yxati
├── .env.example       # Token namunasi
├── .env               # Bot tokeni saqlanadigan fayl (maxfiy)
├── .gitignore         # Gitga qo'shilmaydigan fayllar ro'yxati
└── README.md          # Loyiha hujjatlari va yo'riqnoma
```

---

## 💡 Texnologiyalar
- **Python 3**
- **Aiogram 3** - Zamonaviy asinxron Telegram Bot freymvorki
- **OpenCV (cv2)** - Tasvirlarga professional ishlov berish va filtrlash
- **Pillow & NumPy** - Ko'p o'lchovli matritsalar va tasvir masshtablash
