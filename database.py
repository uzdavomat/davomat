import aiosqlite
from config import DB_NAME
from datetime import datetime


async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        # 1. Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                telegram_id INTEGER UNIQUE,
                role TEXT DEFAULT 'worker' 
            )
        """)

        # 2. Davomat jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT,
                date TEXT,
                check_in TEXT,
                check_out TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # 3. QR Kodlar tarixi jadvali (Bir martalik ishlash uchun)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS qr_history (
                token TEXT PRIMARY KEY,
                action_type TEXT,
                date TEXT,
                used_by_id INTEGER,
                used_by_name TEXT,
                timestamp TEXT
            )
        """)
        await db.commit()


# --- QR MANTIQI FUNKSIYALARI ---

async def check_token_used(token):
    """Tokenning avval ishlatilgan yoki ishlatilmaganligini tekshiradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM qr_history WHERE token = ?", (token,)) as cursor:
            return await cursor.fetchone() is not None


async def mark_token_used(token, action_type, user_id, full_name):
    """Tokenni ishlatilgan deb bazaga yozadi."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_now = datetime.now().strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO qr_history (token, action_type, date, used_by_id, used_by_name, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (token, action_type, date_now, user_id, full_name, timestamp))
        await db.commit()


# --- ASOSIY DAVOMAT VA USER FUNKSIYALARI ---

async def add_user(full_name, telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute("INSERT INTO users (full_name, telegram_id) VALUES (?, ?)",
                             (full_name, telegram_id))
            await db.commit()
            return True
        except Exception:
            return False


async def get_user(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            return await cursor.fetchone()


async def get_all_workers():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT full_name, telegram_id FROM users WHERE role='worker' ORDER BY full_name") as cursor:
            return await cursor.fetchall()


async def delete_worker(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
        await db.commit()


async def mark_attendance(telegram_id, action_type):
    date_today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")

    async with aiosqlite.connect(DB_NAME) as db:
        user = await get_user(telegram_id)
        if not user: return "Siz bazada yo'qsiz!", None
        user_db_id, full_name = user[0], user[1]

        async with db.execute("SELECT id, check_in, check_out FROM attendance WHERE user_id = ? AND date = ?",
                              (user_db_id, date_today)) as cursor:
            record = await cursor.fetchone()

        admin_report_text = None

        if action_type == 'in':
            if record and record[1]:
                return "⚠️ **Siz bugun allaqachon kelishni qayd etgansiz!**", None

            if record and not record[1]:
                await db.execute("UPDATE attendance SET check_in = ? WHERE id = ?", (time_now, record[0]))
            else:
                await db.execute("INSERT INTO attendance (user_id, full_name, date, check_in) VALUES (?, ?, ?, ?)",
                                 (user_db_id, full_name, date_today, time_now))
            await db.commit()

            # Admin uchun xabar tayyorlash (Kelish)
            admin_report_text = f"🟢 **{full_name} Ishga Keldi!**\n👤 Ishchi: **{full_name}**\n🕒 Vaqt: **{time_now}**\n📅 Sana: {date_today}"
            return f"✅ Keldingiz: **{time_now}**", admin_report_text

        elif action_type == 'out':
            if not record or not record[1]:
                return "⚠ Xatolik! Siz bugun hali **Keldi** qilmagansiz.", None
            if record[2]:
                return "⚠ Siz allaqachon **Ketdi** qilgansiz!", None

            await db.execute("UPDATE attendance SET check_out = ? WHERE id = ?", (time_now, record[0]))
            await db.commit()

            # Admin uchun xabar tayyorlash (Ketish)
            admin_report_text = f"🔴 **{full_name} Ketdi!**\n👤 Ishchi: **{full_name}**\n🕒 Vaqt: **{time_now}**\n📅 Sana: {date_today}"
            return f"✅ Ketdingiz: **{time_now}**", admin_report_text

        return "Xatolik yuz berdi.", None


async def get_attendance_data():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
                "SELECT full_name, date, check_in, check_out FROM attendance ORDER BY date DESC, full_name") as cursor:
            return await cursor.fetchall()


# --- BAZANI TOZALASH FUNKSIYASI ---

async def clear_all_attendance_data():
    """Davomat va QR history jadvallarini to'liq tozlaydi."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM attendance")
        await db.execute("DELETE FROM qr_history")
        await db.commit()