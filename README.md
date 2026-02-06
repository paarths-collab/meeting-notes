# Intelligent Meeting Agent 🤖

Automated meeting workflow orchestrator that captures transcripts, extracts tasks, and broadcasts summaries to Notion and Slack.

## 🌟 Features
- **Smart Task Extraction**: Uses Gemini Pro to extract actionable tasks with titles, detailed descriptions, and deadlines.
- **Smart Assignee Mapping**: Automatically resolves "Paarth" to the correct Notion User ID.
- **Human-in-the-Loop**: AutoGen Reflector Agent asks for clarification if details are missing.
- **Rich Summaries**: Generates formatted meeting summaries in Notion (Key Points, Decisions).
- **Multi-Channel Broadcast**: Sends summaries to both Notion and Slack.
- **SOLID Architecture**: Built with dependency injection and modular services.

## 🚀 Quick Start (Production Pipeline)

The system runs in two stages: **Listen** and **Process**.

### 1️⃣ Stage 1: Record & Transcribe (Live)
Refreshes the transcript buffer and starts listening.
```bash
# Clear previous transcript (optional but recommended)
# Windows Powershell:
Clear-Content data/transcripts.txt

# Start Recording
python main.py
```
*Speak into your specific microphone setup. You will see "🎧 Processing chunk..." and "📝 [Text]" in the console.*
*Press `Ctrl+C` to stop when the meeting is over.*

### 2️⃣ Stage 2: Analyze & Execute
Parses the transcript, extracts tasks, updates Notion, and alerts Slack.
```bash
python run_meeting.py
```
*You will see logs for Task Extraction -> Notion Creation -> Slack Notification.*

## 🏗️ Architecture

The system uses **LangGraph** to manage the workflow:

`Planner` -> `Reflector` -> `Executor` -> `Summary` -> `Broadcast` -> `Memory`

- **Planner**: Extracts task list.
- **Reflector**: Checks for missing info (Owner/Deadline).
- **Executor**: Creates tasks in Notion.
- **Summary**: Summarizes the meeting context.
- **Broadcast**: Notifies channels.
- **Memory**: Saves state to `memory/sessions/`.

## 🧪 Testing

- `tests/test_assignee.py`: Verify name-to-ID mapping.
- `tests/test_summary.py`: Verify summary generation.
- `tests/test_solid.py`: Verify service architecture.
