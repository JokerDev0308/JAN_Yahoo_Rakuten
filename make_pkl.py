import pickle
import json
import os
import streamlit as st



def save_cookies_to_pickle(cookie_json_str, output_path='cookies/yahoo_cookies.pkl'):
    try:
        cookies = json.loads(cookie_json_str)

        formatted = []
        for c in cookies:
            cookie = {
                'name': c['name'],
                'value': c['value'],
                'domain': c.get('domain', ''),
                'path': c.get('path', '/'),
                'secure': c.get('secure', False),
                'httpOnly': c.get('httpOnly', False),
            }
            # Optional expiry
            if 'expirationDate' in c:
                cookie['expiry'] = int(c['expirationDate'])
            formatted.append(cookie)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as f:
            pickle.dump(formatted, f)

        st.success(f"✅ Cookie ファイルを `{output_path}` に保存しました。")
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")
