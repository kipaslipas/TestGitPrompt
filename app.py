"""Voice-based student attendance — Streamlit app.

Call out roll numbers and/or names; matched students are auto-detected and
marked Present, while everyone else is auto-filled as Absent.
"""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import streamlit as st

import attendance as att
from matcher import match_transcript

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "students.csv")

st.set_page_config(page_title="Voice Attendance", page_icon="🎙️", layout="wide")


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------
def get_roster() -> att.Roster:
    if "roster" not in st.session_state:
        roster = att.load_roster(DATA_PATH)
        roster.reset()  # everyone starts Absent
        st.session_state.roster = roster
    return st.session_state.roster


roster = get_roster()


# --------------------------------------------------------------------------
# Sidebar: roster management
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("👥 Roster")
    st.caption("Edit students, then save. Saving persists to data/students.csv.")

    editor_rows = [
        {"roll_number": s.roll_number, "name": s.name}
        for s in sorted(roster.students, key=lambda s: s.roll_number)
    ]
    edited = st.data_editor(
        pd.DataFrame(editor_rows, columns=["roll_number", "name"]),
        num_rows="dynamic",
        use_container_width=True,
        key="roster_editor",
    )

    if st.button("💾 Save roster", use_container_width=True):
        new_roster = att.Roster.from_rows(edited.to_dict("records"))
        # Preserve current statuses where roll numbers still exist.
        for s in new_roster.students:
            old = roster.get(s.roll_number)
            if old is not None:
                s.status = old.status
        att.save_roster(new_roster, DATA_PATH)
        st.session_state.roster = new_roster
        st.success(f"Saved {len(new_roster.students)} students.")
        st.rerun()

    st.divider()
    model_size = st.selectbox(
        "Whisper model", ["tiny", "base", "small"], index=0,
        help="Larger = more accurate but slower/heavier. 'tiny' is the safest "
        "default on Streamlit Cloud's free tier (~1 GB RAM). Downloads once.",
    )


# --------------------------------------------------------------------------
# Main: take attendance
# --------------------------------------------------------------------------
st.title("🎙️ Voice Student Attendance")
st.write(
    "Record yourself calling out roll numbers and/or names. "
    "Detected students are marked **Present**; the rest stay **Absent**."
)

col_rec, col_actions = st.columns([2, 1])

with col_rec:
    audio = st.audio_input("Record the roll call")

with col_actions:
    st.write("")
    st.write("")
    if st.button("🔄 Reset to all Absent", use_container_width=True):
        roster.reset()
        st.session_state.pop("last_transcript", None)
        st.rerun()

if audio is not None and st.button("✅ Transcribe & mark attendance", type="primary"):
    with st.spinner("Transcribing locally with Whisper…"):
        try:
            from speech import transcribe_bytes

            transcript = transcribe_bytes(audio.getvalue(), model_size=model_size)
        except Exception as exc:  # noqa: BLE001 - surface any STT failure to the user
            st.error(f"Transcription failed: {exc}")
            transcript = ""

    if transcript:
        st.session_state.last_transcript = transcript
        matched_rolls = match_transcript(transcript, roster.students)
        changed = roster.mark_present(matched_rolls)
        st.success(
            f"Heard {len(matched_rolls)} student(s); "
            f"{len(changed)} newly marked Present."
        )
    else:
        st.warning("No speech detected — please record again.")

if "last_transcript" in st.session_state:
    st.info(f"📝 Transcript: *{st.session_state.last_transcript}*")


# --------------------------------------------------------------------------
# Attendance table + manual override
# --------------------------------------------------------------------------
st.subheader("Attendance")

c1, c2, c3 = st.columns(3)
c1.metric("Total", len(roster.students))
c2.metric("Present", len(roster.present))
c3.metric("Absent", len(roster.absent))

status_df = pd.DataFrame(att.attendance_rows(roster))
if not status_df.empty:
    override = st.data_editor(
        status_df,
        use_container_width=True,
        disabled=["roll_number", "name"],
        column_config={
            "status": st.column_config.SelectboxColumn(
                "status", options=[att.PRESENT, att.ABSENT], required=True
            )
        },
        key="status_editor",
    )
    # Apply any manual status overrides back to the roster.
    for row in override.to_dict("records"):
        roster.set_status(int(row["roll_number"]), row["status"])

    csv_bytes = override.sort_values("roll_number").to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export attendance CSV",
        data=csv_bytes,
        file_name=f"attendance_{datetime.now():%Y%m%d_%H%M%S}.csv",
        mime="text/csv",
        use_container_width=True,
    )
else:
    st.warning("No students in the roster. Add some in the sidebar.")
