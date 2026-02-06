import sys
import subprocess
import json

class WhisperMCPClient:
    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, "mcp/whisper_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        self.req_id = 0

    def transcribe_chunk(self, audio_chunk):
        self.req_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": "call_tool",
            "params": {
                "name": "transcribe_audio",
                "arguments": {
                    "audio": audio_chunk.tolist()
                }
            }
        }

        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()

        response = json.loads(self.proc.stdout.readline())
        return response["result"]["content"][0]["text"]
