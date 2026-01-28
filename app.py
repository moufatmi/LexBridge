import streamlit as st
import google.generativeai as genai
import json

# --- Page Configuration (Must be first) ---
st.set_page_config(
    page_title="LexBridge | AI Legal Comparator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for "Premium Legal Tech" Look ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;600&display=swap');

    /* Global Font Settings */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Headings: The "Legal Authority" Look */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        font-weight: 700 !important;
        color: #f0f2f6; /* Light gray for dark mode compatibility */
    }
    
    h1 {
        font-size: 3rem !important;
        background: -webkit-linear-gradient(45deg, #ffffff, #a0a0a0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Cards/Containers */
    .stTextInput, .stTextArea, .stSelectbox {
        border-radius: 8px;
    }

    /* Primary Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        border: none;
        color: white;
        padding: 0.6rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(75, 108, 183, 0.4);
    }
    
    /* Quick Action Buttons (Secondary) */
    .quick-btn > button {
        background: transparent;
        border: 1px solid #4b6cb7;
        color: #4b6cb7;
    }

    /* Custom Alert/Info Box */
    .stAlert {
        border-left: 4px solid #4b6cb7;
        background-color: rgba(75, 108, 183, 0.1);
    }
    
</style>
""", unsafe_allow_html=True)

def main():
    # --- Session State Initialization ---
    if 'ui_labels' not in st.session_state:
        st.session_state['ui_labels'] = {
            "title": "LexBridge",
            "subtitle": "Bridging legal systems through **Delta Learning**. We focus on what changes.",
            "settings": "Configuration",
            "api_key_label": "Gemini API Key",
            "model_label": "Reasoning Model",
            "interface_lang_label": "Interface Language",
            "translate_btn": "🌐 Translate Interface",
            "source_label": "Source Jurisdiction",
            "target_label": "Target Jurisdiction",
            "concept_label": "Legal Scenario / Clause",
            "analyze_btn": "⚡ Run Legal Analysis",
            "analysis_header": "Legal Delta Analysis",
            "spinner": "Consulting the digital experts...",
            "source_ph": "e.g., France (Civil Law)",
            "target_ph": "e.g., UK (Common Law)",
            "concept_ph": "Paste a contract clause or describe a legal situation..."
        }
    
    # Default values for inputs
    if 'input_source' not in st.session_state: st.session_state['input_source'] = ""
    if 'input_target' not in st.session_state: st.session_state['input_target'] = ""
    if 'input_concept' not in st.session_state: st.session_state['input_concept'] = ""

    ui = st.session_state['ui_labels']

    # --- Sidebar ---
    with st.sidebar:
        st.title(f"⚙️ {ui['settings']}")
        
        # API Key (Password type)
        api_key = st.text_input(ui["api_key_label"], type="password", help="Get your key at aistudio.google.com")
        if not api_key:
            st.info("💡 Tip: You need an API key to see the magic.")

        st.markdown("---")
        
        # Model Selection
        model_options = [
            "gemini-2.0-flash-lite-preview-02-05",
            "gemini-1.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        selected_model = st.selectbox(ui["model_label"], model_options, index=0)
        
        st.markdown("---")
        
        # Translation
        with st.expander("🌍 Language Settings"):
            target_lang = st.text_input(ui["interface_lang_label"], placeholder="e.g., Spanish, Japanese")
            if st.button(ui["translate_btn"]):
                handle_translation(api_key, selected_model, target_lang)

        st.markdown("---")
        st.markdown("*Built for Gemini 3 Hackathon* 🚀")

    # --- Main Interface ---
    
    # Header Section
    col_head_1, col_head_2 = st.columns([3, 1])
    with col_head_1:
        st.title(ui["title"])
        st.markdown(f"#### {ui['subtitle']}")
    with col_head_2:
        # Placeholder for a logo if they had one
        pass

    st.markdown("---")

    # --- Quick Start / Demos (The "Wow" factor) ---
    st.markdown("### ⚡ Quick Start Scenarios")
    q1, q2, q3 = st.columns(3)
    
    if q1.button("🇫🇷 France vs 🇬🇧 UK: Good Faith"):
        st.session_state['input_source'] = "France (Civil Law)"
        st.session_state['input_target'] = "United Kingdom (Common Law)"
        st.session_state['input_concept'] = "Is there a duty of 'Good Faith' during commercial contract negotiations? Can I pull out of a deal at the last minute without penalty?"
        st.rerun()

    if q2.button("🇺🇸 US vs 🇪🇺 EU: Data Privacy"):
        st.session_state['input_source'] = "United States (California)"
        st.session_state['input_target'] = "European Union (GDPR)"
        st.session_state['input_concept'] = "A company collects email addresses for marketing without explicit opt-in consent. Is this legal?"
        st.rerun()

    if q3.button("🇩🇪 Germany vs 🇺🇸 NY: Force Majeure"):
        st.session_state['input_source'] = "Germany (BGB)"
        st.session_state['input_target'] = "New York (Common Law)"
        st.session_state['input_concept'] = "A supplier cannot deliver goods due to an unforeseen global pandemic. The contract has no Force Majeure clause. Are they liable?"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    # --- Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        source_jurisdiction = st.text_input(ui["source_label"], value=st.session_state['input_source'], placeholder=ui["source_ph"])
    with col2:
        target_jurisdiction = st.text_input(ui["target_label"], value=st.session_state['input_target'], placeholder=ui["target_ph"])

    concept = st.text_area(ui["concept_label"], value=st.session_state['input_concept'], height=150, placeholder=ui["concept_ph"])

    # --- Analysis Action ---
    if st.button(ui["analyze_btn"], type="primary", use_container_width=True):
        if not api_key:
            st.error("🔒 Please enter your Gemini API Key in the sidebar to proceed.")
            return
        if not concept.strip():
            st.warning("⚠️ Please describe a legal scenario first.")
            return

        run_analysis(api_key, selected_model, source_jurisdiction, target_jurisdiction, concept, ui)

def handle_translation(api_key, model_name, target_lang):
    """Translates the UI labels using Gemini."""
    if not api_key or not target_lang:
        st.error("Missing API Key or Target Language.")
        return

    try:
        genai.configure(api_key=api_key)
        trans_model = genai.GenerativeModel(model_name)
        
        ui_current = st.session_state['ui_labels']
        
        prompt = f"""
        Translate the values of this JSON to {target_lang}.
        Keep keys identical. Return ONLY raw JSON.
        
        JSON:
        {json.dumps(ui_current)}
        """
        
        with st.spinner(f"Translating interface to {target_lang}..."):
            response = trans_model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            st.session_state['ui_labels'] = json.loads(clean_json)
            st.rerun()
            
    except Exception as e:
        st.error(f"Translation failed: {e}")

def run_analysis(api_key, model_name, source, target, concept, ui):
    """Core analysis logic."""
    try:
        genai.configure(api_key=api_key)
        
        # System instruction: Persona & structured output
        sys_prompt = """
        You are LexBridge, a senior legal consultant specializing in Comparative Law.
        Your goal is 'Delta Learning': Do not explain what is the same. Explain ONLY the difference.
        
        Structure your response in Markdown with these EXACT Level 2 headers:
        ## 🚨 The Core Divergence
        (A 1-sentence summary of the fundamental difference)
        
        ## 🧠 Deep Dive: The Logic Shift
        (Explain WHY the systems differ. e.g., 'Civil law focuses on code, Common law on precedent')
        
        ## 💡 Practical Implication
        (Result for the user: 'In France you are liable, in UK you are free to walk away')
        
        Use concise professional language. simple yet authoritative.
        """
        
        model = genai.GenerativeModel(model_name, system_instruction=sys_prompt)
        
        user_prompt = f"""
        Compare these two jurisdictions:
        Source: {source}
        Target: {target}
        
        Scenario / Concept:
        {concept}
        """
        
        with st.spinner(ui["spinner"]):
            response = model.generate_content(user_prompt)
            
            # --- Result Display ---
            st.markdown("---")
            st.subheader(ui["analysis_header"])
            
            # Using Tabs for cleaner organization of the output if the model follows instruction
            # Since we can't guarantee 100% split, we show the whole markdown with our nice headers.
            # But let's wrap it in a container border
            
            with st.container():
                st.markdown(response.text)
                
            st.success("Analysis Complete.")

    except Exception as e:
        st.error(f"Analysis Error: {e}")

if __name__ == "__main__":
    main()
