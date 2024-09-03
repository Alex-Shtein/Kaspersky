import sqlite3
import json
import os


# Список уязвимостей в продукте X
def top(tag_name):
    """
    Создаёт JSON-файл со списком Топ-5 вендоров ПО, допущенных к наибольшему количеству уязвимостей,
    позволяющих подменить пользовательский интерфейс.
    """
    try:
        # Подключение к базе данных
        with sqlite3.connect("database.sqlite") as connect:
            cursor = connect.cursor()

            # SQL запрос для получения топ-5 вендоров по количеству уязвимостей с заданным тегом
            cursor.execute(
                """
                SELECT v.vendor_name, COUNT(vu.vulnerability_id) AS vulnerability_count
                FROM Vendors v
                JOIN Products p ON v.vendor_id = p.vendor_id
                JOIN Vulnerabilities vu ON p.product_id = vu.product_id
                JOIN Tags t ON vu.vulnerability_id = t.vulnerability_id
                WHERE t.tag_name = ?
                GROUP BY v.vendor_name
                ORDER BY vulnerability_count DESC
                LIMIT 5;
                """,
                (tag_name,),
            )
            results = cursor.fetchall()

            # Если результаты не пустые, создать JSON-файл
            if results:
                if os.path.exists("top.json"):
                    os.remove("top.json")

                with open("top.json", "w") as file:
                    top_vendors = [
                        {"vendor_name": row[0], "vulnerability_count": row[1]}
                        for row in results
                    ]
                    json.dump(top_vendors, file, indent=4)
            else:
                print(f"No vendors found with the tag '{tag_name}'.")

    except sqlite3.Error as e:
        print(f"Database error during fetching top vendors: {e}")


def vulnerability(product_name):
    """
    Создаёт JSON-файл со списоком уязвимостей продкта product_name.
    """
    try:
        # Используем контекстный менеджер для подключения к базе данных
        with sqlite3.connect("database.sqlite") as conn:
            cursor = conn.cursor()

            # Получаем идентификатор продукта
            cursor.execute(
            """
            SELECT product_id FROM Products WHERE product_name = ?
            """,
                (product_name,),
            )
            product_id = cursor.fetchone()

            if product_id is None:
                print(f"Product '{product_name}' not found.")
                return

            product_id = product_id[0]

            # Извлекаем уязвимости для продукта
            cursor.execute(
                """
                SELECT vulnerability_id, vulnerability_name, href 
                FROM Vulnerabilities 
                WHERE product_id = ?
                """,
                (product_id,),
            )
            vulnerabilities = cursor.fetchall()

            def range():
                n = 1
                while True:
                    yield n
                    n += 1

            # Формируем список уязвимостей
            vulnerability_list = {}
            for vuln, i in zip(vulnerabilities, range()):
                if i not in vulnerability_list:
                    vulnerability_list[i] = {}
                vulnerability_list[i] = {
                    "vulnerability_id": vuln[0],
                    "vulnerability_name": vuln[1],
                    "url": vuln[2],
                }

            if os.path.exists("vulnerability.json"):
                os.remove("vulnerability.json")

            # Сохраняем в JSON-файл
            with open("vulnerability.json", "w") as json_file:
                json.dump(vulnerability_list, json_file, indent=4)

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
