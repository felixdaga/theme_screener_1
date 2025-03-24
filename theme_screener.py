import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Theme Investment Screener",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("Theme Investment Screener")
st.markdown("""
This tool helps you screen companies based on their relevance to investment themes.
Select your score columns and adjust their weights to customize your screening criteria.
""")

# File upload
uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx', 'xls'])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)
    
    # Display the first few rows of the data
    st.subheader("Data Preview")
    st.dataframe(df.head())
    
    # Sidebar for column selection and weight adjustments
    st.sidebar.header("Score Selection and Weights")
    
    # Get all columns
    all_columns = df.columns.tolist()
    
    # Allow user to select score columns
    st.sidebar.subheader("Select Score Columns")
    selected_columns = st.sidebar.multiselect(
        "Choose columns to include in scoring (should contain 0 or 1 values)",
        all_columns,
        default=[col for col in all_columns if col.endswith('_final')]
    )
    
    # Create sliders for selected columns
    weights = {}
    if selected_columns:
        st.sidebar.subheader("Adjust Weights")
        for col in selected_columns:
            weights[col] = st.sidebar.slider(
                f"Weight for {col}",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1
            )
    
    # Calculate weighted score
    if weights:
        df['Weighted_Score'] = sum(df[col] * weight for col, weight in weights.items())
        
        # Sort by weighted score
        df_sorted = df.sort_values('Weighted_Score', ascending=False)
        
        # Percentile selection for final basket
        st.subheader("Final Basket Selection")
        percentile = st.slider(
            "Select percentile threshold for final basket",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            help="Companies above this percentile will be included in the final basket"
        )
        
        # Calculate threshold score
        threshold_score = df_sorted['Weighted_Score'].quantile(1 - percentile/100)
        df_filtered = df_sorted[df_sorted['Weighted_Score'] >= threshold_score]
        
        # Display filtered results
        st.markdown(f"### Companies in Top {percentile}th Percentile")
        st.dataframe(df_filtered)
        
        # Display score distribution
        st.subheader("Score Distribution")
        fig_dist = px.histogram(
            df_sorted,
            x='Weighted_Score',
            title=f"Distribution of Weighted Scores (Threshold: {threshold_score:.2f})",
            nbins=50
        )
        fig_dist.add_vline(x=threshold_score, line_dash="dash", line_color="red")
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Visualization section
        st.subheader("Portfolio Characteristics")
        
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Sector Distribution", "Country Distribution", "Score Distribution"])
        
        with tab1:
            sector_dist = df_filtered['Sector'].value_counts()
            fig_sector = px.pie(
                values=sector_dist.values,
                names=sector_dist.index,
                title="Sector Distribution of Final Basket"
            )
            st.plotly_chart(fig_sector, use_container_width=True)
        
        with tab2:
            country_dist = df_filtered['Country'].value_counts()
            fig_country = px.bar(
                x=country_dist.index,
                y=country_dist.values,
                title="Country Distribution of Final Basket"
            )
            st.plotly_chart(fig_country, use_container_width=True)
        
        with tab3:
            fig_scores = go.Figure()
            for col in weights.keys():
                fig_scores.add_trace(go.Box(
                    y=df_filtered[col],
                    name=col,
                    boxpoints='all'
                ))
            fig_scores.update_layout(title="Score Distribution of Final Basket")
            st.plotly_chart(fig_scores, use_container_width=True)
        
        # Conference Call Analysis
        st.subheader("Conference Call Analysis")
        if 'Conference_Call' in df.columns:
            selected_company = st.selectbox(
                "Select a company to analyze its conference call",
                df_filtered['Company'].tolist()
            )
            
            if st.button("Analyze Conference Call"):
                with st.spinner("Analyzing conference call..."):
                    # Get the conference call text
                    call_text = df[df['Company'] == selected_company]['Conference_Call'].iloc[0]
                    
                    # Use custom AI function to analyze the conference call
                    try:
                        analysis = AI.get_surface_chat_completion([
                            {"promptRole": "system", "prompt": "You are a financial analyst. Analyze the following conference call transcript and provide key insights about the company's performance, challenges, and future outlook."},
                            {"promptRole": "user", "prompt": call_text}
                        ])['chatCompletion']['chatCompletionContent']
                        
                        st.markdown("### Analysis Results")
                        st.write(analysis)
                    except Exception as e:
                        st.error(f"Error analyzing conference call: {str(e)}")
        
        # Export functionality
        if st.button("Export Results"):
            output_file = "screening_results.xlsx"
            df_filtered.to_excel(output_file, index=False)
            st.success(f"Results exported to {output_file}")

else:
    st.info("Please upload an Excel file to begin screening.") 