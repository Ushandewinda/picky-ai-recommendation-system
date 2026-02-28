import sqlite3

PRODUCTS = [
    # Electronics
    ("Samsung Galaxy S24", "Electronics", 899, "Android smartphone with high-resolution display and fast processor."),
    ("Sony WH-1000XM5", "Electronics", 329, "Noise-cancelling wireless headphones with long battery life."),
    ("Apple Watch Series 9", "Electronics", 399, "Smartwatch with health tracking, fitness features and notifications."),
    ("Logitech MX Master 3S", "Electronics", 99, "Ergonomic wireless mouse designed for productivity and comfort."),
    ("Canon EOS R50", "Electronics", 749, "Compact mirrorless camera for high quality photos and video."),

    # Clothing
    ("Uniqlo Supima Cotton T-Shirt", "Clothing", 19.9, "Soft breathable cotton t-shirt suitable for everyday wear."),
    ("Levi's 501 Jeans", "Clothing", 89.0, "Classic straight-fit jeans with durable denim material."),
    ("Nike Tech Fleece Hoodie", "Clothing", 110.0, "Lightweight warm hoodie with modern sporty fit."),
    ("Adidas Track Jacket", "Clothing", 65.0, "Comfortable jacket for casual style and training."),
    ("North Face Puffer Jacket", "Clothing", 220.0, "Insulated winter jacket for cold weather protection."),

    # Shoes
    ("Nike Air Force 1", "Shoes", 109.0, "Iconic sneakers with cushioned sole for daily comfort."),
    ("Adidas Ultraboost", "Shoes", 180.0, "Running shoes with responsive cushioning for long-distance comfort."),
    ("New Balance 574", "Shoes", 95.0, "Classic casual sneakers with supportive midsole."),
    ("Dr. Martens 1460 Boots", "Shoes", 169.0, "Leather boots with durable build and signature style."),
    ("Puma RS-X", "Shoes", 120.0, "Chunky sneakers with bold design and comfort."),

    # Home & Kitchen
    ("Philips Air Fryer", "Home & Kitchen", 129.0, "Air fryer for healthier cooking with less oil."),
    ("Instant Pot Duo", "Home & Kitchen", 99.0, "Multi-cooker for pressure cooking, rice, soups and more."),
    ("Dyson V11 Vacuum", "Home & Kitchen", 499.0, "Cordless vacuum with strong suction and smart cleaning modes."),
    ("IKEA Desk Lamp", "Home & Kitchen", 19.0, "Adjustable lamp for study or office desk lighting."),
    ("Non-stick Frying Pan Set", "Home & Kitchen", 35.0, "Durable non-stick pans for easy everyday cooking."),

    # Beauty
    ("CeraVe Moisturising Cream", "Beauty", 16.0, "Hydrating moisturiser with ceramides for dry skin."),
    ("The Ordinary Niacinamide Serum", "Beauty", 8.5, "Serum to reduce blemishes and improve skin texture."),
    ("Maybelline Mascara", "Beauty", 9.9, "Volumising mascara for longer and fuller lashes."),
    ("L'Oreal Shampoo", "Beauty", 6.5, "Nourishing shampoo for smooth and healthy hair."),
    ("Nivea Body Lotion", "Beauty", 5.0, "Daily body lotion for long lasting moisture."),

    # Sports & Fitness
    ("Yoga Mat", "Sports & Fitness", 20.0, "Non-slip yoga mat for workouts and stretching."),
    ("Adjustable Dumbbells", "Sports & Fitness", 150.0, "Space-saving adjustable dumbbells for home training."),
    ("Resistance Bands Set", "Sports & Fitness", 18.0, "Bands for strength training and mobility exercises."),
    ("Fitness Tracker Band", "Sports & Fitness", 39.0, "Basic tracker for steps, sleep and heart rate monitoring."),
    ("Running Water Bottle", "Sports & Fitness", 12.0, "Lightweight bottle for hydration during workouts."),

    # Books
    ("Clean Code", "Books", 32.0, "Software craftsmanship book focused on writing maintainable code."),
    ("Python Crash Course", "Books", 28.0, "Beginner-friendly Python programming guide with projects."),
    ("Design Patterns", "Books", 40.0, "Classic book explaining reusable object-oriented design patterns."),
    ("Atomic Habits", "Books", 14.0, "Practical methods to build good habits and break bad ones."),
    ("Deep Work", "Books", 13.0, "Strategies for focused work and productivity."),

    # Accessories
    ("Anker Power Bank", "Accessories", 25.0, "Portable charger for phones and small devices."),
    ("USB-C Cable Pack", "Accessories", 12.0, "Fast-charging USB-C cables for daily use."),
    ("Laptop Sleeve 13-inch", "Accessories", 15.0, "Protective sleeve for laptops with soft interior."),
    ("Wireless Charger Pad", "Accessories", 19.0, "Convenient wireless charging pad for compatible devices."),
    ("Bluetooth Speaker", "Accessories", 29.0, "Compact speaker with clear sound and easy connectivity."),
]

def main():
    conn = sqlite3.connect("picky.db")
    cur = conn.cursor()

    # Ensure description column exists (safe)
    try:
        cur.execute("ALTER TABLE products ADD COLUMN description TEXT;")
    except sqlite3.OperationalError:
        pass

    # Insert products
    cur.executemany(
        "INSERT INTO products (name, category, price, description) VALUES (?, ?, ?, ?)",
        PRODUCTS
    )

    conn.commit()
    conn.close()
    print(f"Inserted {len(PRODUCTS)} products successfully.")

if __name__ == "__main__":
    main()