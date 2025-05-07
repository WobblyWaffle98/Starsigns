import streamlit as st
from google import genai

client = genai.Client(api_key="AIzaSyA0jZkj5buSGm6AXtXlo6CEeFS1f8q0KSg")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="What happened to Brent oil over the past week"
)

st.title("Starsigns")

st.write(response.text)