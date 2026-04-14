from __future__ import annotations

from dataclasses import dataclass

from models import (
    ClipCandidate,
    ClipReasoning,
    ClipRecipe,
    ExportPackage,
    JobRecord,
    JobStatus,
    SpeakerTurn,
    TranscriptSegment,
    WordTimestamp,
)
from recipes import BUILT_IN_RECIPES_BY_ID
from storage import storage


DEMO_SEGMENTS = [
    ("host", 0.0, 18.0, "Apple keeps marketing AI features it still cannot ship cleanly."),
    ("host", 18.0, 40.0, "If you want a budget creator setup, buy the mic before the lights."),
    ("viewer", 40.0, 47.0, "What laptop should a student programmer get right now?"),
    ("host", 47.0, 80.0, "For most students I still think a used M1 MacBook Air beats flashy Windows specs."),
    ("host", 80.0, 109.0, "Let me show you why this keyboard shortcut setup saves me real editing time."),
    ("viewer", 109.0, 116.0, "Is this new phone actually worth upgrading to?"),
    ("host", 116.0, 152.0, "No, unless your battery is terrible or you really need the camera bump."),
    ("host", 152.0, 178.0, "The bigger story today is that chip prices are dropping faster than people expected."),
]


@dataclass(slots=True)
class PipelineArtifacts:
    transcript: list[TranscriptSegment]
    words: list[WordTimestamp]
    turns: list[SpeakerTurn]
    clips: list[ClipCandidate]


class DemoPipeline:
    def create_transcript(self, job_id: str) -> tuple[list[TranscriptSegment], list[WordTimestamp], list[SpeakerTurn]]:
        segments: list[TranscriptSegment] = []
        words: list[WordTimestamp] = []
        turns: list[SpeakerTurn] = []

        for speaker, start, end, text in DEMO_SEGMENTS:
            topic = self._infer_topic(text)
            confidence = 0.87 if speaker == "host" else 0.81
            segment = TranscriptSegment(
                start_seconds=start,
                end_seconds=end,
                text=text,
                confidence=confidence,
                speaker=speaker,
                topic=topic,
            )
            segments.append(segment)
            turns.append(SpeakerTurn(speaker=speaker, start_seconds=start, end_seconds=end))
            words.extend(self._split_words(text, start, end))
        return segments, words, turns

    def score_clips(self, job_id: str, recipes: list[ClipRecipe], transcript: list[TranscriptSegment]) -> list[ClipCandidate]:
        clips: list[ClipCandidate] = []
        host_segments = [segment for segment in transcript if segment.speaker == "host"]

        for recipe in recipes:
            for segment in host_segments:
                score = self._score_segment(recipe, segment)
                if score < 0.67:
                    continue
                clips.append(
                    ClipCandidate(
                        job_id=job_id,
                        recipe_id=recipe.id,
                        title=self._title_for(recipe, segment),
                        start_seconds=segment.start_seconds,
                        end_seconds=segment.end_seconds,
                        score=round(score, 2),
                        transcript_excerpt=segment.text,
                        reasoning=ClipReasoning(
                            summary=self._summary_for(recipe, segment),
                            hook_strength=min(score, 1.0),
                            topic_match=self._topic_match(recipe, segment),
                            speaker_turn_value=0.9 if segment.speaker == "host" else 0.5,
                            novelty=0.88 if "today" in segment.text.lower() else 0.79,
                            qa_value=0.91 if "?" in segment.text else 0.54,
                            transcript_confidence=segment.confidence,
                        ),
                    )
                )

        clips.sort(key=lambda clip: clip.score, reverse=True)
        return clips[:12]

    def export_clip(self, clip: ClipCandidate) -> ExportPackage:
        clip_path = storage.export_path(clip.id, ".mp4")
        subtitle_path = storage.export_path(clip.id, ".ass")
        metadata_path = storage.export_path(clip.id, ".json")

        clip_path.write_text(
            "Placeholder exported clip. Replace with ffmpeg-driven rendering in production.\n",
            encoding="utf-8",
        )
        subtitle_path.write_text(
            f"[Script Info]\nTitle: {clip.title}\n\n[Events]\nDialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,{clip.transcript_excerpt}\n",
            encoding="utf-8",
        )
        metadata_path.write_text(
            "{\n"
            f'  "clip_id": "{clip.id}",\n'
            f'  "title": "{clip.title}",\n'
            f'  "recipe_id": "{clip.recipe_id}",\n'
            f'  "score": {clip.score}\n'
            "}\n",
            encoding="utf-8",
        )
        return ExportPackage(
            clip_id=clip.id,
            file_path=str(clip_path),
            subtitle_path=str(subtitle_path),
            metadata_path=str(metadata_path),
        )

    def process(self, record: JobRecord) -> JobRecord:
        record.job.status = JobStatus.transcribing
        transcript, words, turns = self.create_transcript(record.job.id)
        record.transcript = transcript
        record.word_timestamps = words
        record.speaker_turns = turns

        record.job.status = JobStatus.analyzing
        recipe_ids = record.job.selected_recipe_ids or list(BUILT_IN_RECIPES_BY_ID)
        recipes = [BUILT_IN_RECIPES_BY_ID[recipe_id] for recipe_id in recipe_ids]
        record.clips = self.score_clips(record.job.id, recipes, transcript)
        record.artifacts = {
            "transcript_model": "demo-faster-whisper-large-v3",
            "analysis_model": "demo-local-llm",
            "source_asset_key": record.job.source_asset.storage_key if record.job.source_asset else None,
        }
        record.job.status = JobStatus.ready
        return record

    def _infer_topic(self, text: str) -> str:
        lowered = text.lower()
        if "apple" in lowered or "phone" in lowered or "laptop" in lowered:
            return "hardware"
        if "chip" in lowered:
            return "industry-news"
        if "keyboard" in lowered or "shortcut" in lowered:
            return "productivity"
        return "general-tech"

    def _split_words(self, text: str, start: float, end: float) -> list[WordTimestamp]:
        parts = text.split()
        if not parts:
            return []
        step = (end - start) / len(parts)
        timestamps: list[WordTimestamp] = []
        current = start
        for part in parts:
            timestamps.append(
                WordTimestamp(
                    word=part,
                    start_seconds=round(current, 2),
                    end_seconds=round(current + step, 2),
                    confidence=0.86,
                )
            )
            current += step
        return timestamps

    def _score_segment(self, recipe: ClipRecipe, segment: TranscriptSegment) -> float:
        lowered = segment.text.lower()
        cue_hits = sum(1 for cue in recipe.cues if cue in lowered)
        question_bonus = 0.15 if "?" in segment.text else 0.0
        confidence_bonus = segment.confidence * 0.2
        return min(0.55 + cue_hits * 0.1 + question_bonus + confidence_bonus, 0.99)

    def _topic_match(self, recipe: ClipRecipe, segment: TranscriptSegment) -> float:
        lowered = segment.text.lower()
        cue_hits = sum(1 for cue in recipe.cues if cue in lowered)
        return min(0.5 + cue_hits * 0.12, 1.0)

    def _title_for(self, recipe: ClipRecipe, segment: TranscriptSegment) -> str:
        return f"{recipe.name}: {segment.text[:58].rstrip('.')}..."

    def _summary_for(self, recipe: ClipRecipe, segment: TranscriptSegment) -> str:
        return (
            f"Selected by the {recipe.name} recipe because it contains a strong standalone "
            f"statement around {segment.topic or 'tech'}."
        )


pipeline = DemoPipeline()
