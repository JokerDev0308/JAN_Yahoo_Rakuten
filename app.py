import streamlit as st
import pandas as pd
import os
from pathlib import Path
import config
from session_manager import SessionManager

session_manager = SessionManager()

def authenticate(username: str, password: str) -> bool:
    """Authenticate user"""
    if session_manager.validate_user(username, password):
        config.CURRENT_USER = username
        session = get_session_id()
        config.LOGIN_STATE[session] = True
        return True
    return False

def get_session_id():
    """Get session ID"""
    return "Admin"  # Dummy value for simplicity

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

class PriceScraperUI:
    def __init__(self):
        self.initialized = False
        self.running = False

    def setup_sidebar(self):
        """Setup the sidebar for user control"""
        with st.sidebar:
            st.subheader("メニュー")
            self._setup_scraping_controls()
            if st.button('リロード', use_container_width=True):
                st.experimental_rerun()  # Modern way to force a rerun

            self.download_excel()

            if st.button("ログアウト", use_container_width=True):
                self.logout()

    def show_login_modal(self):
        """Display login modal for user authentication"""
        col1, col2, col3 = st.columns(3)
        with col2:
            with st.container():
                st.markdown("""
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
                """, unsafe_allow_html=True)

                st.subheader("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")

                login_button = st.button("Login")
                if login_button:
                    if authenticate(username, password):
                        st.session_state.logged_in = True
                        st.success("Login successful!")
                        st.experimental_rerun()  # Re-run to initialize the session
                    else:
                        st.error("Invalid username or password.")

    def _handle_file_upload(self):
        """Handle file upload functionality for JAN codes"""
        uploaded_file = st.file_uploader("JANコードを含むCSVファイルを選択", type="csv")
        if uploaded_file is not None:
            try:
                jan_df = pd.read_csv(uploaded_file)
                st.write("JANコードが読み込まれました:", len(jan_df))
                jan_df.index = jan_df.index + 1
                height = min(len(jan_df) * 35 + 38, 800)
                st.dataframe(jan_df, use_container_width=True, height=height, key="jancode_update")

                # Save to config.JANCODE_SCV
                jan_df.to_csv(config.JANCODE_SCV, index=False)
                st.success(f"JANコードが保存されました {config.JANCODE_SCV}")
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
        else:
            self.load_existing_jan_data()

    def load_existing_jan_data(self):
        """Load existing JAN data if the file is found"""
        try:
            df = pd.read_csv(config.JANCODE_SCV)
            df.index = df.index + 1
            height = min(len(df) * 35 + 38, 800)
            st.dataframe(df, use_container_width=True, height=height, key="jancode_original")
        except FileNotFoundError:
            st.warning("JANコードデータはまだ利用できません。")

    def _setup_scraping_controls(self):
        """Setup scraping control buttons"""
        st.subheader("スクレイピング制御")
        if self.running():
            st.sidebar.button("停 止", type="primary", use_container_width=True, on_click=self.stop_running)
        else:
            st.sidebar.button("開 始", type="secondary", use_container_width=True, on_click=self.start_running)

    def running(self):
        """Check if scraping is running"""
        return os.path.exists(config.RUNNING)

    def start_running(self):
        """Start scraping operation"""
        if not self.running():
            os.makedirs(os.path.dirname(config.RUNNING), exist_ok=True)
        with open(config.RUNNING, 'w') as file:
            file.write('1')

    def stop_running(self):
        """Stop scraping operation"""
        file_path = Path(config.RUNNING)
        file_path.unlink()

    def display_main_content(self):
        """Display main scraping results"""
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
        """Download the scraped Excel file"""
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
        """Logout the user"""
        session = get_session_id()
        config.LOGIN_STATE[session] = False
        config.CURRENT_USER = None
        st.experimental_rerun()  # Re-run to clear the session

    def run(self):
        """Main method to control the app flow"""
        session = get_session_id()
        if session in config.LOGIN_STATE and config.LOGIN_STATE[session]:
            self.setup_sidebar()
            tab1, tab2 = st.tabs(["スクレイプ価格", "JANコードデータ"])
            with tab1:
                self.display_main_content()
            with tab2:
                self._handle_file_upload()
        else:
            self.show_login_modal()

# Initialize and run the app
app = PriceScraperUI()
app.run()
