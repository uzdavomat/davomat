# import os
# from dotenv import load_dotenv

# load_dotenv()
# sdfg

BOT_TOKEN = "8277394474:AAG-p0vu9R3s4wDzEy9BJDqFwOghGXE3S1E"

# ADMIN SOZLAMALARI
SUPER_ADMIN_ID = 724199079

# NOTIFICATION ADMIN ID'larini yuklash va ro'yxatga aylantirish
notification_ids_str = "8329974466"
if notification_ids_str:
    OTHER_ADMIN_IDS = [int(i.strip()) for i in notification_ids_str.split(',') if i.strip().isdigit()]
else:
    OTHER_ADMIN_IDS = []

# Barcha xabarnoma oluvchi IDlar (Bosh Admin va Oddiy Adminlar)
NOTIFICATION_ADMIN_IDS = list(set([SUPER_ADMIN_ID] + OTHER_ADMIN_IDS))

DB_NAME = "attendance.db"
SECRET_KEY = "super_maxfiy_kalit_att_system"

# --- MAOSHLAR VA GRAFIK SOZLAMALARI ---
HOURLY_RATE = 6410 # Soatiga 6410 so'm (Faqat maksimal 9 soatgacha to'lanadi)

# Ish vaqti chegaralari
LATE_TIME_LIMIT = "09:00:00" # Kechikish boshlanadigan vaqt (Kelish chegarasi)

# Tushlik vaqti chegaralari (1 soat hisoblanmaydi)
LUNCH_START = "13:00:00"
LUNCH_END = "14:00:00"