from pydantic import BaseModel, Field
from typing import List


class KeyPoint(BaseModel):
    timestamp: str = Field(..., description="Timestamp in the video, e.g. '02:15'")
    point: str = Field(..., description="Concise description of what happens / is said at this timestamp")


class VideoSummary(BaseModel):
    title_guess: str = Field(..., description="Best-guess title or topic of the video based on the transcript")
    overall_summary: str = Field(..., description="A 3-5 sentence summary of the whole video")
    key_points: List[KeyPoint] = Field(..., description="5-10 key points with timestamps")
    audience: str = Field(..., description="Who this video is most useful for")


class SummarizeRequest(BaseModel):
    url: str = Field(..., description="Full YouTube video URL")


class Category(BaseModel):
    category: str = Field(..., description="Predicted category, e.g. 'tutorial', 'vlog', 'review'")
    confidence: float = Field(..., description="Model's confidence in the prediction, 0-1")


class SummarizeResponse(BaseModel):
    video_id: str
    video_url: str
    summary: VideoSummary
    predicted_category: Category