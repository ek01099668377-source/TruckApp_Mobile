import flet as ft
import sqlite3
import os
import shutil
from datetime import datetime

def init_db():
    conn = sqlite3.connect("trips.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_num TEXT, date TEXT, statement TEXT, revenue REAL,
            driver_wage REAL, gas REAL, oil REAL, toll REAL, fees REAL, expenses REAL,
            wash REAL, maintenance REAL, tip REAL, electricity REAL, deductions REAL, received REAL
        )
    """)
    conn.commit()
    conn.close()

def main(page: ft.Page):
    init_db()

    page.title = "برنامج النقلات - موبايل"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 10

    def get_next_trip_number():
        try:
            conn = sqlite3.connect("trips.db")
            cursor = conn.cursor()
            cursor.execute("SELECT trip_num FROM trips ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            if result and result[0] and str(result[0]).isdigit():
                return str(int(result[0]) + 1)
        except Exception:
            pass
        return "1"

    def create_card(title, color, width=170):
        value_text = ft.Text("0.00", size=18, weight="bold", color="white", text_align=ft.TextAlign.CENTER)
        container = ft.Container(
            content=ft.Column(
                [ft.Text(title, size=12, color="white", text_align=ft.TextAlign.CENTER), value_text],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5
            ),
            bgcolor=color, border_radius=10, padding=10, width=width, height=90
        )
        return container, value_text

    card1, txt_rev = create_card("إجمالي الإيرادات", "#2E7D32")
    card2, txt_exp = create_card("إجمالي المصاريف", "#C62828")
    card3, txt_net = create_card("صافي الربح", "#1565C0")
    card4, txt_drv = create_card("أجر السائق", "#D84315")
    card5, txt_adv = create_card("العهدة المتبقية", "#AD1457")
    card6, txt_rec = create_card("الواصل", "#E65100")
    card7, txt_fin = create_card("المتبقي النهائي", "#6A1B9A", width=360)

    def update_dashboard():
        try:
            conn = sqlite3.connect("trips.db")
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(revenue), SUM(gas+oil+toll+fees+expenses+wash+maintenance+tip+electricity+deductions+driver_wage), SUM(received), SUM(driver_wage) FROM trips")
            data = cursor.fetchone()
            conn.close()

            total_revenue = data[0] or 0
            total_expenses = data[1] or 0 
            total_received = data[2] or 0
            total_driver_wage = data[3] or 0 
            
            net_profit = total_revenue - total_expenses
            final_remaining = net_profit - total_received
            
            txt_rev.value = f"{total_revenue:,.2f}"
            txt_exp.value = f"{total_expenses:,.2f}"
            txt_net.value = f"{net_profit:,.2f}"
            txt_drv.value = f"{total_driver_wage:,.2f}"
            txt_adv.value = f"{final_remaining:,.2f}"
            txt_rec.value = f"{total_received:,.2f}"
            txt_fin.value = f"{final_remaining:,.2f}"
            page.update()
        except Exception:
            pass

    def backup_db(e):
        if os.path.exists("trips.db"):
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_trips_{date_str}.db"
            try:
                shutil.copy("trips.db", backup_name)
                page.snack_bar = ft.SnackBar(ft.Text(f"تم حفظ النسخة: {backup_name}", color="white"), bgcolor="green")
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"خطأ: {ex}", color="white"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

    def show_view_trips(e=None):
        page.clean()
        trips_list = ft.ListView(expand=1, spacing=10, padding=10)
        
        try:
            conn = sqlite3.connect("trips.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, trip_num, date, statement, revenue, received FROM trips ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                trips_list.controls.append(ft.Text("لا توجد نقلات مسجلة حتى الآن.", color="white"))
            else:
                for row in rows:
                    current_id, current_num, current_date, current_stmt, current_rev, current_rec = row
                    
                    def delete_click(e, t_id=current_id):
                        def close_dlg(e):
                            dlg.open = False
                            page.update()
                        def confirm_delete(e):
                            conn = sqlite3.connect("trips.db")
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM trips WHERE id=?", (t_id,))
                            conn.commit()
                            conn.close()
                            dlg.open = False
                            show_view_trips()
                            update_dashboard()

                        dlg = ft.AlertDialog(
                            title=ft.Text("تأكيد الحذف"),
                            content=ft.Text("هل أنت متأكد من حذف هذه النقلة؟"),
                            actions=[
                                ft.TextButton("نعم، احذف", on_click=confirm_delete, style=ft.ButtonStyle(color="red")),
                                ft.TextButton("إلغاء", on_click=close_dlg),
                            ],
                        )
                        page.overlay.append(dlg)
                        dlg.open = True
                        page.update()

                    def edit_click(e, t_id=current_id):
                        show_add_trip(None, t_id)

                    card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"نقلة رقم: {current_num}", weight="bold", color="blue", size=16),
                                ft.Text(f"{current_date}", size=12, color="gray")
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"البيان: {current_stmt}", color="white"),
                            ft.Row([
                                ft.Text(f"الأجر: {current_rev:,.2f}", color="#4CAF50"),
                                ft.Text(f"الواصل: {current_rec:,.2f}", color="#FF9800")
                            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                            ft.Divider(color="gray", height=1),
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT, icon_color="blue", on_click=edit_click),
                                ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=delete_click)
                            ], alignment=ft.MainAxisAlignment.END)
                        ]),
                        bgcolor="#1e1e1e", padding=15, border_radius=10, border=ft.Border.all(1, "#333")
                    )
                    trips_list.controls.append(card)
        except Exception:
            pass

        page.add(
            ft.Text("سجل النقلات", size=22, weight="bold"), ft.Container(height=10),
            trips_list, ft.Container(height=10),
            ft.Button("رجوع للوحة التحكم", bgcolor="gray", width=300, on_click=show_dashboard)
        )
        page.update()
    def show_add_trip(e=None, trip_id=None):
        page.clean()
        
        def create_input(label, default_val="", is_num=True):
            return ft.TextField(
                label=label, value=default_val, height=45, 
                text_size=14, content_padding=10,
                text_align=ft.TextAlign.RIGHT, 
                keyboard_type=ft.KeyboardType.NUMBER if is_num else ft.KeyboardType.TEXT,
                filled=True, fill_color="#2b2b2b",
                border_color="#555555", focused_border_color="blue"
            )

        v_trip_num, v_date, v_statement = get_next_trip_number(), datetime.now().strftime("%Y-%m-%d"), ""
        v_rev, v_gas, v_oil, v_toll, v_fees, v_exp = "0", "0", "0", "0", "0", "0"
        v_wash, v_maint, v_tip, v_elec, v_ded, v_rec = "0", "0", "0", "0", "0", "0"

        if trip_id:
            try:
                conn = sqlite3.connect("trips.db")
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trips WHERE id=?", (trip_id,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    v_trip_num, v_date, v_statement = str(row[1]), str(row[2]), str(row[3])
                    v_rev, v_gas, v_oil = str(row[4]), str(row[6]), str(row[7])
                    v_toll, v_fees, v_exp = str(row[8]), str(row[9]), str(row[10])
                    v_wash, v_maint, v_tip = str(row[11]), str(row[12]), str(row[13])
                    v_elec, v_ded, v_rec = str(row[14]), str(row[15]), str(row[16])
            except Exception:
                pass

        tf_num = create_input("رقم النقلة", v_trip_num, is_num=False)
        tf_date = create_input("التاريخ", v_date, is_num=False)
        tf_stmt = create_input("البيان/العميل", v_statement, is_num=False)
        tf_rev = create_input("أجر الرحلة", v_rev)
        tf_gas = create_input("جاز", v_gas)
        tf_oil = create_input("زيت", v_oil)
        tf_toll = create_input("كارتة", v_toll)
        tf_fees = create_input("رسوم", v_fees)
        tf_exp = create_input("مصاريف", v_exp)
        tf_wash = create_input("غسيل", v_wash)
        tf_maint = create_input("صيانة", v_maint)
        tf_tip = create_input("إكرامية", v_tip)
        tf_elec = create_input("كهرباء", v_elec)
        tf_ded = create_input("خصومات", v_ded)
        tf_rec = create_input("الواصل", v_rec)

        def save_trip(e):
            try:
                rev = float(tf_rev.value or 0)
                drv_wage = rev * 0.2
                
                conn = sqlite3.connect("trips.db")
                cursor = conn.cursor()
                
                if trip_id:
                    cursor.execute("""
                        UPDATE trips SET trip_num=?, date=?, statement=?, revenue=?, driver_wage=?, gas=?, oil=?, toll=?, fees=?, expenses=?, wash=?, maintenance=?, tip=?, electricity=?, deductions=?, received=? WHERE id=?
                    """, (tf_num.value, tf_date.value, tf_stmt.value, rev, drv_wage, 
                          float(tf_gas.value or 0), float(tf_oil.value or 0), float(tf_toll.value or 0), 
                          float(tf_fees.value or 0), float(tf_exp.value or 0), float(tf_wash.value or 0), 
                          float(tf_maint.value or 0), float(tf_tip.value or 0), float(tf_elec.value or 0), 
                          float(tf_ded.value or 0), float(tf_rec.value or 0), trip_id))
                else:
                    cursor.execute("""
                        INSERT INTO trips (trip_num, date, statement, revenue, driver_wage, gas, oil, toll, fees, expenses, wash, maintenance, tip, electricity, deductions, received) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (tf_num.value, tf_date.value, tf_stmt.value, rev, drv_wage,
                          float(tf_gas.value or 0), float(tf_oil.value or 0), float(tf_toll.value or 0), 
                          float(tf_fees.value or 0), float(tf_exp.value or 0), float(tf_wash.value or 0), 
                          float(tf_maint.value or 0), float(tf_tip.value or 0), float(tf_elec.value or 0), 
                          float(tf_ded.value or 0), float(tf_rec.value or 0)))
                
                conn.commit()
                conn.close()
                
                msg = "تم التعديل بنجاح!" if trip_id else "تم حفظ النقلة بنجاح!"
                page.snack_bar = ft.SnackBar(ft.Text(msg, color="white"), bgcolor="green")
                page.snack_bar.open = True
                show_dashboard()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"خطأ: {ex}", color="white"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        def row(f1, f2=None):
            if f2:
                return ft.Row([ft.Container(f1, expand=1), ft.Container(f2, expand=1)], spacing=10)
            return ft.Row([ft.Container(f1, expand=1), ft.Container(expand=1)], spacing=10)

        btn_text = "تحديث النقلة" if trip_id else "حفظ النقلة"

        form_layout = ft.Column(
            controls=[
                ft.Text("تعديل النقلة" if trip_id else "إضافة نقلة جديدة", size=20, weight="bold"),
                ft.Container(height=5),
                row(tf_num, tf_date), row(tf_stmt, tf_rev),
                row(tf_gas, tf_oil), row(tf_toll, tf_fees),
                row(tf_exp, tf_wash), row(tf_maint, tf_tip),
                row(tf_elec, tf_ded), row(tf_rec),
                ft.Container(height=15),
                ft.Button(btn_text, bgcolor="green", width=300, height=45, on_click=save_trip),
                ft.Button("رجوع", bgcolor="gray", width=300, height=45, on_click=show_dashboard),
                ft.Container(height=10)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, scroll=ft.ScrollMode.ADAPTIVE 
        )
        page.add(form_layout)
        page.update()

    def show_dashboard(e=None):
        page.clean()
        update_dashboard()
        
        title = ft.Text("لوحة تحكم النقلات", size=24, weight="bold", color="white")
        cards_grid = ft.Row(controls=[card1, card2, card3, card4, card5, card6, card7], wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=10, run_spacing=10)

        btn_add = ft.Button("إضافة نقلة", bgcolor="blue", width=170, height=50, on_click=lambda e: show_add_trip())
        btn_view = ft.Button("عرض النقلات", bgcolor="#555555", width=170, height=50, on_click=show_view_trips)
        actions_row = ft.Row([btn_add, btn_view], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        btn_backup = ft.Button("نسخة (DB)", bgcolor="#607D8B", width=170, height=45, on_click=backup_db)
        tools_row = ft.Row([btn_backup], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        btn_logout = ft.Button("تسجيل خروج", bgcolor="red", width=360, on_click=show_login)

        page.add(
            title, ft.Container(height=10), cards_grid, ft.Container(height=20), 
            actions_row, ft.Container(height=10), tools_row, ft.Container(height=10), btn_logout
        )
        page.update()

    # --- تعريف شاشة الدخول قبل استدعائها ---
    def show_login(e=None):
        page.clean()
        
        user_field = ft.TextField(label="اسم المستخدم", width=280, text_align=ft.TextAlign.RIGHT, filled=True, fill_color="#2b2b2b")
        pass_field = ft.TextField(label="كلمة المرور", password=True, width=280, text_align=ft.TextAlign.RIGHT, filled=True, fill_color="#2b2b2b")
        
        def login_click(e):
            if user_field.value == "admin" and pass_field.value == "1234":
                show_dashboard()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("اسم المستخدم أو كلمة المرور غير صحيحة!", color="white"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                login_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOCK_PERSON, size=60, color="blue"),
                    ft.Text("تسجيل الدخول", size=24, weight="bold"),
                    ft.Container(height=10), user_field, pass_field, ft.Container(height=10),
                    ft.Button(content=ft.Text("دخول", size=18, weight="bold"), width=280, height=50, bgcolor="green", on_click=login_click)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=30, border_radius=15, bgcolor="#1e1e1e", shadow=ft.BoxShadow(blur_radius=20, color="black45")
        )
        
            page.controls.append(login_card)
            page.update()

    show_login()

if __name__ == "__main__":
    try:
        ft.run(main)
    except Exception as e:
        print(e)