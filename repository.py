from __future__ import annotations

from copy import deepcopy
from typing import Iterable

from models import ClipCandidate, JobRecord, JobSummary


class InMemoryRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}

    def list_jobs(self) -> list[JobSummary]:
        return [deepcopy(record.job) for record in self._jobs.values()]

    def get_job(self, job_id: str) -> JobRecord | None:
        record = self._jobs.get(job_id)
        return deepcopy(record) if record else None

    def save_job(self, record: JobRecord) -> JobRecord:
        self._jobs[record.job.id] = deepcopy(record)
        return deepcopy(record)

    def update_clips(self, job_id: str, clips: Iterable[ClipCandidate]) -> JobRecord:
        record = self._jobs[job_id]
        record.clips = list(clips)
        self._jobs[job_id] = deepcopy(record)
        return deepcopy(record)

    def get_clip(self, clip_id: str) -> tuple[JobRecord, ClipCandidate] | None:
        for record in self._jobs.values():
            for clip in record.clips:
                if clip.id == clip_id:
                    return deepcopy(record), deepcopy(clip)
        return None


repository = InMemoryRepository()
