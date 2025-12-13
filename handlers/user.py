from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from database import get_user, mark_attendance, check_token_used, mark_token_used
from utils import verify_token
from config import SUPER_ADMIN_ID, NOTIFICATION_ADMIN_IDS

router = Router()

worker_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Mening ID raqamim"), KeyboardButton(text="❓ Yordam")]
    ], resize_keyboard=True
)


@router.message(CommandStart())
async def bot_start(message: Message, command: CommandObject, bot: Bot):
    user_id = message.from_user.id
    args = command.args  # QR token

    # 1. Bosh Admin uchun /admin buyrug'ini tekshirish
    if user_id == SUPER_ADMIN_ID and not args:
        await message.answer("Assalomu alaykum Admin! Boshqarish paneliga kirish uchun /admin deb yozing.",
                             reply_markup=worker_kb)
        return

    # 2. Oddiy Adminlar va Ishchilar uchun davomat mantiqi
    user = await get_user(user_id)
    if not user:
        await message.answer(
            f"❌ Kechirasiz, siz tizimda ro'yxatdan o'tmagansiz.\nSizning ID: `{user_id}`\nAdmin bilan bog'laning.")
        return

    full_name = user[1]

    if args:
        is_valid, action_type = verify_token(args)

        if not is_valid:
            await message.answer(f"❌ Xatolik! QR kod noto'g'ri yoki muddati o'tgan.")
            return

        # Bir martalik QR KOD TEKSHIRUVI
        if await check_token_used(args):
            await message.answer(
                "❌ Bu QR kod allaqachon **ishlatilgan**!\n"
                "Iltimos, Davomatni qayd etish uchun **Adminda yangi QR kod** so'rang.",
                parse_mode="Markdown"
            )
            return

        # 3. Davomatni yozish
        status_text, admin_report_text = await mark_attendance(user_id, action_type)

        if status_text.startswith("✅"):
            # Muvaffaqiyatli bo'lsa, tokenni ishlatilgan deb belgilash
            await mark_token_used(args, action_type, user_id, full_name)
            await message.answer(f"👋 Hurmatli **{full_name}**,\n{status_text}", parse_mode="Markdown")

            # 🚨 Barcha Administratorlarga xabar yuborish
            if admin_report_text:
                for admin_chat_id in NOTIFICATION_ADMIN_IDS:
                    await bot.send_message(
                        chat_id=admin_chat_id,
                        text=admin_report_text,
                        parse_mode="Markdown"
                    )
        else:
            # Xato xabari
            await message.answer(f"👋 Hurmatli **{full_name}**,\n{status_text}", parse_mode="Markdown")

    else:
        await message.answer(f"Salom, **{full_name}**. Davomat qilish uchun ofisdagi QR kodni skanerlang.",
                             reply_markup=worker_kb, parse_mode="Markdown")


@router.message(F.text == "ℹ️ Mening ID raqamim")
async def my_id(message: Message):
    await message.answer(
        f"Sizning Telegram ID raqamingiz: `{message.from_user.id}`\nBu raqam sizni ro'yxatga olish uchun kerak bo'ladi.")


@router.message(F.text == "❓ Yordam")
async def help_user(message: Message):
    await message.answer(
        "Siz faqatgina belgilangan joydagi **Keldi** yoki **Ketdi** QR kodlarini skanerlash orqali davomat qila olasiz.\n\n*Boshqa savollar bo'lsa, adminga murojaat qiling.*",
        parse_mode="Markdown")