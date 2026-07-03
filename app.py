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

# 👥 プルダウンの選択肢の先頭に「✨全員分（全体傾向）」を追加する
raw_members = sorted(df["議員名"].unique())
members_options = ["✨全員分（全体傾向）"] + raw_members

# 2. 画面サイドにコントロール（プルダウン等）を配置
st.sidebar.header("設定")

# 💡 初期設定を「全員分」にする設定
target_member = st.sidebar.selectbox(
    "議員名を選んでください:", 
    options=members_options, 
    index=0  # 0番目（つまり「全員分」）を初期選択にする
)

# 💡 もし「そのべ」議員を初期設定（スタート画面）にしたい場合は、上のコードを消して、
# 以下の【3行】のコメントアウト（#）を外し、上のコードの代わりに使ってください。
# default_index = raw_members.index("そのべ") + 1 if "そのべ" in raw_members else 0
# target_member = st.sidebar.selectbox("議員名を選んでください:", options=members_options, index=default_index)


# スライダーの初期値を全体データ用に少し高め（3回）に設定（ごちゃつき防止）
min_count = st.sidebar.slider("最低共起回数:", min_value=2, max_value=20, value=3)

# 3. データの絞り込み処理
if target_member == "✨全員分（全体傾向）":
    # 全員のデータを合算して、単語ペアごとの総共起回数を計算
    df_grouped = df.groupby(["単語A", "単語B"])["共起回数"].sum().reset_index()
    df_filter = df_grouped[df_grouped["共起回数"] >= min_count]
    title_label = f"【区議会全体】のキーワード共起ネットワーク (合計共起回数 {min_count}回以上)"
else:
    # 特定の議員で絞り込み
    df_member = df[df["議員名"] == target_member]
    df_filter = df_member[df_member["共起回数"] >= min_count]
    title_label = f"【{target_member} 議員】のキーワード共起ネットワーク (共起回数 {min_count}回以上)"

# 4. 描画処理
if not df_filter.empty:
    G = nx.from_pandas_edgelist(df_filter, source="単語A", target="単語B", edge_attr="共起回数")
    fig, ax = plt.subplots(figsize=(11, 9))
    
    # 全体表示のときは少し広めに配置
    k_value = 0.8 if target_member == "✨全員分（全体傾向）" else 0.7
    pos = nx.spring_layout(G, k=k_value, seed=42)
    
    # 線の太さと丸の大きさのバランスを調整
    if target_member == "✨全員分（全体傾向）":
        # 全体時は回数が大きくなるため、線の太さの倍率をマイルドにする
        weights = [G[u][v]["共起回数"] * 0.1 for u, v in G.edges()]
        node_sizes = [v * 150 for v in dict(G.degree()).values()]
    else:
        weights = [G[u][v]["共起回数"] * 0.7 for u, v in G.edges()]
        node_sizes = [v * 350 for v in dict(G.degree()).values()]
    
    nx.draw_networkx_nodes(G, pos, node_color="#E3F2FD", node_size=node_sizes, edgecolors="#2196F3", ax=ax)
    nx.draw_networkx_edges(G, pos, width=weights, edge_color="#B0BEC5", alpha=0.5, ax=ax)
    
    current_font = mpl.rcParams['font.family'][0] if isinstance(mpl.rcParams['font.family'], list) else mpl.rcParams['font.family']
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", font_family=current_font, ax=ax)
    
    plt.title(title_label, fontsize=14, fontweight="bold")
    plt.axis("off")
    st.pyplot(fig)
else:
    st.warning("条件に合うデータがありません。最低共起回数を下げるか、別の議員を選択してください。")
