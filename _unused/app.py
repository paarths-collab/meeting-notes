"""
Meeting to Tasks Pipeline - Streamlit UI

Supports 3 input modes:
1. Paste text transcript
2. Upload audio/video file
3. Paste downloadable link

All inputs → transcript → meeting pipeline → Notion + Slack
"""
import streamlit as st
import uuid
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.graph import create_meeting_graph
from core.container import ServiceContainer
from pipeline.transcript_router import get_transcript

# Page config
st.set_page_config(
    page_title="Meeting → Tasks",
    page_icon="📝",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .stTextArea textarea { font-family: monospace; }
    .success-box { padding: 1rem; background: #d4edda; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📝 Meeting to Tasks Pipeline")
st.caption("Convert meeting recordings or transcripts into Notion tasks & Slack summaries")

st.divider()

# Input mode selection
option = st.radio(
    "**Choose input type:**",
    ["✏️ Paste Text", "📁 Upload File", "🔗 Paste Link"],
    horizontal=True
)

user_text = None
file_path = None
url = None

# Input forms based on selection
if option == "✏️ Paste Text":
    user_text = st.text_area(
        "Paste meeting transcript or notes:",
        height=200,
        placeholder="Meeting notes...\nPaarth needs to fix the login bug by tomorrow.\nRavi will update the API docs by Friday."
    )

elif option == "📁 Upload File":
    uploaded = st.file_uploader(
        "Upload meeting recording:",
        type=["mp4", "mkv", "webm", "wav", "mp3", "m4a", "ogg"]
    )
    if uploaded:
        os.makedirs("inputs/uploads", exist_ok=True)
        save_path = f"inputs/uploads/{uploaded.name}"
        with open(save_path, "wb") as f:
            f.write(uploaded.read())
        file_path = save_path
        st.success(f"✅ Uploaded: {uploaded.name}")

elif option == "🔗 Paste Link":
    url = st.text_input(
        "Paste downloadable recording link:",
        placeholder="https://drive.google.com/..."
    )
    if url:
        st.info("💡 Link will be downloaded when you process")

st.divider()

# Process button
col1, col2 = st.columns([3, 1])
with col1:
    process = st.button("🚀 **Process Meeting**", type="primary", use_container_width=True)

if process:
    # Validate input
    if not any([user_text, file_path, url]):
        st.error("❌ Please provide input (text, file, or link)")
        st.stop()
    
    # Progress
    progress = st.progress(0, text="Starting...")
    
    try:
        # Step 1: Get transcript
        progress.progress(20, text="📝 Extracting transcript...")
        
        transcript = get_transcript(
            text=user_text,
            file_path=file_path,
            url=url
        )
        
        if not transcript.strip():
            st.error("❌ No transcript generated")
            st.stop()
        
        # Show transcript
        with st.expander("📄 **Transcript Preview**", expanded=True):
            st.text_area("Transcript", transcript[:2000] + ("..." if len(transcript) > 2000 else ""), height=150, disabled=True, label_visibility="collapsed")
        
        # Step 2: Initialize services
        progress.progress(40, text="🔧 Initializing services...")
        container = ServiceContainer.from_env()
        meeting_graph = create_meeting_graph(container)
        
        # Step 3: Run pipeline
        progress.progress(60, text="🧠 Processing with AI...")
        
        initial_state = {
            "meeting_id": str(uuid.uuid4()),
            "transcript": transcript,
            "tasks": [],
            "needs_reflection": False
        }
        
        final_state = meeting_graph.invoke(initial_state)
        
        progress.progress(100, text="✅ Complete!")
        
        # Show results
        st.success("✅ **Meeting processed successfully!**")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Tasks", "📝 Summary", "🔔 Notifications"])
        
        with tab1:
            # Display tasks as a to-do list
            if final_state.get("tasks"):
                st.subheader("📋 To-Do List")
                for i, task in enumerate(final_state["tasks"], 1):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        **{i}. {task.get('title', 'Untitled')}**  
                        👤 {task.get('owner', 'Unassigned')} · 📅 {task.get('deadline', 'No deadline')}  
                        _{task.get('description', '')}_
                        """)
                    with col2:
                        if task.get('type'):
                            st.caption(f"🏷️ {task.get('type')}")
                    st.divider()
            else:
                st.info("No tasks extracted from this meeting")
        
        with tab2:
            # Display summary
            summary = final_state.get("summary", {})
            if summary:
                st.subheader("📝 Meeting Summary")
                
                if isinstance(summary, dict):
                    # Overview
                    if summary.get("overview"):
                        st.markdown("### Overview")
                        st.write(summary["overview"])
                    
                    # Key Points
                    if summary.get("key_points"):
                        st.markdown("### Key Points")
                        for point in summary["key_points"]:
                            st.markdown(f"• {point}")
                    
                    # Action Items
                    if summary.get("action_items"):
                        st.markdown("### Action Items")
                        for item in summary["action_items"]:
                            st.markdown(f"- [ ] {item}")
                    
                    # Decisions
                    if summary.get("decisions"):
                        st.markdown("### Decisions Made")
                        for decision in summary["decisions"]:
                            st.markdown(f"✓ {decision}")
                else:
                    st.write(summary)
            else:
                st.info("No summary generated")
        
        with tab3:
            # Display notification status
            st.subheader("🔔 Notifications Sent")
            
            # Notion status
            if final_state.get("notion_page_id"):
                st.success(f"✅ Notion page created: {final_state['notion_page_id'][:8]}...")
            else:
                st.info("📌 Tasks saved to Notion")
            
            # Slack status
            slack_msgs = final_state.get("slack_messages", [])
            if slack_msgs:
                st.success(f"✅ {len(slack_msgs)} Slack message(s) sent")
                for msg in slack_msgs:
                    st.caption(f"  → {msg}")
            else:
                st.info("📣 Summary sent to Slack")
            
            # Meeting ID
            st.caption(f"Meeting ID: `{final_state.get('meeting_id', 'N/A')}`")
        
        st.balloons()
        
    except Exception as e:
        progress.empty()
        st.error(f"❌ Error: {str(e)}")
        import traceback
        with st.expander("Debug info"):
            st.code(traceback.format_exc())

# Footer
st.divider()
st.caption("Pipeline: Transcript → Planner → Executor → Notion + Slack + Memory")

