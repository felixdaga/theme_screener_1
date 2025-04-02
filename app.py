import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from chat_analysis import format_data_for_prompt, analyze_with_chatgpt

@st.cache_data
def load_returns_data():
    """Load and cache returns data"""
    try:
        returns = pd.read_excel('returns.xlsx', index_col='DATE')
        msci = pd.read_excel('msci_wrld.xlsx')
        rbics = pd.read_excel('rbics.xlsx')
        # Add fundamentals data loading
        fundamentals = {
            'capex': pd.read_excel('fundamentals/capex.xlsx', index_col='DATE'),
            'revenue': pd.read_excel('fundamentals/revenue.xlsx', index_col='DATE'),
            'ebitda': pd.read_excel('fundamentals/ebitda.xlsx', index_col='DATE'),
            # Add more fundamental items as needed
        }
        return returns, msci, rbics, fundamentals
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

# Load data using cache
RETURNS, MSCIWRLD, RBICS_DF, FUNDAMENTALS = load_returns_data()
if RETURNS is not None and MSCIWRLD is not None and RBICS_DF is not None and FUNDAMENTALS is not None:
    st.success("Data loaded successfully!")

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
        

        
        # Add charts for Most_aligned_rev_name and Least_aligned_rev_name if available
        alignment_cols = ['Most_aligned_rev_name', 'Least_aligned_rev_name']
        for col in alignment_cols:
            if col in df_filtered.columns:
                value_counts = df_filtered[col].value_counts().head(10)
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f'Top 10 by {col}',
                    labels={'x': col, 'y': 'Count'},
                    color=value_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
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

        # Portfolio Returns Analysis
        st.header("Portfolio Returns Analysis")
        if RETURNS is None or MSCIWRLD is None:
            st.error("Please ensure returns data is loaded correctly.")
        else:
            # Get start date from user
            start_date = st.date_input(
                "Select start date",
                value=pd.to_datetime('2018-01-01').date(),
                min_value=pd.to_datetime('2010-01-01').date(),
                max_value=pd.to_datetime('2024-01-01').date()
            )
            
            # Convert start_date to datetime64[ns]
            start_date_dt = pd.to_datetime(start_date)
            
            # Filter RETURNS data for shortlisted portfolio
            portfolio_returns = RETURNS.loc[start_date_dt:, df_filtered['ID'].tolist()]
            
            # Filter RETURNS data for MSCI World constituents
            msci_returns = RETURNS.loc[start_date_dt:, MSCIWRLD['ID'].tolist()]
            
            # Calculate equal-weighted average returns
            portfolio_avg_returns = portfolio_returns.mean(axis=1)
            msci_avg_returns = msci_returns.mean(axis=1)
            
            # Calculate cumulative returns (starting from 0)
            portfolio_cum_returns = (1 + portfolio_avg_returns).cumprod()
            msci_cum_returns = (1 + msci_avg_returns).cumprod()
            
            # Add one day prior to start date with value 1
            prior_date = start_date_dt - pd.Timedelta(days=1)
            portfolio_cum_returns = pd.concat([
                pd.Series(1.0, index=[prior_date]),
                portfolio_cum_returns
            ])
            msci_cum_returns = pd.concat([
                pd.Series(1.0, index=[prior_date]),
                msci_cum_returns
            ])
            
            # Create the plot
            fig = px.line(
                pd.DataFrame({
                    'Portfolio': portfolio_cum_returns,
                    'MSCI World': msci_cum_returns
                }),
                title='Cumulative Returns Comparison (Starting at 1)',
                labels={'value': 'Cumulative Return', 'index': 'Date'}
            )
            
            # Update layout
            fig.update_layout(
                showlegend=True,
                legend_title_text='',
                hovermode='x unified'
            )
            
            # Display the plot
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display total returns
            portfolio_total_return = (portfolio_cum_returns.iloc[-1] - 1) * 100
            msci_total_return = (msci_cum_returns.iloc[-1] - 1) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Portfolio Total Return",
                    f"{portfolio_total_return:.2f}%",
                    f"From {start_date.strftime('%Y-%m-%d')} to {portfolio_cum_returns.index[-1].strftime('%Y-%m-%d')}"
                )
            with col2:
                st.metric(
                    "MSCI World Total Return",
                    f"{msci_total_return:.2f}%",
                    f"From {start_date.strftime('%Y-%m-%d')} to {msci_cum_returns.index[-1].strftime('%Y-%m-%d')}"
                )

        # Portfolio Fundamentals Analysis
        st.header("Portfolio Fundamentals Analysis")
        if FUNDAMENTALS is None:
            st.error("Please ensure fundamentals data is loaded correctly.")
        else:
            # Create two columns for controls
            fund_col1, fund_col2 = st.columns(2)
            
            with fund_col1:
                # Fundamental item selection
                selected_item = st.selectbox(
                    "Select Fundamental Metric",
                    options=list(FUNDAMENTALS.keys()),
                    help="Choose the fundamental metric to analyze"
                )
            
            with fund_col2:
                # Start date selection
                start_date = st.date_input(
                    "Select start date",
                    value=pd.to_datetime('2018-01-01').date(),
                    min_value=pd.to_datetime('2010-01-01').date(),
                    max_value=pd.to_datetime('2024-01-01').date()
                )
            
            if selected_item and start_date:
                # Get the selected fundamental data
                fund_data = FUNDAMENTALS[selected_item]
                
                # Convert start_date to datetime
                start_date_dt = pd.to_datetime(start_date)
                
                # Filter data from start date to latest
                fund_data = fund_data.loc[start_date_dt:]
                
                # Filter columns for portfolio and MSCI World
                portfolio_data = fund_data[df_filtered['ID'].tolist()]
                msci_data = fund_data[MSCIWRLD['ID'].tolist()]
                
                # Calculate aggregated values (using mean)
                portfolio_agg = portfolio_data.mean(axis=1)
                msci_agg = msci_data.mean(axis=1)
                
                # Create the plot
                fig = px.line(
                    pd.DataFrame({
                        'Portfolio': portfolio_agg,
                        'MSCI World': msci_agg
                    }),
                    title=f'{selected_item.capitalize()} Comparison',
                    labels={'value': selected_item.capitalize(), 'index': 'Date'}
                )
                
                # Update layout
                fig.update_layout(
                    showlegend=True,
                    legend_title_text='',
                    hovermode='x unified'
                )
                
                # Display the plot
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate and display summary statistics
                col1, col2 = st.columns(2)
                with col1:
                    portfolio_value = portfolio_agg.mean()
                    st.metric(
                        "Portfolio Mean",
                        f"{portfolio_value:.2f}",
                        f"From {start_date.strftime('%Y-%m-%d')} to {fund_data.index[-1].strftime('%Y-%m-%d')}"
                    )
                with col2:
                    msci_value = msci_agg.mean()
                    st.metric(
                        "MSCI World Mean",
                        f"{msci_value:.2f}",
                        f"From {start_date.strftime('%Y-%m-%d')} to {fund_data.index[-1].strftime('%Y-%m-%d')}"
                    )

        # ChatGPT Portfolio Analysis
        st.header("Ask ChatGPT about the Portfolio")
        
        # Column selection for analysis
        available_columns = df_filtered.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to include in the analysis",
            options=available_columns,
            default=['short_name', 'Composite_Score', 'gics_1_sector', 'country', 'Market cap group'],
            help="Choose which columns to include in the ChatGPT analysis"
        )
        
        # Chunk size selection
        chunk_size = st.number_input(
            "Select chunk size for data processing",
            min_value=1,
            max_value=400,
            value=100,
            help="Number of companies to process in each chunk"
        )
        
        # Question input
        question = st.text_area(
            "Enter your question about the portfolio",
            placeholder="e.g., What are the key sector trends in this portfolio?",
            help="Ask any question about the portfolio composition, characteristics, or patterns"
        )
        
        if st.button("Analyze with ChatGPT"):
            if not selected_columns:
                st.error("Please select at least one column for analysis")
            elif not question:
                st.error("Please enter a question")
            else:
                with st.spinner("Analyzing portfolio with ChatGPT..."):
                    try:
                        # Get analysis from ChatGPT
                        analysis = analyze_with_chatgpt(
                            df_filtered[selected_columns],
                            question,
                            chunk_size=chunk_size
                        )
                        
                        # Display results
                        st.markdown("### Analysis Results")
                        st.markdown(analysis)
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")

        # Company View Module
        st.header("Company View")
        
        # Company selection dropdown
        company_names = df['short_name'].tolist()
        selected_company = st.selectbox(
            "Select a company",
            options=company_names,
            help="Choose a company to view its detailed analysis"
        )
        
        if selected_company:
            # Get company ID
            company_id = df[df['short_name'] == selected_company]['ID'].iloc[0]
            
            # Filter RBICS data
            company_rbics = RBICS_DF[RBICS_DF.barrid == company_id].copy()
            
            if not company_rbics.empty:
                # Display company details
                st.subheader("Company Details")
                company_details = df[df['short_name'] == selected_company].iloc[0]
                for col in company_details.index:
                    if col != 'ID':  # Skip ID as it's internal
                        st.write(f"**{col}:** {company_details[col]}")
                
                # Create line chart
                st.subheader("Trend Analysis")
                fig = px.line(
                    company_rbics,
                    title=f'Analysis for {selected_company}'
                )
                fig.update_layout(
                    margin=dict(t=50, l=25, r=25, b=25),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Display filtered table
                st.subheader("Data Table")
                st.dataframe(company_rbics)
            else:
                st.warning(f"No RBICS data found for {selected_company}")

else:
    st.info("Please upload an Excel file to begin analysis")
    
    # Add sample data format information
    st.markdown("---")
    st.markdown("### Expected Data Format")
    st.markdown("""
    Your Excel file should contain the following columns:
    - `short_name`: Company identifiers
    - `ID`: Company ID for matching with RBICS data
    - Any numeric columns you want to use for scoring
    - `gics_1_sector`: Industry sector classification
    - `country`: Company's country (optional)
    - `Market cap group`: Market capitalization category (optional)
    """) 
