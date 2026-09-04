"""Populate an EMPTY database with synthetic portfolio data; never delete rows."""
import os
from dotenv import load_dotenv
from app.paths import ENV_PATH

load_dotenv(ENV_PATH)
from app.db import get_db_connection


def seed():
    if os.getenv("DEMO_MODE", "").lower() != "true":
        raise SystemExit("Set DEMO_MODE=true; use a separate local database.")
    connection = get_db_connection()
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute("SELECT setting_value FROM site_settings WHERE setting_key='demo_seed_version'")
            if cursor.fetchone():
                print("Demo data already present; no changes.")
                return
            cursor.execute("SELECT (SELECT count(*) FROM leads) + (SELECT count(*) FROM projects) + (SELECT count(*) FROM project_categories)")
            if cursor.fetchone()[0]:
                raise SystemExit("Refusing to seed a populated database. No data changed.")
            for title, slug, parent, image, order in [
                ("Татуировка", "tattoo", None, "linework", 10),
                ("Картины", "paintings", None, "painting", 20),
                ("Графика", "tattoo-graphics", "tattoo", "ornament", 11),
                ("Свободные эскизы", "free-sketches", "tattoo", "linework", 12),
                ("Холст", "paintings-canvas", "paintings", "painting", 21),
            ]:
                cursor.execute("""INSERT INTO project_categories
                    (title,slug,parent_slug,image_url,display_order,short_description)
                    VALUES (%s,%s,%s,%s,%s,%s)""",
                    (title,slug,parent,f"/static/demo/{image}.svg",order,"Демонстрационные работы для знакомства с интерфейсом."))
            for title, slug, category, kind, image, order in [
                ("Тихие вершины", "demo-mountains", "tattoo-graphics", "tattoo", "linework", 1),
                ("Ритм линий", "demo-geometry", "free-sketches", "tattoo", "ornament", 2),
                ("После заката", "demo-sunset", "paintings-canvas", "painting", "painting", 3),
            ]:
                cursor.execute("""INSERT INTO projects (title,slug,category_slug,project_type,
                    short_description,full_description,image_url,is_featured,display_order,style,format)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,TRUE,%s,%s,%s)""",
                    (title,slug,category,kind,"Демонстрационная работа, не реальный заказ.",
                     "Синтетический пример для GitHub-портфолио. Изображение создано как SVG-заглушка; оно не выдаётся за выполненную работу мастера.",
                     f"/static/demo/{image}.svg",order,"Графика","Индивидуальный проект"))
            for i, status in enumerate(("new", "in_work", "done"), 1):
                cursor.execute("""INSERT INTO leads (name,contact,contact_method,service_type,city,
                    idea,personal_data_agreement,lead_status,project_title,lead_source)
                    VALUES (%s,%s,'email','tattoo','Санкт-Петербург',%s,TRUE,%s,%s,'demo')""",
                    (f"Демо-клиент {i}",f"demo{i}@example.com","Тестовая заявка. Персональных данных здесь нет.",status,"Демонстрационный эскиз"))
            cursor.execute("""INSERT INTO city_slots (city,date_label,slot_date,slot_time,status)
                VALUES ('Санкт-Петербург','Демо: свободная дата',CURRENT_DATE + 7,'14:00–17:00','available')""")
            cursor.execute("INSERT INTO site_settings(setting_key,setting_value) VALUES ('demo_seed_version','1')")
        print("Demo data created: 5 categories, 3 projects, 3 synthetic leads, 1 slot.")
    finally:
        connection.close()


if __name__ == "__main__":
    seed()
