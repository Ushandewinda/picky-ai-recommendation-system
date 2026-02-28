import sqlite3
import requests

API_URL = "https://fakestoreapi.com/products"

def main():
    # Fetch from external API
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    items = resp.json()

    conn = sqlite3.connect("picky.db")
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for it in items:
        name = it.get("title", "").strip()
        category = it.get("category", "Other").strip()
        price = float(it.get("price", 0))
        description = (it.get("description") or "").strip()
        image_url = (it.get("image") or "").strip()
        source = "FakeStoreAPI"

        # Avoid duplicates by name (simple approach)
        cur.execute("SELECT id FROM products WHERE name = ?", (name,))
        exists = cur.fetchone()
        if exists:
            skipped += 1
            continue

        cur.execute("""
            INSERT INTO products (name, category, price, description, image_url, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, price, description, image_url, source))

        inserted += 1

    conn.commit()
    conn.close()

    print(f"Imported from FakeStoreAPI: inserted={inserted}, skipped={skipped}, total_api_items={len(items)}")

if __name__ == "__main__":
    main()