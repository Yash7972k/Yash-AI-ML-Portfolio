import streamlit as st
import os
import tempfile
from rag_pipeline import (
    load_and_chunk_pdfs,
    build_vector_store,
    load_vector_store,
    get_rag_chain,
    ask_question,
    FAISS_INDEX_PATH
)

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Notes Chatbot",
    page_icon="📚",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-top: 0.2rem;
        margin-bottom: 2rem;
    }

    .chat-user {
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95rem;
    }

    .chat-bot {
        background: #f1f5f9;
        color: #1e293b;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        font-size: 0.95rem;
        border-left: 3px solid #4f46e5;
    }

    .source-tag {
        background: #e0e7ff;
        color: #4f46e5;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        margin-right: 5px;
        display: inline-block;
        margin-top: 6px;
    }

    .upload-section {
        background: #f8fafc;
        border: 2px dashed #c7d2fe;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 1rem;
    }

    .status-ready {
        background: #dcfce7;
        color: #166534;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.875rem;
    }

    .status-pending {
        background: #fef9c3;
        color: #854d0e;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.875rem;
    }

    div[data-testid="stChatInput"] {
        border-radius: 16px !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #06b6d4);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        width: 100%;
        transition: opacity 0.2s;
    }

    .stButton>button:hover {
        opacity: 0.85;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
use_local_provider = os.getenv("USE_LOCAL_PROVIDER", "true").lower() not in ("false", "0", "no")

# Initialize state variables only on first page load
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "ready" not in st.session_state:
    st.session_state.ready = False


# ── Layout ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2.5], gap="large")

# ── LEFT PANEL ────────────────────────────────────────────────────────────────
with col1:
    st.markdown('<div class="main-title">📚 NoteBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Your AI-powered study companion</div>', unsafe_allow_html=True)

    st.markdown("### Upload Your Notes")
    uploaded_files = st.file_uploader(
        "Upload PDF notes",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

    if st.button("🚀 Process Notes"):
        if not uploaded_files:
            st.error("Please upload at least one PDF!")
        else:
            with st.spinner("Reading and indexing your notes..."):
                tmp_paths = []
                try:
                    for f in uploaded_files:
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        tmp.write(f.read())
                        tmp.flush()
                        tmp.close()  # ← Windows fix: close before PyMuPDF reads it
                        tmp_paths.append(tmp.name)

                    chunks = load_and_chunk_pdfs(tmp_paths)
                    vector_store = build_vector_store(chunks)
                    st.session_state.rag_chain = get_rag_chain(vector_store)
                    st.session_state.ready = True
                    st.session_state.chat_history = []
                    st.success(f"✅ Indexed {len(chunks)} chunks! Start chatting →")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    # Always delete temp files even if error occurs
                    for p in tmp_paths:
                        try:
                            os.unlink(p)
                        except Exception:
                            pass

    st.markdown("---")

    # Load existing index
    if os.path.exists(FAISS_INDEX_PATH) and not st.session_state.ready:
        if st.button("📂 Load Previous Index"):
            with st.spinner("Loading saved index..."):
                try:
                    vector_store = load_vector_store()
                    st.session_state.rag_chain = get_rag_chain(vector_store)
                    st.session_state.ready = True
                    st.success("Loaded! Start chatting →")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.ready:
        st.markdown('<div class="status-ready">🟢 Chatbot is Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pending">🟡 Upload & process notes first</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Important Questions & Topics Section
    if st.session_state.ready:
        if st.button("📋 Show Important Questions & Topics"):
            st.info("⏳ Analyzing your notes to find important concepts...")
            try:
                # Extract important questions
                imp_qs_prompt = """Based ONLY on the provided context/notes, generate exactly 5 different important exam-style questions that a student should be able to answer. Make sure each question covers a DIFFERENT topic or concept.

IMPORTANT: 
- Do NOT repeat the same concept in multiple questions
- Make questions diverse and cover different areas
- Each question should test different knowledge

Format your response EXACTLY like this:
1. [First different question about Topic A]?
2. [Second different question about Topic B]?
3. [Third different question about Topic C]?
4. [Fourth different question about Topic D]?
5. [Fifth different question about Topic E]?

Only provide these 5 questions, nothing else."""
                result_qs = ask_question(st.session_state.rag_chain, imp_qs_prompt)
                
                # Extract important topics
                imp_topics_prompt = """Based ONLY on the provided context/notes, list exactly 10 DIFFERENT main topics and concepts that students should study. Make sure each topic is distinct and covers a different concept. Do NOT repeat the same topic.

Format your response EXACTLY like this:
1. First unique topic
2. Second unique topic
3. Third unique topic
4. Fourth unique topic
5. Fifth unique topic
6. Sixth unique topic
7. Seventh unique topic
8. Eighth unique topic
9. Ninth unique topic
10. Tenth unique topic

Only provide these 10 DIFFERENT topics, nothing else."""
                result_topics = ask_question(st.session_state.rag_chain, imp_topics_prompt)
                
                # Extract key definitions
                key_defs_prompt = """Based ONLY on the provided context/notes, provide 5 DIFFERENT key definitions of important terms. Make sure each term and definition is unique. Do NOT repeat the same term.

Format your response EXACTLY like this:
1. Term One: Clear definition of term one
2. Term Two: Clear definition of term two
3. Term Three: Clear definition of term three
4. Term Four: Clear definition of term four
5. Term Five: Clear definition of term five

Only provide these 5 DIFFERENT definitions, nothing else."""
                result_defs = ask_question(st.session_state.rag_chain, key_defs_prompt)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("❓ Important Questions")
                    st.markdown(result_qs["answer"])
                
                with col2:
                    st.subheader("📚 Key Topics")
                    st.markdown(result_topics["answer"])
                
                st.subheader("🔑 Key Definitions")
                st.markdown(result_defs["answer"])
                
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")
    
    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown("1. Upload your PDF notes\n2. Click **Process Notes**\n3. Ask anything from your notes!")

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    st.info("Tip: the app now prefers the free local fallback path by default. Gemini is only used when you explicitly disable the local provider.")


# ── RIGHT PANEL — CHAT ────────────────────────────────────────────────────────
with col2:
    st.markdown("### 💬 Ask From Your Notes")

    # Chat display
    chat_container = st.container(height=480)
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style='text-align:center; color:#94a3b8; margin-top: 80px;'>
                <div style='font-size:3rem;'>🎓</div>
                <div style='font-size:1.1rem; font-weight:500; margin-top:12px;'>Upload your notes and start asking questions!</div>
                <div style='font-size:0.875rem; margin-top:6px;'>Powered by the free local fallback path by default, with Gemini only used when you switch providers.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">🧑‍🎓 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    sources_html = "".join([
                        f'<span class="source-tag">📄 {os.path.basename(s)}</span>'
                        for s in msg.get("sources", [])
                    ])
                    st.markdown(
                        f'<div class="chat-bot">🤖 {msg["content"]}'
                        f'{"<br>" + sources_html if sources_html else ""}</div>',
                        unsafe_allow_html=True
                    )

    # Input
    user_input = st.chat_input("Ask something from your notes...", disabled=not st.session_state.ready)

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            try:
                result = ask_question(st.session_state.rag_chain, user_input)
                st.session_state.chat_history.append({
                    "role": "bot",
                    "content": result["answer"],
                    "sources": result["sources"]
                })
                if result.get("error") == "quota_exhausted":
                    st.warning("Google Gemini free-tier quota is exhausted, so the app is using the local fallback answer from your uploaded notes.")
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "bot",
                    "content": f"❌ Error: {str(e)}",
                    "sources": []
                })
        st.rerun()