from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

from twitter_analyzer import TwitterAnalyzer

load_dotenv()

app = Flask(__name__)
DEFAULT_TWEET_COUNT = 25
MAX_TWEET_COUNT = 100
NEUTRAL_SENTIMENT_THRESHOLD = 0.01


def _credentials_available():
    required = ["API_KEY", "API_KEY_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
    return all(os.getenv(key) for key in required)


def _summary_from_results(df):
    if df is None or df.empty:
        return {"positive": 0, "neutral": 0, "negative": 0, "avg_polarity": 0}

    positive = int((df["polarity"] > NEUTRAL_SENTIMENT_THRESHOLD).sum())
    negative = int((df["polarity"] < -NEUTRAL_SENTIMENT_THRESHOLD).sum())
    neutral = int((df["polarity"].abs() <= NEUTRAL_SENTIMENT_THRESHOLD).sum())

    return {
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "avg_polarity": round(float(df["polarity"].mean()), 3),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "rows": [],
        "summary": None,
        "error": None,
        "default_count": DEFAULT_TWEET_COUNT,
        "max_count": MAX_TWEET_COUNT,
    }

    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        count = request.form.get("count", str(DEFAULT_TWEET_COUNT)).strip()

        if not keyword:
            context["error"] = "Please enter a keyword."
            return render_template("index.html", **context)

        try:
            count_value = int(count)
        except ValueError:
            context["error"] = "Count must be a valid number."
            return render_template("index.html", **context)

        if count_value <= 0 or count_value > MAX_TWEET_COUNT:
            context["error"] = f"Count must be between 1 and {MAX_TWEET_COUNT}."
            return render_template("index.html", **context)

        if not _credentials_available():
            context["error"] = "Twitter API credentials are missing. Add values to your .env file."
            return render_template("index.html", **context)

        analyzer = TwitterAnalyzer()
        results = analyzer.analyze_tweets(keyword=keyword, count=count_value)

        if results is None:
            context["error"] = "Could not fetch tweets. Check your credentials or Twitter API access."
            return render_template("index.html", **context)

        context["summary"] = _summary_from_results(results)
        context["rows"] = results.to_dict(orient="records")

    return render_template("index.html", **context)


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
