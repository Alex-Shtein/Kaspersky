from bs4 import BeautifulSoup
import sqlite3
import requests
import re


def parse_vendors():
    base_url = "https://threats.kaspersky.com/"
    add_url = "ru/vendor/"

    vendors = {}
    vendor_id = 0

    try:
        with sqlite3.connect("database.sqlite") as connect:
            cursor = connect.cursor()

            while True:
                try:
                    response = requests.get(base_url + add_url)
                    response.raise_for_status()  # Проверка на успешный ответ
                    soup = BeautifulSoup(response.content, "html.parser")
                    table_rows = soup.select("div[class='table__row']")
                    div = soup.select_one("div.pagination__item.next")
                    match = re.search(
                        r"window\.location\.href='https://threats\.kaspersky\.com/(.*)'",
                        str(div),
                    )

                    for table_row in table_rows:
                        vendor_name = (
                            table_row.find("div", class_="table__col")
                            .text.replace("&nbsp;", "")
                            .strip()
                        )
                        if vendor_name not in vendors:
                            vendor_id += 1
                            vendors[vendor_name] = vendor_id

                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Vendors (vendor_id, vendor_name) VALUES (?, ?)
                            """,
                            (
                                vendors[vendor_name],
                                vendor_name,
                            ),
                        )
                        connect.commit()

                    if match:
                        add_url = match.group(1)
                    else:
                        break

                except requests.RequestException as e:
                    print(f"Error fetching {base_url + add_url}: {e}")
                    break  # Прерываем цикл при ошибке запроса

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")


def parse_products():
    base_url = "https://threats.kaspersky.com/"
    add_url = "en/product/"

    products = {}
    product_id = 0

    try:
        with sqlite3.connect("database.sqlite") as connect:
            cursor = connect.cursor()

            while True:
                try:
                    response = requests.get(base_url + add_url)
                    response.raise_for_status()  # Проверка на успешный ответ
                    soup = BeautifulSoup(response.content, "html.parser")
                    table_rows = soup.select("div[class='table__row']")
                    div = soup.select_one("div.pagination__item.next")
                    match = re.search(
                        r"window\.location\.href='https://threats\.kaspersky\.com/(.*)'",
                        str(div),
                    )

                    for table_row in table_rows:
                        product_name = (
                            table_row.select_one(
                                "div[class='table__col table__col_title']"
                            )
                            .text.replace("&nbsp;", "")
                            .strip()
                        )
                        vendor_name = (
                            table_row.select_one("div[class='table__col']")
                            .text.replace("&nbsp;", "")
                            .strip()
                        )

                        # Получаем vendor_id из базы данных
                        cursor.execute(
                            """
                            SELECT vendor_id FROM Vendors WHERE vendor_name = ?
                            """,
                            (vendor_name,),
                        )
                        vendor_ids = cursor.fetchone()  # Извлекаем результат запроса
                        vendor_id = vendor_ids[0] if vendor_ids else None

                        if product_name not in products:
                            product_id += 1
                            products[product_name] = product_id

                        # Используем "INSERT OR IGNORE" для игнорирования дубликатов
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Products (product_id, product_name, vendor_id) VALUES (?, ?, ?)
                            """,
                            (products[product_name], product_name, vendor_id),
                        )
                        connect.commit()

                    if match:
                        add_url = match.group(1)
                    else:
                        break  # Выходим из цикла, если больше нет страниц

                except requests.RequestException as e:
                    print(f"Error fetching {base_url + add_url}: {e}")
                    break  # Прерываем цикл при ошибке запроса

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")


def parse_vulnerabilities():
    try:
        with sqlite3.connect("database.sqlite") as connect:
            cursor = connect.cursor()

            base_url = "https://threats.kaspersky.com/"
            add_url = "ru/vulnerability/"

            while True:
                try:
                    response = requests.get(base_url + add_url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
                    table_rows = soup.select("div[class='table__row']")
                    div = soup.select_one("div.pagination__item.next")
                    match = re.search(
                        r"window\.location\.href='https://threats\.kaspersky\.com/(.*)'",
                        str(div),
                    )

                    for table_row in table_rows:
                        table_cols = table_row.select("div.table__col")
                        vulnerability_id = (
                            table_cols[0].text.replace("&nbsp;", "").strip()
                        )
                        vulnerability_name = (
                            table_cols[1].text.replace("&nbsp;", "").strip()
                        )
                        product_name = table_cols[2].text.replace("&nbsp;", "").strip()
                        href = table_cols[0].find("a")["href"]

                        cursor.execute(
                            """
                            SELECT product_id FROM Products WHERE product_name = ?
                            """,
                            (product_name,),
                        )

                        product_ids = cursor.fetchone()
                        product_id = product_ids[0] if product_ids else None

                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Vulnerabilities (vulnerability_id, vulnerability_name, product_id, href)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                vulnerability_id,
                                vulnerability_name,
                                product_id,
                                href,
                            ),
                        )
                        connect.commit()

                    if match:
                        add_url = match.group(1)
                    else:
                        break

                except requests.RequestException as e:
                    print(f"Error fetching {base_url + add_url}: {e}")
                    break  # Прерываем цикл при ошибке запроса

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")


def parse_tags():
    try:
        with sqlite3.connect("database.sqlite") as connect:
            cursor = connect.cursor()

            cursor.execute(
                """
                SELECT href, vulnerability_id FROM Vulnerabilities
                """
            )

            rows = cursor.fetchall()

            for href, vulnerability_id in rows:
                try:
                    response = requests.get(href)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, "html.parser")
                    tags__tag = soup.select("div.tags__tag")

                    for tag__tag in tags__tag:
                        tag_name = re.search(r"([^</ \xa0]*)", str(tag__tag.text)).group(1)
                        cursor.execute(
                            """
                            INSERT INTO Tags (tag_name, vulnerability_id)
                            VALUES (?, ?)
                            """,
                            (
                                tag_name,
                                vulnerability_id,
                            ),
                        )
                        connect.commit()
                except requests.RequestException as e:
                    print(f"Error fetching {href}: {e}")
                    break

    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
