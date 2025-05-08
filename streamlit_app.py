import streamlit as st
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch # type: ignore

client = genai.Client(api_key="AIzaSyA0jZkj5buSGm6AXtXlo6CEeFS1f8q0KSg")
model_id = "gemini-2.0-flash"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

# User interface
st.title("Star Signs 🌟")
news_type = st.selectbox("Select news category:", ["Macroeconomic", "Oil and Gas"])


# Build query based on type
if st.button("Get News"):
    if news_type == "Macroeconomic":
        user_query = "What’s the latest macroeconomic news from the US and China in the past week? Please write in a way of an economic analyst and in paragraphs"
    else:
        user_query = "What are yesterday update to Brent crude prices and news impacting the price? Please write in a way of an analyst and in paragraphs"

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

