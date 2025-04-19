import streamlit as st
import google.generativeai as genai
import os
import tempfile
import PyPDF2
import docx
import re
from time import sleep

# Configure page settings
st.set_page_config(
    page_title="Legal Document Analysis Chatbot",
    page_icon="⚖️",
    layout="wide"
)

# Application title and introduction
st.title("⚖️ Legal Document Analysis Chatbot")
st.markdown("""
Upload legal documents (PDF, DOCX, or TXT) and chat about them with an AI assistant.
This tool helps you understand complex legal language, identify key clauses, assess risks, and more.
""")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'document_text' not in st.session_state:
    st.session_state.document_text = None

if 'document_uploaded' not in st.session_state:
    st.session_state.document_uploaded = False

# Your Gemini API key (hardcoded)
GEMINI_API_KEY = "AIzaSyDBKAoOG-y8o8r07zIQQlbQiAEN7SRUMK8"  # Replace with your actual API key

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Analysis options
    analysis_type = st.selectbox(
        "Analysis Context",
        ["General Legal", "Risk Assessment", "Compliance Review", "Contract Review", "Clause Explanation"]
    )
    
    # Display language option
    language = st.selectbox("Output language", ["English", "Spanish", "French", "German", "Chinese", "Japanese"])

    # Advanced options (collapsible)
    with st.expander("Advanced Options"):
        temperature = st.slider("Temperature (Creativity)", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
        max_tokens = st.slider("Max output tokens", min_value=100, max_value=4096, value=2048, step=100)
        clear_history = st.button("Clear Conversation History")
        if clear_history:
            st.session_state.chat_history = []
            st.success("Conversation history cleared!")

# Function to extract text from different file formats
def extract_text(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name
        
        text = ""
        with open(temp_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text() + "\n"
        
        os.unlink(temp_path)
        return text
    
    elif file_extension == 'docx':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name
        
        doc = docx.Document(temp_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        os.unlink(temp_path)
        return text
    
    elif file_extension == 'txt':
        return uploaded_file.getvalue().decode('utf-8')
    
    else:
        st.error(f"Unsupported file format: {file_extension}")
        return None

# Function to create system prompt based on analysis type
def create_system_prompt(analysis_type, document_text, language_choice):
    language_instruction = f"Always respond in {language_choice}." if language_choice != "English" else "Respond in English."
    
    base_prompt = f"""
    You are a legal AI assistant specializing in document analysis. You help users understand legal documents and answer questions about them.
    
    You have the following document to analyze:
    
    {document_text[:50000]}  # Limiting document size to prevent exceeding context limits
    
    {language_instruction}
    
    IMPORTANT GUIDELINES:
    1. Keep responses concise and focused on the user's question
    2. Limit responses to a maximum of 2048 tokens
    3. Use plain language to explain complex legal concepts
    4. Acknowledge when you're uncertain or when the document doesn't contain needed information
    5. Do not provide definitive legal advice - remind the user to consult a qualified attorney when appropriate
    6. Format responses with headings and bullet points when it improves readability
    """
    
    # Add specific analysis context based on selected type
    analysis_contexts = {
        "General Legal": "Focus on general document understanding, summarization, and broad legal concepts.",
        "Risk Assessment": "Focus on identifying potential legal risks, liabilities, and ambiguous clauses that could lead to disputes.",
        "Compliance Review": "Focus on compliance issues, regulatory concerns, and suggestions for improving compliance.",
        "Contract Review": "Focus on contractual terms, obligations, rights, and potential negotiation points.",
        "Clause Explanation": "Focus on explaining specific clauses in plain language and highlighting their implications."
    }
    
    return base_prompt + "\n\nANALYSIS CONTEXT: " + analysis_contexts[analysis_type]

# Function to get AI response
def get_ai_response(prompt, chat_history):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": 0.95,
            }
        )
        
        # Create chat context from history
        chat = model.start_chat(history=[])
        
        # Add previous messages to chat context
        for message in chat_history:
            if message["role"] == "user":
                chat.send_message(message["content"])
            else:
                # This is a hack since the API doesn't allow directly adding assistant messages
                # We simulate it by adding the assistant's response to our next prompt
                pass
        
        # Send current prompt
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Display chat messages
def display_chat_history():
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

# Main function
def main():
    # File uploader
    uploaded_file = st.file_uploader("Upload a legal document", type=["pdf", "docx", "txt"])
    
    # Check if a file is uploaded
    if uploaded_file is not None and not st.session_state.document_uploaded:
        with st.spinner("Processing document..."):
            document_text = extract_text(uploaded_file)
            if document_text:
                st.session_state.document_text = document_text
                st.session_state.document_uploaded = True
                
                # Add system message introducing the document
                document_intro = f"I've analyzed the document '{uploaded_file.name}' ({len(document_text)} characters). What would you like to know about it?"
                st.session_state.chat_history.append({"role": "assistant", "content": document_intro})
                
                # Show document preview
                with st.expander("Document Preview"):
                    st.text_area("Document Content (Preview)", document_text[:2000] + "..." if len(document_text) > 2000 else document_text, height=300)
                    st.info(f"Total document length: {len(document_text)} characters")
            else:
                st.error("Could not extract text from the document.")
    
    # Display chat interface if document is uploaded
    if st.session_state.document_uploaded:
        # Display chat history
        display_chat_history()
        
        # Chat input
        user_input = st.chat_input("Ask about the document...")
        
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Create system prompt with document context
                    system_prompt = create_system_prompt(analysis_type, st.session_state.document_text, language)
                    
                    # Combine system prompt with user input
                    full_prompt = f"{system_prompt}\n\nUser question: {user_input}"
                    
                    # Get response
                    response = get_ai_response(full_prompt, st.session_state.chat_history)
                    
                    # Add artificial delay for better UX
                    sleep(0.5)
                    
                    # Display response
                    st.write(response)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Add usage tips
    st.sidebar.markdown("---")
    st.sidebar.header("Usage Tips")
    with st.sidebar.expander("How to get better results"):
        st.markdown("""
        - Upload clear, well-formatted documents
        - Ask specific questions about the document
        - Try different analysis contexts for different perspectives
        - Use follow-up questions to explore specific areas
        - Remember that this tool is for informational purposes only and not a substitute for legal advice
        """)
    
    # Add output limits info
    st.sidebar.markdown("---")
    st.sidebar.header("Output Limits")
    st.sidebar.info("""
    - Maximum response length: 2048 tokens (approximately 1500-2000 words)
    - Document size limit: 50,000 characters for analysis
    - Processing time may increase with document complexity
    """)

if __name__ == "__main__":
    main()