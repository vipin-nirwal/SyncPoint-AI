import os
import json
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Import custom logic
from src.engine import get_chroma_index
from src.utils import process_pdf, STRICT_QA_PROMPT, load_confluence_data

now = datetime.now()
today_str = now.strftime("%A, %B %d, %Y")
current_time = now.strftime("%H:%M")

# --- Configuration & Styling ---
st.set_page_config(page_title="AI Workspace Assistant", page_icon="🤖", layout="wide")

# Modern SaaS Styling with CSS
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfd; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #f0f0f5;
    }
    
    /* Section Headers */
    .sidebar-header {
        font-size: 0.75rem;
        font-weight: 800;
        color: #9ea3b0;
        text-transform: uppercase;
        letter-spacing: 0.1rem;
        padding: 1.5rem 0 0.5rem 0;
    }

    /* Chat Message Bubbles */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid #f0f0f5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* Buttons customization */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    /* Transparent Trash Bin Style */
    [data-testid="column"] button {
        border: none !important;
        background-color: transparent !important;
        padding: 0px !important;
        color: #ccd0d5 !important;
        transition: color 0.3s ease;
        margin-top: 5px;
    }

    [data-testid="column"] button:hover {
        color: #ff4b4b !important;
        background-color: transparent !important;
        transform: scale(1.1);
    }
    
    /* Knowledge Base Labels */
    .kb-label {
        font-size: 0.7rem;
        font-weight: bold;
        color: #5e6ad2;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

HISTORY_FILE = "chat_history.json"

# --- Persistence Logic ---
def load_permanent_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_permanent_history(history_dict):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history_dict, f)

def check_index_has_data():
    try:
        res = st.session_state.index.vector_store._collection.get()
        return len(res.get('ids', [])) > 0
    except: return False

# --- State Initialization ---
if "index" not in st.session_state:
    st.session_state.index = get_chroma_index()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_permanent_history()

if "current_session_name" not in st.session_state:
    st.session_state.current_session_name = None

# --- Sidebar Management ---
with st.sidebar:
    st.title("🚀 AI Workspace")
    
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_session_name = None
        if "chat_engine" in st.session_state: del st.session_state.chat_engine
        st.rerun()

    st.markdown('<p class="sidebar-header">CONNECTIONS</p>', unsafe_allow_html=True)
    
    # Confluence Section
    with st.expander("🌐 Confluence Cloud", expanded=False):
        page_id = st.text_input("Page ID", placeholder="e.g. 5868650508")
        if st.button("Sync Page", use_container_width=True):
            if page_id:
                with st.spinner("Syncing..."):
                    try:
                        base_url = os.getenv("CONFLUENCE_URL")
                        docs = load_confluence_data(base_url, page_id)
                        for doc in docs: st.session_state.index.insert(doc)
                        st.toast(f"Synced: {docs[0].metadata['title']}", icon="✅")
                        if "chat_engine" in st.session_state: del st.session_state.chat_engine
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    # PDF Section
    with st.expander("📄 File Upload", expanded=False):
        up_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
        if up_file and st.button("Index PDF", use_container_width=True):
            if not os.path.exists("data"): os.makedirs("data")
            path = os.path.join("data", up_file.name)
            with open(path, "wb") as f: f.write(up_file.getbuffer())
            doc = process_pdf(path, up_file.name)
            st.session_state.index.insert(doc)
            if "chat_engine" in st.session_state: del st.session_state.chat_engine
            st.toast(f"Indexed {up_file.name}", icon="📄")
            st.rerun()

    st.markdown('<p class="sidebar-header">KNOWLEDGE BASE</p>', unsafe_allow_html=True)
    
    # Categorized Source List
    try:
        all_docs = st.session_state.index.vector_store._collection.get()
        conf_pages = {}
        pdf_files = {}

        if all_docs['ids']:
            for i, d_id in enumerate(all_docs['ids']):
                meta = all_docs['metadatas'][i]
                if meta.get("source") == "Confluence":
                    p_id = meta.get("page_id")
                    if p_id not in conf_pages: conf_pages[p_id] = meta.get("title", "Unknown")
                else:
                    f_name = meta.get("file_name")
                    if f_name and f_name not in pdf_files: pdf_files[f_name] = f_name

            # UI Display: Confluence
            if conf_pages:
                st.markdown('<p class="kb-label">🌐 CONFLUENCE PAGES</p>', unsafe_allow_html=True)
                for p_id, p_title in conf_pages.items():
                    c1, c2 = st.columns([0.85, 0.15])
                    c1.write(f"**{p_title}**")
                    if c2.button("🗑️", key=f"del_conf_{p_id}"):
                        st.session_state.index.vector_store._collection.delete(where={"page_id": p_id})
                        if "chat_engine" in st.session_state: del st.session_state.chat_engine
                        st.rerun()
            
            # UI Display: PDFs
            if pdf_files:
                st.markdown('<p class="kb-label">📄 PDF DOCUMENTS</p>', unsafe_allow_html=True)
                for f_name in pdf_files.keys():
                    c1, c2 = st.columns([0.85, 0.15])
                    c1.write(f"{f_name}")
                    if c2.button("🗑️", key=f"del_pdf_{f_name}"):
                        st.session_state.index.vector_store._collection.delete(where={"file_name": f_name})
                        l_path = os.path.join("data", f_name)
                        if os.path.exists(l_path): os.remove(l_path)
                        if "chat_engine" in st.session_state: del st.session_state.chat_engine
                        st.rerun()
        else:
            st.info("No sources indexed.")
    except Exception as e:
        st.info("Knowledge base empty.")

    st.markdown('<p class="sidebar-header">SAVED SESSIONS</p>', unsafe_allow_html=True)
    s_name_input = st.text_input("Session Title", value=st.session_state.current_session_name or "", placeholder="Enter title...")
    if st.button("💾 Save Conversation", use_container_width=True) and s_name_input:
        st.session_state.chat_sessions[s_name_input] = st.session_state.messages
        save_permanent_history(st.session_state.chat_sessions)
        st.session_state.current_session_name = s_name_input
        st.toast("Saved session!", icon="💾")

    for name in list(st.session_state.chat_sessions.keys()):
        cl, cd = st.columns([0.8, 0.2])
        if cl.button(f"💬 {name}", key=f"load_{name}", use_container_width=True):
            st.session_state.messages = st.session_state.chat_sessions[name].copy()
            st.session_state.current_session_name = name
            if "chat_engine" in st.session_state: del st.session_state.chat_engine
            st.rerun()
        if cd.button("×", key=f"kill_{name}"):
            del st.session_state.chat_sessions[name]
            save_permanent_history(st.session_state.chat_sessions)
            st.rerun()

# --- Main Chat Area ---
st.title("🤖 Intelligent Assistant")
if st.session_state.current_session_name:
    st.info(f"Viewing Session: **{st.session_state.current_session_name}**")

has_knowledge = check_index_has_data()

# Initialize Chat Engine with Time Awareness
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = st.session_state.index.as_chat_engine(
        chat_mode="condense_plus_context",
        text_qa_template=STRICT_QA_PROMPT,
        context_prompt=(
            f"CRITICAL: Today's date is {today_str} (Time: {current_time}).\n"
            "INSTRUCTIONS:\n"
            "- You will see information in various formats (tables, lists, or paragraphs).\n"
            "- When asked about 'next', 'upcoming', or 'future' events, compare the dates in the text to today's date.\n"
            "- If multiple dates exist, identify the one closest to today but in the future.\n"
            "- Use the context below to answer. If the answer isn't there, say you don't know.\n"
            "\nContext: {context_str}\n"
            "History: {chat_history}"
        ),
        system_prompt=f"You are a chronological assistant. Today is {today_str}."
    )

# Render Chat History
for msg in st.session_state.messages:
    av = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=av):
        st.write(msg["content"])

# User Input
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)

    if not has_knowledge:
        ans = "The knowledge base is empty. Please sync Confluence or upload a PDF."
    else:
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat_engine.chat(prompt)
                ans = str(response)
            except Exception as e: ans = f"Error: {e}"

    with st.chat_message("assistant", avatar="🤖"):
        st.write(ans)
    st.session_state.messages.append({"role": "assistant", "content": ans})