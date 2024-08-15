import streamlit as st
import pandas as pd

# Function to adjust spend based on fixed value spread across date range by percentage of total spend
def adjust_spend(df, channel, tactic, adjustment_value, start_date, end_date):
    # Convert 'Date' column to datetime if not already
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter data based on selected channel, tactic, and date range
    mask = (df['Channel'] == channel) & (df['Tactic'] == tactic) & (df['Date'] >= start_date) & (df['Date'] <= end_date)
    filtered_df = df[mask].copy()
    
    # Calculate the total spend for the filtered data
    total_spend = filtered_df['Spend'].sum()
    
    if total_spend > 0:
        # Calculate the percentage of total spend for each day
        filtered_df['Spend Percentage'] = filtered_df['Spend'] / total_spend
        
        # Apply the fixed value adjustment proportionally based on the spend percentage
        filtered_df['Spend Adjustment'] = filtered_df['Spend Percentage'] * adjustment_value
        
        # Add the adjustment to the original spend
        filtered_df['Adjusted Spend'] = filtered_df['Spend'] + filtered_df['Spend Adjustment']
        
        # Update the original dataframe with the adjusted values
        df.loc[mask, 'Spend'] = filtered_df['Adjusted Spend']
    
    return df

# Function to summarize data without the date
def summarize_data(df):
    summary_df = df.groupby(['Channel', 'Tactic'], as_index=False).agg({'Spend': 'sum'})
    summary_df['Adjusted Spend'] = df.groupby(['Channel', 'Tactic'], as_index=False)['Spend'].sum()['Spend']
    return summary_df

# Streamlit app
st.title("Spend Adjustment Tool with Date Range, Curve-based Adjustment, and Summary")

# Step 1: Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Load the CSV into a DataFrame
    df = pd.read_csv(uploaded_file)
    
    st.write("Original Data:")
    st.dataframe(df)
    
    # Step 2: Select channel and tactic
    channel = st.selectbox("Select Channel", df['Channel'].unique())
    tactic = st.selectbox("Select Tactic", df[df['Channel'] == channel]['Tactic'].unique())
    
    # Step 3: Choose a date range
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure the Date column is in datetime format
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Step 4: Choose adjustment method (Fixed Value only, since we're implementing the curve-based adjustment)
    adjustment_value = st.number_input("Enter Fixed Value Adjustment", value=0.0)
    
    # Button to apply adjustment
    if st.button("Apply Adjustment"):
        # Adjust the spend by spreading the fixed value based on the curve of the original spend
        adjusted_df = adjust_spend(df.copy(), channel, tactic, adjustment_value, pd.to_datetime(start_date), pd.to_datetime(end_date))
        
        st.write("Adjusted Data (Detailed with Date):")
        st.dataframe(adjusted_df)
        
        # Create summarized data without dates
        summary_df = summarize_data(adjusted_df)
        
        st.write("Summarized Data (Without Date):")
        st.dataframe(summary_df)
        
        # Option to download the adjusted detailed data
        csv_adjusted = adjusted_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Adjusted Detailed CSV", data=csv_adjusted, file_name="adjusted_spend.csv", mime="text/csv")
        
        # Option to download the summarized data
        csv_summary = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Summarized CSV", data=csv_summary, file_name="summary_spend.csv", mime="text/csv")
