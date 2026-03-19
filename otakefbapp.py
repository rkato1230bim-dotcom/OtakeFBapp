import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
from pathlib import Path


# ==============================
# ページ設定（タイトルとアイコン）
# ==============================
st.set_page_config(page_title="大竹FB", page_icon="🌊")

#↓file自動遷移の非表示
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)


# ==============================
# 画面タイトル
# ==============================
st.title("🌊 大竹FB")
st.markdown("---")
st.write("FBをみんなで書き込んで、見返せるサイト")


# ==============================
# サイドバー
# ==============================
with st.sidebar:
    st.title("🐬 メニュー")
    page = st.radio("", ["📝 新しいFB", "📚 FB一覧"])
    if page == "📚 FB一覧":
        st.switch_page("pages/fblist_page.py")


# ==============================
# Google Sheets API 認証設定
# ==============================
# Google APIで必要な権限（スプレッドシート操作＋Driveアクセス）
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# JSONキーの場所（このpyファイルと同じフォルダに置く）
json_path = Path(__file__).parent / "otakefbapp-ec4996fda6a1.json"

# 認証情報を作成
creds = Credentials.from_service_account_file(
    str(json_path),
    scopes=scope
)

# gspreadクライアント作成（Google Sheets操作の入り口）
client = gspread.Client(auth=creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1n6HRfdTRgphJmsvBqpaEElMH7l3oPgOYLHb3XENBJvU/edit?usp=sharing"
).sheet1


# ==============================
# シートのデータを取得
# ==============================
data = sheet.get_all_records()


# ==============================
# 入力フォーム（投稿部分）
# ==============================
if page == "📝 新しいFB":
    st.header("📝 新しいFB")

TAGS = ["レスキュー", "シミュレーション","生活"]

# フォームにするとEnterで誤送信しない
with st.form("fb_form", clear_on_submit=True):

    # 日付入力
    input_date = st.date_input("日付", value=date.today())

    # 入力者
    author = st.text_input("入力者")

    # FB内容
    memo = st.text_area("メモ")

    #タグ選択
    selected_tags = st.multiselect("タグ", TAGS) 

    # 送信ボタン
    submitted = st.form_submit_button("➕ 登録")


# ==============================
# 登録処理
# ==============================
if submitted:

    # 空チェック
    if author.strip() and memo.strip():

        # 2行目に挿入（1行目はヘッダー）
        if submitted:
         sheet.insert_rows(
            [[
                str(input_date),
                author.strip(),
                memo.strip(),
                ",".join(selected_tags)  # ← 追加（カンマ区切りで保存）
            ]],
            row=2
        )
        st.success("登録完了！")
        st.rerun()

    else:
        st.warning("入力してね")