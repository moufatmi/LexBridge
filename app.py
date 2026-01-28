import streamlit as st
import google.generativeai as genai
import json

def main():
    # Page Configuration
    st.set_page_config(
        page_title="LexBridge",
        page_icon="⚖️",
        layout="wide"
    )

    # --- Session State Initialization ---
    if 'ui_labels' not in st.session_state:
        # Default English Labels
        st.session_state['ui_labels'] = {
            "title": "LexBridge: Legal Delta Learning",
            "subtitle": "Compare legal concepts between jurisdictions, focusing **only on the differences**.",
            "settings": "Settings",
            "api_key_label": "Enter Gemini API Key",
            "model_label": "Choose Model",
            "interface_lang_label": "Interface Language (Translate App)",
            "translate_btn": "Translate Page",
            "source_label": "Source Jurisdiction",
            "source_ph": "e.g., Morocco (Civil Law)",
            "target_label": "Target Jurisdiction",
            "target_ph": "e.g., UK (Common Law)",
            "concept_label": "Legal Scenario or Concept",
            "concept_ph": "Describe the legal situation or concept you want to bridge...",
            "analyze_btn": "Analyze Differences",
            "analysis_header": "### Analysis",
            "error_api": "Please provide a Gemini API Key in the sidebar.",
            "error_concept": "Please enter a legal scenario or concept.",
            "spinner": "Analyzing legal delta..."
        }
    
    if 'current_language' not in st.session_state:
        st.session_state['current_language'] = "English"

    # Shortcuts for cleaner code
    ui = st.session_state['ui_labels']

    # --- Sidebar ---
    with st.sidebar:
        st.title(ui["settings"])
        api_key = st.text_input(ui["api_key_label"], type="password")
        st.markdown("---")
        
        # Model Selection
        model_options = [
            "gemini-2.0-flash-lite-preview-02-05",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash"
        ]
        selected_model = st.selectbox(ui["model_label"], model_options, index=0)
        
        st.markdown("---")
        # --- Translation Controls ---
        target_lang = st.text_input(ui["interface_lang_label"], placeholder="e.g., French, Arabic")
        
        if st.button(ui["translate_btn"]):
            if not api_key:
                st.error("API Key required to translate.")
            elif not target_lang:
                st.warning("Enter a language.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    # Use the user-selected model for translation to avoid 404s
                    trans_model = genai.GenerativeModel(selected_model) 
                    
                    # Prompt to translate JSON keys
                    trans_prompt = f"""
                    Translate the selected values of this JSON object into {target_lang}.
                    Return ONLY raw JSON. Do not use markdown blocks.
                    Keep the keys exactly the same. Translate the values.
                    
                    JSON:
                    {json.dumps(ui)}
                    """
                    
                    with st.spinner(f"Translating to {target_lang}..."):
                        resp = trans_model.generate_content(trans_prompt)
                        # Clean cleanup potential code blocks
                        clean_json = resp.text.replace("```json", "").replace("```", "").strip()
                        new_labels = json.loads(clean_json)
                        
                        # Update State
                        st.session_state['ui_labels'] = new_labels
                        st.session_state['current_language'] = target_lang
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Translation failed: {e}")

    # --- Main Interface ---
    st.title(ui["title"])
    st.markdown(ui["subtitle"])

    col1, col2 = st.columns(2)
    
    with col1:
        source_jurisdiction = st.text_input(ui["source_label"], value=ui.get("source_ph_val", ""), placeholder=ui["source_ph"])
    
    with col2:
        target_jurisdiction = st.text_input(ui["target_label"], value=ui.get("target_ph_val", ""), placeholder=ui["target_ph"])

    concept = st.text_area(ui["concept_label"], height=150, placeholder=ui["concept_ph"])

    if st.button(ui["analyze_btn"], type="primary"):
        if not api_key:
            st.error(ui["error_api"])
            return

        if not concept.strip():
            st.warning(ui["error_concept"])
            return

        try:
            genai.configure(api_key=api_key)
            
# Dynamic System Instruction with Language Context
            lang_context = st.session_state['current_language']
            
            system_instruction = (
                "ROLE: You are LexBridge, a specialized AI agent for 'Comparative Legal Delta Learning'.\n"
                "OBJECTIVE: Compare the user's Source Jurisdiction with the Target Jurisdiction. "
                "Do NOT explain shared concepts. Focus 100% on the divergence (The Delta).\n"
                "INSTRUCTIONS:\n"
                "1. ANALYZE: Identify the core legal concept in the user's input.\n"
                "2. DETECT DELTA: Determine precisely where the logic shifts (e.g., from 'Fault' to 'Strict Liability').\n"
                "3. EXPLAIN: Articulate this shift clearly. Use academic yet accessible language.\n"
                "4. SIMULATE: Provide a brief 'Court Simulation' showing how the outcome changes in the Target Jurisdiction.\n"
                "CONSTRAINTS:\n"
                "- Assume the user is an expert in the Source Law; do not lecture them on it.\n"
                "- FORMAT: Use Markdown. Bold key legal terms.\n"
                f"- IMPORTANT: Respond strictly in {lang_context} language."
            )            
            model = genai.GenerativeModel(
                model_name=selected_model,
                system_instruction=system_instruction
            )

            prompt = f"""
            Source Jurisdiction: {source_jurisdiction}
            Target Jurisdiction: {target_jurisdiction}
            Scenario: {concept}
            """

            with st.spinner(ui["spinner"]):
                response = model.generate_content(prompt)
                st.markdown(ui["analysis_header"])
                st.markdown(response.text)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
