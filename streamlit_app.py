import streamlit as st
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch # type: ignore

client = genai.Client(api_key="AIzaSyA0jZkj5buSGm6AXtXlo6CEeFS1f8q0KSg")
model_id = "gemini-2.0-flash"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

st.set_page_config(layout="wide")

# User interface
st.title("Star Signs 🌟")

# Create two columns
col1, col2 = st.columns(2)

# Add headers to each column
with col1:
    st.header("Macroeconomy")
    with st.chat_message("Macro-Bot", avatar="🌍"):
        st.write("Hello Humans👋, I am Macro Bot")
        user_query = (
        "Provide the latest economic outlook for the global economy from reputable sources, "
        "with a specific focus on the United States and China. Include recent data or revisions "
        "related to key macroeconomic indicators such as inflation, GDP growth, labor market conditions, "
        "unemployment rates, international trade, and consumer sentiment. Mention the source and date "
        "of any forecast or revision cited."
    )


        # Call the model with tools
        response = client.models.generate_content(
            model=model_id,
            contents=user_query,
            config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )
        # Display results
        for part in response.candidates[0].content.parts:
            st.write(part.text)

with col2:
    st.header("Fundamentals")
    # Add more content for Fundamentals here
    with st.chat_message("Fundamental-Bot", avatar="🛢️"):
        st.write("Hello Humans👋, I am Fundamental Bot")
        user_query = (
        "Provide the latest outlook on the crude oil market from reputable sources, "
        "focusing on key fundamentals such as global supply-demand balances, inventory levels, and production forecasts. "
        "Include updates or commentary on OPEC and its allies (OPEC+), as well as major oil-producing and consuming countries "
        "such as the United States, Saudi Arabia, Russia, and China. Mention any recent policy decisions, geopolitical developments, "
        "Do not include any updates on numerical price movements. Cite the sources and dates of any forecasts or revisions."
    )

        # Call the model with tools
        response = client.models.generate_content(
            model=model_id,
            contents=user_query,
            config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )
        # Display results
        for part in response.candidates[0].content.parts:
            st.write(part.text)

