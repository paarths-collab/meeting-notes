from typing import List, Dict

SYSTEM_PROMPT = """
You are an executive assistant.

Your job is to extract ACTION ITEMS from meeting transcripts.

Rules:
- Extract ONLY actionable tasks
- Ignore greetings, discussions, opinions
- Identify:
  - task (short verb phrase)
  - owner (person responsible, if mentioned)
  - deadline (date or time reference, if mentioned)
- If owner or deadline is missing, use null
- Output STRICT JSON only (no explanation)

Example output:
[
  {
    "task": "Finish backend API",
    "owner": "Ravi",
    "deadline": "Friday"
  }
]
"""

def build_prompt(transcript: str) -> List[Dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": transcript}
    ]
