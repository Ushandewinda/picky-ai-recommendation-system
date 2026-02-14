from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Welcome to Picky 🚀</h1><p>AI Powered Smart E-Commerce Recommendation System</p>"

if __name__ == "__main__":
    app.run(debug=True)
