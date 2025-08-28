import streamlit as st
import json
import time
import requests
from factool import Factool

# Page configuration
st.set_page_config(
    page_title="Factool+ Demo - KBQA Fact Checking",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SearXNG connection test
def check_searxng_connection(base_url="http://localhost:8888"):
    """Check if the local SearXNG instance is reachable."""
    try:
        response = requests.get(base_url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

searxng_available = check_searxng_connection()
if not searxng_available:
    st.warning("Cannot connect to local SearXNG instance. Fact-checking is disabled until connection is restored.")

# Initialise session state

if 'factool_instance' not in st.session_state:
    st.session_state.factool_instance = None
if 'results_history' not in st.session_state:
    st.session_state.results_history = []

# Factool Initialisation
def initialize_factool(model_name):
    """Initialise Factool+ instance with selected model"""
    try:
        with st.spinner(f"Initialising Factool+ with {model_name}..."):
            factool_instance = Factool(model_name)
        st.success(f"Factool+ initialised with {model_name}")
        return factool_instance
    except Exception as e:
        st.error(f"Error initialising Factool+: {str(e)}")
        return None

# Result Formatting & Display 
def format_results(results):
    if not results or 'detailed_information' not in results:
        return None
    detailed_info = results['detailed_information'][0]
    return {
        'prompt': detailed_info.get('prompt', ''),
        'response': detailed_info.get('response', ''),
        'response_level_factuality': detailed_info.get('response_level_factuality', False),
        'claim_level_factuality': detailed_info.get('claim_level_factuality', []),
        'reasoning': detailed_info.get('reasoning', ''),
        'avg_claim_factuality': results.get('average_claim_level_factuality', 0),
        'avg_response_factuality': results.get('average_response_level_factuality', 0)
    }

def display_results(results):
    if not results:
        return
    st.subheader("Overall Results")
    col1, col2 = st.columns(2)
    with col1:
        factuality_color = "green" if results['response_level_factuality'] else "red"
        st.markdown(f"**Response Factuality**: <span style='color:{factuality_color}'>{'Factual' if results['response_level_factuality'] else 'Not Factual'}</span>", unsafe_allow_html=True)
    with col2:
        st.metric("Average Claim Factuality", f"{results['avg_claim_factuality']:.2%}")
    st.subheader("Query & Response")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Original Question:**")
        st.info(results['prompt'])
    with col2:
        st.markdown("**Response Being Checked:**")
        st.info(results['response'])
    st.subheader("Detailed Analysis")
    if results['reasoning']:
        st.markdown("**Reasoning:**")
        st.write(results['reasoning'])
    if results['claim_level_factuality']:
        st.markdown("**Claim-by-Claim Analysis:**")
        for i, claim in enumerate(results['claim_level_factuality']):
            if claim is not None:
                claim_status = "Factual" if claim.get('factuality', False) else "Not Factual"
                with st.expander(f"Claim {i+1}: {claim_status}"):
                    if 'claim' in claim:
                        st.write(f"**Claim:** {claim['claim']}")
                    if 'reasoning' in claim:
                        st.write(f"**Reasoning:** {claim['reasoning']}")
                    if 'error' in claim:
                        st.write(f"**Error:** {claim['error']}")

# Main UI
st.title("Factool+")
st.markdown("*Fact-checking system powered by SearXNG*")

# Sidebar configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "OpenAI API Key:",
    type="password",
    help="Enter your OpenAI API key. You can find it at https://platform.openai.com/account/api-keys",
    placeholder="sk-..."
)
if api_key:
    import os
    os.environ['OPENAI_API_KEY'] = api_key

model_options = ["gpt-3.5-turbo", "gpt-4"]
selected_model = st.sidebar.selectbox("Select Foundation Model:", model_options, index=0)

if st.sidebar.button("Initialize Factool+", type="primary", disabled=not api_key):
    if api_key:
        st.session_state.factool_instance = initialize_factool(selected_model)
    else:
        st.sidebar.error("Please enter your OpenAI API key first")

if st.session_state.factool_instance:
    st.sidebar.success("Factool+ Ready")
elif api_key:
    st.sidebar.info("Click 'Initialise Factool+' to get started")
else:
    st.sidebar.warning("Enter OpenAI API Key to begin")

# Main Content 
if st.session_state.factool_instance:
    st.header("Input Section")
    tab1, tab2 = st.tabs(["Manual Input", "Example Templates"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            prompt = st.text_area("Question/Prompt:", placeholder="Enter the question or prompt here...", height=100)
        with col2:
            response = st.text_area("Response to Check:", placeholder="Enter the response that needs fact-checking...", height=100)
    with tab2:
        st.markdown("**Quick Examples:**")
        examples = [
            {"name": "Music Facts", "prompt": "Who wrote Purple Haze?", "response": "The song \"Purple Haze\" was written by Jimi Hendrix. It was released in 1967 and is one of his most famous tracks."},
            {"name": "Historical Facts", "prompt": "When did World War II end?", "response": "World War II ended on September 2, 1945, when Japan formally surrendered aboard the USS Missouri in Tokyo Bay."},
            {"name": "Science Facts", "prompt": "What is the speed of light?", "response": "The speed of light in a vacuum is approximately 300,000 kilometers per second, which is exactly 299,792,458 meters per second."}
        ]
        for example in examples:
            if st.button(f"Load: {example['name']}"):
                prompt = example['prompt']
                response = example['response']
                st.rerun()

    # Run fact checking
    run_disabled = not (prompt and response and searxng_available)
    if st.button("Run Fact Check", type="primary", disabled=run_disabled):
        with st.spinner("Fact-checking in progress..."):
            try:
                inputs = [{"prompt": prompt, "response": response, "category": "kbqa"}]
                start_time = time.time()
                results = st.session_state.factool_instance.run(inputs)
                end_time = time.time()
                formatted_results = format_results(results)
                if formatted_results:
                    formatted_results['processing_time'] = end_time - start_time
                    st.session_state.results_history.insert(0, formatted_results)
                    if len(st.session_state.results_history) > 10:
                        st.session_state.results_history = st.session_state.results_history[:10]
                st.success(f"Fact-checking completed in {end_time - start_time:.2f} seconds")
            except Exception as e:
                st.error(f"Error during fact-checking: {str(e)}")
    elif not searxng_available:
        st.warning("Fact-checking disabled because SearXNG is not reachable.")

    # Results display
    if st.session_state.results_history:
        st.header("Results")
        st.subheader("Latest Result")
        display_results(st.session_state.results_history[0])
        if len(st.session_state.results_history) > 1:
            st.subheader("Previous Results")
            for i, result in enumerate(st.session_state.results_history[1:], 1):
                with st.expander(f"Result {i}: {result['prompt'][:50]}..."):
                    display_results(result)
        st.subheader("Export Results")
        if st.button("Download Results as TXT"):
            txt_data = "\n\n".join([str(item) for item in st.session_state.results_history])
            st.download_button(
                label="Download TXT File",
                data=txt_data,
                file_name=f"factool_results_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
else:
    st.markdown("""
    This demo showcases a fact-checking system that uses:
    - **KBQA Pipeline**: Knowledge Base Question Answering for fact verification
    - **SearXNG Backend**: Self-hosted search engine for information retrieval
    - **LLM Integration**: Various GPT foundation models for NLP tasks
    """)
    st.info("Please initialize Factool using the sidebar to get started.")

# Footer
st.markdown("---")
st.markdown("*MSc Project Demo - Factool+*")
