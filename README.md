# Legal_Document_Analysis
1. Streamlit Web App Setup
Uses streamlit to create an interactive web interface.

st.set_page_config defines page title, icon, and layout.

UI includes:

A main content area for chat.

A sidebar for configuration and tips.

2. Document Upload and Processing
Users can upload legal documents (.pdf, .docx, .txt).

Files are read and converted into text using:

PyPDF2 for PDFs

python-docx for DOCX files

Standard decoding for TXT files

The text is stored in the session_state so it can be referenced throughout the session.

3. Configuration Options (Sidebar)
Users can customize:

Analysis Type (e.g., General Legal, Risk Assessment, Contract Review, etc.)

Output Language (English, Spanish, French, etc.)

Advanced Options:

temperature: Controls randomness/creativity of responses.

max_tokens: Limits the length of the AI's response.

Option to clear chat history.

4. AI Integration with Google Gemini
API is configured using google.generativeai.

It creates a GenerativeModel instance with specified parameters.

The user’s input is combined with the system prompt and sent to the Gemini model.

A basic memory is simulated using the chat history (although true multi-turn memory is limited).

5. System Prompt Construction
A detailed prompt is built to instruct the AI:

Provide explanations in plain language.

Avoid giving legal advice.

Tailor output based on analysis type and language.

Keep responses clear, concise, and formatted.

6. Chat Interface
Displays chat history from the session state.

Accepts new user questions via st.chat_input().

Shows both user questions and AI answers with chat message formatting.

Adds each message to session_state.chat_history.

7. UX Features
Displays a preview of the uploaded document.

Adds artificial delay with sleep() to simulate thinking.

Includes tips and limitations in the sidebar to guide the user.

8. Session Management
st.session_state is used for:

Tracking uploaded document status.

Holding document text.

Keeping chat history across interactions.

✅ Summary
This app allows users to upload a legal document and interactively ask an AI about it using natural language. It's designed for ease of use with customization options for different legal analysis contexts and output languages, while maintaining a legal-safe, advisory-only tone.
