import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ==============================
# ページ設定
# ==============================
st.set_page_config(page_title="FB一覧", page_icon="📚")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

TAGS = ["レスキュー", "CPR","FA","シミュレーション","生活"]

# ==============================
# サイドバー
# ==============================
with st.sidebar:
    st.title("🐬 メニュー")
    page = st.radio("", ["📝 新しいFB", "📚 FB一覧"], index=1)
    if page == "📝 新しいFB":
        st.switch_page("otakefbapp.py")

# ==============================
# Google Sheets 認証
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

# ==============================
# 絞り込みバー
# ==============================
col_search, col_tag, col_sort = st.columns([3, 2, 2])

with col_search:
    keyword = st.text_input("🔍 キーワード検索", placeholder="キーワードを入力...")

with col_tag:
    filter_tag = st.selectbox("タグで絞り込む", ["すべて"] + TAGS)

with col_sort:
    sort_order = st.selectbox("並び順", ["新しい順 ↓", "古い順 ↑"])

st.markdown("---")

# ==============================
# データ絞り込み
# ==============================
filtered = []
for i, row in enumerate(data):
    row_tags = row.get("tags", "")
    row_memo = row.get("memo", "")
    row_author = row.get("author", "")

    # タグフィルター
    if filter_tag != "すべて" and filter_tag not in row_tags:
        continue

    # キーワードフィルター
    if keyword and keyword not in row_memo and keyword not in row_author:
        continue

    filtered.append((i, row))

# ==============================
# ソート
# ==============================
filtered.sort(key=lambda x: x[1].get("date", ""), reverse=(sort_order == "新しい順 ↓"))

# ==============================
# 日付でグループ化して表示
# ==============================
if not filtered:
    st.info("該当するFBがありません")
else:
    # 日付ごとにグループ化
    from collections import defaultdict
    groups = defaultdict(list)
    for i, row in filtered:
        groups[row.get("date", "")].append((i, row))

    # 日付順に並べる
    sorted_dates = sorted(groups.keys(), reverse=(sort_order == "新しい順 ↓"))

    for date_key in sorted_dates:
        st.markdown(f"### 📅 {date_key}")

        rows_in_date = groups[date_key]
        cols = st.columns(2)

        for idx, (i, row) in enumerate(rows_in_date):
            with cols[idx % 2]:
                with st.container():
                    row_tags = row.get("tags", "")
                    tag_list = [t.strip() for t in row_tags.split(",") if t.strip()]

                    with st.container(border=True):
                        # タグ表示
                        if tag_list:
                            tag_str = " ".join([f"`{t}`" for t in tag_list])
                            st.markdown(tag_str)

                        # 編集モード
                        if st.session_state.get(f"edit_{i}"):
                            new_memo = st.text_area("メモ編集", value=row.get("memo", ""), key=f"memo_{i}")
                            new_tags = st.multiselect("タグ編集", TAGS, default=[t.strip() for t in tag_list if t.strip() in TAGS], key=f"tags_{i}")
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button("💾 保存", key=f"save_{i}"):
                                    sheet.update_cell(i + 2, 3, new_memo)
                                    sheet.update_cell(i + 2, 4, ",".join(new_tags))
                                    st.session_state[f"edit_{i}"] = False
                                    st.rerun()
                            with col_cancel:
                                if st.button("キャンセル", key=f"cancel_{i}"):
                                    st.session_state[f"edit_{i}"] = False
                                    st.rerun()

                        else:
                            st.write(row.get("memo", ""))
                            st.caption(f"入力者：{row.get('author', '')}")

                            col_edit, col_del = st.columns(2)
                            with col_edit:
                                if st.button("✏️ 編集", key=f"edit_btn_{i}"):
                                    st.session_state[f"edit_{i}"] = True
                                    st.rerun()
                            with col_del:
                                if st.button("🗑️ 削除", key=f"delete_{i}"):
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