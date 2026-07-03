import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import matplotlib as mpl
import os

# ==============================================================================
# 🔤 日本語文字化け対策
# ==============================================================================
import matplotlib.font_manager as fm
try:
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        font_name = fm.FontProperties(fname=font_path).get_name()
        mpl.rcParams['font.family'] = font_name
    else:
        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'DejaVu Sans', 'sans-serif']
except Exception as e:
    pass

mpl.rcParams['axes.unicode_minus'] = False
# ==============================================================================

st.set_page_config(page_title="議員キーワードネットワーク", layout="wide")
st.title("📊 議員別キーワード共起ネットワーク")

# 1. データの読み込み
@st.cache_data
def load_data():
    return pd.read_csv("looker_co_occurrence.csv")

df = load_data()

# 👥 議員リストを五十音順に取得
raw_members = sorted(df["議員名"].unique())

# ⭐ 【初期表示の設定】開いた瞬間に表示したい議員名を指定
DEFAULT_MEMBER = "石川ナオミ"

# リスト内から「石川ナオミ」の位置を探し、見つからなければ先頭にする
if DEFAULT_MEMBER in raw_members:
    default_index = raw_members.index(DEFAULT_MEMBER)
else:
    default_index = 0

# 2. 画面サイドにコントロール（プルダウン・スライダー）を配置
st.sidebar.header("設定")

target_member = st.sidebar.selectbox(
    "議員名を選んでください:", 
    options=raw_members, 
    index=default_index  # 起動時は石川ナオミ議員を初期選択にする
)

# 1人ずつの表示に戻ったため、スライダーの初期値は「3」に固定してスッキリ見せます
min_count = st.sidebar.slider("最低共起回数:", min_value=2, max_value=10, value=3)

# 3. データの絞り込み処理
df_member = df[df["議員名"] == target_member]
df_filter = df_member[df_member["共起回数"] >= min_count]

title_label = f"【{target_member} 議員】のキーワード共起ネットワーク (共起回数 {min_count}回以上)"

# 4. 描画処理
if not df_filter.empty:
    G = nx.from_pandas_edgelist(df_filter, source="単語A", target="単語B", edge_attr="共起回数")
    fig, ax = plt.subplots(figsize=(11, 9))
    
    # 綺麗に広がる配置アルゴリズム
    pos = nx.spring_layout(G, k=0.7, seed=42)
    
    # 線の太さと丸の大きさのバランス調整
    weights = [G[u][v]["共起回数"] * 0.7 for u, v in G.edges()]
    node_sizes = [v * 350 for v in dict(G.degree()).values()]
    
    nx.draw_networkx_nodes(G, pos, node_color="#E3F2FD", node_size=node_sizes, edgecolors="#2196F3", ax=ax)
    nx.draw_networkx_edges(G, pos, width=weights, edge_color="#B0BEC5", alpha=0.6, ax=ax)
    
    current_font = mpl.rcParams['font.family'][0] if isinstance(mpl.rcParams['font.family'], list) else mpl.rcParams['font.family']
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", font_family=current_font, ax=ax)
    
    plt.title(title_label, fontsize=14, fontweight="bold")
    plt.axis("off")
    st.pyplot(fig)
else:
    st.warning("条件に合うデータがありません。最低共起回数を下げるか、別の議員を選択してください。")
