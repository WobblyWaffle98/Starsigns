import streamlit as st
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch  # type: ignore

# Initialize Google Gemini Client
client = genai.Client(api_key="AIzaSyA0jZkj5buSGm6AXtXlo6CEeFS1f8q0KSg")  # Use Streamlit secrets for safety
model_id = "gemini-2.0-flash"
google_search_tool = Tool(google_search=GoogleSearch())

# Streamlit page setup
st.set_page_config(
    page_title="Stellar Feed",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styling for dark cosmic theme
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #0b0f1a;
        color: #e0e6f0;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #1f2c4c;
        color: white;
        border: 1px solid #3f4c6b;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #2a3b5f;
    }
    .chat-message {
        background-color: #1a1f2e;
        padding: 1rem;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Branding
st.title("🌟 Stellar Feed")
st.caption("🚀 Signals from the Future, Curated by AI")

# Define reusable function
def get_response(prompt: str) -> str:
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    return "\n".join([part.text for part in response.candidates[0].content.parts])

# Prompts
top_news_prompt = (
    "What's the top global news today regarding Politics and International Relations, "
    "Economics and Finance?"
)

macro_prompt = (
    "Provide the latest economic outlook for the global economy from reputable sources, "
    "with a specific focus on the United States and China. Include recent data or revisions "
    "related to key macroeconomic indicators such as inflation, GDP growth, labor market conditions, "
    "unemployment rates, international trade, and consumer sentiment. Mention the source and date "
    "of any forecast or revision cited."
)

fundamentals_prompt = (
    "Provide the latest outlook on the crude oil market from reputable sources, "
    "focusing on key fundamentals such as global supply-demand balances, inventory levels, and production forecasts. "
    "Include updates or commentary on OPEC and its allies (OPEC+), as well as major oil-producing and consuming countries "
    "such as the United States, Saudi Arabia, Russia, and China. Mention any recent policy decisions or geopolitical developments. "
    "Do not include any updates on numerical price movements. Cite the sources and dates of any forecasts or revisions."
)



# Display news content
st.subheader("🌐 Top Global News")
with st.spinner("Fetching top news..."):
    st.write(get_response(top_news_prompt))

# Content Layout
col1, col2 = st.columns(2)

# Column 1: Macro
with col1:
    st.header("📊 Macroeconomy")
    with st.chat_message("Macro-Bot", avatar="🌍"):
        st.markdown("**Hello, I'm Macro Bot. Here's the latest on global economics.**")
        with st.spinner("Retrieving macroeconomic data..."):
            st.write(get_response(macro_prompt))

# Column 2: Fundamentals
with col2:
    st.header("🛢️ Oil Market Fundamentals")
    with st.chat_message("Fundamental-Bot", avatar="🛢️"):
        st.markdown("**Hi, I'm Fundamental Bot. Here's your oil market insight.**")
        with st.spinner("Fetching oil fundamentals..."):
            st.write(get_response(fundamentals_prompt))

# Refresh button at the bottom
st.markdown("---")
if st.button("🔄 Refresh All Feeds"):
    st.experimental_rerun()
