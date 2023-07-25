import streamlit as st

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)
st.title("SEIL SAP Notification analysis")
st.subheader("Data considered for analysis from Jan-2016 to May-2022")
st.subheader("Total notifications considered for this analysis are: 97993")
st.sidebar.success("Select a page above.")
