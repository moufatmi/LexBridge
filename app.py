import streamlit as st
import google.generativeai as genai
import json
import os

# Try importing OpenAI, handle if missing
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

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
        color: #f0f2f6; 
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
            "settings": "Settings",
            "provider_label": "AI Provider",
            "api_key_label": "API Key",
            "test_key_label": "🔑 **Test Key (Gemini Only):**",
            "tip_paste": "💡 Tip: Paste your key to start.",
            "model_label": "Reasoning Model",
            "debug_label": "🔍 Verify Model Availability",
            "lang_settings": "🌍 Language Settings",
            "interface_lang_label": "Interface Language",
            "translate_btn": "🌐 Translate Interface",
            "quick_start_header": "⚡ Quick Start Scenarios",
            "btn_fr_uk": "🇫🇷 France vs 🇬🇧 UK: Good Faith",
            "q1_source": "France (Civil Law)",
            "q1_target": "United Kingdom (Common Law)",
            "q1_concept": "Is there a duty of 'Good Faith' during commercial contract negotiations? Can I pull out of a deal at the last minute without penalty?",
            
            "btn_us_eu": "🇺🇸 US vs 🇪🇺 EU: Data Privacy",
            "q2_source": "United States (California)",
            "q2_target": "European Union (GDPR)",
            "q2_concept": "A company collects email addresses for marketing without explicit opt-in consent. Is this legal?",
            
            "btn_de_ny": "🇩🇪 Germany vs 🇺🇸 NY: Force Majeure",
            "q3_source": "Germany (BGB)",
            "q3_target": "New York (Common Law)",
            "q3_concept": "A supplier cannot deliver goods due to an unforeseen global pandemic. The contract has no Force Majeure clause. Are they liable?",
            
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
    if 'current_language' not in st.session_state: st.session_state['current_language'] = "English"

    ui = st.session_state['ui_labels']
    
    # --- RTL / LTR Logic ---
    # Detect if the current active language is RTL
    rtl_languages = ['arabic', 'ar', 'hebrew', 'he', 'urdu', 'ur', 'persian', 'fa', 'arabe']
    is_rtl = any(lang in st.session_state['current_language'].lower() for lang in rtl_languages)

    if is_rtl:
        st.markdown("""
            <style>
            /* Global RTL Settings */
            .stApp {
                direction: rtl;
                text-align: right;
            }
            
            /* Text Alignment for all standard elements */
            .stMarkdown, .stTextInput, .stTextArea, .stSelectbox, .stButton, p, h1, h2, h3, h4, h5, h6, span, div {
                text-align: right;
            }
            
            /* Ensure inputs are RTL */
            .stTextInput > div > div > input, .stTextArea > div > div > textarea {
                direction: rtl;
                text-align: right;
            }

            /* Fix Sidebar alignment */
            section[data-testid="stSidebar"] {
                direction: rtl;
            }

            /* Fix bullet points */
            ul, ol, li {
                direction: rtl;
                text-align: right;
                margin-right: 1.5em;
                margin-left: 0;
            }
            
            /* Horizontal Blocks (Columns): Ensure they flow Right-to-Left */
            div[data-testid="stHorizontalBlock"] {
                direction: rtl;
            }
            </style>
        """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.header(f"⚙️ {ui['settings']}")
        
        # Provider Selection
        provider = st.selectbox(ui.get("provider_label", "AI Provider"), ["Google Gemini", "OpenAI", "Groq"])
        
        # API Key 
        key_label = f"{provider} {ui['api_key_label']}"
        api_key = st.text_input(key_label, type="password")
        
     

        if not api_key:
            st.info(ui["tip_paste"])

        st.markdown("---")
        
        # Model Selection logic
        if provider == "Google Gemini":
            model_options = [
                "gemini-2.5-flash", 
                "gemini-1.5-pro", 
                "gemini-1.5-flash", 
                "gemini-2.0-flash-exp"
            ]
        elif provider == "OpenAI":
            model_options = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        elif provider == "Groq":
            model_options = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        
        # Add "Other" option to all providers
        model_options.append("Other (Custom)")
        
        selected_option = st.selectbox(ui["model_label"], model_options, index=0)
        
        if selected_option == "Other (Custom)":
            selected_model = st.text_input("Enter Model Name ID", placeholder="e.g., gpt-4-32k")
            if not selected_model:
                st.info("⚠️ Please enter a specific model ID.")
        else:
            selected_model = selected_option
        
        # Debugger (Gemini only for now)
        if provider == "Google Gemini" and st.checkbox(ui["debug_label"]):
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    models = list(genai.list_models())
                    my_models = [m.name.replace("models/", "") for m in models if 'generateContent' in m.supported_generation_methods]
                    st.json(my_models)
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        
        # Translation
        with st.expander(ui["lang_settings"]):
            # Use current language as default value if distinct
            target_lang = st.text_input(ui["interface_lang_label"], placeholder="e.g., Arabic, Spanish")
            if st.button(ui["translate_btn"]):
                handle_translation(api_key, provider, selected_model, target_lang)

        st.markdown("---")
        st.markdown("<div style='text-align: center; color: grey;'>Made by <b>Moussab Fatmi</b> 🇲🇦</div>", unsafe_allow_html=True)

    # --- Main Interface ---
    col_head_1, col_head_2 = st.columns([3, 1])
    with col_head_1:
        st.title(ui["title"])
        st.markdown(f"#### {ui['subtitle']}")

    st.markdown("---")

    # --- Quick Start / Demos ---
    st.markdown(f"### {ui['quick_start_header']}")
    q1, q2, q3 = st.columns(3)
    
    if q1.button(ui["btn_fr_uk"]):
        st.session_state['input_source'] = ui["q1_source"]
        st.session_state['input_target'] = ui["q1_target"]
        st.session_state['input_concept'] = ui["q1_concept"]
        st.rerun()

    if q2.button(ui["btn_us_eu"]):
        st.session_state['input_source'] = ui["q2_source"]
        st.session_state['input_target'] = ui["q2_target"]
        st.session_state['input_concept'] = ui["q2_concept"]
        st.rerun()

    if q3.button(ui["btn_de_ny"]):
        st.session_state['input_source'] = ui["q3_source"]
        st.session_state['input_target'] = ui["q3_target"]
        st.session_state['input_concept'] = ui["q3_concept"]
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True) 

    col1, col2 = st.columns(2)
    with col1:
        source_jurisdiction = st.text_input(ui["source_label"], value=st.session_state['input_source'], placeholder=ui["source_ph"])
    with col2:
        target_jurisdiction = st.text_input(ui["target_label"], value=st.session_state['input_target'], placeholder=ui["target_ph"])

    concept = st.text_area(ui["concept_label"], value=st.session_state['input_concept'], height=150, placeholder=ui["concept_ph"])

    if st.button(ui["analyze_btn"], type="primary", use_container_width=True):
        if not api_key:
            st.error(f"🔒 Please enter your {provider} API Key.")
            return
        if not concept.strip():
            st.warning("⚠️ Please describe a legal scenario first.")
            return

        run_analysis(api_key, provider, selected_model, source_jurisdiction, target_jurisdiction, concept, ui)

def get_system_prompt(source, target):
    return f"""
    ROLE: You are LexBridge, an Elite Comparative Law Architect specializing in the 'Functional Method' of legal comparison.
    CONTEXT: The user is a legal professional transitioning from {{source_jurisdiction}} to {{target_jurisdiction}}.
    OBJECTIVE: Perform a rigorous 'Delta Analysis'. Do NOT define concepts. Focus purely on the structural, procedural, and logical divergences.

    INSTRUCTIONS:
    1. **Strict Delta Focus:** If concepts are 90% similar, ignore them. Focus on the 10% that changes the legal outcome.
    2. **Source Authority:** You MUST cite specific Statutes/Codes for Civil Law (e.g., "DOC Art. 77", "French Civil Code") and Leading Cases/Precedents for Common Law (e.g., "Donoghue v Stevenson", "Rylands v Fletcher").
    3. **Terminology:** Use precise legal terminology in the target language.
    4. **Reasoning:** Contrast the *method* of reasoning.

    RESPONSE STRUCTURE (Translate headers to interface language):
    
    ## ⚡ [The Legal Delta (Executive Summary)]
    (A high-level synthesis of the divergence.)

    ## 🏛️ [Structural & Logical Shift]
    (Explain the deep jurisprudential shift.)

    ## ⚖️ [Courtroom Simulation: The Scenario]
    * **[The Facts]:** ...
    * **[Ruling in Source]:** ...
    * **[Ruling in Target]:** ...

    ## 🧭 [Strategic Adaptation]
    (Actionable advice.)
    
    IMPORTANT: Respond *strictly* in the detected interface language.
    """

def run_analysis(api_key, provider, model_name, source, target, concept, ui):
    sys_prompt = get_system_prompt(source, target)
    user_prompt = f"Compare:\nSource: {source}\nTarget: {target}\nScenario: {concept}"

    try:
        with st.spinner(ui["spinner"]):
            response_text = ""
            
            if provider == "Google Gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name, system_instruction=sys_prompt)
                response = model.generate_content(user_prompt)
                response_text = response.text

            elif provider in ["OpenAI", "Groq"]:
                if OpenAI is None:
                    st.error("❌ 'openai' library not installed. Please run `pip install openai`.")
                    return
                
                base_url = None
                if provider == "Groq":
                    base_url = "https://api.groq.com/openai/v1"
                
                client = OpenAI(api_key=api_key, base_url=base_url)
                
                stream = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True
                )
                response_text = st.write_stream(stream)
            
            # For Gemini, we already have text, display it
            if provider == "Google Gemini":
                st.markdown("---")
                st.subheader(ui["analysis_header"])
                st.markdown(response_text)
            
            st.success("Analysis Complete.")

    except Exception as e:
        st.error(f"Error: {e}")

def handle_translation(api_key, provider, model_name, target_lang):
    if not api_key: return
    
    # Translation Prompt
    ui_current = st.session_state['ui_labels']
    prompt_text = f"Translate values of JSON to {target_lang}. Keep keys identical. Return ONLY raw JSON.\nJSON: {json.dumps(ui_current)}"

    try:
        with st.spinner(f"Translating to {target_lang}..."):
            clean_json = "{}"
            
            if provider == "Google Gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name) 
                resp = model.generate_content(prompt_text)
                clean_json = resp.text
                
            elif provider in ["OpenAI", "Groq"]:
                if OpenAI is None:
                     st.error("Missing openai lib"); return
                
                base_url = "https://api.groq.com/openai/v1" if provider == "Groq" else None
                client = OpenAI(api_key=api_key, base_url=base_url)
                
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt_text}]
                )
                clean_json = resp.choices[0].message.content

            clean_json = clean_json.replace("```json", "").replace("```", "").strip()
            st.session_state['ui_labels'] = json.loads(clean_json)
            st.session_state['current_language'] = target_lang
            st.rerun()

    except Exception as e:
        st.error(f"Translation Error: {e}")

if __name__ == "__main__":
    main()
