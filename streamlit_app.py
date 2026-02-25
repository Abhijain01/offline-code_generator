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

@st.cache_resource(show_spinner="Loading CodeLlama Model into memory... This may take a moment.")
def load_model():
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    files = glob.glob(os.path.join(models_dir, "*.gguf"))
    if not files:
        return None
    
    model_path = files[0]
    return CodeGenerator(model_path)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8112/8112678.png", width=100)
    st.title("Settings")
    st.markdown("---")
    st.markdown("This app uses a locally downloaded **CodeLlama-7B** model via the `ctransformers` inference engine.")
    st.markdown("Responses are generated completely offline. Enjoy fast, private code generation!")
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("💻 Offline Code Generator")
st.markdown("Ask the AI below to generate practically any code, completely offline!")

# Initialize the model
generator = load_model()

if not generator:
    st.error("No model found! Please ensure you have run `python model_downloader.py` first.")
    st.stop()

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
            stream = generator.generate_response(prompt)
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
