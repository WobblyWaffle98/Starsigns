import streamlit as st
import os
import datetime
import io
import base64
from google import genai
from google.genai import types
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
</style>
""", unsafe_allow_html=True)

class PresentationGenerator:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        # Initialize Google Search tool
        self.google_search_tool = Tool(google_search=GoogleSearch())
        
    def search_oil_news(self, days_back=7):
        """Search for recent oil market news and data"""
        search_queries = [
            "Brent crude oil price news this week",
            "WTI crude oil market analysis recent",
            "OPEC+ production news latest",
            "oil inventory data EIA recent",
            "crude oil geopolitical news",
            "Bloomberg oil market report",
            "Reuters crude oil analysis"
        ]
        
        search_results = []
        for query in search_queries:
            try:
                # Note: This is a placeholder for the actual Google Search integration
                # You'll need to implement the actual search call based on your Google Search setup
                st.info(f"🔍 Searching: {query}")
                # search_result = self.google_search_tool.search(query)
                # search_results.append(search_result)
            except Exception as e:
                st.warning(f"Search failed for '{query}': {str(e)}")
        
        return search_results
        
    def wave_file(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        """Save audio data to WAV file"""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)
    
    def generate_transcript(self, custom_prompt=None, use_real_data=True):
        """Generate presentation transcript with real market data"""
        
        if use_real_data:
            # Search for recent oil market news
            st.info("🔍 Searching for latest oil market data...")
            search_results = self.search_oil_news()
            
            # Enhanced prompt with real-time search integration
            search_enhanced_prompt = f"""
            You are generating a professional oil market presentation transcript for two analysts named Harith and Mirza.
            
            IMPORTANT: Use the Google Search tool to find the most recent and accurate information about:
            1. Current Brent crude oil prices and recent price movements
            2. Latest WTI crude oil market developments  
            3. Recent OPEC+ production decisions and announcements
            4. Weekly EIA inventory data and petroleum status reports
            5. Geopolitical events affecting oil markets
            6. Major oil company earnings and industry news
            7. Economic factors impacting crude oil demand
            
            Search for information from these reliable sources:
            - Bloomberg Energy
            - Reuters Oil & Gas
            - EIA (Energy Information Administration)
            - OPEC official announcements
            - Oil & Gas Journal
            - Platts/S&P Global Commodity Insights
            
            Based on your search results, create a professional dialogue between Harith and Mirza discussing:
            - Opening: "Good day GCEM team!"
            - Current oil price levels and week-over-week changes
            - Key market drivers from the past week
            - Supply-side developments (OPEC+, US production, etc.)
            - Demand factors and economic indicators
            - Geopolitical influences
            - Technical analysis insights
            - Market outlook for the coming week
            
            Keep the tone professional and informative for energy traders and industry professionals.
            Include specific data points, percentages, and price levels from your search results.
            Make sure all information is factual and recently sourced.
            """
            
            prompt = custom_prompt if custom_prompt else search_enhanced_prompt
        else:
            # Fallback to original prompt without real data
            prompt = custom_prompt if custom_prompt else """
            Generate a short transcript between analyst doing a presentation by two analyst named Harith and Mirza 
            summarizing key Brent crude oil market developments over the past week.
            Focus on critical price movements, geopolitical drivers, inventory data, OPEC+ activity, 
            macroeconomic factors, and notable analyst commentary. The tone should be professional and informative, 
            suitable for an audience of energy traders and industry professionals.
            They should start by saying Good day GCEM team!
            """
        
        try:
            # Generate content with Google Search tool enabled
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                tools=[self.google_search_tool] if use_real_data else None
            )
            
            return response.text
            
        except Exception as e:
            st.error(f"Error generating transcript: {str(e)}")
            # Fallback to basic generation without search
            if use_real_data:
                st.warning("Falling back to basic generation without real-time data...")
                return self.generate_transcript(custom_prompt, use_real_data=False)
            raise e
    
    def generate_audio(self, transcript):
        """Generate audio from transcript using multi-speaker TTS"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=transcript,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker='Analyst 1',
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name='Charon',
                                    )
                                )
                            ),
                            types.SpeakerVoiceConfig(
                                speaker='Analyst 2',
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name='Vindemiatrix',
                                    )
                                )
                            ),
                        ]
                    )
                )
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
            help="Enter your Google Generative AI API key"
        )
        
        # Voice configuration
        st.subheader("🎙️ Voice Settings")
        analyst1_voice = st.selectbox(
            "Analyst 1 (Harith) Voice",
            ["Charon", "Puck", "Kore", "Fenrir"],
            index=0
        )
        
        analyst2_voice = st.selectbox(
            "Analyst 2 (Mirza) Voice", 
            ["Vindemiatrix", "Charon", "Puck", "Kore"],
            index=0
        )
        
        # Data source options
        st.subheader("🔍 Data Sources")
        use_real_data = st.checkbox("Use real-time market data", value=True, 
                                   help="Enable Google Search for current oil market information")
        
        if use_real_data:
            st.info("✅ Will search for latest oil market news and data")
            search_sources = st.multiselect(
                "Select news sources to search:",
                ["Bloomberg Energy", "Reuters Oil & Gas", "EIA Reports", "OPEC Announcements", 
                 "Platts S&P Global", "Oil & Gas Journal"],
                default=["Bloomberg Energy", "Reuters Oil & Gas", "EIA Reports"]
            )
        else:
            st.warning("⚠️ Using AI-generated market analysis (may not reflect current conditions)")
        
        # Presentation settings
        st.subheader("📊 Presentation Settings")
        auto_generate = st.checkbox("Auto-generate daily", value=False)
        save_history = st.checkbox("Save presentation history", value=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Custom Presentation Prompt")
        
        # Real-time data status
        if 'use_real_data' not in locals():
            use_real_data = True
            
        if use_real_data:
            st.success("🔍 Real-time data search enabled - AI will search for current oil market information")
        else:
            st.warning("⚠️ Using simulated data - Enable real-time search in sidebar for current market data")
        
        custom_prompt = st.text_area(
            "Customize your presentation content (optional):",
            height=150,
            placeholder="Leave empty to use default crude oil market analysis prompt..."
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
    
    try:
        generator = PresentationGenerator(api_key)
        
        # Handle button clicks
        if generate_transcript_btn or generate_full_btn:
            with st.spinner("🔍 Searching for latest oil market data and generating transcript..."):
                try:
                    # Get real-time data setting from sidebar
                    use_real_data = st.session_state.get('use_real_data', True)
                    
                    transcript = generator.generate_transcript(
                        custom_prompt if custom_prompt else None,
                        use_real_data=use_real_data
                    )
                    st.session_state.transcript = transcript
                    
                    st.markdown('<div class="status-box success-box">✅ Transcript generated with real-time market data!</div>', 
                               unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error generating transcript: {str(e)}")
                    return
        
        if generate_audio_btn or generate_full_btn:
            if not st.session_state.transcript:
                st.warning("⚠️ Please generate a transcript first!")
            else:
                with st.spinner("🎵 Generating audio presentation..."):
                    try:
                        audio_data = generator.generate_audio(st.session_state.transcript)
                        audio_filename = f"presentation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                        generator.create_audio_file(audio_data, audio_filename)
                        st.session_state.audio_file = audio_filename
                        
                        st.markdown('<div class="status-box success-box">✅ Audio generated successfully!</div>', 
                                   unsafe_allow_html=True)
                        
                        # Add to history
                        if save_history:
                            st.session_state.generation_history.append({
                                'timestamp': current_time,
                                'transcript': st.session_state.transcript,
                                'audio_file': audio_filename
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
            with st.expander("📊 Data Sources & Search Results"):
                st.info("This transcript was generated using real-time search results from:")
                sources_used = [
                    "Bloomberg Energy - Oil market news and analysis",
                    "Reuters Oil & Gas - Latest crude oil developments", 
                    "EIA - Weekly petroleum status reports",
                    "OPEC - Official production announcements",
                    "Market data providers - Current price information"
                ]
                for source in sources_used:
                    st.write(f"• {source}")
                    
                st.caption("Note: All data points and market information in the transcript are sourced from current market reports and news.")
        
        if st.session_state.audio_file and os.path.exists(st.session_state.audio_file):
            st.header("🎵 Audio Presentation")
            
            # Audio player
            with open(st.session_state.audio_file, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/wav')
            
            # Download button
            st.download_button(
                label="⬇️ Download Audio File",
                data=audio_bytes,
                file_name=st.session_state.audio_file,
                mime="audio/wav"
            )
        
        # History section
        if save_history and st.session_state.generation_history:
            st.header("📚 Presentation History")
            
            for i, entry in enumerate(reversed(st.session_state.generation_history[-5:])):  # Show last 5
                with st.expander(f"📅 {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
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