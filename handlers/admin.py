import os
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import SUPER_ADMIN_ID
from states import AdminStates
from database import add_user, get_all_workers, delete_worker, get_attendance_data, clear_all_attendance_data
from utils import generate_qr_image, export_to_excel

router = Router()

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 Keldi QR"), KeyboardButton(text="📤 Ketdi QR")],
        [KeyboardButton(text="➕ Ishchi qo'shish"), KeyboardButton(text="🗑 Ishchini o'chirish")],
        [KeyboardButton(text="📃 Ishchilar ro'yxati"), KeyboardButton(text="📊 Excel Hisobot")],
        [KeyboardButton(text="🧹 Bazani Tozalash")]
    ], resize_keyboard=True
)


def is_super_admin(message: Message):  # Bosh Adminni tekshirish
    return message.from_user.id == SUPER_ADMIN_ID


@router.message(Command("admin"), lambda msg: is_super_admin(msg))
async def admin_panel(message: Message):
    await message.answer("👨‍💼 **Bosh Admin Panel**", reply_markup=admin_kb, parse_mode="Markdown")


@router.message(F.text.in_({"📥 Keldi QR", "📤 Ketdi QR"}), lambda msg: is_super_admin(msg))
async def send_qr(message: Message, bot: Bot):
    action = "in" if "Keldi" in message.text else "out"
    bot_info = await bot.get_me()
    path = generate_qr_image(bot_info.username, action)

    action_text = "KELISH" if action == "in" else "KETISH"

    await message.answer_photo(
        FSInputFile(path),
        caption=f"📅 **YANGI {action_text} QR kodi**.\n*(Bu QR kod faqat **bir marta** ishlatiladi)*",
        parse_mode="Markdown"
    )
    os.remove(path)


@router.message(F.text == "➕ Ishchi qo'shish", lambda msg: is_super_admin(msg))
async def start_add_worker(message: Message, state: FSMContext):
    await message.answer("Ishchining **Ism va Familiyasini** kiriting:")
    await state.set_state(AdminStates.waiting_for_name)


@router.message(AdminStates.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Endi ishchining **Telegram ID** raqamini kiriting (faqat raqamlarda):")
    await state.set_state(AdminStates.waiting_for_id)


@router.message(AdminStates.waiting_for_id)
async def get_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting (Telegram ID raqami):")
        return

    data = await state.get_data()
    full_name = data['name']
    tg_id = int(message.text)

    if await add_user(full_name, tg_id):
        await message.answer(f"✅ **{full_name}** ({tg_id}) muvaffaqiyatli qo'shildi!")
    else:
        await message.answer("❌ Xatolik! Bu ID bazada mavjud yoki boshqa xato yuz berdi.")

    await state.clear()


@router.message(F.text == "📃 Ishchilar ro'yxati", lambda msg: is_super_admin(msg))
async def show_workers(message: Message):
    workers = await get_all_workers()
    if not workers:
        await message.answer("Ishchilar ro'yxati bo'sh.")
        return

    text = "📜 **Ishchilar Ro'yxati:**\n"
    for idx, (name, tg_id) in enumerate(workers, 1):
        text += f"{idx}. **{name}** — ID: `{tg_id}`\n"

    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "🗑 Ishchini o'chirish", lambda msg: is_super_admin(msg))
async def delete_worker_prompt(message: Message):
    await message.answer(
        "Ishchini ro'yxatdan o'chirish uchun uning **Telegram ID** sini yuboring.\nMasalan: `/del 12345678`")


@router.message(Command("del"), lambda msg: is_super_admin(msg))
async def delete_worker_func(message: Message, command: Command):
    if not command.args or not command.args.isdigit():
        await message.answer("Xato format. Faqat Telegram ID raqamini kiriting. Misol: `/del 123456`")
        return

    tg_id_to_delete = int(command.args)
    await delete_worker(tg_id_to_delete)
    await message.answer(f"🗑 ID raqami **{tg_id_to_delete}** bo'lgan ishchi o'chirildi (yoki ro'yxatda yo'q edi).",
                         parse_mode="Markdown")


@router.message(F.text == "📊 Excel Hisobot", lambda msg: is_super_admin(msg))
async def send_report(message: Message):
    data = await get_attendance_data()
    if not data:
        await message.answer("Hisobot yaratish uchun ma'lumotlar bazasida yozuvlar yo'q.")
        return

    await message.answer("⏳ **Excel Hisobot** tayyorlanmoqda. Iltimos, kuting...")

    try:
        file_path = export_to_excel(data)
        await message.answer_document(FSInputFile(file_path), caption="📅 Davomat bo'yicha to'liq Excel hisoboti")
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"❌ Hisobotni yaratishda xatolik yuz berdi: {e}")


@router.message(F.text == "🧹 Bazani Tozalash", lambda msg: is_super_admin(msg))
async def confirm_clear_db(message: Message):
    confirm_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ HA, Tozalashni Boshlash")],
            [KeyboardButton(text="❌ BEKOR QILISH")]
        ], resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer(
        "⚠️ **DIQQAT!** Bu amal barcha davomat va QR tarixini o'chiradi.\nDavom ettirishga ishonchingiz komilmi?",
        reply_markup=confirm_kb, parse_mode="Markdown")


@router.message(F.text == "✅ HA, Tozalashni Boshlash", lambda msg: is_super_admin(msg))
async def execute_clear_db(message: Message):
    try:
        await clear_all_attendance_data()
        await message.answer("✅ **Baza muvaffaqiyatli tozalandi!** Barcha davomat va QR yozuvlari o'chirildi.",
                             reply_markup=admin_kb, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}", reply_markup=admin_kb)


@router.message(F.text == "❌ BEKOR QILISH", lambda msg: is_super_admin(msg))
async def cancel_clear_db(message: Message):
    await message.answer("❌ Baza tozalash bekor qilindi.", reply_markup=admin_kb)