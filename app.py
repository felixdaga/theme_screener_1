import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load returns data
try:
    RETURNS = pd.read_excel('returns.xlsx', index_col='DATE')
    MSCIWRLD = pd.read_excel('msci_wrld.xlsx')
    st.success("Returns data loaded successfully!")
except Exception as e:
    st.error(f"Error loading returns data: {str(e)}")
    RETURNS = None
    MSCIWRLD = None

# Set page config
st.set_page_config(
    page_title="Company Score Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom color schemes
CUSTOM_COLORS = {
    'sector': px.colors.qualitative.Set3,
    'country': px.colors.qualitative.Pastel,
    'mcap': px.colors.qualitative.Safe
}

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Add title with custom styling
st.markdown("""
    <h1 style='text-align: center; color: #2e4053;'>
        Company Score Analysis Dashboard
    </h1>
    """, unsafe_allow_html=True)

# File upload
uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])

if uploaded_file is not None:
    # Load data
    try:
        df = pd.read_excel(uploaded_file)
        st.success("File successfully loaded!")
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        st.stop()
    
    # Create two columns for the layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Score Analysis")
        
        # Criteria selection - modified to allow any numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            st.error("No numeric columns found in the file!")
            st.stop()
            
        selected_criteria = st.multiselect(
            'Select Scoring Criteria',
            options=numeric_cols,
            default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
            help="Choose the numeric columns to use for composite scoring"
        )
        
        # Weights for selected criteria
        weights = {}
        if selected_criteria:
            st.subheader("Adjust Weights")
            cols = st.columns(len(selected_criteria))
            for i, criterion in enumerate(selected_criteria):
                with cols[i]:
                    weights[criterion] = st.slider(
                        f"{criterion} weight",
                        min_value=0.0,
                        max_value=5.0,
                        value=1.0,
                        step=0.1,
                        key=f"weight_{criterion}",
                        help=f"Adjust the weight for {criterion} in the composite score"
                    )
    
    with col2:
        st.subheader("Percentile Filter")
        percentile_threshold = st.slider(
            "Percentile Threshold",
            min_value=0,
            max_value=100,
            value=50,
            step=1
        )
    
    # Calculate composite scores if criteria are selected
    if selected_criteria and weights:
        # Calculate weighted scores
        total_weight = sum(weights.values())
        weighted_scores = pd.Series(0.0, index=df.index)
        
        for criterion in selected_criteria:
            if df[criterion].max() - df[criterion].min() != 0:
                normalized_scores = (df[criterion] - df[criterion].min()) / (
                    df[criterion].max() - df[criterion].min()
                )
                weighted_scores += normalized_scores * (weights[criterion] / total_weight)
        
        df['Composite_Score'] = weighted_scores
        
        # Display results
        st.markdown("---")
        st.subheader("Results")
        
        # Calculate threshold and filter companies
        threshold = df['Composite_Score'].quantile(percentile_threshold / 100)
        df_filtered = df[df['Composite_Score'] >= threshold].copy()
        
        # Display metrics
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Companies Above Threshold", 
                     len(df_filtered))
        with metric_col2:
            st.metric("Threshold Score", 
                     f"{threshold:.3f}")
        with metric_col3:
            st.metric("Average Score",
                     f"{df_filtered['Composite_Score'].mean():.3f}")
        
        # Create visualizations
        st.markdown("---")
        st.subheader("Portfolio Composition Analysis")
        
        viz_col1, viz_col2 = st.columns(2)
        viz_col3, viz_col4 = st.columns(2)
        
        with viz_col1:
            # Score distribution
            fig_hist = px.histogram(
                df, 
                x='Composite_Score',
                title='Distribution of Composite Scores',
                color_discrete_sequence=['#3498db'],
                nbins=20
            )
            fig_hist.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                title_x=0.5
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with viz_col2:
            # Sector composition
            if 'gics_1_sector' in df.columns:
                sector_counts = df_filtered['gics_1_sector'].value_counts()
                fig_sector = px.pie(
                    values=sector_counts.values,
                    names=sector_counts.index,
                    title=f'Sector Composition (Above {percentile_threshold}th percentile)',
                    color_discrete_sequence=CUSTOM_COLORS['sector'],
                    hole=0.4
                )
                fig_sector.update_traces(textposition='outside', textinfo='percent+label')
                fig_sector.update_layout(title_x=0.5)
                st.plotly_chart(fig_sector, use_container_width=True)
        
        with viz_col3:
            # Country composition
            if 'country' in df.columns:
                country_counts = df_filtered['country'].value_counts()
                fig_country = px.pie(
                    values=country_counts.values,
                    names=country_counts.index,
                    title=f'Country Composition (Above {percentile_threshold}th percentile)',
                    color_discrete_sequence=CUSTOM_COLORS['country'],
                    hole=0.4
                )
                fig_country.update_traces(textposition='outside', textinfo='percent+label')
                fig_country.update_layout(title_x=0.5)
                st.plotly_chart(fig_country, use_container_width=True)
            else:
                st.warning("Country data not available in the uploaded file")
        
        with viz_col4:
            # Market Cap composition
            if 'Market cap group' in df.columns:
                mcap_counts = df_filtered['Market cap group'].value_counts()
                fig_mcap = px.pie(
                    values=mcap_counts.values,
                    names=mcap_counts.index,
                    title=f'Market Cap Composition (Above {percentile_threshold}th percentile)',
                    color_discrete_sequence=CUSTOM_COLORS['mcap'],
                    hole=0.4
                )
                fig_mcap.update_traces(textposition='outside', textinfo='percent+label')
                fig_mcap.update_layout(title_x=0.5)
                st.plotly_chart(fig_mcap, use_container_width=True)
            else:
                st.warning("Market cap group data not available in the uploaded file")
        
        # Add summary metrics
        st.markdown("---")
        st.subheader("Composition Summary")
        summary_cols = st.columns(3)
        
        with summary_cols[0]:
            if 'gics_1_sector' in df.columns:
                st.metric("Number of Sectors", 
                         len(sector_counts))
                st.markdown("**Top 3 Sectors:**")
                for sector, count in sector_counts.head(3).items():
                    st.write(f"- {sector}: {count} companies ({count/len(df_filtered)*100:.1f}%)")
        
        with summary_cols[1]:
            if 'country' in df.columns:
                st.metric("Number of Countries", 
                         len(country_counts))
                st.markdown("**Top 3 Countries:**")
                for country, count in country_counts.head(3).items():
                    st.write(f"- {country}: {count} companies ({count/len(df_filtered)*100:.1f}%)")
        
        with summary_cols[2]:
            if 'Market cap group' in df.columns:
                st.metric("Number of Market Cap Groups", 
                         len(mcap_counts))
                st.markdown("**Market Cap Distribution:**")
                for mcap, count in mcap_counts.items():
                    st.write(f"- {mcap}: {count} companies ({count/len(df_filtered)*100:.1f}%)")
        
        # Display filtered companies
        st.markdown("---")
        st.subheader("Top Companies")
        display_columns = ['short_name', 'Composite_Score', 'gics_1_sector']
        if 'country' in df.columns:
            display_columns.append('country')
        if 'Market cap group' in df.columns:
            display_columns.append('Market cap group')
            
        st.dataframe(
            df_filtered[display_columns]
            .sort_values('Composite_Score', ascending=False)
            .style.format({'Composite_Score': '{:.3f}'})
            .background_gradient(subset=['Composite_Score'], cmap='Blues')
        )

        # Add download button for filtered results
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="Download filtered results",
            data=csv,
            file_name="filtered_companies.csv",
            mime="text/csv",
            help="Download the filtered company data as a CSV file"
        )

        # Add returns analysis section
        st.markdown("---")
        st.subheader("Portfolio Returns Analysis")
        
        # Add returns analysis button
        if st.button("Run equal-weighted returns for shortlisted portfolio"):
            try:
                # Get start date from user
                start_date = st.date_input(
                    "Select start date",
                    value=pd.to_datetime("2018-01-01"),
                    min_value=pd.to_datetime("2000-01-01"),
                    max_value=pd.to_datetime("2024-12-31")
                )
                
                # Filter RETURNS for shortlisted portfolio
                basket_returns = RETURNS[df_filtered['ID'].tolist()]
                basket_returns = basket_returns[basket_returns.index >= start_date]
                
                # Filter RETURNS for MSCI World
                wrld_returns = RETURNS[MSCIWRLD['ID'].tolist()]
                wrld_returns = wrld_returns[wrld_returns.index >= start_date]
                
                # Calculate average returns
                basket_avg_returns = basket_returns.mean(axis=1)
                wrld_avg_returns = wrld_returns.mean(axis=1)
                
                # Calculate cumulative returns (starting from 0)
                basket_cum_returns = (1 + basket_avg_returns).cumprod()
                wrld_cum_returns = (1 + wrld_avg_returns).cumprod()
                
                # Create the plot
                fig_returns = px.line(
                    pd.DataFrame({
                        'Portfolio': basket_cum_returns,
                        'MSCI World': wrld_cum_returns
                    }),
                    title='Cumulative Returns Comparison',
                    labels={'value': 'Cumulative Return', 'index': 'Date'}
                )
                
                fig_returns.update_layout(
                    plot_bgcolor='white',
                    title_x=0.5,
                    legend_title='Index'
                )
                
                # Display the plot
                st.plotly_chart(fig_returns, use_container_width=True)
                
                # Display some statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Portfolio Total Return",
                        f"{(basket_cum_returns.iloc[-1] - 1) * 100:.2f}%"
                    )
                with col2:
                    st.metric(
                        "MSCI World Total Return",
                        f"{(wrld_cum_returns.iloc[-1] - 1) * 100:.2f}%"
                    )
                
            except Exception as e:
                st.error(f"Error calculating returns: {str(e)}")

else:
    st.info("Please upload an Excel file to begin analysis")
    
    # Add sample data format information
    st.markdown("---")
    st.markdown("### Expected Data Format")
    st.markdown("""
    Your Excel file should contain the following columns:
    - `short_name`: Company identifiers
    - Any numeric columns you want to use for scoring
    - `gics_1_sector`: Industry sector classification
    - `country`: Company's country (optional)
    - `Market cap group`: Market capitalization category (optional)
    """) 