from parse import *


def clear_tables():
    """
    Очищает базу данных для её восстановления.
    """
    try:
        with sqlite3.connect("database.sqlite") as connect:
            cursor = connect.cursor()
            cursor.execute("DROP TABLE IF EXISTS Tags")
            cursor.execute("DROP TABLE IF EXISTS Vendors")
            cursor.execute("DROP TABLE IF EXISTS Products")
            cursor.execute("DROP TABLE IF EXISTS Vulnerabilities")
            connect.commit()
    except sqlite3.Error as e:
        print(f"Database error during clearing tables: {e}")


def create_tables():
    """
    Создаёт базу данных с таблицами Vendors, Products, Vulnerabilities, Tags.
    """
    try:
        with sqlite3.connect("database.sqlite") as connect:
            cursor = connect.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Vendors(
                    vendor_id INTEGER PRIMARY KEY,
                    vendor_name TEXT
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Products(
                    product_id INTEGER PRIMARY KEY,
                    product_name TEXT,
                    vendor_id INTEGER,
                    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Vulnerabilities(
                    vulnerability_id TEXT PRIMARY KEY,
                    vulnerability_name TEXT,
                    product_id INTEGER,
                    href TEXT,
                    FOREIGN KEY (product_id) REFERENCES Products(product_id)
                );
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Tags(
                    tag_name TEXT,
                    vulnerability_id TEXT,
                    FOREIGN KEY (vulnerability_id) REFERENCES Vulnerabilities(vulnerability_id)
                )
                """
            )

            connect.commit()
    except sqlite3.Error as e:
        print(f"Database error during table creation: {e}")


def create():
    """
    Вызывает основные функции для создания и заполнения базы данных с таблицами
    Vendors, Products, Vulnerabilities, Tags.
    """
    clear_tables()
    create_tables()
    parse_vendors()
    parse_products()
    parse_vulnerabilities()
    parse_tags()
