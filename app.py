import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
# Add this after your existing imports
import logging
from datetime import datetime

# Add this right after the imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Print to console
        logging.FileHandler('codelens_activity.log')  # Save to file
    ]
)
logger = logging.getLogger(__name__)



# Page configuration
st.set_page_config(
    page_title="CodeLens AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')


st.markdown("""
<style>
    /* CSS Reset and Variables */
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1d4ed8;
        --secondary: #64748b;
        --success: #059669;
        --danger: #dc2626;
        --warning: #d97706;
        --background: #f8fafc;
        --surface: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Global Styles */
    .stApp {
        background: var(--background);
    }

    /* Typography System */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: -0.025em;
    }

    p, span, div {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* Layout Components */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    /* Card Component */
    .card {
        background: var(--surface);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                    0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
                    0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        padding: 4rem 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }

    .hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23ffffff" opacity="0.1" width="100" height="100"/></svg>');
        opacity: 0.1;
    }

    .hero h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        animation: slideUp 0.6s ease-out;
    }

    .hero p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        max-width: 600px;
        animation: slideUp 0.6s ease-out 0.1s;
    }

    /* Chat Interface */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
        height: 60vh;
        overflow-y: auto;
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
        border-radius: var(--border-radius);
        border: 1px solid rgba(0, 0, 0, 0.1);
    }

    .message {
        max-width: 80%;
        padding: 1rem;
        border-radius: 1rem;
        animation: messageSlide 0.3s ease-out;
    }

    .message.user {
        background: var(--primary);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0.25rem;
    }

    .message.assistant {
        background: var(--surface);
        border: 1px solid rgba(0, 0, 0, 0.1);
        margin-right: auto;
        border-bottom-left-radius: 0.25rem;
    }

    /* Code Editor */
    .code-editor {
        background: #1e1e1e;
        border-radius: var(--border-radius);
        padding: 1rem;
        position: relative;
    }

    .code-editor::before {
        content: '• • •';
        position: absolute;
        top: 0.5rem;
        left: 1rem;
        color: #666;
        letter-spacing: 2px;
    }

    /* Button Styles */
    .stButton button {
        width: 100%;
        color: white !important;
        background-color: var(--primary) !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: var(--border-radius) !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    .stButton button:hover {
        background-color: var(--primary-dark) !important;
        color: white !important;
        border: none !important;
        transform: translateY(-2px);
    }

    /* Ensure text and emoji are visible */
    .stButton button p {
        color: white !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* Streamlit specific overrides */
    .stButton button:active, 
    .stButton button:focus {
        color: white !important;
        background-color: var(--primary-dark) !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }

    /* Maintain primary button original styles for other uses */
    .primary-button {
        background: var(--primary);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: var(--border-radius);
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: var(--transition);
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .primary-button:hover {
        background: var(--primary-dark);
        transform: translateY(-1px);
    }

    /* Input Fields */
    .input-field {
        width: 100%;
        padding: 1rem;
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: var(--border-radius);
        transition: var(--transition);
        font-size: 1rem;
        background: white;
    }

    .input-field:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }

    /* Loading States */
    .loading {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: var(--border-radius);
        background: rgba(37, 99, 235, 0.1);
        color: var(--primary);
        animation: pulse 2s infinite;
    }

    /* Badges */
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .badge.success {
        background: rgba(5, 150, 105, 0.1);
        color: var(--success);
    }

    .badge.warning {
        background: rgba(217, 119, 6, 0.1);
        color: var(--warning);
    }

    /* Error Card */
    .error-card {
        background: #fee2e2;
        border: 1px solid #ef4444;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
    }

    .error-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }

    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: var(--transition);
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Code Stats */
    .code-stats {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }

    .stat-item {
        background: white;
        padding: 1rem;
        border-radius: var(--border-radius);
        flex: 1;
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--primary);
    }

    /* Toast Notifications */
    .toast {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        padding: 1rem 2rem;
        border-radius: var(--border-radius);
        background: white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-out;
    }

    .toast.success {
        border-left: 4px solid var(--success);
    }

    .toast.error {
        border-left: 4px solid var(--danger);
    }

    /* Animations */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes messageSlide {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }

    @keyframes shake {
        10%, 90% { transform: translate3d(-1px, 0, 0); }
        20%, 80% { transform: translate3d(2px, 0, 0); }
        30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
        40%, 60% { transform: translate3d(4px, 0, 0); }
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .chat-container {
            height: 70vh;
        }

        .message {
            max-width: 90%;
        }

        .hero {
            padding: 2rem 1rem;
        }

        .hero h1 {
            font-size: 2rem;
        }
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Initializing session state
# Add these with your other session state initializations
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
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

def initialize_llm():
    """Initialize the LLM with error handling and status indicators"""
    try:
        if not GROQ_API_KEY:
            st.error("""
                <div class="error-card">
                    <div class="error-icon">⚠️</div>
                    <h3>API Key Missing</h3>
                    <p>Please set your GROQ_API_KEY in the environment variables.</p>
                </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        return ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="mixtral-8x7b-32768",
            temperature=0.7
        )
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        st.stop()

def analyze_code(code: str, query: str = None, is_initial_analysis: bool = True):
    """Enhanced code analysis with better formatting and structure"""
    try:
        llm = initialize_llm()
        
        if is_initial_analysis:
            prompt_template = """
            Analyze this code with a professional and structured approach:
            
            ```
            {code}
            ```
            
            Please provide a comprehensive analysis following this structure:
            
            ## 🎯 Overview
            [Brief description of the code's purpose and functionality]
            
            ## 🔍 Key Components
            - [Component 1]
            - [Component 2]
            ...
            
            ## 💡 Implementation Highlights
            - [Notable feature 1]
            - [Notable feature 2]
            ...
            
            ## ⚡ Performance Analysis
            - [Performance consideration 1]
            - [Performance consideration 2]
            ...
            
            ## 🛡️ Security Considerations
            - [Security aspect 1]
            
            
            - [Security aspect 2]
            ...
            
            ## ✨ Recommendations
            1. [Improvement suggestion 1]
            2. [Improvement suggestion 2]
            ...
            
            Use clear explanations and provide practical examples where relevant.
            """
        else:
            prompt_template = """
            Context: You're analyzing this code:
            ```
            {code}
            ```
            
            Question: {query}
            
            Previous context:
            {context}
            
            Please provide:
            1. A direct answer to the question
            2. Relevant code examples if applicable
            3. Best practices and recommendations
            4. Any potential gotchas or considerations
            
            Format your response with clear sections and use relevant emojis for better readability.
            """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        
      
        context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in st.session_state.conversation_history[-3:]
        ])
        
        response = chain.invoke({
            "code": code,
            "query": query if query else "",
            "context": context
        })
        
        return response["text"]
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None

def general_question(query: str):
    """Handle general programming questions with enhanced formatting"""
    try:
        llm = initialize_llm()
        
        prompt_template = """
        Answer this programming question with professional insight:
        
        Question: {query}
        
        Please structure your response with:
        1. A clear, direct answer
        2. Practical examples and code snippets
        3. Best practices and common pitfalls
        4. Additional resources or related concepts
        
        Use appropriate formatting and emojis for better readability.
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        
        response = chain.invoke({"query": query})
        return response["text"]
    except Exception as e:
        st.error(f"Error processing question: {str(e)}")
        return None

def display_feature_grid():
    """Display key features in a grid layout"""
    st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">
                <h3>🤖 AI-Powered Analysis</h3>
                <p>Get instant insights into your code structure and quality</p>
            </div>
            <div class="feature-card">
                <h3>📊 Performance Metrics</h3>
                <p>Understand your code's efficiency and areas for improvement</p>
            </div>
            <div class="feature-card">
                <h3>🛡️ Security Checks</h3>
                <p>Identify potential security vulnerabilities</p>
            </div>
            <div class="feature-card">
                <h3>💡 Smart Suggestions</h3>
                <p>Receive personalized recommendations for better code</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_code_stats(code: str):
    """Display code statistics in a visually appealing way"""
    lines = len(code.split('\n'))
    chars = len(code)
    functions = len([line for line in code.split('\n') if 'def ' in line])
    
    st.markdown(f"""
        <div class="code-stats">
            <div class="stat-item">
                <div class="stat-value">{lines}</div>
                <div class="stat-label">Lines</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{functions}</div>
                <div class="stat-label">Functions</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{chars}</div>
                <div class="stat-label">Characters</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_toast(message: str, type: str = "success"):
    """Show a toast notification"""
    st.markdown(f"""
        <div class="toast {type}">
            {message}
        </div>
    """, unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="hero">
        <h1>⚡ CodeLens AI</h1>
        <p>Transform your code with AI-powered insights. Get instant analysis, suggestions, and answers to your programming questions.</p>
    </div>
""", unsafe_allow_html=True)

def display_code_input():
    st.markdown("""
        <div class="card">
            <h2>📝 Code Analysis</h2>
            <p>Paste your code below and let AI analyze it for you.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Add CSS to control the height of the code input area
    st.markdown("""
        <style>
        .stTextArea textarea {
            min-height: 300px !important;
            background-color: #f8f9fa;
            font-family: monospace;
        }
        
        /* Hide empty code section */
        .empty-code-section {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    code_input = st.text_area(
        "",
        height=300,
        key="code_input",
        placeholder="// Paste your code here...",
        help="Your code will be analyzed for patterns, best practices, and potential improvements."
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze Code", type="primary", use_container_width=True):
            if code_input.strip():
                with st.spinner("🤖 Analyzing code..."):
                    process_code(code_input)
            else:
                st.warning("⚠️ Please enter some code to analyze.")
                
    # Only show code section if there's actual code
    if st.session_state.get('current_code'):
        with st.expander("📄 Current Code", expanded=False):
            st.code(st.session_state.current_code, language="python")

def display_chat_interface():
    # Code viewer with syntax highlighting
    with st.expander("📄 Current Code", expanded=False):
        st.code(st.session_state.current_code, language="python")
        if st.button("📝 New Code Analysis"):
            st.session_state.code_submitted = False
            st.rerun()

    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        role_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
        st.markdown(f"""
            <div class="message {msg['role']}">
                {role_icon} {msg['content']}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("💭 Ask a question about your code..."):
        handle_chat_input(prompt)

def authenticate_user():
    """Handle user authentication"""
    if not st.session_state.authenticated:
        st.markdown("""
            <div class="hero">
                <h1>👋 Welcome to CodeLens AI</h1>
                <p>Please enter your name to continue.</p>
            </div>
        """, unsafe_allow_html=True)
        
        
        with st.container():
            username = st.text_input("Enter your name", key="auth_username")
            if st.button("Continue", type="primary"):
                if username.strip():
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    logger.info(f"New user authenticated: {username}")
                    st.rerun()
                else:
                    st.error("Please enter your name to continue")
        return False
    return True


def process_code(code):
    try:
        llm = initialize_llm()
        logger.info(f"User {st.session_state.username} submitted new code for analysis. Length: {len(code)} characters")
        explanation = analyze_code(code)
        if explanation:
            st.session_state.code_submitted = True
            st.session_state.current_code = code
            st.session_state.messages.extend([
                {"role": "user", "content": "Please analyze this code."},
                {"role": "assistant", "content": explanation}
            ])
            st.session_state.conversation_history.extend(st.session_state.messages[-2:])
            st.balloons()
            st.rerun()
    except Exception as e:
        logger.error(f"Error during code analysis for user {st.session_state.username}: {str(e)}")
        st.error(f"Error analyzing code: {str(e)}")


def handle_chat_input(prompt):
    logger.info(f"User {st.session_state.username} sent message: {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("🤔 Thinking..."):
        try:
            if st.session_state.is_code_context:
                response = analyze_code(st.session_state.current_code, prompt, False)
            else:
                response = general_question(prompt)
                
            if response:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })
                st.rerun()
                logger.info(f"Successfully generated response for user {st.session_state.username}")
        except Exception as e:
            logger.error(f"Error generating response for user {st.session_state.username}: {str(e)}")
            st.error("Failed to generate response. Please try again.")

    
            

def main():
    if not authenticate_user():
        return
        
    logger.info(f"User {st.session_state.username} accessed main interface")
    if not st.session_state.get('current_code'):
        display_feature_grid()
        display_code_input()
    else:
        display_chat_interface()
        
    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; padding: 1rem; border-top: 1px solid rgba(0,0,0,0.1);">
            <p>Made with ❤️ for developers everywhere</p>
        </div>
    """, unsafe_allow_html=True)

# Sidebar
# In your sidebar section, add this at the top:
with st.sidebar:
    if st.session_state.authenticated:
        st.markdown(f"""
            <div class="card">
                <h3>👋 Welcome, {st.session_state.username}!</h3>
            </div>
        """, unsafe_allow_html=True)    
    st.markdown("### 🔄 Question Mode")
    st.session_state.is_code_context = st.toggle(
        "Code-specific questions",
        value=st.session_state.is_code_context,
        help="Toggle between code-specific and general questions"
    )
    
    if st.button("🗑️ Clear History", type="secondary"):
        if st.session_state.messages:
            if st.button("🚫 Confirm Clear"):
                st.session_state.messages = []
                st.session_state.code_submitted = False
                st.session_state.current_code = ""
                st.session_state.conversation_history = []
                st.success("✨ History cleared!")
                st.rerun()

    with st.expander("ℹ️ Help"):
        st.markdown("""
            ### Quick Tips
            1. 📝 Paste your code in the editor
            2. 🔍 Get instant AI analysis
            3. 💬 Ask specific questions
            4. 🔄 Switch between modes
            5. 📱 Works on all devices
        """)

if __name__ == "__main__":
    logger.info("Application started")
    main()