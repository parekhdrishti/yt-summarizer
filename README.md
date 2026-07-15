# Reel — YouTube Video Summarizer


**[🔗 Try it live](https://yt-summarizer-0aui.onrender.com)**


Paste a YouTube URL, get a structured summary: overview, audience, and 5–10 key points
each tied to a timestamp in the video.

**Stack:** Python, FastAPI, OpenAI API, `youtube-transcript-api`.

## Screenshots

![Summarizer input screen](demo1.png)
![Structured summary output](demo2.png)

## Features

- **Transcript-based summarization** — pulls captions from any YouTube video and sends
  them to the OpenAI API, which returns a structured JSON summary (overview, audience,
  and timestamped key points).
- **ML-powered category classifier** — a custom-trained text classifier (TF-IDF +
  Logistic Regression, built with scikit-learn) predicts the video's category
  (tutorial, vlog, interview, review, comedy, or educational) directly from the
  transcript, with a confidence score. This model was trained from scratch on a
  labeled dataset built specifically for this project — see [`ml/`](./ml) for the
  training pipeline.

## How it works

1. `youtube-transcript-api` pulls the video's caption track (works for auto-generated
   captions too — no audio download or Whisper needed).
2. The transcript is run through a locally trained ML classifier (`ml/category_model.joblib`)
   to predict the video's category.
3. The transcript (with inline timestamps) is sent to the OpenAI API with a prompt that
   forces structured JSON output matching a fixed schema.
4. FastAPI validates both results against Pydantic models and returns them to the
   frontend, which renders the summary as a timeline with a category badge.
   
## Setup

```bash
cd yt-summarizer
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="sk-..."       # Windows (PowerShell): $env:OPENAI_API_KEY="sk-..."
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** — paste a YouTube URL and hit Summarize.

## Training the ML classifier yourself

The trained model (`ml/category_model.joblib`) is already included in this repo, so
you don't need to retrain it to run the app. But if you want to see how it was built,
or regenerate it yourself:

```bash
python ml/generate_dataset.py    # builds ml/training_data.csv (240 labeled examples)
python ml/train_classifier.py    # trains and saves ml/category_model.joblib
```

The training script prints accuracy and a classification report so you can see how
well it performs.

## API

`POST /api/summarize`

```json
{ "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }
```

Returns:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "summary": {
    "title_guess": "...",
    "overall_summary": "...",
    "audience": "...",
    "key_points": [
      { "timestamp": "00:42", "point": "..." }
    ]
  },
  "predicted_category": {
    "category": "tutorial",
    "confidence": 0.87
  }
}
```

## Project structure

```
yt-summarizer/
├── app/
│   ├── main.py         # FastAPI app + routes
│   ├── summarizer.py   # transcript fetching + OpenAI summarization
│   ├── classifier.py   # loads the trained ML model and predicts category
│   └── models.py       # Pydantic schemas
├── ml/
│   ├── generate_dataset.py   # builds the labeled training dataset
│   ├── train_classifier.py   # trains and saves the classifier
│   ├── training_data.csv     # 240 labeled transcript examples
│   └── category_model.joblib # the trained model
├── static/
│   └── index.html      # single-page frontend
├── requirements.txt
└── README.md
```

## Notes & limitations

- Only works for videos that have an available English transcript (manual or
  auto-generated captions). Videos with captions disabled will return a clear error.
- Long videos are truncated before being sent to the model to control token usage/cost.
- Hosted on Render's free tier — the live demo may take ~30-50 seconds to wake up if it's
  been idle.
- The live demo may fail to fetch transcripts for some videos. This is because 
  YouTube blocks caption requests coming from cloud server IPs (a known limitation 
  of `youtube-transcript-api` on platforms like Render, Railway, and Fly.io). 
- The app works reliably when run locally, since it's not coming from a flagged IP range.
  A production fix would involve routing requests
  through a residential proxy service.
- The classifier's training data is a small, template-generated dataset (240 examples
  across 6 categories) — it generalizes reasonably to unseen text but isn't a
  large-scale production model.
- No database or auth — this is a single-user local/dev tool.
