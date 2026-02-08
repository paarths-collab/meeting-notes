"""
AssemblyAI Service for Real-Time Transcription with Speaker Diarization

Provides speaker identification ("who said what") for meeting transcription.
Uses AssemblyAI's Universal-2 model with streaming transcription.
"""
import os
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

# Configure API
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


def transcribe_file_with_speakers(audio_path: str) -> list[dict]:
    """
    Transcribe an audio file with speaker diarization.
    
    Returns:
        List of dicts with 'speaker' and 'text' keys.
        Example: [{"speaker": "A", "text": "Hello everyone"}, ...]
    """
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_code="en"
    )
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path, config=config)
    
    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Transcription failed: {transcript.error}")
    
    results = []
    for utterance in transcript.utterances:
        results.append({
            "speaker": utterance.speaker,
            "text": utterance.text
        })
    
    return results


def format_transcript_with_speakers(utterances: list[dict]) -> str:
    """Format utterances as readable transcript with speaker labels."""
    lines = []
    for u in utterances:
        lines.append(f"Speaker {u['speaker']}: {u['text']}")
    return "\n".join(lines)


class RealtimeTranscriber:
    """Real-time streaming transcription with speaker diarization."""
    
    def __init__(self, on_transcript=None, on_error=None):
        self.on_transcript = on_transcript or (lambda x: print(f"📝 {x}"))
        self.on_error = on_error or (lambda e: print(f"⚠️ Error: {e}"))
        self.transcriber = None
    
    def start(self):
        """Start real-time transcription session."""
        
        def on_data(transcript: aai.RealtimeTranscript):
            if not transcript.text:
                return
            if isinstance(transcript, aai.RealtimeFinalTranscript):
                self.on_transcript(transcript.text)
        
        def on_error(error: aai.RealtimeError):
            self.on_error(error)
        
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16_000,
            on_data=on_data,
            on_error=on_error
        )
        
        self.transcriber.connect()
        return self.transcriber
    
    def stream_audio(self, audio_chunk: bytes):
        """Stream audio data to AssemblyAI."""
        if self.transcriber:
            self.transcriber.stream(audio_chunk)
    
    def stop(self):
        """Stop transcription session."""
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None


# Quick test
if __name__ == "__main__":
    print("Testing AssemblyAI connection...")
    
    # Test with a simple file if available
    test_files = ["data/test.wav", "data/live_meeting.wav"]
    
    for tf in test_files:
        if os.path.exists(tf):
            print(f"Transcribing {tf}...")
            try:
                results = transcribe_file_with_speakers(tf)
                print(format_transcript_with_speakers(results))
            except Exception as e:
                print(f"Error: {e}")
            break
    else:
        print("No test audio file found. API key is configured!")
        print(f"API Key: {aai.settings.api_key[:8]}...")
