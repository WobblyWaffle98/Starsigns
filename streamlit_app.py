import streamlit as st
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch  # type: ignore

# Initialize Google Gemini Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])  # Use Streamlit secrets for safety
model_id = "gemini-2.0-flash"

# Define the tool
google_search_tool = Tool(google_search=GoogleSearch())

# Streamlit page setup
st.set_page_config(page_title="Star Signs", layout="wide")
st.title("Star Signs 🌟")

# Define a reusable function for model calls
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

# Define prompts
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
    "such as the United States, Saudi Arabia, Russia, and China. Mention any recent policy decisions, geopolitical developments. "
    "Do not include any updates on numerical price movements. Cite the sources and dates of any forecasts or revisions."
)

# Layout with two columns
col1, col2 = st.columns(2)

# Column 1: Macroeconomy
with col1:
    st.header("Macroeconomy")
    with st.chat_message("Macro-Bot", avatar="🌍"):
        st.write("Hello Humans 👋, I am Macro Bot")
        if st.button("Fetch Macro Update", key="macro"):
            with st.spinner("Fetching the latest macroeconomic data..."):
                st.write(get_response(macro_prompt))

# Column 2: Fundamentals
with col2:
    st.header("Fundamentals")
    with st.chat_message("Fundamental-Bot", avatar="🛢️"):
        st.write("Hello Humans 👋, I am Fundamental Bot")
        if st.button("Fetch Oil Market Update", key="fundamentals"):
            with st.spinner("Fetching the latest oil market fundamentals..."):
                st.write(get_response(fundamentals_prompt))
