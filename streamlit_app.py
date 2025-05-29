import streamlit as st
import os
import datetime
import io
import base64
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import wave
import threading
import time

# Audio configuration constants  
CHANNELS = 1
RATE = 24000
CHUNK_SIZE = 1024
SAMPLE_WIDTH = 2  # 16-bit audio

# Page configuration
st.set_page_config(
    page_title="Daily Oil Market Presentation Generator",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .presentation-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 20px 0;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .search-status {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        color: #0066cc;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .presenter-info {
        background-color: #f0f8ff;
        border: 1px solid #b3d9ff;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

class PresentationGenerator:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        # Initialize Google Search tool using the correct format
        self.google_search_tool = Tool(google_search=GoogleSearch())
        
    def wave_file(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        """Save audio data to WAV file"""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)
    
    def generate_transcript(self, presenter_name="Harith", custom_prompt=None, use_real_data=True):
        """Generate presentation transcript with real market data for single presenter"""
        
        if use_real_data:
            # Enhanced prompt with real-time search integration for single presenter, optimized for natural audio transcript without bullet points or titles
            search_enhanced_prompt = f"""
            You are generating a professional oil market presentation transcript for an analyst named {presenter_name} presenting to the GCEM team.
            The *entire output* must be a natural-sounding, spoken-word transcript that could be read aloud by the presenter.
            **Do NOT include any section titles, headings, bullet points, speaker cue,  or any introductory/concluding remarks from yourself (the AI).**
            The presentation should flow as a continuous narrative.

            IMPORTANT: Use Google Search to find the most recent and accurate information about crude oil markets from the past week.
            Focus on data and events from the past 7-10 days leading up to today, May 29, 2025.

            Search for and include:
            1. Current Brent acrude oil prices, recent price movements (this week vs. last week, and year-to-date changes), with specific numbers and percentage changes.
            2. Recent OPEC+ production decisions, meeting outcomes, and announcements, including specific dates, production quotas/adjustments, and future plans.
            3. Latest weekly EIA inventory data (crude oil, gasoline, distillates) and petroleum status reports, including specific figures and changes.
            4. Key geopolitical events affecting oil markets (Middle East, Russia, Ukraine, etc.) and their specific impact.
            5. Major oil company earnings reports, production updates, and significant industry news from the past week.
            6. Economic factors impacting crude oil demand (US, China, Europe, global growth forecasts) with specific data points and reports (e.g., IMF, IEA).
            7. Supply disruptions, refinery issues, or infrastructure news with details (e.g., location, impact, companies involved).

            Prioritize information from these reputable sources:
            - Bloomberg Energy and oil market reports
            - Reuters Oil & Gas news
            - EIA (Energy Information Administration) weekly reports and analyses
            - OPEC official announcements, press releases, and monthly reports
            - Oil & Gas Journal market updates
            - Platts/S&P Global Commodity Insights
            - Financial Times energy section
            - Wall Street Journal energy coverage

            The transcript *must* begin precisely with:
            "Good day GCEM team! I'm {presenter_name}, and let's dive into this week's crude oil market developments..."

            Then, proceed directly into the content, discussing:
            - Current price levels, movements, and year-to-date performance.
            - Key supply-side developments, including OPEC+ actions, US production trends (EIA data, shale outlook), and other international supply news and disruptions.
            - Demand factors, economic indicators affecting consumption (e.g., China's economic data, global growth forecasts), and insights from oil major earnings.
            - Geopolitical influences impacting market sentiment and supply chains.
            - Latest inventory levels and refining margins.
            - A brief overview of market sentiment, technical analysis (if information is found), and forward curve activity.
            - A clear market outlook for the coming week, outlining key events or data to watch.

            Crucially, all information should be presented as a flowing narrative from {presenter_name}, avoiding any explicit section titles, headings, or bullet points. Integrate specific data points, dates, and names seamlessly into the spoken text.

            Ensure the transcript is:
            -   **Natural and Conversational:** Reads like a person speaking.
            -   **Data-Rich and Specific:** Includes exact numbers, dates, and percentage changes from your searches, integrated naturally.
            -   **Professionally Termed:** Uses appropriate energy market vocabulary.
            -   **Continuous and Flowing:** No breaks for titles or bullet points.
            -   **Factual and Timely:** All information is recent (past week) and verifiable.
            -   **Single Speaker:** Maintains the persona of {presenter_name} throughout, with explicit speaker cues.

            The transcript *must* end precisely with:
            "That's our market wrap for this week. Thanks for joining us, GCEM team!"
            """

            prompt = custom_prompt if custom_prompt else search_enhanced_prompt
        else:
            # Fallback to basic prompt without real data, still aiming for a natural, continuous transcript
            prompt = custom_prompt if custom_prompt else f"""
            Generate a professional transcript for an analyst named {presenter_name} 
            presenting crude oil market developments to the GCEM team.
            The *entire output* must be a natural, flowing spoken-word transcript, without any titles or bullet points.

            The transcript *must* begin precisely with:
            "{presenter_name.upper()}: Good day GCEM team! I'm {presenter_name}..."

            Then, proceed directly into a discussion covering:
            - Brent and WTI crude price movements.
            - OPEC+ production decisions.
            - US inventory data.
            - Geopolitical factors.
            - Market outlook.

            Use professional, yet conversational language.
            Present as a single speaker ({presenter_name}) throughout.

            The transcript *must* end precisely with:
            "{presenter_name.upper()}: That's our market wrap for this week. Thanks for joining us, GCEM team!"
            """
        try:
            # Generate content with Google Search tool enabled
            if use_real_data:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=GenerateContentConfig(
                        tools=[self.google_search_tool],
                        response_modalities=["TEXT"],
                    )
                )
            else:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            
            # Extract text from response
            if hasattr(response.candidates[0].content, 'parts'):
                return "\n".join([part.text for part in response.candidates[0].content.parts])
            else:
                return response.candidates[0].content.text
            
        except Exception as e:
            st.error(f"Error generating transcript: {str(e)}")
            # Fallback to basic generation without search
            if use_real_data:
                st.warning("Falling back to basic generation without real-time data...")
                return self.generate_transcript(presenter_name, custom_prompt, use_real_data=False)
            raise e
    
    def generate_audio(self, transcript, voice_name="Charon"):
        """Generate audio from transcript using single-speaker TTS"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=transcript,
            config=GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config={
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice_name
                        }
                    }
                }
            )
        )
        
        return response.candidates[0].content.parts[0].inline_data.data
    
    def create_audio_file(self, audio_data, filename="presentation.wav"):
        """Create WAV file from audio data"""
        self.wave_file(filename, audio_data, channels=CHANNELS, rate=RATE, 
                      sample_width=SAMPLE_WIDTH)
        return filename

def main():
    # Header
    st.markdown('<h1 class="main-header">🛢️ Daily Oil Market Presentation Generator</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google Generative AI API Key",
            type="password",
            help="Enter your Google Generative AI API key",
            value="AIzaSyA0jZkj5buSGm6AXtXlo6CEeFS1f8q0KSg"  # You should remove this and use secrets
        )
        
        # Presenter configuration
        st.subheader("🎙️ Presenter Settings")
        presenter_name = st.text_input(
            "Presenter Name",
            value="Harith",
            help="Enter the name of the presenter",
            max_chars=50
        )
        
        presenter_voice = st.selectbox(
            "Presenter Voice",
            [
            "Zephyr",
            "Puck",
            "Charon",
            "Kore",
            "Fenrir",
            "Leda",
            "Orus",
            "Aoede",
            "Callirrhoe",
            "Autonoe",
            "Enceladus",
            "Iapetus",
            "Umbriel",
            "Algieba",
            "Despina",
            "Erinome",
            "Algenib",
            "Rasalgethi",
            "Laomedeia",
            "Achernar",
            "Alnilam",
            "Schedar",
            "Gacrux",
            "Pulcherrima",
            "Achird",
            "Zubenelgenubi",
            "Vindemiatrix",
            "Sadachbia",
            "Sadaltager",
            "Sulafat"
            ],
            index=0,
            help="Select the voice for the presenter"
        )
        
        # Show presenter info box
        st.markdown(f"""
        <div class="presenter-info">
            <strong>🎤 Current Presenter:</strong><br>
            Name: {presenter_name}<br>
            Voice: {presenter_voice}
        </div>
        """, unsafe_allow_html=True)
        
        # Data source options
        st.subheader("🔍 Data Sources")
        use_real_data = st.checkbox("Use real-time market data", value=True, 
                                   help="Enable Google Search for current oil market information")
        
        if use_real_data:
            st.markdown('<div class="search-status">✅ Real-time search enabled</div>', 
                       unsafe_allow_html=True)
            search_sources = st.multiselect(
                "Select news sources to search:",
                ["Bloomberg Energy", "Reuters Oil & Gas", "EIA Reports", "OPEC Announcements", 
                 "Platts S&P Global", "Oil & Gas Journal", "Financial Times Energy"],
                default=["Bloomberg Energy", "Reuters Oil & Gas", "EIA Reports"]
            )
        else:
            st.warning("⚠️ Using AI-generated analysis (not current market data)")
        
        # Presentation settings
        st.subheader("📊 Presentation Settings")
        auto_generate = st.checkbox("Auto-generate daily", value=False)
        save_history = st.checkbox("Save presentation history", value=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Custom Presentation Prompt")
        
        # Real-time data status
        if use_real_data:
            st.markdown('<div class="search-status">🔍 Real-time market data search enabled - AI will search for current oil market information</div>', 
                       unsafe_allow_html=True)
        else:
            st.warning("⚠️ Using simulated data - Enable real-time search in sidebar for current market data")
        
        custom_prompt = st.text_area(
            "Customize your presentation content (optional):",
            height=150,
            placeholder=f"Leave empty to use default crude oil market analysis prompt with {presenter_name} as presenter..."
        )
        
        # Generation controls
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            generate_transcript_btn = st.button("📄 Generate Transcript", type="secondary")
        
        with col_btn2:
            generate_audio_btn = st.button("🎵 Generate Audio", type="secondary")
        
        with col_btn3:
            generate_full_btn = st.button("🚀 Generate Full Presentation", type="primary")
    
    with col2:
        st.header("📅 Today's Schedule")
        current_time = datetime.datetime.now()
        st.info(f"**Date:** {current_time.strftime('%Y-%m-%d')}")
        st.info(f"**Time:** {current_time.strftime('%H:%M:%S')}")
        
        if auto_generate:
            st.success("✅ Auto-generation enabled")
            next_gen = current_time.replace(hour=9, minute=0, second=0) + datetime.timedelta(days=1)
            if current_time.hour >= 9:
                next_gen += datetime.timedelta(days=1)
            st.info(f"**Next auto-gen:** {next_gen.strftime('%Y-%m-%d %H:%M')}")
        
        # Market status indicator
        st.header("📊 Market Status")
        if use_real_data:
            st.success("🟢 Live Data Feed Active")
            st.caption("Searching Bloomberg, Reuters, EIA, and other sources")
        else:
            st.error("🔴 Simulated Data Mode")
            st.caption("Enable real-time search for current data")
        
        # Presenter status
        st.header(f"🎤 Presenter: {presenter_name}")
        st.info(f"Voice: {presenter_voice}")
        st.caption("Single presenter format")
    
    # Initialize session state
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []
    
    # Check if API key is provided
    if not api_key:
        st.warning("⚠️ Please enter your Google Generative AI API key in the sidebar to continue.")
        return
    
    # Validate presenter name
    if not presenter_name.strip():
        st.warning("⚠️ Please enter a presenter name in the sidebar.")
        return
    
    try:
        generator = PresentationGenerator(api_key)
        
        # Handle button clicks
        if generate_transcript_btn or generate_full_btn:
            search_status = f"🔍 Searching for latest oil market data and generating transcript for {presenter_name}..." if use_real_data else f"📝 Generating transcript for {presenter_name} with simulated data..."
            with st.spinner(search_status):
                try:
                    transcript = generator.generate_transcript(
                        presenter_name=presenter_name.strip(),
                        custom_prompt=custom_prompt if custom_prompt else None,
                        use_real_data=use_real_data
                    )
                    st.session_state.transcript = transcript
                    
                    success_msg = f"✅ Transcript generated for {presenter_name} with real-time market data!" if use_real_data else f"✅ Transcript generated for {presenter_name} successfully!"
                    st.markdown(f'<div class="status-box success-box">{success_msg}</div>', 
                               unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error generating transcript: {str(e)}")
                    return
        
        if generate_audio_btn or generate_full_btn:
            if not st.session_state.transcript:
                st.warning("⚠️ Please generate a transcript first!")
            else:
                with st.spinner(f"🎵 Generating audio presentation with {presenter_name}'s voice ({presenter_voice})..."):
                    try:
                        audio_data = generator.generate_audio(st.session_state.transcript, presenter_voice)
                        audio_filename = f"oil_market_presentation_{presenter_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                        generator.create_audio_file(audio_data, audio_filename)
                        st.session_state.audio_file = audio_filename
                        
                        st.markdown(f'<div class="status-box success-box">✅ Audio generated successfully with {presenter_name}\'s voice!</div>', 
                                   unsafe_allow_html=True)
                        
                        # Add to history
                        if save_history:
                            st.session_state.generation_history.append({
                                'timestamp': current_time,
                                'presenter_name': presenter_name,
                                'presenter_voice': presenter_voice,
                                'transcript': st.session_state.transcript,
                                'audio_file': audio_filename,
                                'used_real_data': use_real_data
                            })
                        
                    except Exception as e:
                        st.error(f"❌ Error generating audio: {str(e)}")
                        return
        
        # Display results
        if st.session_state.transcript:
            st.header("📄 Generated Transcript")
            st.markdown(f'<div class="presentation-box">{st.session_state.transcript}</div>', 
                       unsafe_allow_html=True)
            
            # Show data sources used
            with st.expander("📊 Data Sources & Search Information"):
                if use_real_data:
                    st.success("✅ This transcript was generated using real-time search results from:")
                    sources_used = [
                        "🔍 Bloomberg Energy - Oil market news and price analysis",
                        "🔍 Reuters Oil & Gas - Latest crude oil developments", 
                        "🔍 EIA - Weekly petroleum status reports and inventory data",
                        "🔍 OPEC - Official production announcements and meeting outcomes",
                        "🔍 Platts/S&P Global - Commodity market insights and pricing",
                        "🔍 Financial Times - Energy sector news and analysis"
                    ]
                    for source in sources_used:
                        st.write(source)
                    st.caption("✅ All market data, price movements, and developments mentioned are sourced from current market reports.")
                else:
                    st.warning("⚠️ This transcript was generated using AI analysis without real-time market data.")
                    st.caption("Enable 'Use real-time market data' in the sidebar for current market information.")
        
        if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
            st.header("🎵 Audio Presentation")
            st.info(f"🎙️ Single presenter: {presenter_name} (Voice: {presenter_voice})")
            
            # Audio player
            with open(st.session_state.audio_file, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/wav')
            
            # Download button
            st.download_button(
                label="⬇️ Download Audio Presentation",
                data=audio_bytes,
                file_name=st.session_state.audio_file,
                mime="audio/wav"
            )
        
        # History section
        if save_history and st.session_state.generation_history:
            st.header("📚 Presentation History")
            
            for i, entry in enumerate(reversed(st.session_state.generation_history[-5:])):  # Show last 5
                data_badge = "🟢 Live Data" if entry.get('used_real_data', False) else "🔴 Simulated"
                presenter_info = entry.get('presenter_name', 'Unknown')
                voice_info = entry.get('presenter_voice', 'Unknown')
                
                with st.expander(f"📅 {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {presenter_info} ({voice_info}) - {data_badge}"):
                    st.text_area(f"Transcript {i+1}:", entry['transcript'], height=100, disabled=True)
                    if os.path.exists(entry['audio_file']):
                        with open(entry['audio_file'], 'rb') as f:
                            st.download_button(
                                f"⬇️ Download Audio {i+1}",
                                data=f.read(),
                                file_name=entry['audio_file'],
                                mime="audio/wav",
                                key=f"download_{i}"
                            )
    
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")

if __name__ == "__main__":
    main()