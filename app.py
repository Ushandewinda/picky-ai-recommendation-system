from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_products():
    conn = sqlite3.connect("picky.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = sqlite3.connect("picky.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_recommendations(category, product_id):
    conn = sqlite3.connect("picky.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id != ?", (product_id,))
    products = cursor.fetchall()

    recommendations = []

    for product in products:
        score = 0

        # Content-based similarity scoring
        if product["category"] == category:
            score += 10

        recommendations.append((score, product))

    # Sort by score descending
    recommendations.sort(reverse=True, key=lambda x: x[0])

    # Return top 2 recommendations
    top_recommendations = [item[1] for item in recommendations[:2]]

    conn.close()
    return top_recommendations


@app.route("/")
def home():
    products = get_products()
    return render_template("index.html", products=products)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    recommendations = get_recommendations(product["category"], product_id)
    return render_template("product.html", product=product, recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
