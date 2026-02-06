import sys
import json
import subprocess
import numpy as np


proc = subprocess.Popen(
    [sys.executable, "mcp/whisper_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send fake audio (silence)
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "call_tool",
    "params": {
        "name": "transcribe_audio",
        "arguments": {
            "audio": np.zeros(16000).tolist()
        }
    }
}

try:
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    response = json.loads(proc.stdout.readline())
    print("MCP Whisper Response:", response)
except Exception as e:
    print(f"Error: {e}")
    stdout, stderr = proc.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

