import streamlit as st
import pandas as pd
import config
import os
from pathlib import Path

# Set Streamlit page configuration
st.set_page_config(
    page_title="JANコード価格スクレーパーモニター",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Authentication state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Authentication function
def authenticate(username, password):
    valid_users = {"admin": "password123", "user": "test123"}
    if username in valid_users and valid_users[username] == password:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.error("Invalid username or password")

# Simulated Modal: Show login screen if not authenticated
if not st.session_state.authenticated:
    login_container = st.empty()
    
    with login_container.container():
        st.markdown("### 🔒 ログインが必要です")
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            authenticate(username, password)

    st.stop()  # Block the app until authenticated

# Main app class
class PriceScraperUI:
    def __init__(self):
        self.initialized = False
        self.Running = False

    def setup_sidebar(self):
        with st.sidebar:
            st.subheader("メニュー")
            self._setup_scraping_controls()

            if st.button('リロード', use_container_width=True):
                st.rerun()

            self.download_excel()

            # Logout button
            if st.button("ログアウト", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

    def _setup_scraping_controls(self):
        st.subheader("スクレイピング制御")
        if self.running():
            st.sidebar.button("停 止", type="primary", use_container_width=True, on_click=self.stop_running)
        else:
            st.sidebar.button("開 始", type="secondary", use_container_width=True, on_click=self.start_running)

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
            df = pd.read_excel(config.OUTPUT_XLSX)
            if "Yahoo! Link" in df.columns:
                df.drop(columns=["Yahoo! Link"], inplace=True)

            st.dataframe(df, use_container_width=True)
        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    def download_excel(self):
        try:
            df = pd.read_excel(config.OUTPUT_XLSX)
            if "Yahoo! Link" in df.columns:
                df.drop(columns=["Yahoo! Link"], inplace=True)

            temp_file_path = "/tmp/scraped_data.xlsx"
            df.to_excel(temp_file_path, index=False)

            with open(temp_file_path, "rb") as file:
                st.download_button(
                    label="ダウンロード",
                    data=file,
                    file_name="scraped_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            os.remove(temp_file_path)
        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    def run(self):
        self.setup_sidebar()
        tab1, tab2 = st.tabs(["スクラップ価格", "JANコードデータ"])
        with tab1:
            self.display_main_content()
        with tab2:
            st.write("ここでファイルアップロードができます。")

# Run the app
app = PriceScraperUI()
app.run()
