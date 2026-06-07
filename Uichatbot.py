from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoodBot",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Mood config ───────────────────────────────────────────────────────────────
MOODS = {
    "angry": {
        "label": "😡 Angry",
        "system": "You are an angry AI agent. You respond aggressively and impatiently.",
        "color": "#FF4444",
        "glow": "rgba(255,68,68,0.35)",
        "bg": "rgba(255,68,68,0.08)",
        "border": "rgba(255,68,68,0.4)",
        "gradient": "linear-gradient(135deg, #3a0a0a 0%, #1a0505 100%)",
        "tag": "RAGE MODE",
    },
    "funny": {
        "label": "😂 Funny",
        "system": "You are a very funny AI agent. You respond with humor and jokes.",
        "color": "#FFD700",
        "glow": "rgba(255,215,0,0.35)",
        "bg": "rgba(255,215,0,0.08)",
        "border": "rgba(255,215,0,0.4)",
        "gradient": "linear-gradient(135deg, #1a1400 0%, #0d0d00 100%)",
        "tag": "LAUGH MODE",
    },
    "sad": {
        "label": "😢 Sad",
        "system": "You are a very sad AI agent. You respond in a depressed and emotional tone.",
        "color": "#4488FF",
        "glow": "rgba(68,136,255,0.35)",
        "bg": "rgba(68,136,255,0.08)",
        "border": "rgba(68,136,255,0.4)",
        "gradient": "linear-gradient(135deg, #000a1a 0%, #00050d 100%)",
        "tag": "MELANCHOLY MODE",
    },
}

# ── Session state ─────────────────────────────────────────────────────────────
if "mood" not in st.session_state:
    st.session_state.mood = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []   # list of (role, text)

# ── CSS ───────────────────────────────────────────────────────────────────────
def get_css(mood_key):
    m = MOODS[mood_key] if mood_key else MOODS["funny"]
    c = m["color"]
    glow = m["glow"]
    bg = m["bg"]
    border = m["border"]
    grad = m["gradient"] if mood_key else "linear-gradient(135deg, #0d0d0d 0%, #050505 100%)"
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {{
    background: {grad} !important;
    min-height: 100vh;
    font-family: 'Rajdhani', sans-serif;
}}
[data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 40% at 50% 0%, {glow} 0%, transparent 70%),
        radial-gradient(ellipse 40% 60% at 100% 100%, {glow} 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}}
[data-testid="stMain"] {{ background: transparent !important; position: relative; z-index: 1; }}
[data-testid="stHeader"] {{ display: none; }}
.block-container {{ padding: 2rem 1.5rem 6rem !important; max-width: 760px !important; }}
* {{ box-sizing: border-box; }}

/* ── Typography ── */
h1, h2, h3 {{ font-family: 'Orbitron', monospace !important; }}

/* ── Title ── */
.mood-title {{
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem;
    font-weight: 900;
    color: {c};
    text-shadow: 0 0 30px {glow}, 0 0 60px {glow};
    letter-spacing: 0.12em;
    text-align: center;
    margin-bottom: 0.2rem;
    animation: titlePulse 3s ease-in-out infinite;
}}
@keyframes titlePulse {{
    0%, 100% {{ text-shadow: 0 0 20px {glow}, 0 0 40px {glow}; }}
    50% {{ text-shadow: 0 0 40px {glow}, 0 0 80px {glow}, 0 0 120px {glow}; }}
}}
.mood-tag {{
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.35em;
    color: {c};
    opacity: 0.6;
    text-align: center;
    margin-bottom: 2rem;
}}

/* ── Mood selector cards ── */
.mood-card-row {{
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin: 2rem 0;
}}

/* ── Chat bubble container ── */
.chat-wrapper {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}}
.bubble-user {{
    align-self: flex-end;
    background: {bg};
    border: 1px solid {border};
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.1rem;
    max-width: 80%;
    color: #000000;
    font-size: 1rem;
    line-height: 1.5;
    box-shadow: 0 0 12px {glow};
}}
.bubble-bot {{
    align-self: flex-start;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem;
    max-width: 80%;
    color: #d0d0d0;
    font-size: 1rem;
    line-height: 1.5;
}}
.bubble-label {{
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    margin-bottom: 0.35rem;
    opacity: 0.55;
    font-family: 'Orbitron', monospace;
}}
.label-user {{ color: {c}; text-align: right; }}
.label-bot  {{ color: #888; }}

/* ── Input area ── */
[data-testid="stChatInput"] textarea {{
    background: rgba(0,255,255,0.05) !important;
    border: 1px solid {border} !important;
    border-radius: 12px !important;
    color: black !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    box-shadow: 0 0 18px {glow} !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    box-shadow: 0 0 28px {glow}, 0 0 50px {glow} !important;
}}
[data-testid="stChatInputSubmitButton"] svg {{ stroke: {c} !important; }}

/* ── Streamlit buttons ── */
.stButton > button {{
    background: transparent !important;
    border: 1.5px solid {border} !important;
    color: {c} !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    background: {bg} !important;
    box-shadow: 0 0 20px {glow} !important;
    transform: translateY(-1px) !important;
}}

/* ── Divider ── */
hr {{ border-color: {border} !important; margin: 1.5rem 0 !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 2px; }}

/* ── Spinner ── */
[data-testid="stSpinner"] {{ color: {c} !important; }}

/* ── Info / warning ── */
[data-testid="stAlert"] {{
    background: {bg} !important;
    border-left-color: {c} !important;
    color: #ccc !important;
    font-family: 'Rajdhani', sans-serif !important;
}}
</style>
"""

# ── Render CSS ────────────────────────────────────────────────────────────────
st.markdown(get_css(st.session_state.mood), unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="mood-title">🎭 MOODBOT</div>', unsafe_allow_html=True)
if st.session_state.mood:
    st.markdown(f'<div class="mood-tag">{MOODS[st.session_state.mood]["tag"]} • MISTRAL AI</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="mood-tag">SELECT YOUR MOOD TO BEGIN</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Mood selection ─────────────────────────────────────────────────────────────
if not st.session_state.mood:
    st.markdown("### Choose Your AI Mood")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("😡 ANGRY", key="btn_angry"):
            st.session_state.mood = "angry"
            st.session_state.messages = [SystemMessage(content=MOODS["angry"]["system"])]
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        if st.button("😂 FUNNY", key="btn_funny"):
            st.session_state.mood = "funny"
            st.session_state.messages = [SystemMessage(content=MOODS["funny"]["system"])]
            st.session_state.chat_history = []
            st.rerun()
    with col3:
        if st.button("😢 SAD", key="btn_sad"):
            st.session_state.mood = "sad"
            st.session_state.messages = [SystemMessage(content=MOODS["sad"]["system"])]
            st.session_state.chat_history = []
            st.rerun()

# ── Chat UI ───────────────────────────────────────────────────────────────────
else:
    m = MOODS[st.session_state.mood]

    # Change mood button
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("↩ Change Mood"):
            st.session_state.mood = None
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()

    # Render chat history
    if st.session_state.chat_history:
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        for role, text in st.session_state.chat_history:
            if role == "user":
                st.markdown(
                    f'<div class="bubble-user"><div class="bubble-label label-user">YOU</div>{text}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="bubble-bot"><div class="bubble-label label-bot">{m["label"].upper()} BOT</div>{text}</div>',
                    unsafe_allow_html=True
                )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"You're now in **{m['label']}** mode. Say something!")

    # Input
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Append to LangChain messages
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner("Thinking..."):
            model = ChatMistralAI(model="mistral-small-2506", temperature=0.9)
            response = model.invoke(st.session_state.messages)

        st.session_state.messages.append(AIMessage(content=response.content))
        st.session_state.chat_history.append(("bot", response.content))
        st.rerun()
