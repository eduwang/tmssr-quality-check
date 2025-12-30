import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

st.set_page_config(page_title="학기초 데이터 분석", layout="wide")
st.title("📊 학기초 데이터 분석")

# 다크/라이트 모드 감지 및 색상 설정
def get_theme_colors():
    """브라우저 테마에 적응하는 색상 설정"""
    # Streamlit 테마 베이스 감지
    try:
        theme_base = st.get_option("theme.base")
        is_dark = theme_base == "dark"
    except:
        is_dark = False
    
    if is_dark:
        # 다크 모드
        plot_bgcolor = 'rgba(50, 50, 50, 0.3)'
        paper_bgcolor = 'rgba(14, 17, 23, 0.95)'
        text_color = '#ffffff'
        grid_color = '#444444'
    else:
        # 라이트 모드
        plot_bgcolor = 'rgba(240, 240, 240, 0.5)'
        paper_bgcolor = 'rgba(255, 255, 255, 1)'
        text_color = '#000000'
        grid_color = '#cccccc'
    
    return {
        'plot_bgcolor': plot_bgcolor,
        'paper_bgcolor': paper_bgcolor,
        'text_color': text_color,
        'grid_color': grid_color,
        'is_dark': is_dark
    }

# 데이터 로드
data_path = Path("data_initial_final/0_학기 초 - 약수.csv")

if data_path.exists():
    df = pd.read_csv(data_path)
    
    # TMSSR과 Potential에서 '-'를 NaN으로 처리
    df['TMSSR'] = df['TMSSR'].replace('-', np.nan)
    df['Potential'] = df['Potential'].replace('-', np.nan)
    
    # 결측치 제거
    df_tmssr = df[df['TMSSR'].notna()].copy()
    df_potential = df[df['Potential'].notna()].copy()
    
    theme = get_theme_colors()
    
    # ========== 1. TMSSR 도수분포 ==========
    st.header("1️⃣ TMSSR 도수분포")
    
    if len(df_tmssr) > 0:
        tmssr_order = ['Eliciting', 'Responding', 'Facilitating', 'Extending']
        tmssr_order = [x for x in tmssr_order if x in df_tmssr['TMSSR'].unique()]
        
        tmssr_counts = df_tmssr['TMSSR'].value_counts().reindex(tmssr_order)
        tmssr_total = len(df_tmssr)
        
        # 통계 표시
        col_stats = st.columns(len(tmssr_order))
        for idx, category in enumerate(tmssr_order):
            count = tmssr_counts.get(category, 0)
            percentage = (count / tmssr_total * 100)
            with col_stats[idx]:
                st.metric(category, f"{int(count)}", f"{percentage:.1f}%")
        
        # 막대 그래프
        fig_tmssr = go.Figure()
        colors_tmssr = {
            'Eliciting': '#3498db',
            'Responding': '#f39c12',
            'Facilitating': '#9b59b6',
            'Extending': '#1abc9c'
        }
        
        fig_tmssr.add_trace(go.Bar(
            x=tmssr_order,
            y=tmssr_counts.values,
            text=[f'{int(count)}<br>({count/tmssr_total*100:.1f}%)' 
                  for count in tmssr_counts.values],
            textposition='outside',
            textfont=dict(size=11, family='나눔고딕'),
            marker=dict(
                color=[colors_tmssr.get(cat, '#95a5a6') for cat in tmssr_order],
                line=dict(color='black', width=2)
            ),
            hovertemplate='<b>%{x}</b><br>개수: %{y}<extra></extra>'
        ))
        
        fig_tmssr.update_layout(
            title=dict(
                text='TMSSR 도수분포',
                font=dict(size=16, family='나눔고딕', color=theme['text_color'])
            ),
            xaxis=dict(
                title=dict(text='TMSSR 카테고리', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
            ),
            yaxis=dict(
                title=dict(text='도수', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
            ),
            plot_bgcolor=theme['plot_bgcolor'],
            paper_bgcolor=theme['paper_bgcolor'],
            font=dict(color=theme['text_color']),
            height=400,
            margin=dict(l=60, r=60, t=80, b=60)
        )
        fig_tmssr.update_xaxes(showgrid=False)
        fig_tmssr.update_yaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
        
        st.plotly_chart(fig_tmssr, use_container_width=True)
    
    st.divider()
    
    # ========== 2. Potential 도수분포 ==========
    st.header("2️⃣ Potential 도수분포")
    
    if len(df_potential) > 0:
        potential_order = ['High', 'Low']
        potential_order = [x for x in potential_order if x in df_potential['Potential'].unique()]
        
        potential_counts = df_potential['Potential'].value_counts().reindex(potential_order)
        potential_total = len(df_potential)
        
        # 통계 표시
        col_stats = st.columns(len(potential_order))
        for idx, category in enumerate(potential_order):
            count = potential_counts.get(category, 0)
            percentage = (count / potential_total * 100)
            with col_stats[idx]:
                st.metric(category, f"{int(count)}", f"{percentage:.1f}%")
        
        # 막대 그래프
        fig_potential = go.Figure()
        colors_potential = {
            'High': '#2ecc71',
            'Low': '#e74c3c'
        }
        
        fig_potential.add_trace(go.Bar(
            x=potential_order,
            y=potential_counts.values,
            text=[f'{int(count)}<br>({count/potential_total*100:.1f}%)' 
                  for count in potential_counts.values],
            textposition='outside',
            textfont=dict(size=11, family='나눔고딕'),
            marker=dict(
                color=[colors_potential.get(cat, '#95a5a6') for cat in potential_order],
                line=dict(color='black', width=2)
            ),
            hovertemplate='<b>%{x}</b><br>개수: %{y}<extra></extra>'
        ))
        
        fig_potential.update_layout(
            title=dict(
                text='Potential 도수분포',
                font=dict(size=16, family='나눔고딕', color=theme['text_color'])
            ),
            xaxis=dict(
                title=dict(text='Potential 카테고리', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
            ),
            yaxis=dict(
                title=dict(text='도수', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
            ),
            plot_bgcolor=theme['plot_bgcolor'],
            paper_bgcolor=theme['paper_bgcolor'],
            font=dict(color=theme['text_color']),
            height=400,
            margin=dict(l=60, r=60, t=80, b=60)
        )
        fig_potential.update_xaxes(showgrid=False)
        fig_potential.update_yaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
        
        st.plotly_chart(fig_potential, use_container_width=True)
    
    st.divider()
    
    # ========== 3. 누적 비율 분포 ==========
    st.header("3️⃣ 누적 비율 분포 (Cumulative %)")
    
    col3_1, col3_2 = st.columns(2)
    
    # TMSSR 누적 비율
    with col3_1:
        st.subheader("TMSSR 누적 비율")
        
        if len(df_tmssr) > 0:
            tmssr_order = ['Eliciting', 'Responding', 'Facilitating', 'Extending']
            tmssr_order = [x for x in tmssr_order if x in df_tmssr['TMSSR'].unique()]
            
            tmssr_counts = df_tmssr['TMSSR'].value_counts().reindex(tmssr_order)
            tmssr_total = len(df_tmssr)
            
            # 각 구간의 비율
            individual_percentage = (tmssr_counts / tmssr_total * 100)
            
            # 누적 비율 계산
            cumsum = tmssr_counts.cumsum()
            cum_percentage = (cumsum / tmssr_total * 100)
            
            # 누적 막대 그래프
            fig_tmssr_cum = go.Figure()
            
            colors_tmssr = {
                'Eliciting': '#3498db',
                'Responding': '#f39c12',
                'Facilitating': '#9b59b6',
                'Extending': '#1abc9c'
            }
            
            # 각 카테고리를 스택으로 추가 (하나의 막대에)
            for category in tmssr_order:
                pct = individual_percentage.get(category, 0)
                cum_pct = cum_percentage.get(category, 0)
                
                fig_tmssr_cum.add_trace(go.Bar(
                    x=['TMSSR'],
                    y=[pct],
                    name=category,
                    marker=dict(color=colors_tmssr.get(category, '#95a5a6'), line=dict(color='white', width=2)),
                    text=f'{pct:.1f}%',
                    textposition='inside',
                    textfont=dict(size=10, family='나눔고딕', color='white', weight='bold'),
                    hovertemplate=f'<b>{category}</b><br>비율: {pct:.1f}%<br>누적: {cum_pct:.1f}%<extra></extra>'
                ))
            
            fig_tmssr_cum.update_layout(
                barmode='stack',
                title=dict(
                    text='TMSSR 누적 비율',
                    font=dict(size=16, family='나눔고딕', color=theme['text_color'])
                ),
                xaxis=dict(
                    tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
                ),
                yaxis=dict(
                    title=dict(text='비율 (%)', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                    tickfont=dict(size=11, family='나눔고딕', color=theme['text_color']),
                    range=[0, 100]
                ),
                plot_bgcolor=theme['plot_bgcolor'],
                paper_bgcolor=theme['paper_bgcolor'],
                font=dict(color=theme['text_color']),
                height=400,
                margin=dict(l=60, r=60, t=80, b=60),
                legend=dict(font=dict(size=11, family='나눔고딕')),
                showlegend=True
            )
            
            fig_tmssr_cum.update_xaxes(showgrid=False)
            fig_tmssr_cum.update_yaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
            
            st.plotly_chart(fig_tmssr_cum, use_container_width=True)
    
    # Potential 누적 비율
    with col3_2:
        st.subheader("Potential 누적 비율")
        
        if len(df_potential) > 0:
            potential_order = ['High', 'Low']
            potential_order = [x for x in potential_order if x in df_potential['Potential'].unique()]
            
            potential_counts = df_potential['Potential'].value_counts().reindex(potential_order)
            potential_total = len(df_potential)
            
            # 각 구간의 비율
            individual_percentage = (potential_counts / potential_total * 100)
            
            # 누적 비율 계산
            cumsum = potential_counts.cumsum()
            cum_percentage = (cumsum / potential_total * 100)
            
            # 누적 막대 그래프
            fig_potential_cum = go.Figure()
            
            colors_potential = {
                'High': '#2ecc71',
                'Low': '#e74c3c'
            }
            
            # 각 카테고리를 스택으로 추가 (하나의 막대에)
            for category in potential_order:
                pct = individual_percentage.get(category, 0)
                cum_pct = cum_percentage.get(category, 0)
                
                fig_potential_cum.add_trace(go.Bar(
                    x=['Potential'],
                    y=[pct],
                    name=category,
                    marker=dict(color=colors_potential.get(category, '#95a5a6'), line=dict(color='white', width=2)),
                    text=f'{pct:.1f}%',
                    textposition='inside',
                    textfont=dict(size=10, family='나눔고딕', color='white', weight='bold'),
                    hovertemplate=f'<b>{category}</b><br>비율: {pct:.1f}%<br>누적: {cum_pct:.1f}%<extra></extra>'
                ))
            
            fig_potential_cum.update_layout(
                barmode='stack',
                title=dict(
                    text='Potential 누적 비율',
                    font=dict(size=16, family='나눔고딕', color=theme['text_color'])
                ),
                xaxis=dict(
                    tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
                ),
                yaxis=dict(
                    title=dict(text='비율 (%)', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                    tickfont=dict(size=11, family='나눔고딕', color=theme['text_color']),
                    range=[0, 100]
                ),
                plot_bgcolor=theme['plot_bgcolor'],
                paper_bgcolor=theme['paper_bgcolor'],
                font=dict(color=theme['text_color']),
                height=400,
                margin=dict(l=60, r=60, t=80, b=60),
                legend=dict(font=dict(size=11, family='나눔고딕')),
                showlegend=True
            )
            
            fig_potential_cum.update_xaxes(showgrid=False)
            fig_potential_cum.update_yaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
            
            st.plotly_chart(fig_potential_cum, use_container_width=True)
    
    st.divider()
    
    # ========== 4. 상세 분석 (기존 그래프들) ==========
    st.header("4️⃣ 상세 분석")
    
    st.subheader("4-1. TMSSR 범주별 Potential 분포")
    
    # 두 개의 컬럼으로 시각화
    col1, col2 = st.columns(2)
    
    # ===== TMSSR별 Potential 분포 (세부) =====
    with col1:
        st.subheader("TMSSR 범주별 High/Low 비교")
        
        if len(df_tmssr) > 0:
            # TMSSR별 Potential 분포 분석
            tmssr_potential_crosstab = pd.crosstab(df_tmssr['TMSSR'], df_tmssr['Potential'])
            tmssr_counts = df_tmssr['TMSSR'].value_counts()
            tmssr_total = len(df_tmssr)
            
            # TMSSR 순서 정의
            tmssr_order = ['Eliciting', 'Responding', 'Facilitating', 'Extending']
            tmssr_order = [x for x in tmssr_order if x in df_tmssr['TMSSR'].unique()]
            
            # 통계 정보 표시
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                st.metric("총 데이터", tmssr_total)
            with col1_2:
                st.metric("카테고리 수", len(tmssr_order))
            
            # 상세 통계 표시
            st.write("#### 상세 통계")
            tmssr_stats_list = []
            for category in tmssr_order:
                count = tmssr_counts.get(category, 0)
                percentage = (count / tmssr_total * 100)
                tmssr_stats_list.append({
                    '카테고리': category,
                    '개수': int(count),
                    '비율(%)': f'{percentage:.1f}%'
                })
            tmssr_stats_df = pd.DataFrame(tmssr_stats_list)
            st.dataframe(tmssr_stats_df, use_container_width=True, hide_index=True)
            
            # 누적 막대 그래프 (Potential별)
            if len(tmssr_potential_crosstab) > 0:
                # 정렬
                tmssr_potential_crosstab = tmssr_potential_crosstab.reindex(tmssr_order)
                potential_order = ['High', 'Low']
                potential_order = [x for x in potential_order if x in tmssr_potential_crosstab.columns]
                tmssr_potential_crosstab = tmssr_potential_crosstab[potential_order]
                
                # 백분율 계산
                total_per_category = tmssr_potential_crosstab.sum(axis=1)
                tmssr_potential_percentage = tmssr_potential_crosstab.div(total_per_category, axis=0) * 100
                
                # Plotly 그래프 생성
                fig = go.Figure()
                
                colors = {'High': '#2ecc71', 'Low': '#e74c3c'}
                
                for potential in potential_order:
                    fig.add_trace(go.Bar(
                        x=tmssr_order,
                        y=tmssr_potential_percentage[potential],
                        name=potential,
                        text=[f'{pct:.1f}%<br>({int(count)})' 
                              for pct, count in zip(tmssr_potential_percentage[potential], tmssr_potential_crosstab[potential])],
                        textposition='inside',
                        textfont=dict(size=10, color='white', family='나눔고딕'),
                        marker=dict(color=colors.get(potential, '#95a5a6'), line=dict(color='black', width=1.5)),
                        hovertemplate='<b>%{x}</b><br>' + potential + ': %{y:.1f}%<extra></extra>'
                    ))
                
                fig.update_layout(
                    barmode='stack',
                    title=dict(
                        text='TMSSR 범주별 Potential 비율',
                        font=dict(size=16, family='나눔고딕', color=theme['text_color'])
                    ),
                    xaxis=dict(
                        title=dict(text='TMSSR 카테고리', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                        tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
                    ),
                    yaxis=dict(
                        title=dict(text='비율 (%)', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                        tickfont=dict(size=11, family='나눔고딕', color=theme['text_color']),
                        range=[0, 100]
                    ),
                    legend=dict(
                        title=dict(text='Potential', font=dict(size=12, family='나눔고딕')),
                        font=dict(size=11, family='나눔고딕'),
                        x=0.85,
                        y=0.95
                    ),
                    hovermode='x unified',
                    plot_bgcolor=theme['plot_bgcolor'],
                    paper_bgcolor=theme['paper_bgcolor'],
                    font=dict(color=theme['text_color']),
                    height=500,
                    margin=dict(l=60, r=60, t=80, b=60)
                )
                
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("TMSSR 데이터가 없습니다.")
    
    # ===== Potential 분포 =====
    with col2:
        st.subheader("Potential 분포")
        
        if len(df_potential) > 0:
            # Potential별 TMSSR 분포 분석
            potential_tmssr_crosstab = pd.crosstab(df_potential['Potential'], df_potential['TMSSR'])
            potential_counts = df_potential['Potential'].value_counts()
            potential_total = len(df_potential)
            
            # Potential 순서 정의 (아래부터 위로: Low -> High)
            potential_order = ['Low', 'High']
            potential_order = [x for x in potential_order if x in df_potential['Potential'].unique()]
            
            # 통계 정보 표시
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("총 데이터", potential_total)
            with col2_2:
                st.metric("카테고리 수", len(potential_order))
            
            # 상세 통계 표시
            st.write("#### 상세 통계")
            potential_stats_list = []
            for category in potential_order:
                count = potential_counts.get(category, 0)
                percentage = (count / potential_total * 100)
                potential_stats_list.append({
                    '카테고리': category,
                    '개수': int(count),
                    '비율(%)': f'{percentage:.1f}%'
                })
            potential_stats_df = pd.DataFrame(potential_stats_list)
            st.dataframe(potential_stats_df, use_container_width=True, hide_index=True)
            
            # 누적 막대 그래프 (TMSSR별)
            if len(potential_tmssr_crosstab) > 0:
                # 정렬
                potential_tmssr_crosstab = potential_tmssr_crosstab.reindex(potential_order)
                tmssr_order_for_potential = ['Eliciting', 'Responding', 'Facilitating', 'Extending']
                tmssr_order_for_potential = [x for x in tmssr_order_for_potential if x in potential_tmssr_crosstab.columns]
                potential_tmssr_crosstab = potential_tmssr_crosstab[tmssr_order_for_potential]
                
                # 백분율 계산
                total_per_category = potential_tmssr_crosstab.sum(axis=1)
                potential_tmssr_percentage = potential_tmssr_crosstab.div(total_per_category, axis=0) * 100
                
                # Plotly 그래프 생성
                fig = go.Figure()
                
                colors = {
                    'Eliciting': '#3498db',
                    'Responding': '#f39c12',
                    'Facilitating': '#9b59b6',
                    'Extending': '#1abc9c'
                }
                
                for tmssr in tmssr_order_for_potential:
                    fig.add_trace(go.Bar(
                        x=potential_order,
                        y=potential_tmssr_percentage[tmssr],
                        name=tmssr,
                        text=[f'{pct:.1f}%<br>({int(count)})' 
                              for pct, count in zip(potential_tmssr_percentage[tmssr], potential_tmssr_crosstab[tmssr])],
                        textposition='inside',
                        textfont=dict(size=10, color='white', family='나눔고딕'),
                        marker=dict(color=colors.get(tmssr, '#95a5a6'), line=dict(color='black', width=1.5)),
                        hovertemplate='<b>%{x}</b><br>' + tmssr + ': %{y:.1f}%<extra></extra>'
                    ))
                
                fig.update_layout(
                    barmode='stack',
                    title=dict(
                        text='Potential별 TMSSR 분포',
                        font=dict(size=16, family='나눔고딕', color=theme['text_color'])
                    ),
                    xaxis=dict(
                        title=dict(text='Potential 카테고리', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                        tickfont=dict(size=11, family='나눔고딕', color=theme['text_color'])
                    ),
                    yaxis=dict(
                        title=dict(text='비율 (%)', font=dict(size=12, family='나눔고딕', color=theme['text_color'])),
                        tickfont=dict(size=11, family='나눔고딕', color=theme['text_color']),
                        range=[0, 100]
                    ),
                    legend=dict(
                        title=dict(text='TMSSR', font=dict(size=12, family='나눔고딕')),
                        font=dict(size=11, family='나눔고딕'),
                        x=0.85,
                        y=0.95
                    ),
                    hovermode='x unified',
                    plot_bgcolor=theme['plot_bgcolor'],
                    paper_bgcolor=theme['paper_bgcolor'],
                    font=dict(color=theme['text_color']),
                    height=500,
                    margin=dict(l=60, r=60, t=80, b=60)
                )
                
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=theme['grid_color'])
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Potential 데이터가 없습니다.")
    
    # # 추가 통계 정보
    # st.divider()
    # st.subheader("📈 종합 분석")
    
    # col_stat1, col_stat2 = st.columns(2)
    
    # with col_stat1:
    #     st.write("#### TMSSR 분석")
    #     st.write(f"- 총 유효 데이터: {len(df_tmssr)}개")
    #     st.write(f"- 결측치: {len(df) - len(df_tmssr)}개")
    
    # with col_stat2:
    #     st.write("#### Potential 분석")
    #     st.write(f"- 총 유효 데이터: {len(df_potential)}개")
    #     st.write(f"- 결측치: {len(df) - len(df_potential)}개")

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
    st.info(f"경로: {data_path}")
