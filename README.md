# TestGitPrompt — Voice Student Attendance 🎙️

A Streamlit app that takes class attendance **by voice**. Call out roll numbers
and/or student names; the app transcribes your speech **locally** with Whisper,
auto-detects who was named, marks them **Present**, and auto-fills everyone else
as **Absent**.

## Features

- 🎤 Record a roll call straight from the browser mic (`st.audio_input`)
- 🧠 Offline speech-to-text via [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) — no API key, no internet after the first model download
- 🔎 Matches each student by **roll number OR name**, tolerant of spoken number words ("five") and minor mis-hearings (fuzzy name match)
- ✅ Present/Absent counts, manual override of any row, and CSV export
- 👥 Editable roster persisted to `data/students.csv`

## Setup

```bash
# from the TestGitPrompt folder
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The first transcription downloads the Whisper model (~140 MB for `base`).

## How to use

1. (Optional) Edit the roster in the sidebar and click **Save roster**.
2. Click the mic and call out students, e.g. *"Roll number 5, Priya Sharma… number 12, Daniel Carter."*
3. Click **Transcribe & mark attendance**. Named students flip to Present.
4. Fix any row manually if needed, then **Export attendance CSV**.

## Tests

```bash
pytest -q
```

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI and flow |
| `attendance.py` | Roster + attendance state (pure logic) |
| `matcher.py` | Transcript parsing & roll/name matching (pure logic) |
| `speech.py` | Local Whisper transcription wrapper |
| `data/students.csv` | Editable roster |
| `tests/` | Unit tests for the pure logic |
