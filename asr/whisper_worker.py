# faster-whisper + VAD
from faster_whisper import WhisperModel

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"   # fastest on CPU
)

def transcribe_file(path: str) -> str:
    segments, _ = model.transcribe(
        path,
        vad_filter=False,      # IMPORTANT
        vad_parameters=dict(
            min_silence_duration_ms=500
        )
    )

    text = " ".join(seg.text.strip() for seg in segments)
    return text
