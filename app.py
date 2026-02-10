"""Flask application for AI-powered rehabilitation research assistant."""

from flask import Flask, render_template, request, jsonify

from config import Config
from scraper import PubMedScraper
from analyzer import RehabAnalyzer


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    scraper = PubMedScraper()
    analyzer = RehabAnalyzer()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/search", methods=["POST"])
    def search():
        query = request.form.get("query", "").strip()
        if not query:
            return jsonify({"error": "Please enter a search query."}), 400

        max_results = request.form.get("max_results", Config.MAX_ARTICLES, type=int)
        max_results = min(max(1, max_results), 20)  # Clamp between 1 and 20

        articles = scraper.get_research_data(query, max_results)
        if not articles:
            return jsonify({
                "error": "No articles found. Try a different search term."
            }), 404

        return jsonify({"articles": articles, "count": len(articles)})

    @app.route("/analyze", methods=["POST"])
    def analyze():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body."}), 400

        articles = data.get("articles", [])
        question = data.get("question", "").strip()

        if not articles:
            return jsonify({"error": "No articles provided."}), 400
        if not question:
            return jsonify({"error": "Please enter a question."}), 400

        analysis = analyzer.analyze_research(articles, question)
        return jsonify({"analysis": analysis})

    @app.route("/summarize", methods=["POST"])
    def summarize():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body."}), 400

        articles = data.get("articles", [])
        if not articles:
            return jsonify({"error": "No articles provided."}), 400

        summary = analyzer.summarize_articles(articles)
        return jsonify({"summary": summary})

    @app.route("/compare", methods=["POST"])
    def compare():
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body."}), 400

        articles = data.get("articles", [])
        treatment_a = data.get("treatment_a", "").strip()
        treatment_b = data.get("treatment_b", "").strip()

        if not articles:
            return jsonify({"error": "No articles provided."}), 400
        if not treatment_a or not treatment_b:
            return jsonify({"error": "Please provide both treatments to compare."}), 400

        comparison = analyzer.compare_treatments(articles, treatment_a, treatment_b)
        return jsonify({"comparison": comparison})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
