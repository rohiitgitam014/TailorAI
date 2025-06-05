import streamlit as st
import google.generativeai as genai
import datetime

# =============== Gemini Setup ===============
genai.configure(api_key="AIzaSyB2UAI9PB6qIOI54gVNMX5KVvgoV-RBI1A")
model = genai.GenerativeModel("gemini-1.5-flash")  # Use 1.5 flash free tier

# =============== Helper Functions ===============
def convert_units(height, unit_h, weight, unit_w):
    height_cm = height * 2.54 if unit_h == "inches" else height
    weight_kg = weight * 0.453592 if unit_w == "lbs" else weight
    return round(height_cm, 1), round(weight_kg, 1)

def generate_prompt(height, weight, gender, age, fabric, fit, use_case, style, brands, language):
    base_prompt = (
        f"{age}-year-old {gender}, {height} cm tall, {weight} kg, "
        f"shopping for {fabric} clothes for {use_case}, prefers {fit} fit, style {style}. "
        f"Favorite brands: {', '.join(brands)}. Suggest best size XS–XXL briefly."
    )
    if language == "Hindi":
        base_prompt += " जवाब हिंदी में दें।"
    return base_prompt

def get_size_from_gemini(prompt):
    try:
        response = model.generate_content(prompt, max_tokens=50)  # limit tokens for free tier
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# =============== Streamlit UI ===============
st.set_page_config(page_title="AI Cloth Size Predictor (Flash)", page_icon="🧥")
st.title("🧥 AI Clothing Size Predictor (Gemini 1.5 Flash)")

language = st.selectbox("🌐 Choose Language", ["English", "Hindi"])

hour = datetime.datetime.now().hour
greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
st.markdown(f"👋 {greet}! Let's find your ideal clothing size.")

unit_h = st.radio("Height Unit", ["cm", "inches"], horizontal=True)
unit_w = st.radio("Weight Unit", ["kg", "lbs"], horizontal=True)

height = st.number_input("Height", min_value=50.0, max_value=250.0, value=170.0)
weight = st.number_input("Weight", min_value=20.0, max_value=200.0, value=70.0)
age = st.slider("Age", 10, 100, 25)
gender = st.selectbox("Gender", ["male", "female", "non-binary", "prefer not to say"])

fabric = st.selectbox("Fabric Type", ["cotton", "polyester", "wool", "linen", "denim", "silk", "other"])
fit = st.selectbox("Fit Preference", ["slim", "regular", "loose"])
use_case = st.selectbox("Use Case", ["casual", "formal", "sports", "party", "office", "other"])
style = st.selectbox("Style", ["Minimal", "Streetwear", "Formal", "Boho", "Sporty", "Classic"])
brands = st.multiselect("Favorite Brands", ["H&M", "Zara", "Nike", "Uniqlo", "Levi's", "Adidas"])

if st.button("🎯 Predict My Size"):
    height_cm, weight_kg = convert_units(height, unit_h, weight, unit_w)
    prompt = generate_prompt(height_cm, weight_kg, gender, age, fabric, fit, use_case, style, brands, language)

    with st.spinner("Gemini 1.5 Flash generating your size..."):
        result = get_size_from_gemini(prompt)

    st.success("✅ Size Recommendation")
    st.write(result)
