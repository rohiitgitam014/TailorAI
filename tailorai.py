import streamlit as st
import google.generativeai as genai
import datetime

# Configure Gemini API
genai.configure(api_key="AIzaSyB2UAI9PB6qIOI54gVNMX5KVvgoV-RBI1A")
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "height_cm": None,
        "weight_kg": None,
        "gender": None,
        "age": None
    }

st.set_page_config(page_title="TailorAI Chatbot", page_icon="🧵", layout="wide")

# Sidebar: Get user profile info once for personalized responses
with st.sidebar:
    st.header("🧍 Your Profile (Optional)")
    st.session_state.user_profile["height_cm"] = st.number_input(
        "Height (cm)", min_value=50, max_value=250, value=170
    )
    st.session_state.user_profile["weight_kg"] = st.number_input(
        "Weight (kg)", min_value=20, max_value=200, value=70
    )
    st.session_state.user_profile["gender"] = st.selectbox(
        "Gender", ["male", "female", "non-binary", "prefer not to say"]
    )
    st.session_state.user_profile["age"] = st.slider("Age", 10, 100, 25)
    if st.button("Clear Chat"):
        st.session_state.chat_history = []

st.title("🧵 TailorAI Chatbot — Your Personal Clothing Size Assistant")

if not st.session_state.chat_history:
    # Welcome message from TailorAI
    welcome_msg = (
        "Hello! 👋 I'm TailorAI, your personal assistant to help find the perfect clothing size "
        "and give fashion advice. You can tell me your measurements or just ask questions!"
    )
    st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})

def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# User input text box with placeholder
user_input = st.text_input("💬 Type your question or measurement details here:", placeholder="E.g. What size fits me if I am 170 cm and 70 kg?")

if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Include user profile info in prompt if available for personalized replies
    profile = st.session_state.user_profile
    profile_text = (
        f"User profile: Height {profile['height_cm']} cm, Weight {profile['weight_kg']} kg, "
        f"Gender {profile['gender']}, Age {profile['age']}.\n" if all(profile.values()) else ""
    )

    # Prepare prompt with recent conversation and user profile
    conversation = "\n".join(
        f"{chat['role'].capitalize()}: {chat['content']}" for chat in st.session_state.chat_history[-6:]
    )
    prompt = (
        f"You are TailorAI, a helpful, friendly assistant specialized in clothing size recommendations and fashion advice. "
        f"{profile_text}Conversation:\n{conversation}\nTailorAI:"
    )

    # Get AI response
    reply = get_gemini_response(prompt)
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# Display chat messages in chat bubble style with timestamps
def chat_bubble(message, is_user):
    bubble_color = "#DCF8C6" if is_user else "#E1E1E1"
    align = "right" if is_user else "left"
    time_str = datetime.datetime.now().strftime("%H:%M")
    st.markdown(
        f"""
        <div style='
            background-color: {bubble_color};
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px;
            max-width: 70%;
            text-align: {align};
            float: {align};
            clear: both;
            '>
            <p style='margin:0;'>{message}</p>
            <small style='color: gray;'>{time_str}</small>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

for chat in st.session_state.chat_history:
    chat_bubble(chat["content"], chat["role"] == "user")

# Scroll to the bottom when new messages arrive (works in newer Streamlit versions)
st.markdown(
    """
    <script>
    const chatContainer = window.parent.document.querySelector('section.main > div');
    if(chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    </script>
    """,
    unsafe_allow_html=True,
)
