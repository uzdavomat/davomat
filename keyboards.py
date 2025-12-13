from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Admin Menyusi
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 Keldi QR"), KeyboardButton(text="📤 Ketdi QR")],
        [KeyboardButton(text="➕ Ishchi qo'shish"), KeyboardButton(text="📊 Davomat")],
        [KeyboardButton(text="📃 Ishchilar ro'yxati")]
    ],
    resize_keyboard=True
)

# Ishchi Menyusi (Aslida ular QR skan qiladi, bu shunchaki info)
worker_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ Mening ID raqamim"), KeyboardButton(text="❓ Yordam")]
    ],
    resize_keyboard=True
)