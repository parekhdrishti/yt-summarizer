import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import SummarizeRequest, SummarizeResponse
from .summarizer import summarize_youtube_url, SummarizerError

app = FastAPI(
    title="YouTube Video Summarizer",
    description="Paste a YouTube URL, get a structured summary with key points and timestamps.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server is missing OPENAI_API_KEY. Set it as an environment variable before starting the app.",
        )

    try:
        video_id, summary = summarize_youtube_url(req.url, api_key=api_key)
    except SummarizerError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return SummarizeResponse(
        video_id=video_id,
        video_url=req.url,
        summary=summary,
    )