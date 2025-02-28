import streamlit as st
import pandas as pd
import config
import os
from pathlib import Path
import bcrypt

# Set page configuration
st.set_page_config(
    page_title="JANコード価格スクレーパーモニター",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Column name mapping and ordering
column_name_mapping = {
    'JAN': 'JAN（マスタ）',
    'price': '価格（マスタ）',
    'Yahoo Price': 'yahoo_実質価格',
    'Rakuten Price': '楽天_実質価格',
    'Price Difference': '価格差（マスタ価格‐Y!と楽の安い方）',
    'Min Price URL': '対象リンク（Y!と楽の安い方）',
    'datetime': 'データ取得時間（Y!と楽の安い方）'
}

ordered_columns = [
    'JAN（マスタ）',
    '価格（マスタ）',
    'yahoo_実質価格',
    '楽天_実質価格',
    '価格差（マスタ価格‐Y!と楽の安い方）',
    '対象リンク（Y!と楽の安い方）',
    'データ取得時間（Y!と楽の安い方）'
]

# Class for price scraper UI
class PriceScraperUI:
    def __init__(self):
        self.initialized = False
        self.Running = False
        
    def setup_sidebar(self):
        with st.sidebar:
            if 'logged_in' not in st.session_state or not st.session_state.logged_in:
                self._setup_login()
            else:
                self._setup_scraping_controls()

            if st.button('リロード', use_container_width=True):
                st.rerun()
            
            if 'logged_in' in st.session_state and st.session_state.logged_in:
                self.download_excel()

    def _setup_login(self):
        st.subheader("ログイン")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("ログイン"):
            if self.check_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"ようこそ、{username}さん!")
                st.experimental_rerun()
            else:
                st.error("無効なユーザー名またはパスワードです。")

    def check_login(self, username, password):
        try:
            # Load user data from CSV
            df = pd.read_csv('users.csv')
            user = df[df['username'] == username]

            if not user.empty:
                stored_hashed_password = user.iloc[0]['password'].encode('utf-8')

                # Check if entered password matches the stored hashed password
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    return True
        except FileNotFoundError:
            st.error("ユーザーデータベースが見つかりません。")
        return False

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
        if not self.running():
            os.makedirs(os.path.dirname(config.RUNNING), exist_ok=True)
        with open(config.RUNNING, 'w') as file:
            file.write('1')

    def stop_running(self):
        file_path = Path(config.RUNNING)
        file_path.unlink()

    def display_main_content(self):
        try:
            # Load the DataFrame from the Excel file
            df = pd.read_excel(config.OUTPUT_XLSX)
            
            # Drop the "Yahoo! Link" column
            if "Yahoo! Link" in df.columns:
                df.drop(columns=["Yahoo! Link"], inplace=True)

            df = df.rename(columns=column_name_mapping)[ordered_columns]

            df.index = df.index + 1
            height = min(len(df) * 35 + 38, 800)
            st.dataframe(df, use_container_width=True, height=height, key="result")

        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    def download_excel(self):
        try:
            # Load the DataFrame from the Excel file
            df = pd.read_excel(config.OUTPUT_XLSX)
            # Drop the "Yahoo! Link" column
            if "Yahoo! Link" in df.columns:
                df.drop(columns=["Yahoo! Link"], inplace=True)

            df = df.rename(columns=column_name_mapping)[ordered_columns]

            temp_file_path = "/tmp/scraped_data_updated.xlsx"
            df.to_excel(temp_file_path, index=False)

            # Provide an option to download the updated Excel file
            with open(temp_file_path, "rb") as file:
                st.download_button(
                    label="ダウンロード",
                    data=file,
                    file_name="scraped_data_updated.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            # Optionally, remove the temporary file after download
            os.remove(temp_file_path)

        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    def _handle_file_upload(self):
        uploaded_file = st.file_uploader("JANコードを含むCSVファイルを選択", type="csv")
        if uploaded_file is not None:
            jan_df = pd.read_csv(uploaded_file)
            
            st.write("JANコードが読み込まれました:", len(jan_df))
            jan_df.index = jan_df.index + 1
            height = min(len(jan_df) * 35 + 38, 800)
            
            st.dataframe(jan_df, use_container_width=True, height=height, key="jancode_update")

            jan_df.to_csv(config.JANCODE_SCV, index=False)
            st.success(f"JANコードが保存されました {config.JANCODE_SCV}")

        else:
            try:
                df = pd.read_csv(config.JANCODE_SCV)
                df.index = df.index + 1
                height = min(len(df) * 35 + 38, 800)
                st.dataframe(df, use_container_width=True, height=height, key="jancode_original")
                
            except FileNotFoundError:
                st.warning("JANコードデータはまだ利用できません。")

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
