import streamlit as st
from datetime import datetime, timedelta
import ollama


# Page config

st.set_page_config(
    page_title="ChatBot",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS for chat bubbles

st.markdown(
    """
    <style>
    /* chat container spacing */
    .chat-container { display: flex; flex-direction: column; gap: 12px; padding: 8px 12px; }

    /* one row for each message */
    .msg-row { display: flex; width: 100%; }

    /* bubble base */
    .msg {
        max-width: 70%;
        padding: 10px 14px;
        border-radius: 12px;
        word-wrap: break-word;
        white-space: pre-wrap;
        font-family: "Helvetica", "Arial", sans-serif;
        line-height: 1.4;
        box-shadow: 0 1px 0 rgba(0,0,0,0.04);
    }

    /* user bubble (right) */
    .msg.user {
        margin-left: auto;
        background: grey;
        text-align: right;
        border-radius: 12px 12px 6px 12px;
    }

    /* assistant bubble (left) */
    .msg.assistant {
        margin-right: auto;
        background: grey;
        text-align: left;
        border-radius: 12px 12px 12px 6px;
        border: 1px solid #e6e6e6;
    }

    /* optional small timestamp or meta */
    .msg-meta { font-size: 11px; color: #6b6b6b; margin-bottom: 6px; }

    /* keep the sidebar logo compact */
    .logo-title img { width: 40px; margin-right: 8px; vertical-align: middle; }
    .logo-title { margin-bottom: 18px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# Helper to render a message using HTML

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
        <div class="msg {role}">
          {safe}
        </div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# Ollama reply (full conversation)

def get_ollama_reply(messages, model="phi3"):
    """
    Send the entire conversation (messages list) to Ollama and return the assistant reply.
    """
    try:
        response = ollama.chat(
            model=model,
            messages=messages
        )
        return response['message']['content']
    except Exception as e:
        # Return a readable error message inside the chat so UI doesn't break
        return f"⚠️ Ollama error: {e}"


# Chat management functions

def search_chats(query):
    results = []
    q = query.strip().lower()
    for chat_id, chat_data in st.session_state.chat_history.items():
        if q in chat_data["title"].lower():
            results.append((chat_id, chat_data))
            continue
        for message in chat_data["messages"]:
            if q in message["content"].lower():
                results.append((chat_id, chat_data))
                break
    return results

def reset_session_state():
    st.session_state.chat_history = {}
    st.session_state.current_chat_id = None
    st.session_state.messages = []

def create_new_chat():
    # Reuse an empty existing chat if present
    for chat_id, chat_data in st.session_state.chat_history.items():
        if not chat_data["messages"]:
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = []
            return chat_id

    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chat_history[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now()
    }
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
        if created_at >= today:
            categories["Today"].append((chat_id, chat_data))
        elif created_at >= yesterday:
            categories["Yesterday"].append((chat_id, chat_data))
        elif created_at >= week_start:
            categories["This Week"].append((chat_id, chat_data))
        elif created_at >= last_week_start:
            categories["Last Week"].append((chat_id, chat_data))
        else:
            categories["Older"].append((chat_id, chat_data))

    for category in categories.values():
        category.sort(key=lambda x: x[1].get('created_at', now), reverse=True)

    return categories


# Initialize session state

if 'chat_history' not in st.session_state:
    reset_session_state()
    create_new_chat()
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_search' not in st.session_state:
    st.session_state.show_search = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""


# Sidebar: logo, new chat, search, history

with st.sidebar:
    st.markdown(
        """
        <div class="logo-title">
            <img src="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg">
            <h2>ChatBot</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # New chat & toggle search
    col1, col2 = st.columns([5, 1])
    with col1:
        if st.button("+ New chat", use_container_width=True, key="new_chat_btn"):
            create_new_chat()
            st.rerun()
    with col2:
        if st.button("🔍", key="search_btn", help="Search in chat history"):
            st.session_state.show_search = True
            st.rerun()

    # Search interface
    if st.session_state.show_search:
        search_query = st.text_input("Search chats", value=st.session_state.search_query, key="search_input")
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            st.rerun()

        if search_query:
            search_results = search_chats(search_query)
            if search_results:
                st.markdown("### Search Results")
                for chat_id, chat_data in search_results:
                    is_active = chat_id == st.session_state.current_chat_id
                    if st.button(chat_data["title"], key=f"search_{chat_id}", use_container_width=True, disabled=is_active):
                        st.session_state.current_chat_id = chat_id
                        st.session_state.messages = chat_data["messages"]
                        st.rerun()
            else:
                st.info("No results found")

        if st.button("Clear Search", key="clear_search"):
            st.session_state.show_search = False
            st.session_state.search_query = ""
            st.rerun()

    # Show categorized chat history when not searching
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
    # Sidebar utilities
    if st.button("Clear Current Chat", key="clear_current"):
        if st.session_state.current_chat_id:
            st.session_state.chat_history[st.session_state.current_chat_id]["messages"] = []
            st.session_state.messages = []
            st.rerun()

    if st.button("Clear All History", key="clear_all"):
        reset_session_state()
        create_new_chat()
        st.rerun()


# Main chat area

if st.session_state.current_chat_id is None:
    st.markdown("# What can I help with?")
else:
    # Render stored messages for the current chat
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        if role not in ("user", "assistant"):
            role = "assistant" if role == "system" else role
        render_message(role, message["content"])

    # Chat input
    if prompt := st.chat_input("Message ChatBot"):
        # Add user message to local session messages
        st.session_state.messages.append({"role": "user", "content": prompt})
        render_message("user", prompt)

        # Get assistant reply (send full conversation history)
        with st.spinner("ai assistant is thinking..."):
            reply = get_ollama_reply(st.session_state.messages, model="phi3")

        # Add assistant reply to local session messages and render
        st.session_state.messages.append({"role": "assistant", "content": reply})
        render_message("assistant", reply)

        # Save to chat history
        current_chat_id = st.session_state.current_chat_id
        if current_chat_id:
            st.session_state.chat_history[current_chat_id]["messages"] = st.session_state.messages
            # Update title if it's still "New Chat"
            if st.session_state.chat_history[current_chat_id]["title"] == "New Chat":
                update_chat_title(current_chat_id, st.session_state.messages)
