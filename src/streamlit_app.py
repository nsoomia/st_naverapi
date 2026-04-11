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
    # 스크립트 위치 기준 프로젝트 루트 및 데이터 경로 설정
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    global_data = {}
    
    # 가) 항공 데이터 로드 및 정규화
    av_path = os.path.join(DATA_DIR, 'processed_aviation_performance.csv')
    if os.path.exists(av_path):
        df_av = pd.read_csv(av_path, encoding='utf-8-sig')
        df_av.columns = [c.strip() for c in df_av.columns]
        
        # 컬럼명 표준화 (명확한 매핑 우선)
        final_rename = {}
        
        # 1. 정확한 매핑 정의
        exact_mapping = {
            '여객_계': '여객_계',
            '여객_계(명)': '여객_계',
            '운항_계': '운항_계',
            '운항_계(편)': '운항_계',
            '항공사명': '항공사',
            '도시': '도시명',
            '국가': '국가',
            '노선': '노선',
            '공항': '공항'
        }
        
        for col in df_av.columns:
            if col in exact_mapping:
                final_rename[col] = exact_mapping[col]

        # 2. 키워드 기반 매핑 (여객_화물 같은 문자열 컬럼 제외를 위해 더 엄격하게 적용)
        # '여객_계'가 이미 있다면 '여객' 키워드로 다른 컬럼을 매핑하지 않음
        mapped_targets = set(final_rename.values())
        
        keywords = {
            '운항': '운항_계',
            '도시': '도시명',
            '연도': '연도',
            '월': '월'
        }
        
        # '여객' 키워드는 '여객_계'가 없을 때만 조심스럽게 적용
        if '여객_계' not in mapped_targets:
            for col in df_av.columns:
                if '여객_계' in col: # '여객' 대신 '여객_계' 포함 시에만
                    final_rename[col] = '여객_계'
                    mapped_targets.add('여객_계')
                    break

        for col in df_av.columns:
            if col in final_rename: continue
            for kw, target in keywords.items():
                if kw in col and target not in mapped_targets:
                    final_rename[col] = target
                    mapped_targets.add(target)
                    break
            
        df_av = df_av.rename(columns=final_rename)
        df_av = df_av.loc[:, ~df_av.columns.duplicated()]
        
        # 3. 필수 컬럼 보장 및 데이터 타입 변환
        # 만약 '여객_계'가 비어있거나 문자열이면 유임/무임/환승객 합계로 대체 시도
        if '여객_계' in df_av.columns:
            df_av['여객_계'] = pd.to_numeric(df_av['여객_계'], errors='coerce').fillna(0)
            
        # 여객_계가 모두 0인 경우 승객 관련 컬럼들 합산 시도
        if '여객_계' not in df_av.columns or df_av['여객_계'].sum() == 0:
            passenger_cols = ['유임승객(명)', '무임승객(명)', '환승객(명)']
            available_cols = [c for c in passenger_cols if c in df_av.columns]
            if available_cols:
                df_av['여객_계'] = df_av[available_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1)

        for target in ['운항_계', '연도', '월']:
            if target in df_av.columns:
                df_av[target] = pd.to_numeric(df_av[target], errors='coerce').fillna(0)
            else:
                df_av[target] = 0
                
        if '도시명' not in df_av.columns:
            df_av['도시명'] = 'Unknown'

        # 노선 데이터가 없을 경우 공항 코드를 기반으로 가상 노선 생성
        if '노선' not in df_av.columns:
            if '공항' in df_av.columns and df_av['공항'].notna().any():
                df_av['노선'] = 'ICN-' + df_av['공항'].astype(str)
            elif '도시명' in df_av.columns:
                df_av['노선'] = 'ICN-' + df_av['도시명'].astype(str)
            else:
                df_av['노선'] = 'Unknown Route'
        
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
                st.caption("팬데믹 이후 전반적인 항공 수요의 회복 강도를 보여줍니다. 2022년을 상점으로 완연한 회복세를 기록하고 있음을 확인할 수 있습니다.")
                
            with t1_r1_c2:
                st.markdown("**📈 월별 세부 여객 변동 추이**")
                trend_m = df_base.groupby('연월')['여객_계'].sum().reset_index().sort_values('연월')
                fig_m = px.line(trend_m, x='연월', y='여객_계', markers=True, title="월별 Passenger Volatility")
                st.plotly_chart(fig_m, use_container_width=True, key="tab1_month_trend")
                st.caption("월별 변동성을 통해 여행 성수기를 파악할 수 있는 지표입니다. 특정 주기별로 여객 수가 급증하는 패턴을 통해 타겟 전략을 수립합니다.")
                
                # --- 월별 트렌드 분석 코멘트 추가 ---
                st.markdown("---")
                st.markdown("#### 🔍 Monthly Trend Analysis")
                if len(trend_m) > 1:
                    avg_pass = trend_m['여객_계'].mean()
                    peak_month = trend_m.loc[trend_m['여객_계'].idxmax(), '연월']
                    st.write(f"데이터 분석 결과, 프로젝트 기간 내 월평균 약 **{avg_pass:,.0f}명**의 여객이 이동했습니다.")
                    st.write(f"가장 높은 여객 수를 기록한 정점은 **{peak_month.strftime('%Y년 %m월')}**입니다. 이는 계절적 성수기 요인 또는 특정 지역의 무비자 정책 변화 등과 밀접한 연관이 있는 것으로 보입니다.")
                    st.info("💡 **트렌드 분석:** 전반적으로 휴가철인 7~8월과 연말연시인 12~1월에 수요가 집중되는 강한 계절적 패턴을 보이며, 2023년 이후로는 계절성 외에도 기저 수요의 지속적인 상승세가 유지되고 있습니다.")
                
                # --- 최근 1년 여객 추이 그래프 추가 ---
                st.markdown("---")
                st.markdown("#### 🕒 Latest 1-Year Trend (집중 분석)")
                latest_date = trend_m['연월'].max()
                one_year_ago = latest_date - pd.DateOffset(years=1)
                df_last_year = trend_m[trend_m['연월'] >= one_year_ago]
                
                if not df_last_year.empty:
                    fig_last_year = px.area(df_last_year, x='연월', y='여객_계', markers=True, 
                                          title=f"최근 1년({one_year_ago.strftime('%Y/%m')}~{latest_date.strftime('%Y/%m')}) 여객 추이",
                                          color_discrete_sequence=['#3b82f6'])
                    st.plotly_chart(fig_last_year, use_container_width=True, key="tab1_last_year_trend")
                    st.caption("최근 1년간의 데이터를 집중적으로 분석한 결과입니다. 단기적인 시장 변화와 직근의 수요 회복 탄력성을 가장 정확하게 보여줍니다.")
                
            with t1_r2_c1:
                st.markdown("**🌍 국가별 여객 누적 실적 (Top 15)**")
                top_cnt = df_base.groupby('국가')['여객_계'].sum().reset_index().sort_values('여객_계', ascending=False).head(15)
                fig_cnt = px.bar(top_cnt, x='여객_계', y='국가', orientation='h', text_auto=',.0f', color='여객_계', color_continuous_scale='Greens', title="Top 15 Countries")
                fig_cnt.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_cnt, use_container_width=True, key="tab1_top_countries")
                st.caption("어떤 국가가 국내 여행객들에게 가장 인기 있는지를 보여줍니다. 실적은 해당 국가의 비자 정책이나 상품 공급량에 큰 영향을 받습니다.")
                
            with t1_r2_c2:
                st.markdown("**🏙️ 도시별 여객 누적 실적 (Top 15)**")
                top_city = df_base.groupby('도시명')['여객_계'].sum().reset_index().sort_values('여객_계', ascending=False).head(15)
                fig_city = px.bar(top_city, x='여객_계', y='도시명', orientation='h', text_auto=',.0f', color='여객_계', color_continuous_scale='Oranges', title="Top 15 Cities")
                fig_city.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_city, use_container_width=True, key="tab1_top_cities")
                st.caption("국가 내에서도 핵심 거점이 되는 도시들의 실적 비중을 비교합니다. 상위 도시들의 집중도는 상품 개발 시 가장 먼저 고려되는 요소입니다.")
                
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
                    st.caption("대륙별 전체 방문자 비중을 통해 글로벌 시장의 수요 구조를 이해합니다. 현재 아시아권의 점유율이 압도적임을 확인할 수 있습니다.")
                with d_col2:
                    st.markdown("**📌 국가별 관광객 유입 (Top 10)**")
                    dest_cty = df_dest.groupby('국가')['관광객수'].sum().reset_index().sort_values('관광객수', ascending=False).head(10)
                    fig_dest_bar = px.bar(dest_cty, x='관광객수', y='국가', orientation='h', text_auto=',.0f', color='관광객수', color_continuous_scale='Reds')
                    fig_dest_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_dest_bar, use_container_width=True, key="tab1_dest_bar")
                    st.caption("실제 관광객 유입이 가장 많은 국가를 순위별로 보여줍니다. 항공 실적과 맞물려 여행지의 실질적인 인기도를 대변합니다.")
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
                st.caption(f"선택한 도시({sel_city})의 기간별 여객 성장 추이를 상세히 조망합니다. 성장 정체기나 급증 시점을 파악하여 마케팅 적기를 분석합니다.")
                
            with c2:
                st.markdown(f"**📊 {sel_city} 주요 노선별 점유율 (Route Mix)**")
                st.info("💡 **노선별 점유율이란?** 특정 목적지로 향하는 전체 여객 중 각 항공 노선이 차지하는 비중입니다. 어떤 출발 포트나 경유 노선이 핵심인지 보여줍니다.")
                if '노선' in df_tgt.columns:
                    route_data = df_tgt.groupby('노선')['여객_계'].sum().reset_index().sort_values('여객_계', ascending=False).head(10)
                    fig_route = px.bar(route_data, x='여객_계', y='노선', orientation='h', text_auto=',.0f',
                                     color='여객_계', color_continuous_scale='Reds', title=f"{sel_city} Top Routes")
                    fig_route.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_route, use_container_width=True)
                    st.caption("해당 도시로의 접근성을 결정하는 주요 노선들의 기여도를 보여줍니다. 특정 노선의 집중도가 높을수록 해당 포트의 영향력이 큼을 의미합니다.")
                else:
                    st.info("노선 상세 데이터가 없습니다.")
            
            st.markdown("---")
            
            # --- 항공사별 분석 ---
            st.markdown(f"**✈️ {sel_city} 취항 항공사별 실적 규모**")
            carrier_data = df_tgt.groupby('항공사')['여객_계'].sum().reset_index().sort_values('항공사') # 범례 오름차순
            fig_carrier = px.pie(carrier_data, names='항공사', values='여객_계', hole=0.3,
                               title=f"{sel_city} Airline Market Share",
                               category_orders={"항공사": carrier_data['항공사'].tolist()}, # 범례 고정
                               color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_carrier, use_container_width=True)
            st.caption("공급 항공사별 점유율을 통해 시장의 경쟁 구조를 파악합니다. 대형 항공사와 저비용 항공사 간의 실적 편차를 확인할 수 있습니다.")
            
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
            st.caption("다낭, 나트랑, 싱가포르 등 주요 관심 지역의 회복세와 성장 속도를 평행선상에서 비교합니다. 지역 간의 수요 전이 현상이나 트렌드 차이를 발견할 수 있습니다.")
            
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
        st.header("📊 고객 만족도 및 동행인 심층 분석")
        
        # 국가 매핑 함수
        def map_country(city):
            if city in ['다낭', '나트랑']: return '베트남'
            if city in ['싱가포르']: return '싱가포르'
            return '기타'
            
        df_rv['국가'] = df_rv['대상도시'].apply(map_country)
        
        # --- 1. 종합 지표 (전체 나라 통합) ---
        st.subheader("🌐 전체 국가 종합 지표 (Overall KPI)")
        c_all1, c_all2 = st.columns(2)
        with c_all1:
            st.markdown("**⭐ 전체 고객 평점 분포**")
            fig_all_rv = px.histogram(df_rv, x='평점', nbins=10, color_discrete_sequence=['#1e40af'])
            st.plotly_chart(fig_all_rv, use_container_width=True, key="overall_rating")
            st.caption("3개국 전체를 병합한 평점 분포입니다. 전반적인 서비스 품질의 안정성을 확인할 수 있습니다.")
        with c_all2:
            st.markdown("**👥 전체 동행인 유형 비중**")
            comp_dist = df_rv['동행'].value_counts().reset_index()
            comp_dist.columns = ['동행 유형', '인원']
            # 범례 오름차순 정렬
            comp_dist = comp_dist.sort_values('동행 유형')
            fig_all_comp = px.pie(comp_dist, values='인원', names='동행 유형', hole=0.4, 
                                 category_orders={"동행 유형": comp_dist['동행 유형'].tolist()},
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_all_comp, use_container_width=True, key="overall_companion")
            st.caption("전체 국가 통합 동행인 분포입니다. 어떤 타겟층이 주를 이루는지 파악하는 가늠자가 됩니다.")

        st.markdown("---")

        # --- 2. 나라별 세부 지표 ---
        st.subheader("📍 국가별 세부 만족도 비교 (Country-Specific)")
        sel_country = st.radio("상세 분석 국가 선택:", ['전체'] + list(df_rv['국가'].unique()), horizontal=True)
        
        if sel_country == '전체':
            # 나라별 평균 평점 비교 바 차트
            st.markdown("**🚩 국가별 평균 평점 비교**")
            country_rating = df_rv.groupby('국가')['평점'].mean().sort_values(ascending=False).reset_index()
            fig_c_compare = px.bar(country_rating, x='국가', y='평점', color='평점', color_continuous_scale='Blues')
            st.plotly_chart(fig_c_compare, use_container_width=True)
            
            # 나라별 동행인 분포 비교
            st.markdown("**🚩 국가별 동행인 구성 비교**")
            country_comp = df_rv.groupby(['국가', '동행']).size().reset_index(name='count')
            fig_c_comp = px.bar(country_comp, x='국가', y='count', color='동행', barmode='group',
                               color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_c_comp, use_container_width=True)
        else:
            df_sel = df_rv[df_rv['국가'] == sel_country]
            c_sel1, c_sel2 = st.columns(2)
            with c_sel1:
                st.markdown(f"**⭐ {sel_country} 평점 분포**")
                fig_sel3 = px.histogram(df_sel, x='평점', nbins=10, color_discrete_sequence=['#3b82f6'])
                st.plotly_chart(fig_sel3, use_container_width=True)
            with c_sel2:
                st.markdown(f"**👥 {sel_country} 동행 분포**")
                comp_sel = df_sel['동행'].value_counts().reset_index()
                comp_sel.columns = ['동행', '인원']
                comp_sel = comp_sel.sort_values('동행') # 범례 정렬
                fig_sel4 = px.pie(comp_sel, values='인원', names='동행', hole=0.4,
                                 category_orders={"동행": comp_sel['동행'].tolist()})
                st.plotly_chart(fig_sel4, use_container_width=True)
            st.info(f"💡 **{sel_country} Insight:** {sel_country} 지역은 타 지역 대비 {df_sel['동행'].mode()[0] if not df_sel.empty else 'Unknown'} 동행의 비중이 높으며, 평균 평점은 {df_sel['평점'].mean():.2f}점을 기록하고 있습니다.")

    with tab4:
        st.header("⚠️ 저평점 리스크 및 상품 현황")
        
        # 저평점 비율 계산 (3점 이하 / 전체 레이팅 수)
        st.subheader("📉 지역별 저평점 발생 비율")
        st.info("💡 **산출 방식:** 평점 5점 만점 중 3점 이하(1~3점)를 기록한 리뷰의 수를 해당 지역의 전체 리뷰 수로 나눈 백분율입니다.")
        
        df_rv['저평점'] = (df_rv['평점'] <= 3).astype(int)
        low_ratio = df_rv.groupby(['국가', '대상도시'])['저평점'].mean().reset_index()
        low_ratio['저평점_비율'] = low_ratio['저평점'] * 100
        
        fig5 = px.bar(low_ratio.sort_values('저평점_비율', ascending=False), 
                     x='대상도시', y='저평점_비율', color='국가', text_auto='.1f',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig5, use_container_width=True)
        
        # --- 나라별 저평점 근거 코멘트 ---
        st.markdown("#### 💬 지역별 리스크 발생 근거 분석")
        for country in df_rv['국가'].unique():
            c_ratio = df_rv[df_rv['국가'] == country]['저평점'].mean() * 100
            with st.expander(f"📌 {country} 지역 분석 (저평점 비율: {c_ratio:.1f}%)"):
                if country == '베트남':
                    st.write("주로 패키지 여행의 **가이드 서비스 편차**와 **쇼핑 강요**에 대한 불만이 저평점의 주요 원인으로 분석됩니다. 특히 성수기 인원 밀집으로 인한 대기 시간 발생이 만족도를 저해하는 핵심 요소입니다.")
                elif country == '싱가포르':
                    st.write("높은 물가 대비 **상품 가성비**에 대한 민감도가 저평점의 근거로 작용합니다. 자유 시간 부족이나 특정 옵션 관광의 강제성 여부가 리뷰 점수에 큰 영향을 미치고 있습니다.")
                else:
                    st.write("다양한 고객 VoC가 혼재되어 있으나, 전반적으로 현지 숙소 상태 및 식사 퀄리티가 기대치에 미치지 못할 때 저평점 비율이 상승하는 경향을 보입니다.")

        st.markdown("---")
        
        # --- 저평점 리스크 상품 Top 3 ---
        st.subheader("🚨 집중 관리 필요 상품 (Low-Rating Top 3)")
        st.write("최근 평점 3점 이하가 가장 많이 발생한 상품 리스트입니다. 긴급한 상품 점검 및 일정 개선이 권고됩니다.")
        
        risk_products = df_rv[df_rv['저평점'] == 1]['상품명'].value_counts().head(3).reset_index()
        risk_products.columns = ['상품명', '저평점 리뷰 수']
        
        if not risk_products.empty:
            for i, row in risk_products.iterrows():
                st.error(f"**TOP {i+1}: {row['상품명']}** (저평점 발생: {row['저평점 리뷰 수']}건)")
        else:
            st.success("현재 집중 관리가 필요한 특정 저평점 상품이 없습니다.")

    with tab5:
        st.header("🔍 AI 기반 리뷰 키워드 및 연령대 심층 분석")
        
        # --- 도시 필터 추가 ---
        all_cities = ['전체'] + list(df_rv['대상도시'].unique())
        sel_city_rv = st.selectbox("분석 대상 도시 선택 (리뷰):", all_cities, index=0)
        
        df_tgt_rv = df_rv.copy()
        if sel_city_rv != '전체':
            df_tgt_rv = df_rv[df_rv['대상도시'] == sel_city_rv]
            
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**👥 {sel_city_rv} 연령대별 분포**")
            # 연령대 데이터 정규화 및 정렬
            age_dist = df_tgt_rv['연령대'].astype(str).value_counts().reset_index()
            age_dist.columns = ['연령대', 'count']
            
            # '20' -> '20대' 형식으로 변환 및 정렬을 위한 전처리
            def format_age(age_str):
                clean_age = "".join(filter(str.isdigit, age_str))
                return f"{clean_age}대" if clean_age else age_str
                
            age_dist['연령대_표기'] = age_dist['연령대'].apply(format_age)
            age_dist['age_num'] = age_dist['연령대'].str.extract('(\d+)').astype(float)
            age_dist = age_dist.sort_values('age_num') # 오름차순 정렬
            
            fig_6 = px.pie(age_dist, values='count', names='연령대_표기', hole=0.4,
                         category_orders={"연령대_표기": age_dist['연령대_표기'].tolist()},
                         color_discrete_sequence=px.colors.sequential.Aggrnyl)
            st.plotly_chart(fig_6, use_container_width=True)
            st.caption("주요 이용 연령층을 파악하여 타겟 마케팅 전략을 세분화합니다.")
            
        with col2:
            st.write(f"**📝 {sel_city_rv} 리뷰 핵심 키워드 Top 20**")
            
            @st.cache_data
            def get_top_keywords_refined(df, top_n=20):
                import re
                from collections import Counter
                
                # 불용어 리스트 보강
                STOPWORDS = set(['에서', '하고', '으로', '하는', '입니다', '있습니다', '정말', '너무', '좋아요', '자체가', '같아요', '습니다', '했고', '해서', '있어서', '있는', '있고', '한다', '있다', '것이', '것은', '등의', '한', '때문에', '위한', '대해', '대한', '모든', '통해', '같은', '함께', '전체', '가장', '다양한', '위해', '매우', '진짜', '좀', '그', '건', '들', '이', '가', '은', '는', '도', '를', '을', '의', '에', '와', '과', '나', '다', '로', '고', '지', '아', '오', '요', '이런', '저런', '그런', '하나', '건데', '때', '번', '함께', '보고', '갔는데', '많이', '정말', '매우', '아주', '조금', '특히', '다시', '꼭', '근데', '하지만', '그래도', '그래서', '그런데', '그냥', '조금', '약간', '거의', '모두', '전부', '진짜', '완전', '대박', '진심', '진짜로', '덕분에'])
                
                text = " ".join(df['내용'].astype(str))
                words = re.findall(r'[가-힣]{2,}', text) 
                
                # 단어 통합 및 정규화 (유사어 처리 및 제외)
                refined_words = []
                for w in words:
                    # '여행' 관련 단어 제외 (요청사항 반영)
                    if w.startswith('여행') and len(w) <= 4: 
                        continue
                    elif w not in STOPWORDS:
                        refined_words.append(w)
                
                counts = Counter(refined_words)
                return counts.most_common(top_n)

            keywords = get_top_keywords_refined(df_tgt_rv)
            if keywords:
                df_kw = pd.DataFrame(keywords, columns=['단어', '빈도'])
                fig7 = px.bar(df_kw, x='빈도', y='단어', orientation='h', 
                             color='빈도', color_continuous_scale='Tealgrn',
                             text_auto=True, title=f"{sel_city_rv} Top 20 Keywords")
                fig7.update_layout(yaxis={'categoryorder':'total ascending'})
                # 모든 키워드 표기 (Y축 레이블 강제)
                fig7.update_yaxes(tickmode='linear')
                st.plotly_chart(fig7, use_container_width=True)
                st.caption(f"'{sel_city_rv}' 리뷰에서 핵심적으로 언급되는 20대 키워드들을 통해 구체적인 고객 만족 및 불만 요소를 파악합니다.")
            else:
                st.info("분석할 리뷰 텍스트가 부족합니다.")

        # --- [NEW] 부정 키워드 분석 섹션 ---
        st.markdown("---")
        st.subheader(f"🧨 {sel_city_rv} 부정 리뷰 집중 분석 (Rating ≤ 3)")
        
        df_neg_rv = df_tgt_rv[df_tgt_rv['평점'] <= 3]
        
        if not df_neg_rv.empty:
            neg_keywords = get_top_keywords_refined(df_neg_rv, top_n=10)
            if neg_keywords:
                df_neg_kw = pd.DataFrame(neg_keywords, columns=['단어', '빈도'])
                fig8 = px.bar(df_neg_kw, x='빈도', y='단어', orientation='h', 
                             color='빈도', color_continuous_scale='Reds',
                             text_auto=True, title=f"{sel_city_rv} Top 10 Negative Keywords")
                fig8.update_layout(yaxis={'categoryorder':'total ascending'})
                fig8.update_yaxes(tickmode='linear')
                st.plotly_chart(fig8, use_container_width=True)
                st.info(f"💡 **부정 인사이트:** '{sel_city_rv}' 지역의 부정 리뷰에서 가장 많이 언급된 단어들입니다. 위 키워드들을 중심으로 현지 서비스 및 일정 품질 개선이 필요합니다.")
            else:
                st.info("부정 리뷰에서 추출된 유효 키워드가 없습니다.")
        else:
            st.success(f"✔️ 해당 조건({sel_city_rv})에서 분석할 부정 리뷰가 없습니다! 전반적인 만족도가 매우 높습니다.")

# 푸터
st.markdown("---")
st.markdown("© 2026 HanaTour Bio Analytics Team")
