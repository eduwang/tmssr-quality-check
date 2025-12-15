import os
import re
from datetime import datetime
from typing import Tuple, List, Dict

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(page_title="TMSSR Quality Check", layout="wide")


def parse_user_and_timestamp_from_filename(path: str) -> Tuple[str, datetime]:
    """
    파일명 형식: "사용자명_YYYY. M. D. 오전/오후 H-MM-SS.csv"
    예) "영준정_2025. 12. 4. 오후 11-50-53.csv"
    반환: (사용자명, datetime)
    """
    base = os.path.basename(path)
    if not base.lower().endswith(".csv"):
        raise ValueError(f"Not a CSV file: {base}")
    name_part, rest = base.rsplit(".csv", 1)[0].split("_", 1)

    # 2025. 12. 4. 오후 11-50-53
    m = re.match(
        r"^(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(오전|오후)\s*(\d{1,2})-(\d{2})-(\d{2})$",
        rest.strip(),
    )
    if not m:
        raise ValueError(f"Unexpected datetime format in filename: {base}")
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    ampm, hh, mm, ss = m.group(4), int(m.group(5)), int(m.group(6)), int(m.group(7))

    # 한국어 AM/PM 처리
    if ampm == "오전":
        hour = 0 if hh == 12 else hh
    else:  # 오후
        hour = 12 if hh == 12 else hh + 12

    ts = datetime(year, month, day, hour, mm, ss)
    return name_part, ts


def read_csv_with_encoding(path: str) -> pd.DataFrame:
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    # 마지막 시도: 인코딩 자동 추정 없이 기본
    return pd.read_csv(path)


CATEGORY_CANONICAL: Dict[str, str] = {
    "eliciting": "Eliciting",
    "responding": "Responding",
    "facilitating": "Facilitating",
    "faciliatating": "Facilitating",  # 흔한 오탈자 대비
    "extending": "Extending",
}
CATEGORIES: List[str] = [
    "Eliciting",
    "Responding",
    "Facilitating",
    "Extending",
]


def aggregate_folder(data_dir: str) -> pd.DataFrame:
    """data_dir 내 모든 CSV에 대해 사용자/시간별, 카테고리별 Low/High 개수를 집계"""
    rows = []
    csv_files = sorted(
        [
            os.path.join(data_dir, f)
            for f in os.listdir(data_dir)
            if f.lower().endswith(".csv")
        ]
    )
    for fpath in csv_files:
        try:
            user, ts = parse_user_and_timestamp_from_filename(fpath)
        except Exception:
            # 파일명이 규칙과 다르면 스킵 (필요 시 경고 노출)
            continue

        df = read_csv_with_encoding(fpath)

        # 필요한 컬럼 표준화
        cols = {c.strip(): c for c in df.columns}
        tm_col = None
        pot_col = None
        # TMSSR / Potential 컬럼 찾기 (대소문자 및 공백 관대하게)
        for c in df.columns:
            cl = str(c).strip().lower()
            if cl == "tmssr":
                tm_col = c
            if cl == "potential":
                pot_col = c
        if tm_col is None or pot_col is None:
            # 필수 컬럼 없으면 스킵
            continue

        tm_vals = (
            df[tm_col]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(lambda x: CATEGORY_CANONICAL.get(x, None))
        )
        pot_vals = df[pot_col].astype(str).str.strip().str.lower()

        for cat in CATEGORIES:
            mask_cat = tm_vals == cat
            if mask_cat.any():
                low_count = (pot_vals[mask_cat] == "low").sum()
                high_count = (pot_vals[mask_cat] == "high").sum()
            else:
                low_count = 0
                high_count = 0

            rows.append(
                {
                    "user": user,
                    "timestamp": ts,
                    "category": cat,
                    "low": int(low_count),
                    "high": int(high_count),
                    "file": os.path.basename(fpath),
                }
            )

    if not rows:
        return pd.DataFrame(columns=["user", "timestamp", "category", "low", "high", "file"])

    df_all = pd.DataFrame(rows)
    df_all.sort_values(["user", "timestamp", "category"], inplace=True)

    # 사용자별 파일(=타임스탬프) 순서대로 포인트 인덱스 부여 (1..N)
    point_map = (
        df_all[["user", "timestamp", "file"]]
        .drop_duplicates()
        .sort_values(["user", "timestamp"])
        .copy()
    )
    point_map["point"] = point_map.groupby("user").cumcount() + 1
    df_all = df_all.merge(point_map, on=["user", "timestamp", "file"], how="left")
    return df_all


def plot_user_point_totals(df_user: pd.DataFrame, user: str):
    """사용자별 데이터 포인트(파일 단위) 기준 Low/High 총합 꺾은선 그래프"""
    # 포인트 순서
    order = (
        df_user[["point", "timestamp", "file"]]
        .drop_duplicates()
        .sort_values(["point"])
    )
    x_vals = [str(int(p)) for p in order["point"].tolist()]  # 카테고리형 축으로 사용

    # 포인트별 총합 계산
    totals = (
        df_user.groupby("point", as_index=False)[["low", "high"]].sum()
        .sort_values("point")
    )
    y_low = []
    y_high = []
    by_point = {int(r.point): (int(r.low), int(r.high)) for _, r in totals.iterrows()}
    for p in order["point" ].tolist():
        low, high = by_point.get(int(p), (0, 0))
        y_low.append(low)
        y_high.append(high)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_low,
            mode="lines+markers",
            name="Low 합계",
            line=dict(color="#1f77b4"),
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_high,
            mode="lines+markers",
            name="High 합계",
            line=dict(color="#ff7f0e"),
            marker=dict(size=6),
        )
    )
    fig.update_layout(
        title_text=f"사용자: {user} — 데이터 포인트별 Low/High 총합",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig.update_xaxes(
        title_text="데이터 포인트(파일 순서)",
        type="category",
        categoryorder="array",
        categoryarray=x_vals,
        tickmode="array",
        tickvals=x_vals,
        ticktext=x_vals,
    )
    fig.update_yaxes(title_text="개수")
    return fig


def plot_user_points(df_user: pd.DataFrame, user: str):
    """사용자별 데이터 포인트(파일 단위) 기준 범주별 Low/High 꺾은선 서브플롯"""
    # 포인트 순서
    order = (
        df_user[["point", "timestamp", "file"]]
        .drop_duplicates()
        .sort_values(["point"])
    )
    x_vals = [str(int(p)) for p in order["point"].tolist()]

    # 카테고리별 서브플롯 2x2 구성
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=CATEGORIES,
        horizontal_spacing=0.08,
        vertical_spacing=0.15,
    )
    cat_to_pos = {"Eliciting": (1, 1), "Responding": (1, 2), "Facilitating": (2, 1), "Extending": (2, 2)}

    first_legend = True
    for cat in CATEGORIES:
        r, c = cat_to_pos[cat]
        sub = (
            df_user[df_user["category"] == cat]
            .sort_values(["point"])  # 포인트 순서로 정렬
        )
        by_point = {int(row.point): (int(row.low), int(row.high)) for _, row in sub.iterrows()}
        y_low = []
        y_high = []
        for p in order["point"].tolist():
            low, high = by_point.get(int(p), (0, 0))
            y_low.append(low)
            y_high.append(high)

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_low,
                mode="lines+markers",
                name="Low",
                line=dict(color="#1f77b4"),
                marker=dict(size=6),
                showlegend=first_legend,
            ),
            row=r,
            col=c,
        )
        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_high,
                mode="lines+markers",
                name="High",
                line=dict(color="#ff7f0e"),
                marker=dict(size=6),
                showlegend=first_legend,
            ),
            row=r,
            col=c,
        )
        first_legend = False

    fig.update_layout(
        title_text=f"사용자: {user} — 범주별 Low/High 변화 (포인트 기준)",
        height=650,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    # 모든 서브플롯 X축을 카테고리 축으로 고정
    for (r, c) in [(1,1),(1,2),(2,1),(2,2)]:
        fig.update_xaxes(
            title_text="데이터 포인트(파일 순서)",
            type="category",
            categoryorder="array",
            categoryarray=x_vals,
            tickmode="array",
            tickvals=x_vals,
            ticktext=x_vals,
            row=r,
            col=c,
        )
    fig.update_yaxes(title_text="개수")
    return fig


st.title("TMSSR 사용자별 데이터 포인트 대시보드")
st.caption("data_new 폴더의 파일명을 기준으로 사용자/파일 단위로 TMSSR/Potential을 집계하며, X축은 시간 대신 데이터 포인트(파일 순서)를 사용합니다.")

default_dir = os.path.join(os.getcwd(), "data_new")
data_dir = st.text_input("데이터 폴더 경로", value=default_dir)

if not os.path.isdir(data_dir):
    st.error("유효한 폴더 경로가 아닙니다. 'data_new' 폴더를 확인하세요.")
    st.stop()

df = aggregate_folder(data_dir)
if df.empty:
    st.warning("CSV에서 TMSSR/Potential을 찾지 못했거나 집계할 데이터가 없습니다.")
    st.stop()

users = sorted(df["user"].unique().tolist())
# 사용자별 데이터 포인트(파일) 개수 계산
user_point_counts = (
    df[["user", "point"]].drop_duplicates().groupby("user").size().to_dict()
)
user_labels = [f"{u} ({user_point_counts.get(u, 0)})" for u in users]
label_to_user = {label: u for label, u in zip(user_labels, users)}
selected_label = st.selectbox("사용자 선택", options=user_labels, index=0)
sel_users = [label_to_user[selected_label]]
sel_categories = st.multiselect("카테고리 선택", CATEGORIES, default=CATEGORIES)

df_view = df[df["user"].isin(sel_users) & df["category"].isin(sel_categories)]

st.subheader("시각화")
for u in sel_users:
    df_u = df_view[df_view["user"] == u]
    if df_u.empty:
        continue
    # 1) 포인트별 High/Low 총합 꺾은선
    fig_total = plot_user_point_totals(df_u, user=u)
    st.plotly_chart(fig_total, use_container_width=True)

    # 2) 범주별 High/Low 꺾은선
    fig = plot_user_points(df_u, user=u)
    st.plotly_chart(fig, use_container_width=True)

    # 포인트-파일 매핑 표 제공 (사용자가 어떤 파일이 어떤 포인트인지 이해하도록)
    mapping = (
        df_u[["point", "timestamp", "file"]]
        .drop_duplicates()
        .sort_values(["point"])
    )
    mapping["timestamp"] = mapping["timestamp"].astype("datetime64[ns]")
    st.dataframe(mapping.rename(columns={"point": "데이터 포인트", "timestamp": "시간", "file": "파일"}), use_container_width=True)

with st.expander("집계 데이터 테이블 보기"):
    st.dataframe(df_view.sort_values(["user", "point", "category"]))

st.caption("Low/High 개수는 각 파일 내 TMSSR 카테고리 행의 Potential 값을 집계한 결과입니다.")

