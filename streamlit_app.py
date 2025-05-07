import streamlit as st
from google import genai

# Replace with your actual Gemini API key
client = genai.Client(api_key="YOUR_API_KEY")

def get_latest_oil_gas_news():
    """Fetches the latest news about the oil and gas market using a search engine."""
    try:
        search_results = client.generative_model(model_name="gemini-pro").generate_content(
            "What is the latest news regarding the oil and gas market over the past week?"
        ).text
        return search_results
    except Exception as e:
        return f"Error fetching news: {e}"

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works in a few words"
)

st.title("⛽ Oil & Gas Market Chatbot")
st.write(
    "Let's start exploring the oil and gas market! Ask me anything."
)
st.write(response.text)

latest_news = get_latest_oil_gas_news()
if latest_news:
    st.subheader("Latest Oil & Gas Market News:")
    st.write(latest_news)
else:
    st.info("Could not retrieve the latest news at this time.")
