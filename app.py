from flask import Flask, jsonify, render_template, request

from twitter_analyzer import TwitterAnalyzer

app = Flask(__name__)


def _classify_sentiment(polarity: float) -> str:
    if polarity > 0.1:
        return "positive"
    if polarity < -0.1:
        return "negative"
    return "neutral"


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    keyword = str(payload.get("keyword", "Trump")).strip() or "Trump"

    try:
        count = int(payload.get("count", 50))
    except (TypeError, ValueError):
        return jsonify({"error": "Count must be a number."}), 400

    if count < 5 or count > 100:
        return jsonify({"error": "Count must be between 5 and 100."}), 400

    try:
        analyzer = TwitterAnalyzer()
        df = analyzer.analyze_tweets(keyword=keyword, count=count)
    except Exception:
        return jsonify({"error": "Failed to initialize analyzer."}), 500

    if df is None or df.empty:
        return jsonify({"error": "No tweets were returned from the Twitter API."}), 500

    tweets = []
    positive = negative = neutral = 0

    for _, row in df.iterrows():
        polarity = float(row["polarity"])
        sentiment = _classify_sentiment(polarity)

        if sentiment == "positive":
            positive += 1
        elif sentiment == "negative":
            negative += 1
        else:
            neutral += 1

        tweets.append(
            {
                "tweet": row["tweet"],
                "polarity": round(polarity, 3),
                "subjectivity": round(float(row["subjectivity"]), 3),
                "sentiment": sentiment,
                "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
            }
        )

    response = {
        "keyword": keyword,
        "count": len(tweets),
        "average_polarity": round(float(df["polarity"].mean()), 3),
        "average_subjectivity": round(float(df["subjectivity"].mean()), 3),
        "sentiment_breakdown": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
        },
        "tweets": tweets,
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=False)
