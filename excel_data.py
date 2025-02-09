import pandas as pd
import streamlit as st
from pathlib import Path

def get_excel_data():
    """
    Read pesticide data from Excel file
    """
    try:
        # Get the path to the Excel file
        file_path = Path(__file__).parent.parent / "attached_assets" / "PESTICIDE INFO..xlsx"
        
        # Read the Excel file
        df = pd.read_excel(str(file_path))
        
        # Clean and prepare data
        df = df.iloc[:, [0, 1]]  # Select first two columns
        df.columns = ['Item Name', 'Price']  # Rename columns
        
        # Clean the data
        df['Item Name'] = df['Item Name'].str.strip()
        df['Price'] = pd.to_numeric(
            df['Price'].astype(str)
                .str.replace('₹', '')
                .str.replace(',', '')
                .str.strip(),
            errors='coerce'
        )
        
        # Drop any rows with NaN values
        df = df.dropna()
        
        st.write(f"Successfully loaded {len(df)} items from Excel file")
        return df
        
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return pd.DataFrame(columns=['Item Name', 'Price'])