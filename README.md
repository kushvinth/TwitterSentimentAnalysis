# Twitter Sentiment Analysis

Simple Twitter sentiment analyzer with:
- a backend analyzer (`twitter_analyzer.py`)
- a Flask website UI (`app.py`)

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your Twitter credentials in `.env`:

```bash
cp .env.example .env
```

## Run the website

```bash
python app.py
```

Then open: `http://127.0.0.1:5000`

## Run backend script only

```bash
python twitter_analyzer.py
```
