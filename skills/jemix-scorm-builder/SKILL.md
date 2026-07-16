---
name: jemix-scorm-builder
description: Builds and repairs JEMIX Academy SCORM 1.2 lessons from structured slide content and synthesized narration. Use for JEMIX Academy packaging, especially 20-screen sales-manager lessons with slide01.mp3 through slide20.mp3, corporate UX, quizzes, SCORM score/status reporting, LMS iframe compatibility, media-path validation, and troubleshooting blank previews or missing audio/images.
---

# JEMIX SCORM Builder

## Standard

Build a self-contained SCORM 1.2 package with:
- 20 screens;
- `audio/slide01.mp3` through `audio/slide20.mp3`;
- passing score 80%;
- audience: sales managers;
- local assets only;
- no runtime `fetch()`.

Never use the old 12-screen package as the source of truth for a 20-screen lesson.

## Workflow

1. Confirm the expected screen count before building.
2. Validate all 20 MP3 files.
3. Reject WAV data renamed to `.mp3` (`RIFF....WAVE`).
4. Embed lesson data directly in `app.js`; do not load JSON with `fetch()` inside the LMS iframe.
5. Use exact runtime paths:
   - `images/<filename>`
   - `audio/slideNN.mp3`
6. Include every runtime resource in `imsmanifest.xml`.
7. Write ZIP paths with POSIX `/` separators.
8. Initialize SCORM 1.2, store raw score, set `passed` at 80%+, and commit.
9. Validate ZIP integrity and required entries before reporting success.

## LMS compatibility

- Treat a blank gray preview as JavaScript startup failure, not as a successful SCORM load.
- Treat `0:00 / 0:00` audio as a wrong path or invalid media payload.
- Add an on-screen JavaScript error fallback.
- Upload rebuilt packages as a new SCORM object when LMS caching is suspected.
- Keep slide count, navigation count, progress denominator, and audio count identical.

## Audio rules

SaluteSpeech may return WAV bytes even when `audio/mpeg` is requested.

Detect payloads:
- MP3: starts with `ID3` or MPEG frame sync;
- WAV: starts with `RIFF` and contains `WAVE`.

Convert WAV to a real MP3 with FFmpeg before packaging. Never accept a WAV file merely renamed to `.mp3`.

## Lesson 1.1 invariant

For the approved lesson 1.1 build:
- slide data: 20 objects;
- navigation: 20 items;
- progress: out of 20;
- narration: 20 MP3 files;
- package: self-contained SCORM 1.2.

## Troubleshooting

Read `references/troubleshooting.md` when the LMS preview is blank, images are broken, audio shows `0:00 / 0:00`, resources are reported missing, or SCORM status is not recorded.
