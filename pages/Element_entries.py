
import streamlit as st
import pandas as pd
import os

# Set local database file
DB_FILE = "element_entries.csv"

st.title("📄 Elements Entry Form")

# --- Input fields ---
doc_type = st.text_input("Type of Document")
description = st.text_area("Brief Description")
key_amount = st.number_input("Key Element Amount", min_value=0.0, step=0.01)
key_name = st.text_input("Key Element Name")

# Load existing entries
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=["Document Type", "Description", "Key Element Amount", "Key Element Name"])

# --- Save Button ---
if st.button("💾 Save Entry"):
    if doc_type and description and key_name:
        new_entry = {
            "Document Type": doc_type,
            "Description": description,
            "Key Element Amount": key_amount,
            "Key Element Name": key_name
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.success("✅ Entry saved successfully!")
    else:
        st.warning("⚠️ Please fill in all required fields.")

# --- Load External CSV File ---
st.sidebar.subheader("📂 Load External CSV (Optional)")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

display_df = None

if uploaded_file is not None:
    try:
        display_df = pd.read_csv(uploaded_file)
        st.success("✅ Uploaded file loaded successfully.")
    except Exception as e:
        st.error(f"❌ Error loading uploaded file: {e}")
else:
    display_df = df  # Use the saved entries

# --- Show Final DataFrame ---
st.subheader("📋 Displayed Entries")
if not display_df.empty:
    st.dataframe(display_df, height=200)  # Adjust height to make it scrollable)

    # --- Download Button ---
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="document_entries.csv",
        mime="text/csv"
    )
else:
    st.info("No entries to display yet.")
