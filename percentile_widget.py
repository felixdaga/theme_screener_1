from ipywidgets import FloatSlider, VBox, Output
import plotly.express as px
import pandas as pd

def create_percentile_widget(df):
    # Create output widget for displaying results
    percentile_output = Output()
    
    # Create percentile slider
    percentile_slider = FloatSlider(
        value=50,
        min=0,
        max=100,
        step=1,
        description='Percentile Threshold:',
        style={'description_width': 'initial'}
    )
    
    def on_percentile_change(change):
        with percentile_output:
            percentile_output.clear_output()
            
            # Calculate threshold value
            threshold = df['Composite_Score'].quantile(change['new'] / 100)
            
            # Filter dataframe
            global df_sl
            df_sl = df[df['Composite_Score'] >= threshold].copy()
            
            # Display number of companies
            print(f"Number of companies above {change['new']}th percentile: {len(df_sl)}")
            
            # Create sector composition pie chart
            sector_counts = df_sl['sector'].value_counts()
            fig = px.pie(values=sector_counts.values, 
                        names=sector_counts.index,
                        title=f'Sector Composition (Companies above {change["new"]}th percentile)')
            fig.show()
            
            # Display filtered dataframe
            print("\nFiltered Companies:")
            display(df_sl)
    
    # Link the slider to the update function
    percentile_slider.observe(on_percentile_change, names='value')
    
    # Display widgets
    display(percentile_slider)
    display(percentile_output)
    
    # Trigger initial update
    on_percentile_change({'new': percentile_slider.value})
    
    return df_sl 