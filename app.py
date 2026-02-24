from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "picky_secret_key"


# -------------------------
# Database connection
# -------------------------
def get_db_connection():
    conn = sqlite3.connect("picky.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# Product functions
# -------------------------
def get_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return products


def get_products_with_text():
    """
    Fetch minimal fields needed to build TF-IDF text corpus.
    """
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, name, category, description, price
        FROM products
    """).fetchall()
    conn.close()
    return rows


def get_product_by_id(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return product


def get_rating_stats(product_id):
    conn = get_db_connection()
    row = conn.execute("""
        SELECT AVG(rating) as avg_rating, COUNT(rating) as count_rating
        FROM ratings
        WHERE product_id = ?
    """, (product_id,)).fetchone()
    conn.close()

    if row["avg_rating"] is None:
        return 0, 0
    return round(row["avg_rating"], 1), row["count_rating"]


# -------------------------
# Recommendation functions
# -------------------------
def get_user_preferred_categories(user_id=1):
    """
    Simple preference model:
    categories where the user's average rating >= 4.
    """
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT p.category, AVG(r.rating) as avg_rating
        FROM ratings r
        JOIN products p ON r.product_id = p.id
        WHERE r.user_id = ?
        GROUP BY p.category
        HAVING avg_rating >= 4
        ORDER BY avg_rating DESC
    """, (user_id,)).fetchall()
    conn.close()

    return [row["category"] for row in rows]


def get_personalised_recommendations(user_id=1, limit=3):
    """
    Homepage personalised recs:
    - If user has preferred categories, recommend products from those categories
      excluding products already rated by user.
    - Otherwise fallback to top-rated products globally.
    """
    preferred_categories = get_user_preferred_categories(user_id)
    conn = get_db_connection()

    if not preferred_categories:
        recs = conn.execute("""
            SELECT p.*, IFNULL(AVG(r.rating), 0) as avg_rating
            FROM products p
            LEFT JOIN ratings r ON p.id = r.product_id
            GROUP BY p.id
            ORDER BY avg_rating DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return recs

    placeholders = ",".join(["?"] * len(preferred_categories))
    recs = conn.execute(f"""
        SELECT p.*
        FROM products p
        WHERE p.category IN ({placeholders})
          AND p.id NOT IN (
              SELECT product_id FROM ratings WHERE user_id = ?
          )
        LIMIT ?
    """, (*preferred_categories, user_id, limit)).fetchall()

    conn.close()
    return recs


def get_tfidf_recommendations(product_id, top_n=3):
    """
    Content-based filtering using TF-IDF + cosine similarity.
    Build text from: name + category + description.
    Return top_n most similar products (excluding itself).
    """
    products = get_products_with_text()

    corpus = []
    ids = []
    for p in products:
        text = f"{p['name']} {p['category']} {(p['description'] or '')}"
        corpus.append(text)
        ids.append(p["id"])

    if product_id not in ids:
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    sim_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    idx = ids.index(product_id)
    scores = list(enumerate(sim_matrix[idx]))

    # sort by similarity desc, remove itself
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = [s for s in scores if ids[s[0]] != product_id]

    top_indices = [s[0] for s in scores[:top_n]]
    top_ids = [ids[i] for i in top_indices]

    # fetch full product rows in same order
    conn = get_db_connection()
    recs = []
    for pid in top_ids:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
        if row:
            recs.append(row)
    conn.close()

    return recs


# -------------------------
# Routes
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            conn.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        conn.close()

        session["user_id"] = user["id"]
        session["username"] = username
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/")
def home():
    products = get_products()
    user_id = session.get("user_id", 1)
    personalised = get_personalised_recommendations(user_id=user_id, limit=3)
    return render_template("index.html", products=products, personalised=personalised)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        return "Product not found", 404

    # TF-IDF recommendations (AI content-based)
    recommendations = get_tfidf_recommendations(product_id, top_n=3)

    avg_rating, rating_count = get_rating_stats(product_id)

    return render_template(
        "product.html",
        product=product,
        recommendations=recommendations,
        avg_rating=avg_rating,
        rating_count=rating_count
    )


@app.route("/rate/<int:product_id>", methods=["POST"])
def rate_product(product_id):
    rating = request.form.get("rating")
    if rating is None:
        return redirect(url_for("product_detail", product_id=product_id))

    user_id = session.get("user_id", 1)

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO ratings (user_id, product_id, rating) VALUES (?, ?, ?)",
        (user_id, product_id, int(rating))
    )
    conn.commit()
    conn.close()

    return redirect(url_for("product_detail", product_id=product_id))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []

    if q:
        conn = get_db_connection()
        like = f"%{q}%"
        results = conn.execute("""
            SELECT * FROM products
            WHERE name LIKE ? OR category LIKE ? OR description LIKE ?
        """, (like, like, like)).fetchall()
        conn.close()

    return render_template("search.html", query=q, results=results)

# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)