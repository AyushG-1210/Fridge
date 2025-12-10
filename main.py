import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION & CSS ---
st.set_page_config(page_title="Fridge", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to hide default Streamlit headers and tighten spacing for mobile
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 1rem; padding-left: 1rem; padding-right: 1rem;}
        div[data-testid="stGrid"] {gap: 10px;}
    </style>
""", unsafe_allow_html=True)

CSV_FILE = 'fridge_data.csv'

# --- 2. DATA FUNCTIONS ---
def load_data():
    try:
        df = pd.read_csv(CSV_FILE)
        # Convert string dates back to datetime objects for calculation
        df['Date Added'] = pd.to_datetime(df['Date Added'])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['Item', 'Date Added'])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def get_time_display(date_added):
    """Calculates how long the item has been in the fridge"""
    delta = datetime.now() - date_added
    if delta.days == 0:
        hours = delta.seconds // 3600
        return f"{hours}h ago"
    return f"{delta.days}d ago"

# --- 3. APP LOGIC ---
df = load_data()

# --- TOP BAR (Plus Button) ---
col1, col2 = st.columns([6, 1]) # Push button to the right

with col2:
    # Popover creates a small container that opens when clicked
    with st.popover("➕", use_container_width=True):
        st.write("Add Item")
        with st.form("add_form", border=False):
            new_item_name = st.text_input("Name", placeholder="e.g. Milk")
            if st.form_submit_button("Save"):
                if new_item_name:
                    new_entry = pd.DataFrame({
                        'Item': [new_item_name], 
                        'Date Added': [datetime.now()]
                    })
                    df = pd.concat([df, new_entry], ignore_index=True)
                    save_data(df)
                    st.rerun()

st.markdown("---") # The <hr> separator

# --- THE CUBES (Grid Layout) ---
if not df.empty:
    # Sort by newest first
    df = df.sort_values(by='Date Added', ascending=False).reset_index(drop=True)
    
    # Create a grid of 3 columns (adjust to 2 if your phone screen is very narrow)
    cols = st.columns(3)
    
    for index, row in df.iterrows():
        # Cycle through columns: 0, 1, 2, 0, 1, 2...
        current_col = cols[index % 3]
        
        with current_col:
            # The "Cube" is a container with a border
            with st.container(border=True):
                # Item Name (Bold)
                st.markdown(f"**{row['Item']}**")
                
                # Time Display (Small text)
                time_str = get_time_display(row['Date Added'])
                st.caption(f"🕒 {time_str}")
                
                # Delete Button (Small garbage can)
                if st.button("🗑️", key=f"del_{index}"):
                    df = df.drop(index)
                    save_data(df)
                    st.rerun()

else:
    st.info("Fridge is empty.")