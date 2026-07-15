import json
import os
import re
from urllib.parse import urlparse, parse_qs

from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from .models import VideoSummary
from .classifier import predict_category

MODEL_NAME = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


class SummarizerError(Exception):
    """Raised for any user-facing error in the summarization pipeline."""


def extract_video_id(url: str) -> str:
    """Pull the 11-character YouTube video ID out of most common URL shapes."""
    parsed = urlparse(url.strip())

    if parsed.hostname in ("youtu.be",):
        video_id = parsed.path.lstrip("/")
    elif parsed.hostname and "youtube.com" in parsed.hostname:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/embed/") or parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/")[2]
        else:
            video_id = ""
    else:
        # Fallback: maybe the user just pasted the raw ID
        video_id = url.strip() if re.fullmatch(r"[\w-]{11}", url.strip()) else ""

    if not video_id or not re.fullmatch(r"[\w-]{11}", video_id):
        raise SummarizerError(
            "Couldn't find a valid YouTube video ID in that URL. "
            "Try a link like https://www.youtube.com/watch?v=XXXXXXXXXXX"
        )
    return video_id


def _format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def fetch_transcript(video_id: str) -> str:
    """Fetch transcript and return it as a single text blob with inline timestamps."""
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
    except (TranscriptsDisabled, NoTranscriptFound):
        raise SummarizerError(
            "This video doesn't have an available English transcript/captions, "
            "so it can't be summarized."
        )
    except VideoUnavailable:
        raise SummarizerError("That video is unavailable (private, deleted, or region-locked).")
    except Exception as exc:  # noqa: BLE001
        raise SummarizerError(f"Couldn't fetch the transcript: {exc}")

    lines = []
    for snippet in fetched:
        ts = _format_timestamp(snippet.start)
        text = snippet.text.replace("\n", " ").strip()
        if text:
            lines.append(f"[{ts}] {text}")

    if not lines:
        raise SummarizerError("The transcript came back empty.")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are an expert video summarizer. You will be given a YouTube video's \
transcript, where each line is prefixed with a timestamp like [MM:SS] or [HH:MM:SS].

Produce a structured summary as JSON matching exactly this schema:
{
  "title_guess": string,
  "overall_summary": string,
  "key_points": [ { "timestamp": string, "point": string }, ... ],
  "audience": string
}

Rules:
- key_points should have 5 to 10 entries, ordered by timestamp, spread across the whole video (not just the start).
- Each timestamp in key_points MUST be copied from a nearby line in the transcript (same format, e.g. "02:15" or "1:04:30").
- overall_summary should be 3-5 sentences capturing the main takeaway of the video.
- audience should be one short sentence describing who would find this video useful.
- Output ONLY valid JSON, no markdown fences, no commentary.
"""


def summarize_transcript(transcript_text: str, api_key: str) -> VideoSummary:
    client = OpenAI(api_key=api_key)

    # Keep prompt size sane for very long videos.
    max_chars = 60000
    if len(transcript_text) > max_chars:
        half = max_chars // 2
        transcript_text = (
            transcript_text[:half]
            + "\n...[transcript truncated for length]...\n"
            + transcript_text[-half:]
        )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Transcript:\n\n{transcript_text}"},
            ],
            response_format={"type": "json_object"},
        )
    except Exception as exc:  # noqa: BLE001
        raise SummarizerError(f"OpenAI API call failed: {exc}")

    raw = response.choices[0].message.content
    try:
        data = json.loads(raw)
        return VideoSummary(**data)
    except Exception as exc:  # noqa: BLE001
        raise SummarizerError(f"Model returned unexpected output: {exc}")


def summarize_youtube_url(url: str, api_key: str) -> tuple[str, VideoSummary, dict]:
    video_id = extract_video_id(url)
    transcript_text = fetch_transcript(video_id)
    summary = summarize_transcript(transcript_text, api_key=api_key)
    category = predict_category(transcript_text)
    return video_id, summary, category