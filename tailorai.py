import streamlit as st
import google.generativeai as genai
import datetime
import re

# Configure Gemini API
genai.configure(api_key="AIzaSyB2UAI9PB6qIOI54gVNMX5KVvgoV-RBI1A")
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize user profile info in session state
if "profile" not in st.session_state:
    st.session_state.profile = {
        "height_cm": None,
        "weight_kg": None,
        "age": None,
        "gender": None,
        "fabric": None,
        "fit": None,
        "use_case": None,
        "style": None,
        "brands": []
    }

st.title("🧥 TailorAI Chatbot — Your Clothing Size & Fashion Assistant")

def convert_units(height, unit_h, weight, unit_w):
    if height is None or weight is None:
        return None, None
    height_cm = height * 2.54 if unit_h == "inches" else height
    weight_kg = weight * 0.453592 if unit_w == "lbs" else weight
    return height_cm, weight_kg

def generate_prompt(profile, conversation_history):
    # Compose prompt for Gemini with profile & conversation
    base_prompt = (
        f"A {profile.get('age', '?')}-year-old {profile.get('gender', 'person')} with a height of {profile.get('height_cm', '?')} cm "
        f"and weight of {profile.get('weight_kg', '?')} kg is shopping for {profile.get('fabric', '?')} clothes to wear for {profile.get('use_case', '?')}. "
        f"They prefer a {profile.get('fit', '?')} fit and their style is {profile.get('style', '?')}. "
        f"Preferred brands are: {', '.join(profile.get('brands', [])) or 'not specified'}. "
        f"Suggest the best size (XS–XXL) with explanation.\n"
        "Conversation:\n"
    )
    for msg in conversation_history[-6:]:
        role = msg["role"].capitalize()
        content = msg["content"]
        base_prompt += f"{role}: {content}\n"
    base_prompt += "Assistant:"
    return base_prompt

def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def extract_numbers(text):
    return list(map(float, re.findall(r"\d+\.?\d*", text)))

def extract_info_from_text(text):
    # Simple extraction logic (can be improved with NLP)
    info = {}
    text = text.lower()
    
    # Height
    if "cm" in text:
        nums = extract_numbers(text)
        if nums:
            info["height_cm"] = nums[0]
    elif "inch" in text or "inches" in text:
        nums = extract_numbers(text)
        if nums:
            info["height_cm"] = nums[0] * 2.54
    
    # Weight
    if "kg" in text:
        nums = extract_numbers(text)
        if nums:
            info["weight_kg"] = nums[0]
    elif "lb" in text or "lbs" in text:
        nums = extract_numbers(text)
        if nums:
            info["weight_kg"] = nums[0] * 0.453592

    # Age
    if "year" in text:
        nums = extract_numbers(text)
        if nums:
            info["age"] = int(nums[0])

    # Gender
    for g in ["male", "female", "non-binary"]:
        if g in text:
            info["gender"] = g
            break

    # Fabric
    for f in ["cotton", "polyester", "wool", "linen", "denim", "silk"]:
        if f in text:
            info["fabric"] = f
            break

    # Fit
    for f in ["slim", "regular", "loose"]:
        if f in text:
            info["fit"] = f
            break

    # Use case
    for u in ["casual", "formal", "sports", "party", "office"]:
        if u in text:
            info["use_case"] = u
            break

    # Style
    for s in ["minimal", "streetwear", "formal", "boho", "sporty", "classic"]:
        if s in text:
            info["style"] = s
            break

    # Brands - simple check
    possible_brands = ["h&m", "zara", "nike", "uniqlo", "levi's", "adidas"]
    brands_found = [b for b in possible_brands if b in text]
    if brands_found:
        info["brands"] = brands_found

    return info

def chat_bubble(message, is_user):
    color = "#DCF8C6" if is_user else "#F0F0F0"
    align = "right" if is_user else "left"
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            padding: 10px 15px;
            border-radius: 15px;
            margin: 10px;
            max-width: 70%;
            float: {align};
            clear: both;
            ">
            {message}
        </div>
        """, unsafe_allow_html=True
    )

# Show conversation history
for chat in st.session_state.chat_history:
    chat_bubble(chat["content"], chat["role"]=="user")

# User input box
user_input = st.text_input("💬 Ask TailorAI anything or enter your measurements:")

if user_input:
    # Save user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Extract info from user message to update profile
    new_info = extract_info_from_text(user_input)
    st.session_state.profile.update({k: v for k, v in new_info.items() if v is not None})

    # Check if enough info is present to make a prediction
    profile = st.session_state.profile
    needed_fields = ["height_cm", "weight_kg", "age", "gender", "fabric", "fit", "use_case", "style"]
    missing = [f for f in needed_fields if not profile.get(f)]
    if missing:
        reply = (
            f"I need a bit more info to help you better. Could you please tell me your "
            f"{', '.join(missing)}?"
        )
    else:
        # Generate prompt & get response from Gemini
        prompt = generate_prompt(profile, st.session_state.chat_history)
        reply = get_gemini_response(prompt)

    # Save assistant reply
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Rerun so chat history updates (Streamlit quirk)
    st.experimental_rerun()
