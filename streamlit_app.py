"""
Summary Score Calculator - Streamlit Web App

Interactive calculator to evaluate text quality using Summary Score (S_SS) metric
from Saini & Sengupta (2024).

Deploy to Streamlit Cloud:
  1. Push to GitHub
  2. Go to https://share.streamlit.io
  3. Connect your GitHub repo
  4. Select this file (streamlit_app.py)
  5. Get a public link
"""

import streamlit as st
import pandas as pd
from src.metrics import calculate_all_metrics

st.set_page_config(
    page_title="Summary Score Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 32px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Summary Score Calculator")
st.markdown("Evaluate text quality using the Summary Score (S_SS) metric from **Saini & Sengupta (2024)**")

st.markdown("""
---
### Metric Definitions

| Metric | Range | Meaning |
|--------|-------|---------|
| **Summary Score (S_SS)** | 0–100 | Aggregate quality score |
| **Text Entropy** | 0–8 bits/char | Information density; higher = more vocabulary diversity |
| **Readability** | 0–100 | Flesch Reading Ease; higher = easier to read |
| **Cohesion** | 0–100 | Sentence structure quality |
| **Coherence** | 0–100 | Repetition analysis; higher = less repetitive |
| **Lexical Density** | 0–100% | Unique words / total words; higher = richer vocabulary |

---
""")

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📝 Paste Your Text")
    text_input = st.text_area(
        "Enter text to analyze:",
        height=250,
        placeholder="Paste the text you want to analyze here...",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("⚙️ Settings")
    model_name = st.text_input("Model/Source Name", "My Model", help="e.g., GPT-4, Claude, Llama")
    run_number = st.number_input("Run Number", min_value=1, max_value=100, value=1)

st.divider()

if st.button("📊 Calculate Metrics", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.error("❌ Please enter some text to analyze.")
    elif len(text_input.strip()) < 20:
        st.error("❌ Text must be at least 20 characters long.")
    else:
        try:
            metrics = calculate_all_metrics(text_input)

            st.success("✅ Analysis complete!")

            st.subheader(f"Results for: {model_name} (Run {run_number})")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Summary Score",
                    f"{metrics['summaryScore']:.1f}",
                    help="Aggregate quality metric (0–100)"
                )

            with col2:
                st.metric(
                    "Word Count",
                    f"{metrics['wordCount']}",
                    help="Total words"
                )

            with col3:
                st.metric(
                    "Sentences",
                    f"{metrics['sentenceCount']}",
                    help="Total sentences"
                )

            with col4:
                st.metric(
                    "Readability",
                    f"{metrics['readability']:.1f}",
                    help="Flesch Reading Ease (0–100)"
                )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Core Metrics")
                metrics_display = {
                    "Entropy": f"{metrics['entropy']:.4f} bits/char",
                    "Readability": f"{metrics['readability']:.2f} (Flesch)",
                    "Cohesion": f"{metrics['cohesion']:.2f}",
                    "Coherence": f"{metrics['coherence']:.2f}",
                }

                for label, value in metrics_display.items():
                    st.write(f"**{label}:** {value}")

            with col2:
                st.subheader("Text Statistics")
                stats_display = {
                    "Unique Words": metrics['uniqueWords'],
                    "Lexical Density": f"{metrics['lexicalDensity']:.2f}%",
                    "Avg Words/Sentence": f"{metrics['avgWordsPerSentence']:.2f}",
                    "Syllables": metrics['syllableCount'],
                }

                for label, value in stats_display.items():
                    st.write(f"**{label}:** {value}")

            st.divider()

            st.subheader("📥 Export Results")

            results_df = pd.DataFrame([{
                'model': model_name,
                'run': run_number,
                'text_length': len(text_input),
                **metrics
            }])

            csv_data = results_df.to_csv(index=False)

            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"summary_score_{model_name}_{run_number}.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.info("""
            **How to use these metrics:**
            - **Higher Summary Score** → better overall quality
            - **Higher Readability** → easier to understand
            - **Higher Coherence** → less repetitive
            - **Higher Lexical Density** → richer vocabulary
            """)

        except Exception as e:
            st.error(f"❌ Error calculating metrics: {str(e)}")

st.divider()

with st.expander("📖 About This Tool"):
    st.markdown("""
    ### Summary Score Metric

    This tool implements the Summary Score (S_SS) metric from:

    > Saini, M., & Sengupta, E. (2024). "Artificial intelligence inspired fog-cloud-based
    > visual-assistance framework for blind and visually-impaired people."
    > *Multimedia Tools and Applications*. DOI: 10.1007/s11042-024-20159-1

    **Formula:**
    ```
    S_SS = [E_norm + R_norm + C_norm + Ch_norm] / 4 × 100
    ```

    Where:
    - `E_norm` = normalized entropy (0–1)
    - `R_norm` = normalized readability (0–1)
    - `C_norm` = normalized cohesion (0–1)
    - `Ch_norm` = normalized coherence (0–1)

    ### Use Cases

    - **LLM Output Evaluation** - Compare quality across different models
    - **Text Summarization** - Measure summary quality
    - **Content Writing** - Ensure readability and vocabulary richness
    - **Research** - Quantify text quality for experiments

    ### Limitations

    - Surface metrics don't measure factual correctness
    - Results are language-dependent (English optimized)
    - Scores are relative, not absolute quality measures
    """)

with st.expander("💡 Deploy to Streamlit Cloud"):
    st.markdown("""
    ### How to get a public link:

    1. **Push code to GitHub**
       ```bash
       git push origin main
       ```

    2. **Go to https://share.streamlit.io**
       - Sign in with GitHub
       - Click "New app"
       - Select your repository
       - Select branch: `main`
       - Set main file path: `streamlit_app.py`
       - Click "Deploy"

    3. **Get your public link** - Streamlit will provide a URL like:
       ```
       https://text-generation-experiment-xxxx.streamlit.app
       ```

    4. **Share the link** - Anyone can now use it!
    """)

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
Built with <a href='https://streamlit.io' target='_blank'>Streamlit</a> |
Metrics from <a href='https://doi.org/10.1007/s11042-024-20159-1' target='_blank'>Saini & Sengupta (2024)</a>
</div>
""", unsafe_allow_html=True)
