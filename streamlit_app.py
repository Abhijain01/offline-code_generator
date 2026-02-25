import streamlit as st
from engine import CodeGenerator
import glob
import os
import sys

# Configure the Streamlit page
st.set_page_config(
    page_title="Offline Code Generator", 
    page_icon="💻", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful premium UI
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #1e2430;
        border: 1px solid #2d3748;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #262c38;
        border: 1px solid #3b4252;
    }
    
    /* Code block styling */
    pre {
        background-color: #1a1b24 !important;
        border-radius: 8px !important;
        border: 1px solid #30363d !important;
    }
    
    /* Header gradient */
    h1 {
        background: -webkit-linear-gradient(45deg, #4F46E5, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="Loading Engine... This may take a moment.")
def load_model(api_key=None):
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    files = glob.glob(os.path.join(models_dir, "*.gguf"))
    model_path = files[0] if files else "missing_model.gguf"
    
    return CodeGenerator(model_path, api_key=api_key)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8112/8112678.png", width=100)
    st.title("Settings")
    
    # Initialize a temporary generator to check mode
    temp_gen = load_model()
    
    if temp_gen.mode == "cloud":
        # Look for secret first, otherwise ask user
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            st.warning("⚠️ API Key Required")
            api_key = st.text_input("Enter your Gemini API Key:", type="password")
            if not api_key:
                st.info("You must provide an API key to use the cloud code generator.")
            else:
                st.session_state.gemini_key = api_key
            st.markdown("---")
            
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("💻 Code Generator")
st.markdown("Ask the AI below to generate practically any code.")

# Re-Initialize the model with the active key
active_api_key = st.session_state.get("gemini_key", os.environ.get("GEMINI_API_KEY"))
generator = load_model(api_key=active_api_key)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me to write some code... (e.g., 'Write a Python function to parse JSON')"):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Give a visual indication that the model is processing the prompt
        message_placeholder.markdown("🧠 **Thinking...** *(This can take 1-2 minutes on CPU before the first word appears)*")
        
        # We need to collect the stream chunks
        try:
            stream = generator.generate_response(prompt, api_key=active_api_key)
            for chunk in stream:
                # Clean up known token artifacts based on engine.py's implementation
                clean_chunk = chunk.replace('Ġ', ' ').replace('Ċ', '\n').replace('<|im_end|>', '')
                full_response += clean_chunk
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
                
            # Remove cursor once generation is finished
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Error during generation: {e}")
            full_response = f"An error occurred: {e}"
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
