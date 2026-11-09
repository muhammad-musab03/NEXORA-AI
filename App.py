
import streamlit as st
import streamlit.components.v1 as components
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from openai import APIError
from AI_Client import create_history, get_study_response
from Rag import RAGStore

# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="WOLF AI",
    page_icon="🐺",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "chat_history.json"
DOCUMENTS_DIR = BASE_DIR / "documents"

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------
# RAG Store
# -----------------------------------

@st.cache_resource
def get_rag_store():
    return RAGStore()


rag_store = get_rag_store()


# -----------------------------------
# Animated dark theme + compact input
# -----------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #070910;
    --panel: #101522;
    --red: #ff3548;
    --text: #f2f5ff;
    --muted: #929bb0;
}

.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, #20203a 0%, transparent 50%),
        linear-gradient(145deg, #070910, #0b0e18 55%, #10101b);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080a12, #101321);
    border-right: 1px solid #292b40;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent;
}

h1, h2, h3, p, label { color: var(--text); }

.wolf-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(35px, 6vw, 62px);
    font-weight: 800;
    text-align: center;
    letter-spacing: 7px;
    color: #fff;
    text-shadow: 0 0 10px #ff354866, 0 0 30px #ff354855;
    animation: titleGlow 3s ease-in-out infinite alternate;
}

.wolf-subtitle {
    text-align: center;
    color: #a8b0c5;
    font-size: 15px;
    margin-bottom: 28px;
}

@keyframes titleGlow {
    from { text-shadow: 0 0 8px #ff354833; }
    to { text-shadow: 0 0 16px #ff3548aa, 0 0 38px #ff354844; }
}

.wolf-mark {
    text-align: center;
    font-size: 62px;
    animation: wolfFloat 3s ease-in-out infinite;
    filter: drop-shadow(0 0 14px #ff354877);
}

@keyframes wolfFloat {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-7px) scale(1.04); }
}

.section-title {
    color: #ff6574;
    font-family: 'Orbitron', sans-serif;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 10px 0;
}

.feature-card {
    background: linear-gradient(135deg, #151a2b, #0d101a);
    border: 1px solid #292f46;
    border-radius: 15px;
    padding: 18px;
    min-height: 115px;
    margin-bottom: 10px;
    transition: all .25s ease;
}

.feature-card:hover {
    border-color: #ff3548;
    box-shadow: 0 0 20px #ff354822;
    transform: translateY(-3px);
}

.feature-card h4 { color: white; margin: 0 0 8px 0; }
.feature-card p { color: #a6aec2; font-size: 13px; margin: 0; }

[data-testid="stChatMessage"] {
    scroll-margin-top: 28px;
    background: linear-gradient(135deg, #111624, #0d111c);
    border: 1px solid #272d40;
    border-radius: 16px;
    padding: 15px;
    margin-bottom: 12px;
    animation: messageIn .35s ease;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #f4f5f8 !important;
    border-color: #d7dbe5 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] li,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"] strong {
    color: #111111 !important;
}

@keyframes messageIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    color: #f2f5ff;
    font-size: 15px;
    line-height: 1.7;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1 {
    color: #ff7582;
    font-size: 22px;
    font-weight: 650;
    line-height: 1.4;
    margin-top: 8px;
    margin-bottom: 10px;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2 {
    color: #ff7582;
    font-size: 19px;
    font-weight: 600;
    line-height: 1.4;
    margin-top: 8px;
    margin-bottom: 8px;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
    color: #ff7582;
    font-size: 17px;
    font-weight: 600;
    line-height: 1.4;
    margin-top: 6px;
    margin-bottom: 6px;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
    font-size: 15px;
    font-weight: 400;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong {
    font-weight: 600;
}

[data-testid="stChatMessage"] code {
    color: #ffb3bb;
    background: #1b2030;
    border-radius: 5px;
}

/* Chat Input */

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {
    background: transparent !important;
    box-shadow: none !important;
}

[data-testid="stBottom"] {
    padding-top: 8px !important;
    padding-bottom: 12px !important;
}

[data-testid="stChatInput"] {
    max-width: 620px !important;
    width: min(62%, 620px) !important;
    min-width: 280px !important;
    margin: 0 auto !important;
    border: 1px solid #343a52 !important;
    border-radius: 11px !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 1px #ff354811, 0 0 14px #00000033 !important;
    min-height: 42px !important;
    max-height: 112px !important;
    transition: width .25s ease, border-color .25s ease, box-shadow .25s ease;
    animation: inputAppear .45s ease both;
}

[data-testid="stChatInput"]:focus-within {
    width: min(76%, 760px) !important;
}

@keyframes inputAppear {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stChatInput"]:focus-within {
    border-color: #ff3548 !important;
    box-shadow: 0 0 14px #ff354833 !important;
}

[data-testid="stChatInput"] textarea {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    background: transparent !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    line-height: 1.4 !important;
    caret-color: #111111 !important;
    padding-top: 7px !important;
    padding-bottom: 7px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #555b69 !important;
    -webkit-text-fill-color: #555b69 !important;
    opacity: 1;
}

[data-testid="stChatInput"] button {
    background: #050505 !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 9px !important;
    width: 34px !important;
    min-width: 34px !important;
    height: 32px !important;
    min-height: 32px !important;
    margin-right: 5px !important;
    transition: background .2s ease, transform .2s ease, box-shadow .2s ease !important;
}

[data-testid="stChatInput"] button svg { display: none !important; }

[data-testid="stChatInput"] button::after {
    content: "●";
    color: #fff;
    font-size: 13px;
    line-height: 1;
}

[data-testid="stChatInput"] button:hover {
    background: #fff !important;
    transform: scale(1.05);
    box-shadow: 0 0 12px #ffffff44 !important;
}

[data-testid="stChatInput"] button:hover::after { color: #050505; }

[data-testid="stChatInput"] button:active {
    background: #ffd84d !important;
    transform: scale(.94);
}

[data-testid="stChatInput"] button:active::after { color: #050505; }

.stButton > button {
    background: linear-gradient(135deg, #191d2c, #111521);
    color: #f3f5ff;
    border: 1px solid #30364d;
    border-radius: 10px;
    transition: all .2s ease;
}

.stButton > button:hover {
    color: white;
    border-color: #ff3548;
    box-shadow: 0 0 14px #ff354833;
}

hr { border-color: #292e42; }

div[data-testid="stSpinner"] p { color: #ff7582; }

.welcome-card {
    text-align: center;
    padding: 24px 12px;
    background: linear-gradient(135deg, #111625bb, #151020bb);
    border: 1px solid #292e43;
    border-radius: 18px;
    margin: 10px 0 24px;
}

.welcome-card h2 { font-size: 23px; margin-bottom: 8px; }
.welcome-card p { color: #a8b0c5; margin-bottom: 0; }

.history-label {
    color: #ff7582;
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 8px 0;
}

div[data-testid="stSidebar"] .stCaption { color: #939db4; }

/* Author Credit */

.author-credit {
    position: fixed;
    top: 12px;
    right: 58px;
    z-index: 999999;
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    letter-spacing: 1px;
    color: #ffcf45;
    opacity: .9;
    text-shadow: 0 0 8px #ffcf4566;
    animation: authorPulse 2.5s ease-in-out infinite alternate;
    pointer-events: none;
}

@keyframes authorPulse {
    from { opacity: .55; text-shadow: 0 0 3px #ffcf4533; }
    to { opacity: 1; text-shadow: 0 0 10px #ffcf45aa; }
}

/* Mobile */

@media (max-width: 600px) {
    .wolf-title { letter-spacing: 4px; }
    .wolf-mark { font-size: 48px; }

    [data-testid="stChatMessage"] { padding: 12px; }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        font-size: 14px;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1 {
        font-size: 20px;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2 {
        font-size: 18px;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
        font-size: 16px;
    }

    .author-credit {
        top: 8px;
        right: 38px;
        font-size: 8px;
        letter-spacing: .5px;
    }

    [data-testid="stChatInput"] {
        width: calc(100% - 24px) !important;
        min-width: 0 !important;
    }

    [data-testid="stChatInput"]:focus-within {
        width: calc(100% - 12px) !important;
    }
}
</style>

<div class="author-credit">AUTHOR MUHAMMAD MUSAB</div>
""", unsafe_allow_html=True)


# -----------------------------------
# History Functions
# -----------------------------------

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}

    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def render_copy_answer_button(answer, key):
    """Render a copy button for the complete assistant answer."""

    answer_json = json.dumps(answer, ensure_ascii=False)
    button_id = f"copy-answer-{key}"

    components.html(
        f"""
        <button id="{button_id}" style="
            padding:7px 12px;
            background:#080a10;
            color:#f4f6ff;
            border:1px solid #343a52;
            border-radius:8px;
            cursor:pointer;
            font-size:12px;
            font-weight:600;
            transition:all .2s ease;
        ">📋 Copy Answer</button>

        <script>
        const btn = document.getElementById("{button_id}");
        const answerText = {answer_json};

        btn.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText(answerText);
                btn.textContent = "✓ Copied";
                btn.style.background = "#ffffff";
                btn.style.color = "#080a10";

                setTimeout(() => {{
                    btn.textContent = "📋 Copy Answer";
                    btn.style.background = "#080a10";
                    btn.style.color = "#f4f6ff";
                }}, 1400);

            }} catch (error) {{
                const area = document.createElement("textarea");
                area.value = answerText;
                area.style.position = "fixed";
                area.style.left = "-9999px";

                document.body.appendChild(area);
                area.select();

                const success = document.execCommand("copy");
                area.remove();

                btn.textContent = success ? "✓ Copied" : "Copy failed";

                if (success) {{
                    btn.style.background = "#ffffff";
                    btn.style.color = "#080a10";

                    setTimeout(() => {{
                        btn.textContent = "📋 Copy Answer";
                        btn.style.background = "#080a10";
                        btn.style.color = "#f4f6ff";
                    }}, 1400);
                }}
            }}
        }});
        </script>
        """,
        height=43,
    )


# -----------------------------------
# Document Helper Functions
# -----------------------------------

def safe_filename(filename):
    """Create a safe filename for local document storage."""

    name = Path(filename).name
    return re.sub(r"[^a-zA-Z0-9._-]", "_", name)


def save_original_document(filename, file_bytes):
    """Save the original uploaded document locally."""

    file_hash = hashlib.sha256(file_bytes).hexdigest()
    safe_name = safe_filename(filename)

    file_path = DOCUMENTS_DIR / f"{file_hash}_{safe_name}"

    file_path.write_bytes(file_bytes)

    return file_path


def delete_original_documents(filename):
    """Delete locally saved original files with the given name."""

    safe_name = safe_filename(filename)

    for file_path in DOCUMENTS_DIR.glob(f"*_{safe_name}"):
        if file_path.is_file():
            file_path.unlink()


# -----------------------------------
# Session State
# -----------------------------------

if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_history()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = create_history()

if "active_chat_type" not in st.session_state:
    st.session_state.active_chat_type = "normal"

if "active_document_name" not in st.session_state:
    st.session_state.active_document_name = None


def new_conversation():
    """Start a fresh normal chat without document retrieval."""
    st.session_state.current_chat_id = None
    st.session_state.messages = create_history()
    st.session_state.active_chat_type = "normal"
    st.session_state.active_document_name = None


def start_document_chat(filename):
    """Start a brand-new chat connected only to the selected document."""
    st.session_state.current_chat_id = None
    st.session_state.messages = create_history()
    st.session_state.active_chat_type = "document"
    st.session_state.active_document_name = filename


# -----------------------------------
# Sidebar
# -----------------------------------

with st.sidebar:

    st.markdown('<div class="wolf-mark">🌐</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">AI ASSISTANT</div>',
        unsafe_allow_html=True
    )

    st.write("Explore ideas. Understand concepts. Keep learning.")

    st.divider()

    if st.button("＋  New Conversation", use_container_width=True):
        new_conversation()
        st.rerun()

    # -----------------------------------
    # Study Tools
    # -----------------------------------

    st.markdown(
        '<div class="section-title">YOUR STUDY TOOLS</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="feature-card">
        <h4>✦ Explain Concepts</h4>
        <p>Understand difficult topics step by step.</p>
    </div>

    <div class="feature-card">
        <h4>◈ Summarize Text</h4>
        <p>Turn lengthy material into clear notes.</p>
    </div>

    <div class="feature-card">
        <h4>⌘ Practice Questions</h4>
        <p>Prepare with useful questions and answers.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # -----------------------------------
    # RAG Document Upload
    # -----------------------------------

    st.markdown(
        '<div class="section-title">📚 KNOWLEDGE BASE</div>',
        unsafe_allow_html=True
    )

    st.caption("Upload documents and ask questions about their content.")

    uploaded_files = st.file_uploader(
        "Upload your documents",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT and MD"
    )

    if st.button(
        "⚡ Process Documents",
        use_container_width=True,
        disabled=not uploaded_files
    ):

        for uploaded_file in uploaded_files:

            try:
                file_bytes = uploaded_file.getvalue()

                with st.spinner(f"Processing {uploaded_file.name}..."):

                    result = rag_store.add_document(
                        uploaded_file.name,
                        file_bytes
                    )

                    save_original_document(
                        uploaded_file.name,
                        file_bytes
                    )

                if isinstance(result, dict):
                    chunk_count = result.get("chunks", "Processed")
                    page_count = result.get("pages")

                    if page_count is not None:
                        st.success(
                            f"✓ {uploaded_file.name} processed "
                            f"({page_count} pages, {chunk_count} chunks)"
                        )
                    else:
                        st.success(
                            f"✓ {uploaded_file.name} processed "
                            f"({chunk_count} chunks)"
                        )

                else:
                    st.success(f"✓ {uploaded_file.name} processed successfully.")

            except Exception as error:
                st.error(f"Could not process {uploaded_file.name}: {error}")

    # -----------------------------------
    # Saved Documents
    # -----------------------------------

    st.markdown("**Saved Documents**")

    try:
        saved_documents = rag_store.list_documents()

        if not saved_documents:
            st.caption("No documents uploaded yet.")

        else:
            for index, document in enumerate(saved_documents):

                filename = document.get("filename", "Unknown document")
                file_type = document.get("file_type", "Document")
                chunks = document.get("chunks", 0)
                uploaded_at = document.get("uploaded_at", "")

                with st.expander(f"📄 {filename}"):

                    st.caption(f"Type: {file_type}")
                    st.caption(f"Chunks: {chunks}")

                    if uploaded_at:
                        st.caption(f"Uploaded: {uploaded_at}")

                    if st.button(
                        "💬 Start New Document Chat",
                        key=f"open_document_{index}_{hashlib.md5(filename.encode()).hexdigest()[:8]}",
                        use_container_width=True
                    ):
                        start_document_chat(filename)
                        st.rerun()

                    if st.button(
                        "🗑 Delete Document",
                        key=f"delete_document_{index}_{hashlib.md5(filename.encode()).hexdigest()[:8]}",
                        use_container_width=True
                    ):

                        try:
                            rag_store.delete_document(filename)
                            delete_original_documents(filename)

                            st.success("Document deleted successfully.")
                            st.rerun()

                        except Exception as error:
                            st.error(f"Delete failed: {error}")

    except Exception as error:
        st.warning(f"Could not load document list: {error}")

    # -----------------------------------
    # Knowledge Base Statistics
    # -----------------------------------

    try:
        stats = rag_store.get_stats()

        if stats:
            st.divider()
            st.markdown("**Knowledge Base Statistics**")

            st.caption(
                f"Documents: {stats.get('total_documents', 0)}"
            )

            st.caption(
                f"Total Chunks: {stats.get('total_chunks', 0)}"
            )

    except Exception:
        pass

    st.divider()

    # -----------------------------------
    # Chat History
    # -----------------------------------

    st.markdown(
        '<div class="history-label">◈  CHAT HISTORY</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.all_chats:
        st.caption("Your conversations will appear here.")

    for chat_id, chat_data in reversed(
        list(st.session_state.all_chats.items())
    ):

        history_icon = (
            "📄" if chat_data.get("chat_type") == "document" else "💬"
        )

        if st.button(
            history_icon + "  " + chat_data.get("title", "Untitled Chat"),
            key=f"history_{chat_id}",
            use_container_width=True
        ):

            st.session_state.current_chat_id = chat_id
            st.session_state.messages = chat_data.get(
                "messages", create_history()
            )
            st.session_state.active_chat_type = chat_data.get(
                "chat_type", "normal"
            )
            st.session_state.active_document_name = chat_data.get(
                "document_name"
            )
            st.rerun()


# -----------------------------------
# Main Header
# -----------------------------------

st.markdown('<div class="wolf-mark">🐺</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="wolf-title">WOLF AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="wolf-subtitle">YOUR INTELLIGENT STUDY COMPANION</div>',
    unsafe_allow_html=True
)


# -----------------------------------
# Welcome Screen
# -----------------------------------

visible_messages = [
    message
    for message in st.session_state.messages
    if message["role"] != "system"
]

if not visible_messages:

    st.markdown("""
    <div class="welcome-card">
        <h2>What are we learning today?</h2>
        <p>Ask a question, explore an idea, or master a new concept.</p>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------
# Display Conversation + Copy Button
# -----------------------------------

for index, message in enumerate(visible_messages):

    if message["role"] == "user":

        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])

    elif message["role"] == "assistant":

        with st.chat_message("assistant", avatar="🐺"):
            st.markdown(message["content"])

            render_copy_answer_button(
                message["content"],
                f"history-{index}"
            )


# -----------------------------------
# Chat Input + Mode-Aware RAG Search
# -----------------------------------

if st.session_state.active_chat_type == "document":
    st.caption(
        f"📄 Document Chat: **{st.session_state.active_document_name}**"
    )
else:
    st.caption("💬 Normal Chat — document search is turned off.")

prompt = st.chat_input(
    "Ask about the selected document..." 
    if st.session_state.active_chat_type == "document"
    else "Ask WOLF AI anything about your studies..."
)


if prompt:

    # Add the user's actual question to the visible conversation.
    next_messages = st.session_state.messages + [
        {"role": "user", "content": prompt}
    ]

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    try:

        with st.chat_message("assistant", avatar="🐺"):

            with st.spinner("WOLF AI is thinking..."):

                rag_results = None

                # RAG is used ONLY in Document Chat.
                if (
                    st.session_state.active_chat_type == "document"
                    and st.session_state.active_document_name
                ):
                    rag_results = rag_store.search(
                        question=prompt,
                        top_k=5,
                        min_score=0.25,
                        source=st.session_state.active_document_name
                    )

                answer = get_study_response(
                    next_messages,
                    rag_results=rag_results,
                    document_mode=(
                        st.session_state.active_chat_type == "document"
                    ),
                    document_name=st.session_state.active_document_name
                )

            st.markdown(answer)

            render_copy_answer_button(
                answer,
                "new-answer"
            )

            # Auto Scroll
            components.html(
                """
                <script>
                (() => {
                    const scrollToLatestAnswer = () => {
                        try {
                            const win = window.parent;
                            const doc = win.document;

                            const messages = Array.from(
                                doc.querySelectorAll(
                                    '[data-testid="stChatMessage"]'
                                )
                            );

                            const latestMessage =
                                messages[messages.length - 1];

                            if (latestMessage) {
                                latestMessage.scrollIntoView({
                                    behavior: "smooth",
                                    block: "start"
                                });

                                const candidates = [
                                    doc.querySelector(
                                        '[data-testid="stAppViewContainer"]'
                                    ),
                                    doc.querySelector('section.main'),
                                    doc.scrollingElement
                                ].filter(Boolean);

                                candidates.forEach((el) => {
                                    try {
                                        const rect =
                                            latestMessage.getBoundingClientRect();

                                        const parentRect =
                                            el.getBoundingClientRect
                                            ? el.getBoundingClientRect()
                                            : { top: 0 };

                                        if (
                                            rect.bottom > parentRect.bottom ||
                                            rect.top < parentRect.top
                                        ) {
                                            el.scrollTo({
                                                top:
                                                    el.scrollTop +
                                                    rect.top -
                                                    parentRect.top - 24,
                                                behavior: "smooth"
                                            });
                                        }
                                    } catch (_) {}
                                });
                            }
                        } catch (error) {}
                    };

                    setTimeout(scrollToLatestAnswer, 250);
                    setTimeout(scrollToLatestAnswer, 700);
                    setTimeout(scrollToLatestAnswer, 1200);
                })();
                </script>
                """,
                height=1
            )

        # -----------------------------------
        # Save Conversation in ONE Chat History
        # -----------------------------------

        updated_messages = next_messages + [
            {"role": "assistant", "content": answer}
        ]

        chat_id = st.session_state.current_chat_id

        if chat_id is None:
            chat_id = datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )
            title = prompt[:40]
            st.session_state.current_chat_id = chat_id
        else:
            existing_chat = st.session_state.all_chats.get(chat_id, {})
            title = existing_chat.get("title", prompt[:40])

        st.session_state.messages = updated_messages

        st.session_state.all_chats[chat_id] = {
            "title": title,
            "messages": updated_messages,
            "updated_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "chat_type": st.session_state.active_chat_type,
            "document_name": (
                st.session_state.active_document_name
                if st.session_state.active_chat_type == "document"
                else None
            )
        }

        save_history(st.session_state.all_chats)

    except (APIError, ValueError, RuntimeError) as error:

        st.error(
            "Could not get an answer. Please check your API "
            "configuration, document database and internet connection."
        )

        print(f"WOLF AI error: {error}")

    except Exception as error:

        st.error(
            "Something went wrong while processing your request."
        )

        print(f"Unexpected error: {error}")
