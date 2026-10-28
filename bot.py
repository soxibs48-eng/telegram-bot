import asyncio
import io
import logging
import sys
from typing import Dict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config
from enhancer import ImageEnhancer

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ImageEnhancerBot")

# Telegram Bot va Dispatcher yaratish
if not config.BOT_TOKEN:
    logger.error("BOT_TOKEN aniqlanmadi! .env fayliga bot tokeningizni kiriting.")

bot = None
dp = Dispatcher()

# Foydalanuvchi so'nggi yuborgan rasmining file_id sini eslab qolish uchun kesh
user_last_file: Dict[int, str] = {}


def get_mode_keyboard(file_id: str, current_mode: str = "autohd") -> InlineKeyboardMarkup:
    """
    Rasm tagiga chiqadigan interaktiv inline tugmalar
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="🌟 Ultra HD (Tavsiya)" + (" ✅" if current_mode == "autohd" else ""),
                callback_data=f"mode:autohd:{file_id[:20]}",
            ),
            InlineKeyboardButton(
                text="👤 Portret / Yuz" + (" ✅" if current_mode == "portrait" else ""),
                callback_data=f"mode:portrait:{file_id[:20]}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔍 4x Super Aniqlik" + (" ✅" if current_mode == "superres" else ""),
                callback_data=f"mode:superres:{file_id[:20]}",
            ),
            InlineKeyboardButton(
                text="⚡ Tezkor Tiklash" + (" ✅" if current_mode == "fast" else ""),
                callback_data=f"mode:fast:{file_id[:20]}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📁 Asl sifatda yuklash (Fayl)",
                callback_data=f"doc:{file_id[:20]}",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """
    /start komandasi uchun handler
    """
    user_name = message.from_user.first_name if message.from_user else "Foydalanuvchi"
    welcome_text = (
        f"👋 <b>Assalomu alaykum, {user_name}!</b>\n\n"
        "Men <b>AI Image Enhancer</b> botiman — xira, sifati past yoki xiralashgan rasmlarni "
        "tiniq va yuqori sifatli (HD) qilib tiklab beraman.\n\n"
        "<b>Qanday imkoniyatlar mavjud?</b>\n"
        "✨ <b>Ultra HD</b>: Rasmni 2x kattalashtirib, detallari va ranglarini kuchaytiradi\n"
        "👤 <b>Portret rejimi</b>: Yuz terisi va ko'z/qirralarni tiniqlashtiradi\n"
        "🔍 <b>4x Super Resolution</b>: Chuqur qirra tiklash va 4 karra masshtablash\n"
        "⚡ <b>Tezkor rejim</b>: Bir zumda xiralikni ketkazish\n"
        "📁 <b>Fayl formatida</b>: Telegram siqishisiz to'liq original sifatda yuklash\n\n"
        "👉 <i>Hoziroq xira rasmingizni yuboring!</i>"
    )
    await message.answer(welcome_text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """
    /help komandasi uchun handler
    """
    help_text = (
        "📖 <b>Botdan foydalanish bo'yicha yo'riqnoma:</b>\n\n"
        "1. Xira yoki sifati past rasmni oddiy rasm yoki <b>fayl (hujjat)</b> shaklida yuboring.\n"
        "2. Bot avtomatik ravishda Ultra HD rejimida sifatni oshirib beradi.\n"
        "3. Rasm ostidagi tugmalar orqali Portret, 4x Super Aniqlik yoki Tezkor rejimlarni tanlashingiz mumkin.\n"
        "4. Telegram rasm sifatini tushirmasligi uchun <b>'📁 Asl sifatda yuklash'</b> tugmasidan foydalaning!\n\n"
        "Savol yoki takliflar bo'lsa, adminga murojaat qiling."
    )
    await message.answer(help_text)


async def process_image_bytes(raw_bytes: bytes, mode: str) -> tuple[bytes, str]:
    """
    Berilgan baytlarni tanlangan rejim bo'yicha qayta ishlash
    """
    if mode == "portrait":
        out_bytes = ImageEnhancer.enhance_portrait(raw_bytes)
        mode_label = "👤 Portret rejimi"
    elif mode == "superres":
        out_bytes = ImageEnhancer.enhance_super_res_4x(raw_bytes)
        mode_label = "🔍 4x Super Aniqlik"
    elif mode == "fast":
        out_bytes = ImageEnhancer.enhance_fast(raw_bytes)
        mode_label = "⚡ Tezkor tiklash"
    else:
        out_bytes = ImageEnhancer.enhance_auto_hd(raw_bytes)
        mode_label = "🌟 Ultra HD rejim"

    return out_bytes, mode_label


@dp.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    """
    Foydalanuvchi rasm yuborganda ishlaydigan handler
    """
    status_msg = await message.answer("⏳ <i>Rasmingiz qabul qilindi. Sifatini oshirish boshlanmoqda...</i>")

    try:
        # Eng yuqori sifatli rasmni olish
        photo = message.photo[-1]
        file_id = photo.file_id

        # Keshga saqlash
        if message.from_user:
            user_last_file[message.from_user.id] = file_id

        # Telegramdan rasmni xotiraga yuklab olish
        file_info = await bot.get_file(file_id)
        file_io = io.BytesIO()
        await bot.download_file(file_info.file_path, file_io)
        raw_bytes = file_io.getvalue()

        # Ultra HD rejimida qayta ishlash
        enhanced_bytes, mode_label = await process_image_bytes(raw_bytes, mode="autohd")

        # Natijani yuborish
        result_file = BufferedInputFile(enhanced_bytes, filename="enhanced_image.jpg")
        caption = (
            f"✅ <b>Rasm tayyor!</b>\n"
            f"🎯 <b>Rejim:</b> {mode_label}\n"
            f"💡 <i>Quyidagi tugmalar orqali boshqa rejimlarda ham sinab ko'rishingiz mumkin:</i>"
        )

        await message.reply_photo(
            photo=result_file,
            caption=caption,
            reply_markup=get_mode_keyboard(file_id, current_mode="autohd"),
        )

        # Holat xabarini o'chirish
        await status_msg.delete()

    except Exception as e:
        logger.exception("Rasm qayta ishlashda xatolik:")
        await status_msg.edit_text(f"❌ Kechirasiz, rasmni qayta ishlashda xatolik yuz berdi: {e}")


@dp.message(F.document)
async def handle_document(message: Message, bot: Bot):
    """
    Foydalanuvchi fayl/hujjat shaklida rasm yuborganda ishlaydigan handler
    """
    doc = message.document
    if not doc or not (doc.mime_type and doc.mime_type.startswith("image/")):
        await message.answer("⚠️ Iltimos, faqat rasm faylini yuboring (JPG, PNG, WEBP).")
        return

    status_msg = await message.answer("⏳ <i>Hujjat qabul qilindi. Sifatini maksimal oshirmoqdaman...</i>")

    try:
        file_id = doc.file_id
        if message.from_user:
            user_last_file[message.from_user.id] = file_id

        file_info = await bot.get_file(file_id)
        file_io = io.BytesIO()
        await bot.download_file(file_info.file_path, file_io)
        raw_bytes = file_io.getvalue()

        enhanced_bytes, mode_label = await process_image_bytes(raw_bytes, mode="autohd")

        doc_file = BufferedInputFile(enhanced_bytes, filename=f"hd_{doc.file_name or 'enhanced.jpg'}")
        caption = f"✅ <b>Asl formatdagi Ultra HD rasm tayyor!</b>\n🎯 Rejim: {mode_label}"

        await message.reply_document(
            document=doc_file,
            caption=caption,
            reply_markup=get_mode_keyboard(file_id, current_mode="autohd"),
        )
        await status_msg.delete()

    except Exception as e:
        logger.exception("Hujjat qayta ishlashda xatolik:")
        await status_msg.edit_text(f"❌ Rasmni qayta ishlashda xatolik: {e}")


@dp.callback_query(F.data.startswith("mode:"))
async def handle_mode_change(callback: CallbackQuery, bot: Bot):
    """
    Inline tugmalar orqali rejimni almashtirganda ishlaydi
    """
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer("Noto'g'ri so'rov.")
        return

    mode = parts[1]
    user_id = callback.from_user.id
    file_id = user_last_file.get(user_id)

    if not file_id:
        await callback.answer("Eski rasm topilmadi. Iltimos, rasmni qayta yuboring.", show_alert=True)
        return

    await callback.answer("⏳ Tanlangan rejimda qayta ishlanmoqda...")

    try:
        file_info = await bot.get_file(file_id)
        file_io = io.BytesIO()
        await bot.download_file(file_info.file_path, file_io)
        raw_bytes = file_io.getvalue()

        enhanced_bytes, mode_label = await process_image_bytes(raw_bytes, mode=mode)
        result_file = BufferedInputFile(enhanced_bytes, filename=f"enhanced_{mode}.jpg")

        caption = (
            f"✅ <b>Yangi natija tayyor!</b>\n"
            f"🎯 <b>Rejim:</b> {mode_label}\n"
            f"💡 <i>Boshqa rejimlarni ham sinab ko'rishingiz mumkin:</i>"
        )

        await callback.message.reply_photo(
            photo=result_file,
            caption=caption,
            reply_markup=get_mode_keyboard(file_id, current_mode=mode),
        )

    except Exception as e:
        logger.exception("Rejim o'zgartirishda xatolik:")
        await callback.message.answer(f"❌ Qayta ishlashda xatolik: {e}")


@dp.callback_query(F.data.startswith("doc:"))
async def handle_send_as_doc(callback: CallbackQuery, bot: Bot):
    """
    Rasmni Telegram siqishisiz, to'liq sifatli fayl (document) sifatida yuklab berish
    """
    user_id = callback.from_user.id
    file_id = user_last_file.get(user_id)

    if not file_id:
        await callback.answer("Eski rasm topilmadi. Iltimos, yangi rasm yuboring.", show_alert=True)
        return

    await callback.answer("⏳ Fayl tayyorlanmoqda...")

    try:
        file_info = await bot.get_file(file_id)
        file_io = io.BytesIO()
        await bot.download_file(file_info.file_path, file_io)
        raw_bytes = file_io.getvalue()

        enhanced_bytes, _ = await process_image_bytes(raw_bytes, mode="autohd")
        doc_file = BufferedInputFile(enhanced_bytes, filename="ultra_hd_quality.jpg")

        await callback.message.reply_document(
            document=doc_file,
            caption="📁 <b>Original Ultra HD sifatli fayl (siqilmagan holda).</b>",
        )

    except Exception as e:
        logger.exception("Fayl yuborishda xatolik:")
        await callback.message.answer(f"❌ Fayl yuborishda xatolik: {e}")


async def main():
    token = config.BOT_TOKEN.strip()
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or ":" not in token:
        print("\n" + "=" * 65)
        print("⚠️  DIQQAT: Botni ishga tushirish uchun BOT_TOKEN kiritilishi shart!")
        print("1. Telegramda @BotFather ga kiring va /newbot orqali bot oching.")
        print("2. Olingan tokenni '.env' faylidagi BOT_TOKEN qatoriga yozing:")
        print("   BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
        print("3. So'ngra 'python bot.py' buyrug'ini qayta bajaring.")
        print("=" * 65 + "\n")
        return

    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    logger.info("Bot ishga tushdi va xabarlarni qabul qilishga tayyor...")
    # Eski kutilmagan yangilanishlarni tozalash (drop pending updates)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
