import streamlit as st
from datetime import datetime, timedelta
import ollama
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

# -------------------- OCR FUNCTIONS --------------------
def ocr_from_image(uploaded_image):
    image = Image.open(uploaded_image)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    text = pytesseract.image_to_string(image)
    return text.strip()

def ocr_from_pdf(uploaded_pdf):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="ChatBot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CSS --------------------
st.markdown("""
<style>
.chat-container { display: flex; flex-direction: column; gap: 12px; padding: 8px 12px; }
.msg-row { display: flex; width: 100%; }
.msg {
    max-width: 70%; padding: 10px 14px; border-radius: 12px; word-wrap: break-word;
    white-space: pre-wrap; font-family: "Helvetica", "Arial", sans-serif; line-height: 1.4;
    box-shadow: 0 1px 0 rgba(0,0,0,0.04);
}
.msg.user { margin-left: auto; text-align: right; border-radius: 12px 12px 6px 12px; color:white; border: 1px solid #e6e6e6;}
.msg.assistant { margin-right: auto; text-align: left; border-radius: 12px 12px 12px 6px; border: 1px solid #e6e6e6; }
.logo-title img { width: 40px; margin-right: 8px; vertical-align: middle; }
.logo-title { margin-bottom: 18px; }
</style>
""", unsafe_allow_html=True)

# -------------------- HELPER FUNCTIONS --------------------
def render_message(role: str, content: str):
    safe = (
        content.replace("&", "&amp;")
               .replace("<", "&lt;")
               .replace(">", "&gt;")
               .replace("\n", "<br>")
    )
    html = f"""
    <div class="chat-container">
      <div class="msg-row">
        <div class="msg {role}">{safe}</div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def get_ollama_reply(messages, model="phi3"):
    try:
        response = ollama.chat(model=model, messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Ollama error: {e}"

def reset_session_state():
    st.session_state.chat_history = {}
    st.session_state.current_chat_id = None
    st.session_state.messages = []

def create_new_chat():
    for chat_id, chat_data in st.session_state.chat_history.items():
        if not chat_data["messages"]:
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = []
            return chat_id
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_history[chat_id] = {"title": "New Chat", "messages": [], "created_at": datetime.now()}
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    return chat_id

def update_chat_title(chat_id, messages):
    if messages:
        for message in messages:
            if message["role"] == "user":
                title = message["content"][:30] + "..." if len(message["content"]) > 30 else message["content"]
                st.session_state.chat_history[chat_id]["title"] = title
                break

def get_categorized_chats():
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)
    categories = {"Today": [], "Yesterday": [], "This Week": [], "Last Week": [], "Older": []}
    for chat_id, chat_data in st.session_state.chat_history.items():
        created_at = chat_data.get("created_at", now)
        if created_at >= today: categories["Today"].append((chat_id, chat_data))
        elif created_at >= yesterday: categories["Yesterday"].append((chat_id, chat_data))
        elif created_at >= week_start: categories["This Week"].append((chat_id, chat_data))
        elif created_at >= last_week_start: categories["Last Week"].append((chat_id, chat_data))
        else: categories["Older"].append((chat_id, chat_data))
    for category in categories.values(): category.sort(key=lambda x: x[1].get('created_at', now), reverse=True)
    return categories

# -------------------- INITIALIZE SESSION --------------------
if 'chat_history' not in st.session_state: reset_session_state(); create_new_chat()
if 'current_chat_id' not in st.session_state: st.session_state.current_chat_id = None
if 'messages' not in st.session_state: st.session_state.messages = []
if 'show_search' not in st.session_state: st.session_state.show_search = False
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("""
    <div class="logo-title">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg">
        <h2>ChatBot</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([5,1])
    with col1:
        if st.button("+ New chat", use_container_width=True, key="new_chat_btn"):
            create_new_chat(); st.rerun()
    with col2:
        if st.button("🔍", key="search_btn", help="Search in chat history"):
            st.session_state.show_search = True; st.rerun()

    if st.session_state.show_search:
        search_query = st.text_input("Search chats", value=st.session_state.search_query, key="search_input")
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query; st.rerun()
        if search_query:
            results = []
            q = search_query.strip().lower()
            for chat_id, chat_data in st.session_state.chat_history.items():
                if q in chat_data["title"].lower() or any(q in msg["content"].lower() for msg in chat_data["messages"]):
                    results.append((chat_id, chat_data))
            if results:
                st.markdown("### Search Results")
                for chat_id, chat_data in results:
                    is_active = chat_id == st.session_state.current_chat_id
                    if st.button(chat_data["title"], key=f"search_{chat_id}", use_container_width=True, disabled=is_active):
                        st.session_state.current_chat_id = chat_id; st.session_state.messages = chat_data["messages"]; st.rerun()
            else:
                st.info("No results found")
        if st.button("Clear Search", key="clear_search"):
            st.session_state.show_search = False; st.session_state.search_query = ""; st.rerun()
    if not st.session_state.show_search:
        categories = get_categorized_chats()
        for category, chats in categories.items():
            if chats:
                st.markdown(f"### {category}")
                for chat_id, chat_data in chats:
                    title = chat_data["title"]
                    is_active = chat_id == st.session_state.current_chat_id
                    if st.button(title, key=f"chat_{chat_id}", use_container_width=True, disabled=is_active):
                        st.session_state.current_chat_id = chat_id
                        st.session_state.messages = chat_data["messages"]
                        st.rerun()
    st.write("---")
    if st.button("Clear Current Chat", key="clear_current"):
        if st.session_state.current_chat_id:
            st.session_state.chat_history[st.session_state.current_chat_id]["messages"] = []
            st.session_state.messages = []
            st.rerun()
    if st.button("Clear All History", key="clear_all"):
        reset_session_state(); create_new_chat(); st.rerun()

# -------------------- MAIN CHAT AREA --------------------
if st.session_state.current_chat_id is None:
    st.markdown("# What can I help with?")
else:
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        if role not in ("user", "assistant"): role = "assistant" if role=="system" else role
        render_message(role, message["content"])

    # -------------------- CHAT INPUT (NEW STYLE) --------------------
    user_input = st.chat_input(
        "Message ChatBot or attach a file",
        accept_file=True,
        file_type=["png","jpg","jpeg","pdf"]
    )

    if user_input:
        # Handle text
        if user_input.text:
            st.session_state.messages.append({"role": "user", "content": user_input.text})
            render_message("user", user_input.text)

        # Handle uploaded files
        if user_input["files"]:
            for f in user_input["files"]:
                if f.type == "application/pdf":
                    text = ocr_from_pdf(f)
                else:
                    text = ocr_from_image(f)
                st.session_state.messages.append({"role": "user", "content": text})
                render_message("user", text)

        # Get assistant reply
        with st.spinner("ai assistant is thinking..."):
            reply = get_ollama_reply(st.session_state.messages, model="phi3")
        st.session_state.messages.append({"role": "assistant", "content": reply})
        render_message("assistant", reply)

        # Save to chat history
        current_chat_id = st.session_state.current_chat_id
        if current_chat_id:
            st.session_state.chat_history[current_chat_id]["messages"] = st.session_state.messages
            if st.session_state.chat_history[current_chat_id]["title"] == "New Chat":
                update_chat_title(current_chat_id, st.session_state.messages)
