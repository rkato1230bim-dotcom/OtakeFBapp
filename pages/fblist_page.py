import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


# ==============================
# ページ設定
# ==============================
st.set_page_config(page_title="FB一覧", page_icon="📚")
#↓fileの非表示
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

TAGS = ["レスキュー", "シミュレーション","生活"]

with st.sidebar:
    st.title("🐬 メニュー")
    page = st.radio("", ["📝 新しいFB", "📚 FB一覧"], index=1)
    if page == "📝 新しいFB":
        st.switch_page("otakefbapp.py")

# ==============================
# Google Sheets API 認証設定
# ==============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.Client(auth=creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1n6HRfdTRgphJmsvBqpaEElMH7l3oPgOYLHb3XENBJvU/edit?usp=sharing"
).sheet1

data = sheet.get_all_records()

# ==============================
# FB一覧
# ==============================
st.title("📚 FB一覧")

filter_tag = st.selectbox("🔍 タグで絞り込む", ["すべて"] + TAGS)

if not data:
    st.info("初めての投稿者になろう！")
else:
    for i, row in enumerate(data):
        row_tags = row.get("tags", "")
        if filter_tag != "すべて" and filter_tag not in row_tags:
            continue

        with st.container():
            col1, col2 = st.columns([8, 1])

            with col1:
                st.markdown(f"### {row.get('date','')}")
                st.write("入力者:", row.get("author",""))
                st.write(row.get("memo",""))
                if row_tags:
                    for t in row_tags.split(","):
                        st.markdown(f"`{t.strip()}`")

            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state[f"confirm_{i}"] = True

            if st.session_state.get(f"confirm_{i}"):
                st.warning("本当に消しますか？")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("はい", key=f"yes_{i}"):
                        sheet.delete_rows(start_index=i + 2, end_index=i + 2)
                        st.session_state[f"confirm_{i}"] = False
                        st.rerun()
                with col_no:
                    if st.button("いいえ", key=f"no_{i}"):
                        st.session_state[f"confirm_{i}"] = False
                        st.rerun()

        st.markdown("---")