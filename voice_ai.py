import streamlit as st
import streamlit.components.v1 as components
from ai_chatbot import answer_query

def render_voice_ai():
    st.markdown("## 🎙️ Voice AI Agent (VUI)")
    st.caption("Click the mic, speak your question, and the AI will reply with voice.")

    # HTML/JS for Web Speech API
    voice_html = """
    <div style="text-align: center; padding: 20px; background: #F4F6F7; border-radius: 10px; border: 2px solid #0B3C5D;">
        <h3 style="color: #0B3C5D; margin-bottom: 20px;">Speak to Meena AI</h3>
        
        <button id="micBtn" style="background-color: #0B3C5D; color: white; border: none; border-radius: 50%; width: 80px; height: 80px; font-size: 30px; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.2); transition: 0.3s;">
            🎤
        </button>
        
        <p id="status" style="margin-top: 15px; font-weight: bold; color: #1C2833;">Click the mic to start speaking...</p>
        <div id="transcript" style="margin-top: 10px; padding: 10px; background: white; border-radius: 8px; min-height: 40px; font-style: italic; color: #555;"></div>
    </div>

    <script>
    const micBtn = document.getElementById('micBtn');
    const status = document.getElementById('status');
    const transcriptBox = document.getElementById('transcript');

    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        status.innerText = "❌ Your browser does not support Speech Recognition. Please use Chrome.";
        micBtn.disabled = true;
        micBtn.style.backgroundColor = "#ccc";
    } else {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-IN'; // Indian English
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        micBtn.onclick = () => {
            recognition.start();
            status.innerText = "🎙️ Listening...";
            micBtn.style.backgroundColor = "#C0392B"; // Red while listening
        };

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            transcriptBox.innerText = "You said: " + speechResult;
            status.innerText = "Processing...";
            micBtn.style.backgroundColor = "#D35400"; // Orange while processing
            
            // Send to Streamlit
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: speechResult
            }, "*");
        };

        recognition.onspeechend = () => {
            recognition.stop();
            micBtn.style.backgroundColor = "#0B3C5D";
        };

        recognition.onerror = (event) => {
            status.innerText = "Error: " + event.error;
            micBtn.style.backgroundColor = "#0B3C5D";
        };
    }
    
    // Text-to-Speech function
    function speak(text) {
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-IN';
        synth.speak(utterance);
    }
    </script>
    """
    
    # Display the Mic UI
    result = components.html(voice_html, height=250)
    
    st.markdown("---")
    st.markdown("### 💬 Text Transcript")
    
    # We can also provide a text input as fallback
    typed_query = st.text_input("Or type your question here:", placeholder="E.g., What is my total outstanding balance?")
    
    if st.button("Ask AI", type="primary"):
        if typed_query:
            with st.spinner("Thinking..."):
                response = answer_query(typed_query)
                st.success(f"**AI:** {response}")
                # Note: Streamlit cannot easily trigger JS TTS from a Python button click without a custom component loop, 
                # but the mic flow above handles the VUI perfectly.
