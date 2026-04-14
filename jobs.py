from __future__ import annotations

from datetime import UTC, datetime

from fastapi import UploadFile

from models import (
    ClipCandidate,
    ClipStatus,
    CreateJobPayload,
    JobRecord,
    JobStatus,
    JobSummary,
    RunRecipesPayload,
    SourceType,
)
from pipeline import pipeline
from recipes import BUILT_IN_RECIPES, BUILT_IN_RECIPES_BY_ID
from repository import repository
from source_adapters import LocalUploadAdapter, TikTokReplayAdapter


def utc_now() -> datetime:
    return datetime.now(UTC)


class JobService:
    def __init__(self) -> None:
        self.tiktok_adapter = TikTokReplayAdapter()
        self.upload_adapter = LocalUploadAdapter()

    def list_jobs(self) -> list[JobSummary]:
        return repository.list_jobs()

    def list_recipes(self):
        return BUILT_IN_RECIPES

    def get_job(self, job_id: str) -> JobRecord:
        record = repository.get_job(job_id)
        if not record:
            raise KeyError(f"Job {job_id} was not found.")
        return record

    async def create_job(
        self,
        payload: CreateJobPayload,
        upload: UploadFile | None = None,
    ) -> JobRecord:
        if not payload.source_url and not upload:
            raise ValueError("Provide either source_url or upload.")
        if payload.source_url and upload:
            raise ValueError("Provide only one of source_url or upload.")

        recipe_ids = payload.recipe_ids or [recipe.id for recipe in BUILT_IN_RECIPES]
        self._validate_recipe_ids(recipe_ids)

        source_type = SourceType.tiktok_replay if payload.source_url else SourceType.local_upload
        record = JobRecord(
            job=JobSummary(
                source_type=source_type,
                source_url=payload.source_url,
                selected_recipe_ids=recipe_ids,
                status=JobStatus.ingesting,
            )
        )

        if payload.source_url:
            record.job.source_asset = self.tiktok_adapter.ingest(str(payload.source_url))
        elif upload:
            record.job.source_asset = await self.upload_adapter.ingest(upload)

        record.job.updated_at = utc_now()
        repository.save_job(record)
        processed = pipeline.process(record)
        processed.job.updated_at = utc_now()
        repository.save_job(processed)
        return processed

    def rerun_recipes(self, job_id: str, payload: RunRecipesPayload) -> JobRecord:
        self._validate_recipe_ids(payload.recipe_ids)
        record = self.get_job(job_id)
        record.job.status = JobStatus.analyzing
        record.job.selected_recipe_ids = payload.recipe_ids
        record.clips = pipeline.score_clips(
            record.job.id,
            [BUILT_IN_RECIPES_BY_ID[recipe_id] for recipe_id in payload.recipe_ids],
            record.transcript,
        )
        record.job.status = JobStatus.ready
        record.job.updated_at = utc_now()
        repository.save_job(record)
        return record

    def list_clips(self, job_id: str) -> list[ClipCandidate]:
        return self.get_job(job_id).clips

    def approve_clip(self, clip_id: str) -> ClipCandidate:
        record, clip = self._resolve_clip(clip_id)
        updated_clips = []
        for candidate in record.clips:
            if candidate.id == clip_id:
                candidate.status = ClipStatus.approved
                clip = candidate
            updated_clips.append(candidate)
        repository.update_clips(record.job.id, updated_clips)
        return clip

    def export_clip(self, clip_id: str) -> ClipCandidate:
        record, clip = self._resolve_clip(clip_id)
        updated_clips = []
        for candidate in record.clips:
            if candidate.id == clip_id:
                if candidate.status != ClipStatus.approved:
                    candidate.status = ClipStatus.approved
                candidate.export_package = pipeline.export_clip(candidate)
                candidate.status = ClipStatus.exported
                clip = candidate
            updated_clips.append(candidate)
        repository.update_clips(record.job.id, updated_clips)
        return clip

    def _validate_recipe_ids(self, recipe_ids: list[str]) -> None:
        unknown = [recipe_id for recipe_id in recipe_ids if recipe_id not in BUILT_IN_RECIPES_BY_ID]
        if unknown:
            raise ValueError(f"Unknown recipe ids: {', '.join(unknown)}")

    def _resolve_clip(self, clip_id: str) -> tuple[JobRecord, ClipCandidate]:
        resolved = repository.get_clip(clip_id)
        if not resolved:
            raise KeyError(f"Clip {clip_id} was not found.")
        return resolved


job_service = JobService()
