"""
Summary Score Calculator - Clean Streamlit Web App
"""

import streamlit as st
import pandas as pd
from src.metrics import calculate_all_metrics

st.set_page_config(page_title="Summary Score Calculator", page_icon="📊", layout="wide")

st.title("📊 Summary Score Calculator")
st.markdown("Evaluate text quality using Summary Score (S_SS) from Saini & Sengupta (2024)")
st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area("Paste text:", height=200, placeholder="Enter text here...")

with col2:
    model_name = st.text_input("Model Name", "My Model")
    run_number = st.number_input("Run", min_value=1, value=1)

if st.button("Calculate", use_container_width=True, type="primary"):
    if not text_input.strip():
        st.error("Enter text to analyze")
    elif len(text_input.strip()) < 20:
        st.error("Text must be at least 20 characters")
    else:
        try:
            metrics = calculate_all_metrics(text_input)

            st.success("✓ Analysis complete")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Summary Score", f"{metrics['summaryScore']:.1f}")
            col2.metric("Words", metrics['wordCount'])
            col3.metric("Sentences", metrics['sentenceCount'])
            col4.metric("Readability", f"{metrics['readability']:.1f}")

            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Quality Metrics**")
                st.write(f"Entropy: {metrics['entropy']:.4f} bits/char")
                st.write(f"Cohesion: {metrics['cohesion']:.2f}")
                st.write(f"Coherence: {metrics['coherence']:.2f}")

            with col2:
                st.write("**Text Statistics**")
                st.write(f"Unique Words: {metrics['uniqueWords']}")
                st.write(f"Lexical Density: {metrics['lexicalDensity']:.2f}%")
                st.write(f"Avg Words/Sentence: {metrics['avgWordsPerSentence']:.2f}")

            st.divider()

            results_df = pd.DataFrame([{
                'model': model_name,
                'run': run_number,
                **metrics
            }])

            st.download_button(
                label="Download CSV",
                data=results_df.to_csv(index=False),
                file_name=f"score_{model_name}_{run_number}.csv",
                mime="text/csv",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")

st.divider()
st.caption("Metrics from: Saini, M., & Sengupta, E. (2024). Multimedia Tools and Applications.")
