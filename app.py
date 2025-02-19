import streamlit as st
import pandas as pd
from config import JANCODE_SCV, OUTPUT_XLSX, RUNNING, WAITING

class PriceScraperUI:
    def __init__(self):
        self.title = "📊 JAN Code Price Scraper Monitor"
        
    def setup_sidebar(self):
        with st.sidebar:
            self._handle_file_upload()
            self._setup_scraping_controls()
            if st.button("Refresh"):
                st.rerun()

    def _handle_file_upload(self):
        st.write("### Upload JAN Code File")
        uploaded_file = st.file_uploader("Choose a CSV file with JAN codes", type="csv")
        if uploaded_file is not None:
            jan_df = pd.read_csv(uploaded_file)
            st.write("JAN Codes loaded:", len(jan_df))
            st.dataframe(jan_df)
            jan_df.to_csv(JANCODE_SCV, index=False)
            st.success(f"JAN codes saved to {JANCODE_SCV}")

    def _setup_scraping_controls(self):
        st.write("### Scraping Control")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Scraping"):
                st.session_state.scraping = True
                st.success("Scraping started!")
        with col2:
            if st.button("Stop Scraping"):
                st.session_state.scraping = False
                st.error("Scraping stopped!")

    def display_main_content(self):
        st.write("### Scraped Prices")
        try:
            df = pd.read_excel(OUTPUT_XLSX)
            st.dataframe(df)
            
            st.write("### Statistics")
            st.write(df.describe())
        except FileNotFoundError:
            st.warning("No scraped data available yet.")

    def run(self):
        st.title(self.title)
        self.setup_sidebar()
        self.display_main_content()

# Initialize and run the app
app = PriceScraperUI()
app.run()
