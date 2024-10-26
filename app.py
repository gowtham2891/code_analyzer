import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from datetime import datetime
import time
from dotenv import load_dotenv
import logging
import json


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("code_wizard.log"),  # Save logs to a file
        logging.StreamHandler()  # Ensure logs are captured in terminal
    ]
)
logger = logging.getLogger('CodeWizard')

# Function to log user interactions with consistent formatting
def log_interaction(username, interaction_type, content):
    """Log user interactions with detailed formatting."""
    log_message = f"{datetime.now().isoformat()} - {username} - {interaction_type}: {content}"
    logger.info(log_message)

# Function to log code submissions
def log_code_submission(code: str, username: str):
    """Log code submissions with proper formatting."""
    logger.info(f"Code Submission from {username}")
    logger.info("-" * 80)  # Delimiter
    logger.info(code)
    logger.info("-" * 80)  # Delimiter

# Function to log analysis results
def log_analysis(username: str, analysis_type: str, content: str):
    """Log analysis results with proper formatting."""
    logger.info(f"Analysis Result for {username} - Type: {analysis_type}")
    logger.info("-" * 80)
    logger.info(content)
    logger.info("-" * 80)
    

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Page configuration
st.set_page_config(
    page_title="Code Wizard",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Hides the Streamlit toolbar */
    .stApp > header {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)


# Enhanced CSS with modern styling
st.markdown("""
<style>
    /* Modern styling */
    .stApp {
        background-color: #f8fafc;
    }

    .welcome-container {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 1rem;
        margin-bottom: 2rem;
        animation: fadeIn 0.8s ease-out;
    }

    .welcome-title {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    .stats-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }

    .stats-card:hover {
        transform: translateY(-5px);
    }

    .stat-item {
        display: inline-block;
        margin: 0 1rem;
        text-align: center;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Code area styling */
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        font-size: 0.9rem;
        background-color: #f8fafc;
    }

    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }

    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
    }

    /* Additional styling for chat interface */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s ease-out;
    }

    .user-message {
        background-color: #e0f2fe;
        margin-left: 2rem;
    }

    .assistant-message {
        background-color: #f0fdf4;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'code_submitted' not in st.session_state:
    st.session_state.code_submitted = False
if 'current_code' not in st.session_state:
    st.session_state.current_code = ""
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'is_code_context' not in st.session_state:
    st.session_state.is_code_context = True
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
    log_interaction("SYSTEM", "session_start", f"New session started at {st.session_state.session_start}")
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = 0
if 'code_analyses' not in st.session_state:
    st.session_state.code_analyses = 0

def show_welcome_screen():
    """Display the welcome screen and handle user name input."""
    st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">🪄 Welcome to Code Wizard</h1>
            <p style="font-size: 1.2rem; color: #4b5563;">Your magical companion for code analysis and improvement</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("welcome_form"):
        name = st.text_input(
            "🧙‍♂️ What's your name, fellow wizard?",
            placeholder="Enter your name to begin..."
        )
        submitted = st.form_submit_button("✨ Begin Your Coding Journey", use_container_width=True)
        
        if submitted:
            if len(name.strip()) >= 2:
                st.session_state.user_name = name
                log_interaction(name, "login", "User logged in successfully")
                st.success(f"Welcome aboard, {name}! 🌟")
                time.sleep(1)
                st.rerun()
            else:
                log_interaction("SYSTEM", "login_failed", "Invalid name attempt - less than 2 characters")
                st.warning("🪄 Please enter a valid name (at least 2 characters)")


def show_user_stats():
    """Display user session statistics and log detailed session information."""
    session_duration = datetime.now() - st.session_state.session_start
    duration_mins = int(session_duration.total_seconds() / 60)
    
    # Log detailed session statistics
    session_stats = {
        'user': st.session_state.user_name,
        'duration_minutes': duration_mins,
        'questions_asked': st.session_state.questions_asked,
        'code_analyses': st.session_state.code_analyses,
        'session_start': st.session_state.session_start.isoformat(),
        'chat_history_length': len(st.session_state.conversation_history)
    }
    
    logger.info(
        "Session Statistics",
        delimiter='---Stats Begin---',
        content=json.dumps(session_stats, indent=2)
    )
    
    # Display stats in UI
    st.markdown("""
        <div class="stats-card">
            <div class="stat-item">
                <h3>⏱️ Session Duration</h3>
                <p>{} mins</p>
            </div>
            <div class="stat-item">
                <h3>❓ Questions Asked</h3>
                <p>{}</p>
            </div>
            <div class="stat-item">
                <h3>🔍 Code Analyses</h3>
                <p>{}</p>
            </div>
        </div>
    """.format(duration_mins, st.session_state.questions_asked, st.session_state.code_analyses), 
    unsafe_allow_html=True)

def initialize_llm():
    """Initialize and return the Groq LLM client."""
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not found in environment variables")
        st.error("⚠️ GROQ_API_KEY not found. Please set it in your environment variables.")
        st.stop()
    
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="mixtral-8x7b-32768",
        temperature=0.7
    )

def analyze_code(code: str, query: str = None, is_initial_analysis: bool = True):
    """Analyze code using the Groq LLM."""
    try:
        llm = initialize_llm()
        
        if is_initial_analysis:
            log_interaction(st.session_state.user_name, "initial_analysis", "Starting initial code analysis")
            prompt_template = """
            As a coding expert, analyze this code:
            
            ```
            {code}
            ```
            
            Provide a detailed yet engaging analysis including:
            1. 🎯 Overview of what the code does
            2. 🔍 Key components and their functionality
            3. 💡 Notable programming concepts used
            4. ⚡ Performance considerations
            5. 🛡️ Security considerations if applicable
            6. ✨ Potential improvements and best practices
            
            Make your explanation clear, engaging, and actionable, using emojis and formatting to enhance readability.
            """
         else:
            log_interaction(st.session_state.user_name, "follow_up_question", query)
            prompt_template = """
            Question about the code:
            ```
            {code}
            ```
            
            Question: {query}
            
            Previous context:
            {context}
            
            Provide a focused, clear answer with relevant code references and examples where applicable.
            Use emojis and formatting to make the explanation more engaging.
            """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        
        context = "\n".join([f"{msg['role']}: {msg['content']}" 
                           for msg in st.session_state.conversation_history[-3:]])
        
        response = chain.invoke({
            "code": code,
            "query": query if query else "",
            "context": context
        })
        
        # Log the analysis result
        log_analysis(
            st.session_state.user_name,
            "initial_analysis" if is_initial_analysis else "follow_up",
            response["text"]
        )
        
        return response["text"]
    except Exception as e:
        error_msg = f"Error in code analysis: {str(e)}"
        logger.error(error_msg)
        st.error(error_msg)
        return None

def general_question(query: str):
    """Handle general programming questions using the Groq LLM."""
    try:
        logger.info(f"Processing general question: {query}")
        llm = initialize_llm()
        
        prompt_template = """
        Answer this programming question:
        Question: {query}
        
        Provide a clear, comprehensive answer with examples where applicable.
        Use emojis and formatting to make the explanation engaging.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        
        response = chain.invoke({"query": query})
        logger.info("Successfully generated response for general question")
        return response["text"]
    except Exception as e:
        logger.error(f"Error processing general question: {str(e)}")
        st.error(f"Error processing question: {str(e)}")
        return None

def main():
    """Main application logic."""
    logger.info("Starting Code Wizard application")
    
    if not st.session_state.user_name:
        show_welcome_screen()
    else:
        # Log session statistics periodically
        session_stats = {
            'user': st.session_state.user_name,
            'duration_minutes': int((datetime.now() - st.session_state.session_start).total_seconds() / 60),
            'questions_asked': st.session_state.questions_asked,
            'code_analyses': st.session_state.code_analyses,
            'session_start': st.session_state.session_start.isoformat(),
            'chat_history_length': len(st.session_state.conversation_history)
        }
        logger.info(f"Session Statistics: {json.dumps(session_stats, indent=2)}")
def main():
    """Main application logic with comprehensive logging."""
    logger.info("Starting Code Wizard application")
    
    if not st.session_state.user_name:
        show_welcome_screen()
    else:
        # Display welcome header
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 class="welcome-title">Hello, {st.session_state.user_name}! 🌟</h1>
                <p style="font-size: 1.2rem; color: #4b5563;">Ready to make some coding magic? ✨</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Log session statistics
        session_duration = datetime.now() - st.session_state.session_start
        session_stats = {
            'user': st.session_state.user_name,
            'duration_minutes': int(session_duration.total_seconds() / 60),
            'questions_asked': st.session_state.questions_asked,
            'code_analyses': st.session_state.code_analyses,
            'session_start': st.session_state.session_start.isoformat(),
            'chat_history_length': len(st.session_state.conversation_history)
        }
        logger.info(f"Current Session Statistics:\n{json.dumps(session_stats, indent=2)}")
        
        show_user_stats()
        
        # Main content area
        if not st.session_state.code_submitted:
            st.markdown("### 📝 Let's analyze your code!")
            code_input = st.text_area(
                "",
                height=300,
                placeholder="Paste your code here and let's make it better together! 🚀"
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔍 Analyze Code", type="primary", use_container_width=True):
                    if code_input.strip():
                        # Log code submission
                        log_interaction(st.session_state.user_name, "code_submission", "User submitted code for analysis")
                        log_code_submission(code_input, st.session_state.user_name)
                        
                        with st.spinner("🤖 Analyzing your code..."):
                            st.session_state.current_code = code_input
                            explanation = analyze_code(code_input, is_initial_analysis=True)
                            
                            if explanation:
                                st.session_state.code_submitted = True
                                log_interaction(st.session_state.user_name, "analysis_complete", "Initial code analysis completed")
                                
                                # Update conversation history
                                st.session_state.messages.append({
                                    "role": "user",
                                    "content": "Please analyze this code."
                                })
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": explanation
                                })
                                st.session_state.conversation_history.extend(st.session_state.messages[-2:])
                                st.session_state.code_analyses += 1
                                
                                log_interaction(
                                    st.session_state.user_name, 
                                    "conversation_update",
                                    "Added initial analysis to conversation history"
                                )
                                st.rerun()
                    else:
                        log_interaction(st.session_state.user_name, "error", "Attempted to analyze empty code")
                        st.warning("⚠️ Please enter some code before analysis.")
        else:
            # Code viewer with syntax highlighting
            with st.expander("📄 View Current Code", expanded=False):
                st.code(st.session_state.current_code, language="python")
                if st.button("📝 Submit New Code"):
                    log_interaction(st.session_state.user_name, "action", "Requested to submit new code")
                    st.session_state.code_submitted = False
                    st.rerun()
            
            # Chat interface
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input("💭 Ask me anything about the code..."):
                log_interaction(st.session_state.user_name, "question", prompt)
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.questions_asked += 1
                
                with st.spinner("🤔 Thinking..."):
                    if st.session_state.is_code_context:
                        response = analyze_code(
                            st.session_state.current_code,
                            prompt,
                            is_initial_analysis=False
                        )
                    else:
                        response = general_question(prompt)
                        
                    if response:
                        log_interaction(
                            st.session_state.user_name,
                            "response",
                            f"Generated response for: {prompt[:50]}..."
                        )
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        st.session_state.conversation_history.extend([
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": response}
                        ])
                        st.rerun()

        # Sidebar settings
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            
            # Context mode toggle
            previous_context = st.session_state.is_code_context
            st.session_state.is_code_context = st.toggle(
                "Code-specific questions",
                value=st.session_state.is_code_context,
                help="Toggle between code-specific and general programming questions"
            )
            
            # Log context mode changes
            if previous_context != st.session_state.is_code_context:
                log_interaction(
                    st.session_state.user_name,
                    "settings_change",
                    f"Changed context mode to: {'code-specific' if st.session_state.is_code_context else 'general'}"
                )
            
            # Clear chat button
            if st.button("🗑️ Clear Chat"):
                if st.session_state.messages:
                    log_interaction(st.session_state.user_name, "action", "Cleared chat history")
                    
                    # Clear all session state variables
                    st.session_state.messages = []
                    st.session_state.code_submitted = False
                    st.session_state.current_code = ""
                    st.session_state.conversation_history = []
                    
                    st.success("✨ Chat cleared!")
                    st.rerun()
            
            # Session end button
            if st.button("🚪 End Session"):
                log_interaction(st.session_state.user_name, "session_end", "User ended session")
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    try:
        logger.info("Starting Code Wizard application")
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("An unexpected error occurred. Please try again.")
