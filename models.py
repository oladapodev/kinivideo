from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


def utc_now() -> datetime:
    return datetime.now(UTC)


class JobStatus(str, Enum):
    queued = "queued"
    ingesting = "ingesting"
    transcribing = "transcribing"
    analyzing = "analyzing"
    ready = "ready"
    failed = "failed"


class ClipStatus(str, Enum):
    suggested = "suggested"
    approved = "approved"
    rejected = "rejected"
    exported = "exported"


class SourceType(str, Enum):
    tiktok_replay = "tiktok_replay"
    local_upload = "local_upload"


class AssetRef(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    storage_key: str
    source_type: SourceType
    filename: str
    content_type: str
    origin_url: HttpUrl | None = None
    created_at: datetime = Field(default_factory=utc_now)


class RecipeWeights(BaseModel):
    hook_strength: float = 1.0
    topic_match: float = 1.0
    speaker_turn: float = 0.5
    novelty: float = 1.0
    qa_value: float = 0.8
    confidence: float = 0.7


class ClipRecipe(BaseModel):
    id: str
    name: str
    description: str
    prompt: str
    target_durations: list[int]
    cues: list[str]
    caption_preset: str
    aspect_ratio: str = "9:16"
    weights: RecipeWeights = Field(default_factory=RecipeWeights)


class TranscriptSegment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    start_seconds: float
    end_seconds: float
    text: str
    confidence: float
    speaker: str | None = None
    topic: str | None = None


class WordTimestamp(BaseModel):
    word: str
    start_seconds: float
    end_seconds: float
    confidence: float


class SpeakerTurn(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    speaker: str
    start_seconds: float
    end_seconds: float


class ClipReasoning(BaseModel):
    summary: str
    hook_strength: float
    topic_match: float
    speaker_turn_value: float
    novelty: float
    qa_value: float
    transcript_confidence: float


class ExportPackage(BaseModel):
    clip_id: str
    file_path: str
    subtitle_path: str
    metadata_path: str
    exported_at: datetime = Field(default_factory=utc_now)


class ClipCandidate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    recipe_id: str
    title: str
    start_seconds: float
    end_seconds: float
    score: float
    status: ClipStatus = ClipStatus.suggested
    transcript_excerpt: str
    reasoning: ClipReasoning
    export_package: ExportPackage | None = None


class JobSummary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_type: SourceType
    source_url: HttpUrl | None = None
    source_asset: AssetRef | None = None
    status: JobStatus = JobStatus.queued
    selected_recipe_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    error_message: str | None = None


class JobRecord(BaseModel):
    job: JobSummary
    transcript: list[TranscriptSegment] = Field(default_factory=list)
    word_timestamps: list[WordTimestamp] = Field(default_factory=list)
    speaker_turns: list[SpeakerTurn] = Field(default_factory=list)
    clips: list[ClipCandidate] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class CreateJobPayload(BaseModel):
    source_url: HttpUrl | None = None
    recipe_ids: list[str] = Field(default_factory=list)


class RunRecipesPayload(BaseModel):
    recipe_ids: list[str]


class JobListResponse(BaseModel):
    jobs: list[JobSummary]


class RecipeListResponse(BaseModel):
    recipes: list[ClipRecipe]
