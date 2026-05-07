import wave
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, run

from app.core.config import settings

SUPPORTED_WAVE_SUFFIXES = {".wav", ".wave"}


class MediaPreparationError(ValueError):
    pass


@dataclass(frozen=True)
class PreparedMedia:
    source_path: Path
    normalized_path: Path
    sample_rate_hz: int
    format: str
    normalized: bool


def prepare_media_for_transcription(meeting_id: str, media_path: str) -> PreparedMedia:
    source_path = Path(media_path).expanduser().resolve()
    if not source_path.exists() or not source_path.is_file():
        raise MediaPreparationError("Meeting media is not available for transcription.")

    if source_path.suffix.lower() in SUPPORTED_WAVE_SUFFIXES:
        return _prepare_wave_media(source_path)

    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path is None:
        raise MediaPreparationError(
            "This media format needs FFmpeg for local transcription. "
            "Install FFmpeg or set ECHOMINUTES_FFMPEG_PATH, then retry."
        )

    output_dir = settings.workspace_dir / "transcription" / meeting_id
    output_dir.mkdir(parents=True, exist_ok=True)
    normalized_path = output_dir / "normalized.wav"

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(source_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(normalized_path),
    ]
    result: CompletedProcess[str] = run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not normalized_path.exists():
        error_tail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
        detail = f" FFmpeg: {error_tail}" if error_tail else ""
        raise MediaPreparationError(f"Failed to prepare media for transcription.{detail}")

    return PreparedMedia(
        source_path=source_path,
        normalized_path=normalized_path,
        sample_rate_hz=16000,
        format="wav",
        normalized=True,
    )


def get_ffmpeg_path() -> str | None:
    configured_path = settings.ffmpeg_path
    if configured_path:
        candidate = Path(configured_path).expanduser().resolve()
        if candidate.exists() and candidate.is_file():
            return str(candidate)

    path_in_system = which("ffmpeg")
    if path_in_system:
        return path_in_system

    try:
        from imageio_ffmpeg import get_ffmpeg_exe
    except ImportError:
        return None

    try:
        return get_ffmpeg_exe()
    except Exception:
        return None


def _prepare_wave_media(source_path: Path) -> PreparedMedia:
    try:
        with wave.open(str(source_path), "rb") as wave_file:
            sample_rate = wave_file.getframerate()
    except (wave.Error, EOFError) as error:
        raise MediaPreparationError(
            "Only valid WAV files can be transcribed without FFmpeg. "
            "Install FFmpeg or import a supported audio file."
        ) from error

    return PreparedMedia(
        source_path=source_path,
        normalized_path=source_path,
        sample_rate_hz=sample_rate,
        format="wav",
        normalized=False,
    )
