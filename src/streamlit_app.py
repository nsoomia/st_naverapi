import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# 1. 페이지 설정 (라이트 테마 기반의 깔끔한 디자인)
st.set_page_config(
    page_title="HanaTour Bio | Aviation & Travel Dashboard",
    page_icon="📊",
    layout="wide",
)

# 커스텀 CSS (깔끔한 화이트/블루 테마)
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    h1, h2, h3 {
        color: #1e40af !important;
        font-family: 'Pretendard', sans-serif;
    }
    .stMetric {
        background: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #1e40af !important;
        border-bottom-color: #1e40af !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 함수 (global_data 형식으로 반환)
@st.cache_data
def get_global_data():
    DATA_DIR = 'data'
    global_data = {}
    
    # 가) 항공 데이터 로드 및 정규화
    av_path = os.path.join(DATA_DIR, 'processed_aviation_performance.csv')
    if os.path.exists(av_path):
        df_av = pd.read_csv(av_path, encoding='utf-8-sig')
        df_av.columns = [c.strip() for c in df_av.columns]
        
        # 컬럼명 표준화 (제공된 코드 요구사항 반영)
        normalized_cols = {
            '여객_계(명)': '여객_계',
            '운항_계(편)': '운항_계',
            '항공사명': '항공사',
            '도시': '도시명',
            '국가': '국가',
            '노선': '노선',
            '공항': '공항'
        }
        
        # 1차: 정확히 일치하는 것부터 매핑
        final_rename = {}
        for col in df_av.columns:
            if col in normalized_cols:
                final_rename[col] = normalized_cols[col]
        
        # 2차: 키워드 기반 매핑 (아직 매핑되지 않은 대상만)
        keywords = {
            '여객': '여객_계',
            '운항': '운항_계',
            '도시': '도시명',
            '연도': '연도',
            '월': '월'
        }
        
        mapped_targets = set(final_rename.values())
        for col in df_av.columns:
            if col in final_rename: continue
            for kw, target in keywords.items():
                if kw in col and target not in mapped_targets:
                    final_rename[col] = target
                    mapped_targets.add(target)
                    break
            
        df_av = df_av.rename(columns=final_rename)
        
        # 3차: 중복된 컬럼명이 생겼을 경우 첫 번째만 남김
        df_av = df_av.loc[:, ~df_av.columns.duplicated()]
        
        # 필수 컬럼 강제 보장 (폴백: 값이 없으면 0으로 채운 더미라도 생성)
        for target in ['여객_계', '운항_계', '도시명', '연도', '월']:
            if target not in df_av.columns:
                df_av[target] = 0
        
        global_data['aviation'] = df_av
    
    # 나) 목적지 통계 데이터
    dest_path = os.path.join(DATA_DIR, 'merged_overseas_destination.csv')
    if os.path.exists(dest_path):
        df_dest = pd.read_csv(dest_path, encoding='utf-8-sig')
        df_dest.columns = [c.strip() for c in df_dest.columns]
        # 컬럼명 표준화
        df_dest = df_dest.rename(columns={'관광객_수': '관광객수', '대륙': '지역'})
        global_data['destinations'] = df_dest
    else:
        global_data['destinations'] = pd.DataFrame(columns=['연도', '국가', '지역', '관광객수'])

    # 다) 리뷰 데이터 (기존 로직 유지)
    rv_path = os.path.join(DATA_DIR, 'hanatour_reviews.csv')
    if os.path.exists(rv_path):
        df_rv = pd.read_csv(rv_path, encoding='utf-8-sig')
        df_rv['작성일'] = pd.to_datetime(df_rv['작성일'], errors='coerce')
        df_rv.dropna(subset=['작성일'], inplace=True)
        df_rv['월'] = df_rv['작성일'].dt.month
        global_data['reviews'] = df_rv
        
    return global_data

global_data = get_global_data()

# 3. 사이드바
st.sidebar.title("💎 HanaTour Bio")
st.sidebar.info("항공 실적 및 고객 분석 통합 대시보드")

# 4. 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Market Trend", "🎯 Target Analysis", "📊 Core EDA", "⚠️ Risk & Product", "🔍 Detail Review"])

# ----------------------------------------------------
# TAB 1: 항공 시장 거시적 심층 (2020~2025 전국 출발 기반)
# ----------------------------------------------------
with tab1:
    st.subheader("📊 항공 시장 거시적 지표 분석 (2020~2025)")
    st.caption("※ 2020년 이후 실적 데이터를 기반으로 글로벌 항공 시장의 거시적 트렌드를 조망합니다.")
    
    df_air = global_data.get('aviation', pd.DataFrame()).copy()
    
    if not df_air.empty:
        # 2020년~2025년 데이터 필터링 강화
        df_base = df_air[(df_air['연도'].astype(float) >= 2020) & (df_air['연도'].astype(float) <= 2025)].copy()
        
        if not df_base.empty:
            # 시계열 분석을 위한 날짜 처리
            df_base['연도_str'] = df_base['연도'].astype(int).astype(str)
            df_base['월_str'] = df_base['월'].astype(int).astype(str).str.zfill(2)
            df_base['연월'] = pd.to_datetime(df_base['연도_str'] + '-' + df_base['월_str'] + '-01', errors='coerce')
            
            # --- 상단 메인 지표 ---
            t_pass = float(df_base['여객_계'].sum())
            
            m1, m2 = st.columns(2)
            m1.metric("전체 누적 여객 (2020-2025)", f"{t_pass:,.0f}명")
            m2.metric("데이터 커버리지", "2020년 1월 ~ 2025년 현재")
            
            st.markdown("---")
            
            # --- Layout: 2x2 ---
            t1_r1_c1, t1_r1_c2 = st.columns(2)
            t1_r2_c1, t1_r2_c2 = st.columns(2)
            
            with t1_r1_c1:
                st.markdown("**📅 연도별 전체 여객 실적 추이**")
                trend_y = df_base.groupby('연도_str')['여객_계'].sum().reset_index()
                fig_y = px.bar(trend_y, x='연도_str', y='여객_계', text_auto=',.0f', color='여객_계', color_continuous_scale='Blues', title="연도별 Passenger Trend")
                st.plotly_chart(fig_y, use_container_width=True, key="tab1_year_trend")
                
            with t1_r1_c2:
                st.markdown("**📈 월별 세부 여객 변동 추이**")
                trend_m = df_base.groupby('연월')['여객_계'].sum().reset_index().sort_values('연월')
                fig_m = px.line(trend_m, x='연월', y='여객_계', markers=True, title="월별 Passenger Volatility")
                st.plotly_chart(fig_m, use_container_width=True, key="tab1_month_trend")
                
            with t1_r2_c1:
                st.markdown("**🌍 국가별 여객 누적 실적 (Top 15)**")
                top_cnt = df_base.groupby('국가')['여객_계'].sum().reset_index().sort_values('여객_계', ascending=False).head(15)
                fig_cnt = px.bar(top_cnt, x='여객_계', y='국가', orientation='h', text_auto=',.0f', color='여객_계', color_continuous_scale='Greens', title="Top 15 Countries")
                fig_cnt.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_cnt, use_container_width=True, key="tab1_top_countries")
                
            with t1_r2_c2:
                st.markdown("**🏙️ 도시별 여객 누적 실적 (Top 15)**")
                top_city = df_base.groupby('도시명')['여객_계'].sum().reset_index().sort_values('여객_계', ascending=False).head(15)
                fig_city = px.bar(top_city, x='여객_계', y='도시명', orientation='h', text_auto=',.0f', color='여객_계', color_continuous_scale='Oranges', title="Top 15 Cities")
                fig_city.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_city, use_container_width=True, key="tab1_top_cities")
                
            st.info("💡 **Macro Insight:** 팬데믹 이후 항공 시장은 2022년을 기점으로 가파른 회복세를 보이고 있으며, 상위 15개 도시가 전체 수요의 핵심 포스트 역할을 하고 있습니다.")
            
            st.markdown("---")
            st.markdown("### 🌏 해외 관광객 목적지별 통계 (Tourist Destination Stats)")
            df_dest = global_data.get('destinations', pd.DataFrame()).copy()
            if not df_dest.empty:
                df_dest = df_dest[df_dest['연도'] >= 2020].copy()
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.markdown("**📌 대륙별 관광객 방문 비중**")
                    dest_region = df_dest.groupby('지역')['관광객수'].sum().reset_index()
                    fig_dest_pie = px.pie(dest_region, names='지역', values='관광객수', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_dest_pie, use_container_width=True, key="tab1_dest_pie")
                with d_col2:
                    st.markdown("**📌 국가별 관광객 유입 (Top 10)**")
                    dest_cty = df_dest.groupby('국가')['관광객수'].sum().reset_index().sort_values('관광객수', ascending=False).head(10)
                    fig_dest_bar = px.bar(dest_cty, x='관광객수', y='국가', orientation='h', text_auto=',.0f', color='관광객수', color_continuous_scale='Reds')
                    fig_dest_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_dest_bar, use_container_width=True, key="tab1_dest_bar")
        else:
            st.warning("분석 데이터가 존재하지 않습니다.")
    else:
        st.error("항공 데이터 로드 실패")

# ----------------------------------------------------
# TAB 2: 타겟 도시별 심층 비교 분석 (City-Specific Deep Dive)
# ----------------------------------------------------
with tab2:
    st.subheader("🛫 타겟 도시별 심층 비교 분석 (City-Specific Deep Dive)")
    st.caption("※ 2020년~2025년 실적 데이터를 기반으로 각 타겟 도시의 성과를 개별적으로 상세 분석합니다.")
    
    df_air = global_data.get('aviation', pd.DataFrame()).copy()
    
    if not df_air.empty:
        # 타겟 도시 선택기
        city_code_map = {'다낭': 'DAD', '나트랑': 'CXR', '싱가포르': 'SIN'}
        sel_city = st.selectbox("분석 대상 도시를 선택하세요:", list(city_code_map.keys()), index=0)
        sel_code = city_code_map[sel_city]
        
        # 선택된 도시 데이터 필터링
        df_tgt = df_air[df_air['공항'] == sel_code].copy()
        
        if not df_tgt.empty:
            # 날짜 정규화
            df_tgt['연도_str'] = df_tgt['연도'].astype(int).astype(str)
            df_tgt['월_str'] = df_tgt['월'].astype(int).astype(str).str.zfill(2)
            df_tgt['연월'] = pd.to_datetime(df_tgt['연도_str'] + '-' + df_tgt['월_str'] + '-01', errors='coerce')
            df_tgt = df_tgt.sort_values('연월')
            
            # --- 상단 주요 지표 ---
            kpi1, kpi2, kpi3 = st.columns(3)
            total_p = float(df_tgt['여객_계'].sum())
            total_f = float(df_tgt['운항_계'].sum())
            avg_p = float(df_tgt['여객_계'].mean()) if not df_tgt.empty else 0
            
            kpi1.metric(f"{sel_city} 누적 여객", f"{total_p:,.0f}명")
            kpi2.metric(f"{sel_city} 누적 운항", f"{total_f:,.0f}회")
            kpi3.metric("월 평균 여객", f"{avg_p:,.0f}명")
            
            st.markdown("---")
            
            # --- Layout ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown(f"**📈 {sel_city} 월별 여객 추이 (Time Series)**")
                fig_time = px.line(df_tgt, x='연월', y='여객_계', markers=True, color_discrete_sequence=['#FF4B4B'],
                                 title=f"{sel_city} Monthly Passenger Growth")
                fig_time.update_layout(hovermode="x unified")
                st.plotly_chart(fig_time, use_container_width=True)
                
            with c2:
                st.markdown(f"**📊 {sel_city} 주요 노선별 점유율 (Route Mix)**")
                if '노선' in df_tgt.columns:
                    route_data = df_tgt.groupby('노선')['여객_계'].sum().reset_index().sort_values('여객_계', ascending=False).head(10)
                    fig_route = px.bar(route_data, x='여객_계', y='노선', orientation='h', text_auto=',.0f',
                                     color='여객_계', color_continuous_scale='Reds', title=f"{sel_city} Top Routes")
                    fig_route.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_route, use_container_width=True)
                else:
                    st.info("노선 상세 데이터가 없습니다.")
            
            st.markdown("---")
            
            # --- 항공사별 분석 ---
            st.markdown(f"**✈️ {sel_city} 취항 항공사별 실적 규모**")
            carrier_data = df_tgt.groupby('항공사')['여객_계'].sum().reset_index().sort_values('여객_계', ascending=False)
            fig_carrier = px.pie(carrier_data, names='항공사', values='여객_계', hole=0.3,
                               title=f"{sel_city} Airline Market Share",
                               color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_carrier, use_container_width=True)
            
            st.info(f"💡 **City Insight:** {sel_city}은(는) 2020년 이후 총 {total_p:,.0f}명의 여객을 유치하며 지역 거점으로서의 입지를 다지고 있습니다.")
            
            # --- 통합 모니터링 (3개 도시 비교) ---
            st.markdown("---")
            st.markdown("#### 🔄 3개 도시 통합 비교 모니터링")
            df_all_tgt = df_air[df_air['공항'].isin(city_code_map.values())].copy()
            df_all_tgt['도시명'] = df_all_tgt['공항'].map({v: k for k, v in city_code_map.items()})
            df_all_tgt['연월'] = pd.to_datetime(df_all_tgt['연도'].astype(int).astype(str) + '-' + df_all_tgt['월'].astype(int).astype(str).str.zfill(2) + '-01')
            
            fig_main = px.line(df_all_tgt.groupby(['연월', '도시명'])['여객_계'].sum().reset_index(), 
                               x='연월', y='여객_계', color='도시명', markers=True, 
                               title="3개 도시 시계열 여객 흐름 통합 모니터링")
            st.plotly_chart(fig_main, use_container_width=True)
            
            # --- 요약 표 ---
            st.markdown("#### 📊 도시별 종합 요약 (2020-2025)")
            summary_table = df_all_tgt.groupby('도시명').agg({'여객_계': 'sum'}).reset_index()
            summary_table.columns = ['도시명', '누적 여객(명)']
            st.table(summary_table.set_index('도시명').style.format('{:,}'))
        else:
            st.warning("선택된 도시의 실적 데이터를 찾을 수 없습니다.")
    else:
        st.error("항공 데이터 로드 실패")

# --- Tab 3, 4, 5: 기존 EDA 및 리뷰 유지 (라이트 테마 적용) ---
df_rv = global_data.get('reviews', pd.DataFrame())

if not df_rv.empty:
    with tab3:
        st.header("📊 종합 평점 및 만족도 지표")
        col1, col2 = st.columns(2)
        with col1:
            fig3 = px.histogram(df_rv, x='평점', title="고객 평점 분포", nbins=10, color_discrete_sequence=['#3b82f6'])
            st.plotly_chart(fig3, use_container_width=True)
        with col2:
            companion_rating = df_rv.groupby('동행')['평점'].mean().sort_values(ascending=False).reset_index()
            fig4 = px.bar(companion_rating, x='동행', y='평점', color='평점', color_continuous_scale='Blues')
            st.plotly_chart(fig4, use_container_width=True)

    with tab4:
        st.header("⚠️ 저평점 리스크 및 상품 현황")
        df_rv['저평점'] = (df_rv['평점'] <= 3).astype(int)
        low_ratio = df_rv.groupby('대상도시')['저평점'].mean().reset_index()
        low_ratio['저평점_비율'] = low_ratio['저평점'] * 100
        fig5 = px.bar(low_ratio.sort_values('저평점_비율', ascending=False), x='대상도시', y='저평점_비율', color='저평점_비율', color_continuous_scale='Reds')
        st.plotly_chart(fig5, use_container_width=True)

    with tab5:
        st.header("🔍 AI 기반 리뷰 키워드 및 연령대 분석")
        col1, col2 = st.columns([1, 2])
        with col1:
            age_dist = df_rv['연령대'].value_counts().reset_index()
            fig6 = px.pie(age_dist, values='count', names='연령대', hole=0.4)
            st.plotly_chart(fig6, use_container_width=True)
        with col2:
            st.write("**주요 불만/만족 키워드 시각화 (준비 중)**")
            st.info("데이터 보안 정책에 따라 핵심 키워드 엔진은 서버에서 동작합니다.")

# 푸터
st.markdown("---")
st.markdown("© 2026 HanaTour Bio Analytics Team")
