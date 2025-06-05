import streamlit as st
import google.generativeai as genai
from datetime import datetime

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyB2UAI9PB6qIOI54gVNMX5KVvgoV-RBI1A")  # Replace with your Gemini API Key
model = genai.GenerativeModel("gemini-pro")

# --- Page Config ---
st.set_page_config(page_title="TailorAI Chatbot", layout="centered")

st.title("🧵 TailorAI Chatbot — Your Personal Clothing Size Assistant")

# --- Initialize chat history ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Display chat history (top) ---
for chat in st.session_state.chat_history:
    is_user = chat["role"] == "user"
    align = "right" if is_user else "left"
    bubble_color = "#DCF8C6" if is_user else "#F1F0F0"
    st.markdown(
        f"""
        <div style="background-color: {bubble_color}; padding: 10px 15px;
                    border-radius: 15px; margin: 5px 0; max-width: 75%;
                    float: {align}; clear: both; font-size: 16px;">
            {chat["content"]}
            <div style="text-align: right; font-size: 12px; color: gray;">
                {chat["timestamp"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# --- Input form (bottom) ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your question or measurement details here:")
    submitted = st.form_submit_button("Send")

# --- Get Gemini response ---
def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- Handle user input ---
if submitted and user_input:
    timestamp = datetime.now().strftime("%H:%M")

    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })

    # Build prompt for Gemini with context
    last_messages = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history[-5:]
    )
    prompt = f"You are TailorAI, a fashion and clothing size expert chatbot.\n{last_messages}\nAssistant:"

    # Get Gemini's reply
    reply_text = get_gemini_response(prompt)

    # Add AI response to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": reply_text,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    # Rerun to update chat view
    st.experimental_rerun()

