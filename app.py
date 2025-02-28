import streamlit as st
import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager

session_manager = SessionManager()

def authenticate(username: str, password: str) -> bool:
    if session_manager.validate_user(username, password):
        session_id = session_manager.create_session(username)
        st.session_state.session_id = session_id
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    return False

# Add session validation at app startup
if "session_id" in st.session_state:
    session = session_manager.get_session(st.session_state.session_id)
    if session:
        st.session_state.authenticated = True
        st.session_state.username = session["username"]
    else:
        st.session_state.authenticated = False
else:
    st.session_state.authenticated = False




# Set Streamlit page configuration
st.set_page_config(
    page_title="JANコード価格スクレーパーモニター",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Column name mappings
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

# Main application class
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

            df = df.rename(columns=column_name_mapping)[ordered_columns]
            df.index = df.index + 1
            height = min(len(df) * 35 + 38, 800)
            st.dataframe(df, use_container_width=True, height=height, key="result")
        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    def download_excel(self):
        try:
            df = pd.read_excel(config.OUTPUT_XLSX)
            if "Yahoo! Link" in df.columns:
                df.drop(columns=["Yahoo! Link"], inplace=True)

            df = df.rename(columns=column_name_mapping)[ordered_columns]

            temp_file_path = "/tmp/scraped_data_updated.xlsx"
            df.to_excel(temp_file_path, index=False)

            with open(temp_file_path, "rb") as file:
                st.download_button(
                    label="ダウンロード",
                    data=file,
                    file_name="scraped_data_updated.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            os.remove(temp_file_path)
        except FileNotFoundError:
            st.warning("スクレイピングされたデータはまだない。")

    
    def logout(self):
        if "session_id" in st.session_state:
            del st.session_state.session_id
        st.session_state.authenticated = False
        st.rerun()

    def run(self):
        self.setup_sidebar()
        tab1, tab2 = st.tabs(["スクラップ価格", "JANコードデータ"])
        with tab1:
            self.display_main_content()
        with tab2:
            self._handle_file_upload()

# Initialize and run the app
app = PriceScraperUI()
app.run()
