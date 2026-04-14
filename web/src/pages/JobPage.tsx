import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { approveClip, exportClip, fetchJob, rerunRecipes } from "../lib/api";
import type { ClipCandidate, JobRecord } from "../lib/api";

const DEFAULT_RERUN_RECIPES = ["news-recap", "qa"];

export function JobPage() {
  const { jobId = "" } = useParams();
  const [job, setJob] = useState<JobRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyClipId, setBusyClipId] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId || jobId === "demo") {
      setError("Create a job from the ingest page to review a real result.");
      return;
    }
    fetchJob(jobId)
      .then(setJob)
      .catch((err: Error) => setError(err.message));
  }, [jobId]);

  async function handleApprove(clipId: string) {
    setBusyClipId(clipId);
    try {
      const updated = await approveClip(clipId);
      setJob((current) =>
        current
          ? {
              ...current,
              clips: current.clips.map((clip) => (clip.id === clipId ? updated : clip)),
            }
          : current,
      );
    } finally {
      setBusyClipId(null);
    }
  }

  async function handleExport(clipId: string) {
    setBusyClipId(clipId);
    try {
      const updated = await exportClip(clipId);
      setJob((current) =>
        current
          ? {
              ...current,
              clips: current.clips.map((clip) => (clip.id === clipId ? updated : clip)),
            }
          : current,
      );
    } finally {
      setBusyClipId(null);
    }
  }

  async function handleRerun() {
    if (!job) {
      return;
    }
    const updated = await rerunRecipes(job.job.id, DEFAULT_RERUN_RECIPES);
    setJob(updated);
  }

  if (error) {
    return <section className="panel"><p className="error">{error}</p></section>;
  }

  if (!job) {
    return <section className="panel"><p>Loading job...</p></section>;
  }

  return (
    <section className="stack">
      <div className="panel status-panel">
        <div>
          <p className="eyebrow">Processing Status</p>
          <h2>Job {job.job.id.slice(0, 8)}</h2>
          <p>
            Source: <strong>{job.job.source_type}</strong> · Status: <strong>{job.job.status}</strong>
          </p>
          <p>Recipes: {job.job.selected_recipe_ids.join(", ")}</p>
        </div>
        <button className="secondary-button" onClick={handleRerun}>
          Rerun with default review recipes
        </button>
      </div>

      <div className="review-grid">
        <section className="panel">
          <p className="eyebrow">Transcript Review</p>
          <h3>Segment Timeline</h3>
          <div className="timeline">
            {job.transcript.map((segment) => (
              <article key={segment.id} className="timeline-item">
                <div>
                  <strong>
                    {segment.start_seconds.toFixed(0)}s - {segment.end_seconds.toFixed(0)}s
                  </strong>
                  <span>{segment.speaker} · {segment.topic}</span>
                </div>
                <p>{segment.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="panel">
          <p className="eyebrow">Clip Review</p>
          <h3>Suggested Highlights</h3>
          <div className="clip-list">
            {job.clips.map((clip) => (
              <ClipCard
                key={clip.id}
                clip={clip}
                busy={busyClipId === clip.id}
                onApprove={() => handleApprove(clip.id)}
                onExport={() => handleExport(clip.id)}
              />
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}

function ClipCard({
  clip,
  busy,
  onApprove,
  onExport,
}: {
  clip: ClipCandidate;
  busy: boolean;
  onApprove: () => void;
  onExport: () => void;
}) {
  return (
    <article className="clip-card">
      <div className="clip-card-header">
        <div>
          <strong>{clip.title}</strong>
          <span>
            {clip.start_seconds.toFixed(0)}s - {clip.end_seconds.toFixed(0)}s · score {clip.score}
          </span>
        </div>
        <span className="pill">{clip.status}</span>
      </div>
      <p>{clip.transcript_excerpt}</p>
      <p className="reasoning">{clip.reasoning.summary}</p>
      <div className="metrics">
        <span>Hook {clip.reasoning.hook_strength.toFixed(2)}</span>
        <span>Topic {clip.reasoning.topic_match.toFixed(2)}</span>
        <span>Q&A {clip.reasoning.qa_value.toFixed(2)}</span>
        <span>Confidence {clip.reasoning.transcript_confidence.toFixed(2)}</span>
      </div>
      <div className="actions">
        <button className="secondary-button" onClick={onApprove} disabled={busy}>
          {busy ? "Working..." : "Approve"}
        </button>
        <button className="primary-button" onClick={onExport} disabled={busy}>
          {busy ? "Working..." : "Export"}
        </button>
      </div>
      {clip.export_package ? (
        <div className="export-meta">
          <span>{clip.export_package.file_path}</span>
          <span>{clip.export_package.subtitle_path}</span>
        </div>
      ) : null}
    </article>
  );
}
