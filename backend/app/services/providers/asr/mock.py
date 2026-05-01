from app.schemas.transcript import TranscriptSegment


class MockASRProvider:
    def transcribe_placeholder(self) -> list[TranscriptSegment]:
        return [
            TranscriptSegment(
                id="seg-001",
                speaker="Speaker 1",
                start_ms=0,
                end_ms=8200,
                text="Thanks everyone. Today we need to align the P0 desktop skeleton.",
                confidence=0.96,
            ),
            TranscriptSegment(
                id="seg-002",
                speaker="Speaker 2",
                start_ms=8400,
                end_ms=16200,
                text="The backend should expose health and settings first, then mock providers.",
                confidence=0.94,
            ),
            TranscriptSegment(
                id="seg-003",
                speaker="Speaker 1",
                start_ms=17000,
                end_ms=24100,
                text="Great. Real media import and transcription can wait until P1.",
                confidence=0.88,
            ),
        ]
