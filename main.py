import streamlit as st
import json
import base64
from openai import OpenAI

# === Background Image Function ===
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load and encode local background image
bg_image_base64 = get_base64_image("bg1.jpg")  # Update with your image filename

# === Set Streamlit Page Config ===
st.set_page_config(
    page_title="🩹 First Aid Advisor",
    layout="centered",
    initial_sidebar_state="expanded"
)

# === Inject Background Image and Bold Styling ===
st.markdown(f"""
    <style>
    html, body {{
        background-image: url("data:image/jpg;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    .stApp {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 1rem;
    }}

    /* Bold all visible text */
    h1, h2, h3, h4, h5, h6, label, p, div, span {{
        font-weight: bold !important;
    }}
    </style>
""", unsafe_allow_html=True)

# === UI ===
st.title("🩹 First Aid Advisor")
st.markdown("---")
st.markdown("### Describe your situation and get guidance from official medical sources **and** AI.")
st.markdown("---")

# === Form ===
with st.form("first_aid_form"):
    openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

    user_input = st.text_area(
        "What's happening?",
        placeholder="e.g., I cut my finger and it's bleeding.",
        height=100,
        help="Describe your medical situation in detail"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.form_submit_button("🚑 Get Advice", use_container_width=True)

# === Stop if API key is missing ===
if submit_button and not openai_api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

# === Init OpenAI client ===
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)

# === Load First Aid Guidelines ===
@st.cache_data
def load_guidelines():
    with open("first_aid_data.json", "r") as f:
        return json.load(f)

guidelines = load_guidelines()

# === First Aid Matching ===
def get_guideline_response(text):
    text_lower = text.lower()
    for condition, data in guidelines.items():
        if any(kw in text_lower for kw in data["keywords"]):
            steps = [f"{i+1}. {step}" for i, step in enumerate(data["steps"])]
            return "\n\n".join(steps)
    return "❗ Sorry, I couldn't find specific first aid steps for this situation. Please seek help."

# === OpenAI Advice ===
def get_openai_response(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a certified first aid assistant providing accurate and concise first aid advice."},
                {"role": "user", "content": f"Someone says: '{text}'. What are the step-by-step first aid instructions?"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI Error: {e}"

# === Handle Submission ===
if submit_button:
    if not user_input.strip():
        st.warning("Please describe the situation.")
    else:
        st.markdown("---")
        st.subheader("📘 WHO/Red Cross Guidelines")
        with st.spinner("Analyzing..."):
            who_steps = get_guideline_response(user_input)
            st.success(f"**{who_steps}**")

        st.markdown("---")
        st.subheader("🤖 AI Advice (OpenAI)")
        with st.spinner("Contacting OpenAI..."):
            ai_steps = get_openai_response(user_input)
            st.info(f"**{ai_steps}**")

# === Disclaimer ===
st.markdown("---")
st.markdown("⚠️ *This tool is for informational purposes only. In case of emergency, call your local emergency number.*")
