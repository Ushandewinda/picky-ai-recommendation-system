import sqlite3

def create_database():
    conn = sqlite3.connect("picky.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def insert_sample_products():
    conn = sqlite3.connect("picky.db")
    cursor = conn.cursor()

    products = [
        ("iPhone 15", "Electronics", 999),
        ("Nike Air Max", "Shoes", 150),
        ("MacBook Pro", "Electronics", 1999),
        ("Adidas Hoodie", "Clothing", 80)
    ]

    cursor.executemany(
        "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
        products
    )

    conn.commit()
    conn.close()
