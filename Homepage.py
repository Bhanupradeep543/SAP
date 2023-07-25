import streamlit as st

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)
st.markdown(f"""<style>.stApp {{                        
             background: url("https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.linkedin.com%2Fcompany%2Fseil-energy-india-limited&psig=AOvVaw2iyuaQ5bFFXtfQx2D3Rw_C&ust=1690385020699000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCJCexdSXqoADFQAAAAAdAAAAABAE");
             background-size: cover}}
         </style>""",unsafe_allow_html=True)

st.title("Main Page")
st.subheader("SEIL SAP Notification analysis")
st.sidebar.success("Select a page above.")
