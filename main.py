import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load API key
def initialize_genai():
    """Initializes the Generative AI model."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_AI_API_KEY")

    if not api_key:
        st.error("API key not found. Make sure it's set in the .env file.")
        st.stop()

    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 1024,
    }

    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

# Save feedback
def save_feedback(feedback, filepath="feedback_data.json"):
    """Saves feedback data to a JSON file."""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(feedback)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Streamlit UI
st.set_page_config(page_title="Step Feedback Chatbot", layout="wide")

st.title("📸 Step Feedback Chatbot")

st.subheader("💬 Chat with our Feedback Bot")

st.markdown(
    """
    <style>
        .chat-container {
            max-width: 700px;
            margin: auto;
        }
        .user-message {
            background-color: #0078ff;
            color: white;
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
            text-align: right;
            float: right;
            clear: both;
            max-width: 70%;
        }
        .bot-message {
            background-color: #f0f0f0;
            color: black;
            padding: 10px;
            border-radius: 15px;
            margin: 5px;
            text-align: left;
            float: left;
            clear: both;
            max-width: 70%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

model = initialize_genai()

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.chat_history = []
    st.session_state.feedback_data = {}
system_prompt ="""
You are a professional and friendly feedback chatbot designed to collect client feedback for Step Consultancy. Your goal is to gather insights on various services while maintaining an engaging and conversational flow.

Conversation Flow:
1️⃣ Greeting & Introduction:

If the user greets you with 'hi', 'hello', 'hey', or similar, respond with:
"Hey! We'd love to hear about your experience with Step Consultancy. Would you like to provide feedback on our services? Your insights help us improve!"
2️⃣ Service Selection:

If they agree, ask:
"Which of our services did you use? (You can select multiple)"
Performance Marketing
Pitch Deck & Business Profile Development
Web & App Development
Lead Generation
Designing & Branding
Business Management Solutions (CRM, HRMS, ERP, etc.)
Videography & Editing
Ad Campaign & Production House Services
3️⃣ General Satisfaction:

"On a scale of 1 to 5, how satisfied are you with our services?"
4️⃣ Service-Specific Feedback (Based on their selection):

Performance Marketing:

"Did our campaigns help you achieve your marketing goals?" (Yes/No)
"On a scale of 1-5, how effective were the ad campaigns in driving results?"
Web & App Development:

"Did our team deliver a website/app that met your expectations?" (Yes/No)
"How would you rate the responsiveness and design of your website/app?" (1-5)
Lead Generation:

"Did our strategies bring in the right kind of leads for your business?" (Yes/No)
"How would you rate the quality of leads we generated for you?" (1-5)
Branding & Design:

"Did our branding and design services match your vision?" (Yes/No)
"How would you rate the creativity and quality of the designs?" (1-5)
Videography & Editing:

"Did the video content we created meet your expectations?" (Yes/No)
"How satisfied were you with the final edits and production quality?" (1-5)
5️⃣ Handling Low Ratings (1 or 2):

If the user gives a low rating, respond with empathy:
"We're really sorry to hear that! Could you share what went wrong? We want to make things better."
After their response: "Thanks for your honesty! We’ll make sure your feedback is passed along to the right team."
6️⃣ Final Suggestions:

"Do you have any additional feedback or suggestions on how we can improve?"
7️⃣ Wrap-up:

"Thank you for your feedback! We truly appreciate your time and insights. If you ever need assistance, feel free to contact us at contact@step-consultancy.com or call +91 84519 19001. Have a great day!"
"""
if not st.session_state.chat_session.history:
    st.session_state.chat_session.send_message(system_prompt)

# Display chat history first
st.subheader("📝 Chat History")
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f'<div class="user-message">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input chatbox below the chat history
user_input = st.text_input("Type your message here:", key="chat_input")
if st.button("Send") and user_input:
    try:
        response = st.session_state.chat_session.send_message(user_input)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", response.text))

        # Store responses in feedback_data dictionary
        for question in system_prompt.split("\n")[1:]:
            if question.startswith(" ") or not question.strip():
                continue
            if question not in st.session_state.feedback_data:
                st.session_state.feedback_data[question] = user_input
                break

        # Save feedback if all questions are answered
        if len(st.session_state.feedback_data) == 8:
            save_feedback(st.session_state.feedback_data)
            st.session_state.feedback_data = {}
            st.success("Feedback submitted successfully!")
        
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

