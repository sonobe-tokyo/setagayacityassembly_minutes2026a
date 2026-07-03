import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="議員キーワードネットワーク", layout="wide")
st.title("📊 議員別キーワード共起ネットワーク")

# 1. データの読み込み（公開用にGitHubやWeb上のURL、または同じフォルダに置いたCSVを指定）
# ※不特定多数公開の場合、Googleドライブではなく、データを同じ場所にアップロードするのが確実です。
@st.cache_data
def load_data():
    return pd.read_csv("looker_co_occurrence.csv")


df = load_data()
members = sorted(df["議員名"].unique())

# 2. 画面サイドにコントロール（プルダウン等）を配置
st.sidebar.header("設定")
target_member = st.sidebar.selectbox("議員名を選んでください:", members)
min_count = st.sidebar.slider("最低共起回数:", min_value=2, max_value=10, value=3)

# 3. 描画処理
df_member = df[df["議員名"] == target_member]
df_filter = df_member[df_member["共起回数"] >= min_count]

if not df_filter.empty:
    G = nx.from_pandas_edgelist(
        df_filter, source="単語A", target="単語B", edge_attr="共起回数"
    )
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.7, seed=42)

    weights = [G[u][v]["共起回数"] * 0.7 for u, v in G.edges()]
    node_sizes = [v * 350 for v in dict(G.degree()).values()]

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="#E3F2FD",
        node_size=node_sizes,
        edgecolors="#2196F3",
        ax=ax,
    )
    nx.draw_networkx_edges(
        G, pos, width=weights, edge_color="#B0BEC5", alpha=0.6, ax=ax
    )
    nx.draw_networkx_labels(
        G, pos, font_size=10, font_weight="bold", ax=ax
    )  # ※クラウドサーバー公開時は英数字、または標準ゴシックが当たります

    plt.axis("off")
    st.pyplot(fig)
else:
    st.warning("条件に合うデータがありません。設定を変更してください。")
