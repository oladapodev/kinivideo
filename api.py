from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from jobs import job_service
from models import CreateJobPayload, JobListResponse, RecipeListResponse, RunRecipesPayload

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/recipes", response_model=RecipeListResponse)
def list_recipes() -> RecipeListResponse:
    return RecipeListResponse(recipes=job_service.list_recipes())


@router.get("/jobs", response_model=JobListResponse)
def list_jobs() -> JobListResponse:
    return JobListResponse(jobs=job_service.list_jobs())


@router.post("/jobs")
async def create_job(
    source_url: str | None = Form(default=None),
    recipe_ids: str | None = Form(default=None),
    upload: UploadFile | None = File(default=None),
):
    parsed_recipe_ids = json.loads(recipe_ids) if recipe_ids else []
    try:
        payload = CreateJobPayload(source_url=source_url, recipe_ids=parsed_recipe_ids)
        return await job_service.create_job(payload, upload)
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        return job_service.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/jobs/{job_id}/transcript")
def get_transcript(job_id: str):
    try:
        record = job_service.get_job(job_id)
        return {
            "segments": record.transcript,
            "word_timestamps": record.word_timestamps,
            "speaker_turns": record.speaker_turns,
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/recipes/run")
def rerun_recipes(job_id: str, payload: RunRecipesPayload):
    try:
        return job_service.rerun_recipes(job_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs/{job_id}/clips")
def list_clips(job_id: str):
    try:
        return {"clips": job_service.list_clips(job_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/clips/{clip_id}/approve")
def approve_clip(clip_id: str):
    try:
        return job_service.approve_clip(clip_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/clips/{clip_id}/export")
def export_clip(clip_id: str):
    try:
        return job_service.export_clip(clip_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
