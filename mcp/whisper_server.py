import sys
import json
import whisper
import numpy as np

model = whisper.load_model("small")

def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def handle(req):
    if req["method"] == "list_tools":
        return {
            "tools": [
                {
                    "name": "transcribe_audio",
                    "description": "Transcribe 16kHz mono audio",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "audio": {
                                "type": "array",
                                "items": {"type": "number"}
                            }
                        },
                        "required": ["audio"]
                    }
                }
            ]
        }

    if req["method"] == "call_tool":
        audio = np.array(
            req["params"]["arguments"]["audio"],
            dtype="float32"
        )

        result = model.transcribe(audio, fp16=False)

        return {
            "content": [
                {"type": "text", "text": result["text"]}
            ]
        }

    return {"error": "unknown method"}

def main():
    for line in sys.stdin:
        req = json.loads(line)
        res = handle(req)
        send({
            "jsonrpc": "2.0",
            "id": req.get("id"),
            "result": res
        })

if __name__ == "__main__":
    main()
