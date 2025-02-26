import streamlit as st
import pandas as pd
from config import JANCODE_SCV, OUTPUT_XLSX, RUNNING, WAITING

class PriceScraperUI:
    def __init__(self):
        self.title = "📊 JAN Code Price Scraper Monitor"
        
    def setup_sidebar(self):
        with st.sidebar:
            self._setup_scraping_controls()
            if st.button("Refresh"):
                st.rerun()

    def _handle_file_upload(self):
        st.write("### Upload JAN Code File")
        uploaded_file = st.file_uploader("Choose a CSV file with JAN codes", type="csv")
        if uploaded_file is not None:
            jan_df = pd.read_csv(uploaded_file)
            
            st.write("JAN Codes loaded:", len(jan_df))
            jan_df.index = jan_df.index + 1
            height = min(len(jan_df) * 35 + 38, 800)
            
            st.dataframe(jan_df, use_container_width=True, height=height, key = "jancode_update")

            jan_df.to_csv(JANCODE_SCV, index=False)
            st.success(f"JAN codes saved to {JANCODE_SCV}")

        else:
            try:
                df = pd.read_excel(JANCODE_SCV)
                df.index = df.index + 1
                height = min(len(df) * 35 + 38, 800)
                st.dataframe(df, use_container_width=True, height=height, key = "jancode_original")
                
            except FileNotFoundError:
                st.warning("No scraped data available yet.")

    def _setup_scraping_controls(self):
        st.write("### Scraping Control")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Scraping",use_container_width=True):
                st.session_state.scraping = True
                st.success("Scraping started!")
        with col2:
            if st.button("Stop Scraping",use_container_width=True):
                st.session_state.scraping = False
                st.error("Scraping stopped!")

    def display_main_content(self):
        st.write("### Scraped Prices")
        try:
            df = pd.read_excel(OUTPUT_XLSX)
            df.index = df.index + 1
            height = min(len(df) * 35 + 38, 800)
            st.dataframe(df, use_container_width=True, height=height, key = "result")
            
        except FileNotFoundError:
            st.warning("No scraped data available yet.")

    def download_excel(self):
        try:
            # Provide an option to download the existing Excel file directly
            with open(OUTPUT_XLSX, "rb") as file:
                st.download_button(
                    label="Download Scraped Data",
                    data=file,
                    file_name="scraped_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        except FileNotFoundError:
            st.warning("No scraped data available yet.")

    def run(self):
        st.title(self.title)
        self.setup_sidebar()

        tab1, tab2 = st.tabs([ "Result", "JAN Code"])

        with tab1:
            self.download_excel()
            self.display_main_content()
        with tab2:
            self._handle_file_upload()

# Initialize and run the app
app = PriceScraperUI()
app.run()
