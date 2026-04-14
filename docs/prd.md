# KiniVideo PRD

## Document Role

This is the product source of truth for KiniVideo v1. Code, design, and implementation details should follow this document unless a newer PRD revision explicitly replaces it.

## Product Summary

KiniVideo is an open-source, replay-first web app that converts TikTok LIVE replays into high-quality short and medium clips. It is designed for a single creator workflow first, with AI suggesting high-value moments and the creator approving which clips to export.

The product minimizes data, storage, and device strain by fetching and processing source videos on a remote machine instead of requiring full local downloads.

## Problem

TikTok's built-in clip suggestions do not reliably find the genuinely interesting parts of long tech livestreams. Manual review is slow, stressful, and expensive when bandwidth, storage, and compute are constrained. Existing tools either:

- focus on local-file editing instead of remote replay workflows
- are libraries instead of creator-ready products
- lack configurable clip styles for different content goals
- do not preserve enough reasoning for creator review

## Primary User

- Solo creator
- English-first tech livestreams
- Wants better highlight quality than TikTok defaults
- Needs remote processing because local bandwidth, storage, or device performance is limited

## Goals

- Turn a TikTok LIVE replay URL into ranked short and medium clip candidates
- Keep source video handling remote-first, with optional local upload fallback
- Expose a review flow where AI explains why each clip was chosen
- Support multiple clip styles through configurable recipes
- Export ready-to-post clip packages with rendered captions and metadata
- Stay open-source and self-hostable, with optional model API fallback

## Non-Goals

- Multi-tenant SaaS, billing, or team permissions in v1
- Fully automatic posting in v1
- Real-time live clipping in v1
- Full editing suite parity with desktop NLE tools
- Building around proprietary-only AI providers

## User Workflow

1. User submits a TikTok replay URL or optional local upload.
2. KiniVideo ingests the source remotely and stores it in object storage.
3. The backend extracts audio, creates a transcript with timestamps, and generates candidate highlights using one or more recipes.
4. The user opens the job page to inspect processing state, transcript segments, candidate clips, and scoring rationale.
5. The user approves or rejects clips.
6. The backend exports approved clips with captions and metadata packages.
7. The user downloads the final clips or uses the metadata for manual posting.

## Core Product Requirements

### Ingestion

- Accept TikTok replay URLs as the primary input
- Accept local file uploads as an optional fallback
- Keep source retention until manual delete
- Fail clearly for expired, invalid, or inaccessible replay URLs

### Processing

- Store transcript segments with sentence-level timestamps
- Support optional higher-precision alignment and diarization passes
- Run recipe-based highlight scoring instead of one fixed clip heuristic
- Default to quality over quantity by returning fewer, stronger clip candidates

### Review

- Show the clip timeline and transcript in the browser
- Show ranking rationale for each clip
- Allow approving, rejecting, and rerunning recipes without re-ingesting

### Export

- Export short clips and medium-length clips
- Generate styled captions
- Generate metadata including title suggestions, reasons, and transcript excerpt
- Export clips manually rather than auto-posting

## Clip Recipe Model

Recipes are reusable clip-generation profiles. Each recipe defines:

- prompt or instruction framing
- target durations
- scoring weights
- content cues
- caption preset
- output aspect ratio and format

Planned built-in recipes:

- Hot Take
- Q&A
- Explainer Tip
- Product Demo
- News Recap
- Debate/Rant

## Success Criteria

### Product Success

- User can submit a replay URL without downloading the full source video locally
- User gets ranked clips with start/end times, transcript context, and reasoning
- User can review and approve clips in the browser
- Approved clips export reliably with captions and metadata

### Quality Success

- Clip suggestions are meaningfully better than TikTok default suggestions
- Different recipes produce visibly different clip selections
- Precision is preferred over recall in the default configuration

## Constraints and Principles

- Open-source first
- Self-hostable core
- TikTok-first but extensible
- Local model inference preferred, API fallback allowed
- Remote processing preferred for bandwidth and storage efficiency

## Release Scope for v1

- Web app with ingest, job status, transcript review, and clip review/export screens
- FastAPI backend with a durable data model and queue-friendly service boundaries
- Initial source adapter for TikTok replay URLs
- Initial storage abstraction with local dev storage and S3-compatible production path
- Recipe-based highlight generation framework

## Future Direction

- YouTube and Twitch source adapters
- Near-live clipping
- Posting integrations
- Smarter analytics and reporting
- Multi-user and multi-creator operation
