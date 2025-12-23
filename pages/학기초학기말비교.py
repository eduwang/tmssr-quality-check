import os
import re
from datetime import datetime
from typing import Tuple, Dict, List
from collections import defaultdict

import pandas as pd
import streamlit as st


st.set_page_config(page_title="학기 초/말 비교", layout="wide")


def parse_user_and_timestamp_from_filename(path: str) -> Tuple[str, datetime]:
    """
    파일명 형식: "사용자명_YYYY. M. D. 오전/오후 H-MM-SS.csv"
    예) "문지원_2025. 12. 4. 오전 9-48-33.csv"
    반환: (사용자명, datetime)
    """
    base = os.path.basename(path)
    if not base.lower().endswith(".csv"):
        raise ValueError(f"Not a CSV file: {base}")
    name_part, rest = base.rsplit(".csv", 1)[0].split("_", 1)

    # 2025. 12. 4. 오전 11-50-53
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
    return pd.read_csv(path)


def count_user_utterances(data_dir: str, skip_rows: int = 0) -> Dict[str, int]:
    """
    각 폴더에서 CSV 파일들을 읽고, 사용자(첫 컬럼)가 말한 행의 개수를 세기
    skip_rows: 각 파일에서 제외할 초반 행의 개수
    """
    user_counts = defaultdict(int)
    
    csv_files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.lower().endswith(".csv")
    ]
    
    for fpath in csv_files:
        try:
            user, ts = parse_user_and_timestamp_from_filename(fpath)
        except Exception:
            continue
        
        df = read_csv_with_encoding(fpath)
        
        # skip_rows만큼 초반 행 제외
        if skip_rows > 0:
            df = df.iloc[skip_rows:]
        
        # 첫 번째 컬럼이 사용자명 (사용자, 날짜/시간, ...)
        if len(df.columns) > 0:
            user_col = df.columns[0]
            # 해당 사용자가 입력한 행의 개수
            user_count = (df[user_col].astype(str).str.strip() == user).sum()
            user_counts[user] += user_count
    
    return dict(user_counts)


def get_file_count_by_user(data_dir: str) -> Dict[str, int]:
    """각 사용자별 파일 개수"""
    user_files = defaultdict(set)
    
    csv_files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.lower().endswith(".csv")
    ]
    
    for fpath in csv_files:
        try:
            user, ts = parse_user_and_timestamp_from_filename(fpath)
            user_files[user].add(os.path.basename(fpath))
        except Exception:
            continue
    
    return {u: len(files) for u, files in user_files.items()}


def count_total_files(data_dir: str) -> int:
    """폴더 내 전체 CSV 파일 개수"""
    return len([f for f in os.listdir(data_dir) if f.lower().endswith(".csv")])


st.title("📊 학기 초/말 비교 분석")
st.caption("9월 11일(학기 초) vs 12월 4일(학기 말) 데이터 비교")

early_dir = "data_comparison/학기 초(9월 11일)"
late_dir = "data_comparison/학기 말(12월 4일)"

# 데이터 집계
# 학기 초: 처음 8행 제외, 학기 말: 처음 6행 제외
early_utterances = count_user_utterances(early_dir, skip_rows=8)
late_utterances = count_user_utterances(late_dir, skip_rows=6)
early_files = get_file_count_by_user(early_dir)
late_files = get_file_count_by_user(late_dir)
early_total_files = count_total_files(early_dir)
late_total_files = count_total_files(late_dir)

all_users = sorted(set(list(early_utterances.keys()) + list(late_utterances.keys())))

# 레이아웃: 좌우 2개 컬럼
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 학기 초 (9월 11일)")
    st.metric("전체 파일 개수", early_total_files)
    
    st.write("**사용자별 발화 수**")
    early_df = pd.DataFrame({
        "사용자": all_users,
        "발화 수": [early_utterances.get(u, 0) for u in all_users],
        "파일 개수": [early_files.get(u, 0) for u in all_users],
    })
    early_df = early_df.sort_values("발화 수", ascending=False)
    st.dataframe(early_df, use_container_width=True, hide_index=True)
    
    early_total = sum(early_utterances.values())
    st.metric("전체 발화 수", early_total)

with col2:
    st.subheader("📅 학기 말 (12월 4일)")
    st.metric("전체 파일 개수", late_total_files)
    
    st.write("**사용자별 발화 수**")
    late_df = pd.DataFrame({
        "사용자": all_users,
        "발화 수": [late_utterances.get(u, 0) for u in all_users],
        "파일 개수": [late_files.get(u, 0) for u in all_users],
    })
    late_df = late_df.sort_values("발화 수", ascending=False)
    st.dataframe(late_df, use_container_width=True, hide_index=True)
    
    late_total = sum(late_utterances.values())
    st.metric("전체 발화 수", late_total)

# 비교 요약
st.divider()
st.subheader("📈 비교 요약")

comparison_col1, comparison_col2, comparison_col3 = st.columns(3)

with comparison_col1:
    file_change = late_total_files - early_total_files
    st.metric("파일 개수 변화", f"{file_change:+d}", 
              f"{early_total_files} → {late_total_files}")

with comparison_col2:
    utterance_change = late_total - early_total
    st.metric("발화 수 변화", f"{utterance_change:+d}", 
              f"{early_total} → {late_total}")

with comparison_col3:
    if early_total_files > 0:
        early_avg = early_total / early_total_files
        late_avg = late_total / late_total_files if late_total_files > 0 else 0
        st.metric("파일당 평균 발화 수", f"{late_avg:.1f}", 
                  f"{early_avg:.1f} → {late_avg:.1f}")

# 사용자별 상세 비교
st.divider()
st.subheader("👥 사용자별 상세 비교")

comparison_table = []
for u in all_users:
    e_utt = early_utterances.get(u, 0)
    l_utt = late_utterances.get(u, 0)
    e_file = early_files.get(u, 0)
    l_file = late_files.get(u, 0)
    
    comparison_table.append({
        "사용자": u,
        "학기초_발화": e_utt,
        "학기말_발화": l_utt,
        "발화증감": l_utt - e_utt,
        "학기초_파일": e_file,
        "학기말_파일": l_file,
        "파일증감": l_file - e_file,
    })

comparison_df = pd.DataFrame(comparison_table)
st.dataframe(comparison_df, use_container_width=True, hide_index=True)
