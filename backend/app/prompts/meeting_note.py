from app.schemas.transcript import TranscriptSegment

STANDARD_MEETING_NOTE_PROMPT = """Write enterprise-ready Qwen-style meeting minutes.

Requirements:
- Write in the same primary language as the transcript.
- Do not invent facts, owners, dates, or decisions that are not present.
- Preserve speaker names when they matter for accountability.
- Keep action items specific and mark unknown owners as "Unassigned".
- Return Markdown only.

Use this Markdown structure exactly:

# Meeting Minutes

## Summary

## Decisions

## Action Items

## Risks And Follow-ups

## Speaker Notes

Ground the note only in the transcript segments provided.
"""


def build_meeting_note_prompt(segments: list[TranscriptSegment]) -> str:
    transcript_lines = "\n".join(
        f"- {segment.speaker} [{segment.start_ms}-{segment.end_ms}ms]: {segment.text}"
        for segment in segments
    )
    return f"{STANDARD_MEETING_NOTE_PROMPT}\n\nTranscript:\n{transcript_lines}"
