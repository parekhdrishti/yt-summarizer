# Reel — YouTube Video Summarizer

Paste a YouTube URL, get a structured summary: overview, audience, and 5–10 key points
each tied to a timestamp in the video.

**Stack:** Python, FastAPI, OpenAI API, `youtube-transcript-api`.

## How it works

1. `youtube-transcript-api` pulls the video's caption track (works for auto-generated
   captions too — no audio download or Whisper needed).
2. The transcript (with inline timestamps) is sent to the OpenAI API with a prompt that
   forces structured JSON output matching a fixed schema.
3. FastAPI validates that JSON against a Pydantic model and returns it to the frontend,
   which renders it as a timeline.

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

Optional — override the model (defaults to `gpt-4o-mini`):

```bash
export OPENAI_MODEL="gpt-4o-mini"
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** — paste a YouTube URL and hit Summarize.

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
  }
}
```

## Project structure
