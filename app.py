import streamlit as st

import pandas as pd
import config
import os
from pathlib import Path
from session_manager import SessionManager
import config
from http.cookies import SimpleCookie

session_manager = SessionManager()

def authenticate(username: str, password: str) -> bool:
    if session_manager.validate_user(username, password):
        config.CURRENT_USER = username
        # session = get_session_id()
        # config.LOGIN_STATE[session] = True
        return True
    return False

# def get_session_id():
#     params = st.query_params()
#     cookie_value = params.get("X", [""])[0]  
#     return cookie_value

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

        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False

    def setup_sidebar(self):
        with st.sidebar:
            st.subheader("メニュー")
            self._setup_scraping_controls()

            if st.button('リロード', use_container_width=True):
                st.rerun()

            self.download_excel()

            # Logout button
            if st.button("ログアウト", use_container_width=True):
                self.logout()


    def show_login_modal(self):
        col1, col2, col3 = st.columns(3)
        with col2:
                        
            with st.container(border=True):

                st.markdown(
                    """
                    <style>
                        #login{
                            text-align:center;
                        }

                        .stButton{
                            text-align:center;
                        }

                        .stButton>button{
                            min-width:7rem;
                        }
                    </style>
                    """
                , unsafe_allow_html=True)
                
                st.subheader("ログイン")

                username = st.text_input("ユーザー名")
                password = st.text_input("パスワード", type="password")
                
                login_button = st.button("ログイン")
                if login_button:
                    if authenticate(username, password):
                        st.session_state.logged_in = True
                        st.success("ログインに成功しました!")
                        st.rerun()
                    else:
                        st.error("ユーザー名またはパスワードが無効です。")


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
        # session = get_session_id()
        st.session_state.logged_in = False
        # config.LOGIN_STATE[session] = False
        config.CURRENT_USER = None
        st.rerun()

    def run(self):
        #session = get_session_id()
        # if session in config.LOGIN_STATE and config.LOGIN_STATE[session]:
        if st.session_state.logged_in:
            self.setup_sidebar()
            tab1, tab2 = st.tabs(["スクラップ価格", "JANコードデータ"])
            with tab1:
                self.display_main_content()
            with tab2:
                self._handle_file_upload()
        else:
            self.show_login_modal()

# Initialize and run the app
app = PriceScraperUI()
app.run()
