import streamlit as st
import pandas as pd
import config
import os
from pathlib import Path

st.set_page_config(
    page_title="JANコード価格スクレーパーモニター",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

class PriceScraperUI:
    def __init__(self):
        self.initialized = False
        self.Running = False
        
    def setup_sidebar(self):
        with st.sidebar:
            self._setup_scraping_controls()

            if st.button('リロード', use_container_width=True):
                st.rerun()
            
            self.download_excel()
            

    def _handle_file_upload(self):
        uploaded_file = st.file_uploader("JANコードを含むCSVファイルを選択", type="csv")
        if uploaded_file is not None:
            jan_df = pd.read_csv(uploaded_file)
            
            st.write("JANコードが読み込まれました:", len(jan_df))
            jan_df.index = jan_df.index + 1
            height = min(len(jan_df) * 35 + 38, 800)
            
            st.dataframe(jan_df, use_container_width=True, height=height, key = "jancode_update")

            jan_df.to_csv(config.JANCODE_SCV, index=False)
            st.success(f"JANコードが保存されました {config.JANCODE_SCV}")

        else:
            try:
                df = pd.read_csv(config.JANCODE_SCV)
                df.index = df.index + 1
                height = min(len(df) * 35 + 38, 800)
                st.dataframe(df, use_container_width=True, height=height, key = "jancode_original")
                
            except FileNotFoundError:
                st.warning("JANコードデータはまだ利用できません。")

    def _setup_scraping_controls(self):
        st.subheader("スクレイピング制御")

        if self.running():
            st.sidebar.button("停 止", type="primary", use_container_width=True,
                            on_click=self.stop_running)
        else:
            st.sidebar.button("開 始", type="secondary", use_container_width=True,
                            on_click=self.start_running)

    def running(self):
       return os.path.exists(config.RUNNING) 
    
    def start_running(self):
        with open(config.RUNNING, 'w') as file:
            file.write('')

    def stop_running(self):
        file_path = Path(config.RUNNING)
        file_path.unlink()


    def display_main_content(self):
        
        try:
            df = pd.read_excel(config.OUTPUT_XLSX)
            df.index = df.index + 1
            height = min(len(df) * 35 + 38, 800)
            st.dataframe(df, use_container_width=True, height=height, key = "result")
            
        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    def download_excel(self):
        try:
            # Provide an option to download the existing Excel file directly
            with open(config.OUTPUT_XLSX, "rb") as file:
                st.download_button(
                    label="ダウンロード",
                    data=file,
                    file_name="scraped_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    def run(self):
        self.setup_sidebar()

        tab1, tab2 = st.tabs([ "スクラップ価格", "JANコードデータ"])

        with tab1:
            self.display_main_content()

        with tab2:
            self._handle_file_upload()

# Initialize and run the app
app = PriceScraperUI()
app.run()
