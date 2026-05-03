from app.schemas.transcript import TranscriptSegment

STANDARD_MEETING_NOTE_PROMPT = """Write concise Qwen-style meeting minutes.

Use this Markdown structure:

# Meeting Minutes

## Summary

## Decisions

## Action Items

Ground the note only in the transcript segments provided.
"""


def build_meeting_note_prompt(segments: list[TranscriptSegment]) -> str:
    transcript_lines = "\n".join(
        f"- {segment.speaker} [{segment.start_ms}-{segment.end_ms}ms]: {segment.text}"
        for segment in segments
    )
    return f"{STANDARD_MEETING_NOTE_PROMPT}\n\nTranscript:\n{transcript_lines}"
