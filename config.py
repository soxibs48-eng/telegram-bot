import os
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    print("[OGOHLANTIRISH] BOT_TOKEN topilmadi! Iltimos, .env fayliga bot tokeningizni kiriting.")
