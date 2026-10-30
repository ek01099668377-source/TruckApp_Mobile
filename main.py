import flet as ft
import sqlite3
import os
import shutil
from datetime import datetime

# ==========================================
# 1. إعدادات قاعدة البيانات (مهم جداً للأندرويد)
# ==========================================
def get_db_path():
    # الحصول على المسار الآمن للتطبيق على الهاتف
    app_data_dir = os.getenv("FLET_APP_STORAGE_DATA")
    if not app_data_dir:
        # مسار احتياطي لو شغال على الكمبيوتر
     app_data_dir = os.path.dirname(os.path.abspath(file))
    return os.path.join(app_data_dir, "trips.db")

def init_db():
    # مسار مضمون وموثوق في الأندرويد
    db_path = os.path.join(os.getenv("FLET_APP_STORAGE_DATA"), "trips.db")
    
    # لو المسار مش موجود، هنستخدم مسار بديل
    if not os.getenv("FLET_APP_STORAGE_DATA"):
        db_path = "trips.db"
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_num TEXT,
            date TEXT,
            statement TEXT,
            revenue REAL,
            driver_wage REAL,
            gas REAL,
            oil REAL,
            toll REAL,
            fees REAL,
            maintenance REAL,
            tip REAL,
            electricity REAL,
            wash REAL,
            deduction REAL
        )
    """)
    conn.commit()
    conn.close()

# ==========================================
# 2. دالة الحفظ
# ==========================================
def save_trip(page, tf_num, tf_date, tf_stat, tf_rev, tf_gas, tf_oil, tf_toll, tf_fees, tf_maint, tf_tip, tf_elec, tf_wash, tf_ded, trip_id=None):
    try:
        rev = float(tf_rev.value or 0)
        drv_wage = rev * 0.2
        
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if trip_id:
            cursor.execute("""
                UPDATE trips SET trip_num=?, date=?, statement=?, revenue=?, driver_wage=?, gas=?, oil=?, toll=?, fees=?, maintenance=?, tip=?, electricity=?, wash=?, deduction=? WHERE id=?
            """, (tf_num.value, tf_date.value, tf_stat.value, rev, drv_wage, float(tf_gas.value or 0), float(tf_oil.value or 0), float(tf_toll.value or 0), float(tf_fees.value or 0), float(tf_maint.value or 0), float(tf_tip.value or 0), float(tf_elec.value or 0), float(tf_wash.value or 0), float(tf_ded.value or 0), trip_id))
        else:
            cursor.execute("""
                INSERT INTO trips (trip_num, date, statement, revenue, driver_wage, gas, oil, toll, fees, maintenance, tip, electricity, wash, deduction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tf_num.value, tf_date.value, tf_stat.value, rev, drv_wage, float(tf_gas.value or 0), float(tf_oil.value or 0), float(tf_toll.value or 0), float(tf_fees.value or 0), float(tf_maint.value or 0), float(tf_tip.value or 0), float(tf_elec.value or 0), float(tf_wash.value or 0), float(tf_ded.value or 0)))
        
        conn.commit()
        conn.close()
        page.snack_bar = ft.SnackBar(ft.Text("تم الحفظ بنجاح!"), bgcolor="green")
        page.snack_bar.open = True
        page.update()
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"خطأ في الحفظ: {e}"), bgcolor="red")
        page.snack_bar.open = True
        page.update()

# ==========================================
# 3. الدالة الرئيسية وواجهة التطبيق
# ==========================================
def main(page: ft.Page):
    page.title = "إدارة الرحلات"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # محاولة تهيئة الداتابيز
    try:
        init_db()
    except Exception as e:
        page.add(ft.Text(f"خطأ في قاعدة البيانات: {e}", color="red"))
        return

    # إنشاء حقول الإدخال
    tf_num = ft.TextField(label="رقم الرحلة")
    tf_date = ft.TextField(label="التاريخ", value=datetime.now().strftime("%Y-%m-%d"))
    tf_stat = ft.TextField(label="البيان")
    tf_rev = ft.TextField(label="الإيراد", keyboard_type=ft.KeyboardType.NUMBER)
    tf_gas = ft.TextField(label="بنزين", keyboard_type=ft.KeyboardType.NUMBER)
    tf_oil = ft.TextField(label="زيت", keyboard_type=ft.KeyboardType.NUMBER)
    tf_toll = ft.TextField(label="رسوم طرق", keyboard_type=ft.KeyboardType.NUMBER)
    tf_fees = ft.TextField(label="رسوم", keyboard_type=ft.KeyboardType.NUMBER)
    tf_maint = ft.TextField(label="صيانة", keyboard_type=ft.KeyboardType.NUMBER)
    tf_tip = ft.TextField(label="بقشيش", keyboard_type=ft.KeyboardType.NUMBER)
    tf_elec = ft.TextField(label="كهرباء", keyboard_type=ft.KeyboardType.NUMBER)
    tf_wash = ft.TextField(label="غسيل", keyboard_type=ft.KeyboardType.NUMBER)
    tf_ded = ft.TextField(label="خصم", keyboard_type=ft.KeyboardType.NUMBER)

    # زر الحفظ
    btn_save = ft.ElevatedButton(
        text="حفظ الرحلة",
        icon=ft.Icons.SAVE,
        on_click=lambda e: save_trip(page, tf_num, tf_date, tf_stat, tf_rev, tf_gas, tf_oil, tf_toll, tf_fees, tf_maint, tf_tip, tf_elec, tf_wash, tf_ded)
    )

    # إضافة العناصر للصفحة
    page.add(
        ft.AppBar(title=ft.Text("تطبيق TruckApp"), bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
        ft.Column(
            controls=[
                tf_num, tf_date, tf_stat, tf_rev,
                tf_gas, tf_oil, tf_toll, tf_fees,
                tf_maint, tf_tip, tf_elec, tf_wash, tf_ded,
                btn_save
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )
    )

# ==========================================
# 4. تشغيل التطبيق (مع حماية من الإغلاق المفاجئ)
# ==========================================
if __name__ == "__main__":
    def run_app(page: ft.Page):
        try:
            main(page)
        except Exception as e:
            # هنا هنخلي التطبيق يمسح الشاشة السوداء ويطبع الخطأ
            page.controls.clear() 
            page.add(
                ft.Text("حدث خطأ أثناء التشغيل:", color="red", size=20, weight="bold"),
                ft.Text(str(e), color="red", size=16, selectable=True)
            )
            page.update()

    ft.app(target=run_app)