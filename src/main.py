import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data_loader import load_all_data, preprocess_and_merge
from src.analytics_engine import AnalyticsEngine
from src.ui_elements import render_analysis_box, apply_custom_style, PRIMARY_COLOR, SECONDARY_COLOR

# ---------------------------------------------------------
# 1. 전역 설정 및 스타일 적용
# ---------------------------------------------------------
st.set_page_config(page_title="HanaTour Travel Insight Dashboard", layout="wide")
apply_custom_style()

# 데이터 분석 엔진 초기화
def get_engine():
    return AnalyticsEngine()

engine = get_engine()

# ---------------------------------------------------------
# ---------------------------------------------------------
# 2. 사이드바 메뉴 (탭 대체)
# ---------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/ko/c/c5/Hanatour_logo.png", width=150)

tab_names = [
    "📈 항공 성과 추이", "📍 도시별 통합 EDA", "📊 하나투어 판매 상품 요약", 
    "🔍 리뷰 및 전략 심층 분석", "🛡️ 리스크 모니터링", "✨ 맞춤 추천 위저드"
]
selected_tab = st.sidebar.radio("📋 분석 메뉴 선택", tab_names)

filtered_df = engine.df

# ---------------------------------------------------------
# 3. 메인 타이틀
# ---------------------------------------------------------
st.title("✈️ 하나투어 여행 상품 성과 및 전략 분석")
st.markdown("가정 기반의 상품 분석 및 시뮬레이션을 위한 통합 데이터 분석 도구입니다.")

# ---------------------------------------------------------
# 탭 1: 항공 성과 추이 (Yearly/Monthly/Country/City)
# ---------------------------------------------------------
if selected_tab == "📈 항공 성과 추이":
    st.subheader("✈️ 글로벌 항공 성과 및 시장 데이터 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. 연도별 전체 여객 실적 추이
        yearly_data = engine.get_yearly_aviation_performance()
        fig_yearly = px.line(yearly_data, x="연도", y="유임승객(명)", title="연도별 전체 여객 실적 추이", markers=True)
        st.plotly_chart(fig_yearly, use_container_width=True)
        
        render_analysis_box(
            "연도별 시장 성장성 분석",
            f"과거 {len(yearly_data)}개년의 글로벌 통합 전 노선 유임승객 데이터를 합산하여 도출한 전체 시장 규모 추이임.",
            "펜데믹 이후 항공 시장의 회복탄력성을 연도별 누적 데이터를 통해 확인할 수 있으며, 전년 대비 성장률 기반의 상품 공급량 조절 전략이 유효함."
        )

    with col2:
        # 2. 월별 세부 여객 변동 추이
        monthly_perf = engine.get_monthly_aviation_performance()
        fig_monthly = px.area(monthly_perf, x="월", y="유임승객(명)", title="월별 세부 여객 변동 추이")
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        render_analysis_box(
            " 월별 항공 수요 분석",
            "하나투어와 연동된 다낭(DAD), 나트랑(CXR), 싱가포르(SIN) 노선의 과거 12개월간 평균 항공객수 데이터 기반으로 함.",
            "여름 휴가철(7-8월)과 겨울 성수기(1월)에 항공 수요가 집중되는 전형적인 시즈널리티 트렌드를 보이며, 항공 수요가 높은 시즌에 평점 관리 강화가 필요함."
        )

    col3, col4 = st.columns(2)
    
    with col3:
        # 3. 국가별 여객 누적 실적 (Top 10)
        country_data = engine.get_cumulative_performance_by_country().head(10)
        fig_country = px.bar(country_data, x="유임승객(명)", y="국가", orientation='h', 
                             title="국가별 여객 누적 실적 (Top 10)", color="유임승객(명)", color_continuous_scale="Viridis")
        st.plotly_chart(fig_country, use_container_width=True)
        
        render_analysis_box(
            "국가별 시장 지배력",
            "인천공항 및 주요 거점 공항에서 출발하는 국가별 누적 승객 데이터를 집계한 결과임.",
            "동남아시아 및 일본 노선의 압도적인 누적 실적은 하나투어의 리소스 배분이 해당 지역에 집중되어야 함을 강력히 시사함."
        )

    with col4:
        # 4. 도시별 여객 누적 실적 (Top 10)
        city_cum_data = engine.get_cumulative_performance_by_city().head(10)
        fig_city_cum = px.bar(city_cum_data, x="유임승객(명)", y="도시", orientation='h',
                              title="도시별 여객 누적 실적 (Top 10)", color="유임승객(명)", color_continuous_scale="Plasma")
        st.plotly_chart(fig_city_cum, use_container_width=True)
        
        render_analysis_box(

            " 도시별 거점 누적 분석",
            "실질적인 여객 유입이 가장 큰 상위 10개 도시의 누적 실적 지표임.",
            "중단거리 핵심 거점 도시(다낭, 방콕 등)에 대한 상품 집중도를 유지하면서도, 누적 실적 성장세가 뚜렷한 신규 도시 발굴이 병행되어야 함."
        )


# ---------------------------------------------------------
# 탭 2: 3개 도시(다낭/나트랑/싱가포르) 항공 분석
# ---------------------------------------------------------
if selected_tab == "📍 도시별 통합 EDA":
    st.subheader("📍 핵심 3개 도시(다낭/나트랑/싱가포르) 항공 분석")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 1. 3개 도시 연도별 여객 실적 추이
        city_yearly = engine.get_specific_cities_aviation_yearly()
        fig_city_yearly = px.line(city_yearly, x="연도", y="유임승객(명)", color="도시",
                                  title="연도별 여객 실적 추이", markers=True)
        st.plotly_chart(fig_city_yearly, use_container_width=True)
        
        render_analysis_box(
            "도시별 연도 성과 분석",
            "다낭(DAD), 나트랑(CXR), 싱가포르(SIN) 노선의 최근 연도별 누적 실적임.",
            "도시별 회복 시점과 성장 가속도 확인이 가능하며, 다낭의 시장 확대가 가장 두드러짐."
        )

    with col2:
        # 2. 3개 도시 월별 여객 변동 추이
        city_monthly = engine.get_specific_cities_aviation_monthly()
        fig_city_monthly = px.line(city_monthly, x="월", y="유임승객(명)", color="도시",
                                   title="월별 여객 변동 추이", markers=True)
        st.plotly_chart(fig_city_monthly, use_container_width=True)
        
        render_analysis_box(
            "도시별 시즌성 분석",
            "월별 평균 유임승객 데이터를 통해 시즈널리티 편차를 가시화함.",
            "성수기 집중도가 높은 다낭/나트랑과 달리 싱가포르는 연중 고른 수요를 보임."
        )

    with col3:
        # 3. 도시별 항공사별 점유율 (Stacked Bar)
        airline_share = engine.get_airline_share_in_specific_cities()
        fig_airline = px.bar(airline_share, x="도시", y="유임승객(명)", color="항공사명", 
                             title="도시별 항공사별 점유율 (Top 5)", barmode="stack")
        st.plotly_chart(fig_airline, use_container_width=True)
        
        render_analysis_box(
            "도시별 항공사 점유율",
            "각 도시별 시장 점유율 상위 5개 항공사의 유임승객 비중임.",
            "LCC 중심의 노선 구조를 확인할 수 있으며, 특정 항공사와의 협력 강화를 통한 원가 절감 전략이 유효함."
            "FSC 비중이 높은 도시들의 경우 가격 민감도가 낮을 것."
        )


# ---------------------------------------------------------
# 탭 3: 판매 상품 요약 (사용자님이 만족하셨던 3열 교차 분석 포함)
# ---------------------------------------------------------
# ---------------------------------------------------------
# 탭 3: 판매상품분석
# ---------------------------------------------------------
if selected_tab == "📊 하나투어 판매 상품 요약":
    st.header("📦 하나투어 판매 상품 요약")
    
    # [방어 로직] 필수 컬럼 존재 여부 확인
    if '상품군' not in filtered_df.columns:
        st.warning("⚠️ '상품군' 데이터가 아직 로드되지 않았거나 분석 필터 결과에 포함되지 않았습니다. 사이드바 설정을 확인하거나 페이지를 새로고침해 주세요.")
        st.stop()
        
    # 상단 3열 그래프 배치
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 1. 상품군별 구성 비중 (Pie)
        category_dist = engine.get_category_distribution(filtered_df)
        if not category_dist.empty:
            fig_pie = px.pie(category_dist, values='상품수', names='상품군', 
                             title="상품군별 구성 비중", hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
        
    with col2:
        # 2. 상품군별 성과 비교 (평점)
        category_perf = engine.get_category_performance(filtered_df)
        if not category_perf.empty:
            fig_perf = px.bar(category_perf, x='상품군', y='평점', color='상품군',
                              title="상품군별 평균 평점", text_auto='.2f',
                              color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
        
    with col3:
        # 3. 지역별 상품 포트폴리오 (Stacked Bar)
        regional_dist = engine.get_regional_category_distribution(filtered_df)
        if not regional_dist.empty:
            fig_region = px.bar(regional_dist, x='대상도시', y='상품수', color='상품군',
                                title="지역별 상품 포트폴리오", barmode='stack',
                                color_discrete_sequence=px.colors.qualitative.Antique)
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # XAI 분석 근거 및 해석 제공
    st.divider()
    
    render_analysis_box(
        "상품군별 시장 점유율 및 성과 분석",
        f"하나투어 통합 데이터베이스 내 {len(filtered_df)}건의 상품 마스터 및 실제 예약 트렌드를 기반으로 패키지, 에어텔, 투어/티켓 비중을 산출함.",
        "다낭은 '패키지' 위주의 가족 단위 상품이 강세를 보이나, 싱가포르와 나트랑은 '에어텔' 및 '현지투어/티켓'의 비중이 점차 확대되고 있음. 특히 투어/티켓 상품군의 평점이 가장 높게 형성되어, 단품 위주의 자유여행 시장 대응 전략이 유효함을 시사함."
    )


    # [교차 분석 섹션 복구]
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    with sub_col1:
        st.subheader("💰 가격대 및 만족도")
        detail_perf = engine.get_category_performance(filtered_df)
        st.plotly_chart(px.scatter(detail_perf, x="성인가격", y="평점", size="상품수", color="상품군", log_x=True, title="가격 vs 평점 상관도"), use_container_width=True)
    render_analysis_box(
        "가격 대비 가치(Value for Money) 분석",
        "성인가격(KRW)과 고객 평점 7.4만 건의 교차 산점도를 기반으로 산출된 가성비 지표임.",
        "버블 차트를 통해 상품군별 가격대와 평점의 상관관계를 한눈에 파악할 수 있습니다. "
        "에어텔 상품군은 가격 민감도가 높으나 만족도가 고르게 분포하며, 패키지 상품군은 특정 가격대(80~120만 원)에 밀집되어 브랜드 충성도를 형성하고 있습니다. "
        "버블의 크기는 해당 그룹의 상품 수를 의미하며, 볼륨이 큰 그룹일수록 하나투어의 주력 시장임을 시사합니다."
    )
    with sub_col2:
        st.subheader("✈️ 항공사 공급 점유율")
        @st.cache_data
        def get_integrated_airline_share_v2():
            import os
            data_dir = r'data'
            files = ['hanatour_danang_airtel_integrated.csv', 'hanatour_danang_integrated.csv', 'hanatour_danang_tour_ticket_integrated.csv', 'hanatour_nhatrang_airtel_integrated.csv', 'hanatour_nhatrang_integrated.csv', 'hanatour_nhatrang_tour_ticket_integrated.csv', 'hanatour_singapore_airtel_integrated.csv', 'hanatour_singapore_integrated.csv', 'hanatour_singapore_tour_ticket_integrated.csv']
            combined = []
            for f in files:
                f_path = os.path.join(data_dir, f)
                if os.path.exists(f_path):
                    tmp = pd.read_csv(f_path, encoding='utf-8-sig', usecols=lambda x: x in ['항공사명', '항공사', '대상도시'])
                    if '항공사명' in tmp.columns: tmp.rename(columns={'항공사명': '항공사'}, inplace=True)
                    if '대상도시' in tmp.columns: tmp.rename(columns={'대상도시': '도시'}, inplace=True)
                    tmp['도시'] = '다낭' if 'danang' in f else ('나트랑' if 'nhatrang' in f else '싱가포르')
                    combined.append(tmp[['도시', '항공사']])
            if not combined: return pd.DataFrame()
            full = pd.concat(combined, ignore_index=True).dropna(subset=['항공사'])
            full['유형'] = full['항공사'].apply(lambda x: 'FSC' if any(f in str(x) for f in ['대한항공', '아시아나', '싱가포르', '베트남']) else 'LCC')
            return full

        airline_data = get_integrated_airline_share_v2()
        if not airline_data.empty:
            share_df = airline_data.groupby(['도시', '항공사']).size().reset_index(name='상품수')
            st.plotly_chart(px.bar(share_df, x="도시", y="상품수", color="항공사", barmode="stack", title="도시별 항공사 분포"), use_container_width=True)

    with sub_col3:
        st.subheader("📊 FSC vs LCC 비중")
        if not airline_data.empty:
            type_df = airline_data.groupby(['도시', '유형']).size().reset_index(name='상품수')
            st.plotly_chart(px.bar(type_df, x="도시", y="상품수", color="유형", barmode="relative", text_auto=True, title="도시별 공급 비율"), use_container_width=True)

    render_analysis_box(
        "하나투어 상품 내 항공사 비중",
        "각 도시별 LCC와 FSC의 비중 확인 가능",
        "시장 전체 항공객수 추이와 실제 하나투어가 공급 중인 상품의 항공사 비중을 비교 분석할 수 있음. 특정 도시에 특정 항공사 비중이 쏠려 있다면, 해당 항공사의 스케줄 변동이 상품 운영 리스크로 직결될 수 있으므로 공급망 다변화 전략이 필요함을 시사함."
    )

    st.markdown("---")
    st.subheader("👥 고객 세그먼트별 맞춤 전략 지표 (Segment Strategy)")
    seg_metrics = engine.get_segment_strategy_metrics(filtered_df)

    if seg_metrics:
        seg_c1, seg_c2 = st.columns(2)
        with seg_c1:
            st.markdown("#### 💸 세그먼트별 가격-평점 민감도")
            fig_sens = px.scatter(seg_metrics['price_sensitivity'], x='성인가격', y='평점', 
                                  color='연령대', symbol='동행', size='리뷰ID',
                                  title="타겟별 가격 수용도 및 민감도 분석")
            # 범주 시인성 확보를 위해 가로 길이를 줄이고 여백 조정
            fig_sens.update_layout(width=500, legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_sens, use_container_width=False)
        with seg_c2:
            st.markdown("#### 👨‍👩‍👧 아동 동반 가족여행: 체험 vs 일정 분리")
            fig_split = px.bar(seg_metrics['family_satisfaction'], x="항목", y="평균평점", 
                               color="항목", title="가족 타겟의 만족도 디커플링 현상", text="평균평점")
            fig_split.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_split.update_layout(yaxis=dict(range=[0, 5]))
            st.plotly_chart(fig_split, use_container_width=True)
            
        render_analysis_box(
            "세그먼트 타겟 맞춤화 핵심 인사이트",
            "연령대별/동행별 평균 판매가와 평균 평점의 교차 산점도(가격 민감도) 및 리뷰 내용의 NLP 키워드 그룹(엑티비티 vs 쇼핑/동선) 기반 '체험 vs 일정' 만족도 분리 산출 결과임.",
            "① 단가 민감도: 연령과 그룹 성격에 따라 가격 탄력성이 극명히 갈립니다. 50대 이상의 부부/가족 그룹은 고가 상품에서도 평점 하락이 방어되는 '비탄력적/프리미엄 추구형' 특성을 보이는 반면, 2030 에어텔/투어 그룹은 저가 투입 시 높은 평점으로 보상하는 '탄력적/가성비 추구형' 채널임이 입증되었습니다.\n"
            "② 만족도 디커플링: 아동 동반 여행객 집단의 텍스트를 정밀 분석한 결과, 리조트 수영장 등 '핵심 체험(Activity) 만족도'는 매우 높으나 쇼핑/대기 등 '일정 만족도'에서 치명적인 평점 누수(디커플링 현상)가 발생 중입니다. 이는 보호자(부모)의 체력적 피로도가 평점을 깎아내리는 주범이므로, 가족 전담 투어 상품은 수익 구조상 쇼핑을 강제하기보다 초기 단가를 높이되 '선택적 자유일정'을 100% 보장하는 형태로 기획되어야 합니다."
        )

    st.markdown("---")
    st.subheader("🎯 상품 포트폴리오 최적화 지표 (Portfolio Optimization)")
    port_metrics = engine.get_portfolio_optimization_metrics(filtered_df)
    
    if port_metrics:
        port_c1, port_c2 = st.columns(2)
        with port_c1:
            st.markdown("#### 🧭 가상의 마진-평점 매트릭스 (Margin-Rating)")
            st.caption("※ **수익성(추정 마진율) 산출 근거**: 상품 기본 마진 15% + (쇼핑 1회당 3% 추가 마진)으로 가정하여 환산함")
            fig_margin = px.scatter(port_metrics['margin_matrix'], x="추정마진율(%)", y="평점", 
                                    color="대상도시", size="쇼핑횟수",
                                    title="수익성 vs 만족도 4분면 맵", hover_name="대상도시")
            fig_margin.add_hline(y=4.0, line_dash="dash", line_color="red")
            fig_margin.add_vline(x=25, line_dash="dash", line_color="red")
            st.plotly_chart(fig_margin, use_container_width=True)
            

        with port_c2:
            st.markdown("#### ⏳ 가상 예측 이탈 퍼널 (Funnel Churn Model)")
            fig_funnel = go.Figure(go.Funnel(
                y=port_metrics['funnel_data']['단계'],
                x=port_metrics['funnel_data']['잔존율(%)'],
                textinfo="value+percent initial"
            ))
            fig_funnel.update_layout(title="예약 퍼널 단계별 고객 이탈 예측")
            st.plotly_chart(fig_funnel, use_container_width=True)
        st.info("""
        **💡 수익성(마진율) 알고리즘 상세 근거**
        - **기본 마진 15% (Base Margin)**: 대형 홀세일 여행사의 일반적인 패키지 항공/숙박 중간 유통 기여 이익률 중간값을 반영했습니다.
        - **쇼핑 커미션 3% (Kick-back)**: 다낭, 나트랑 등 핵심 노선의 기형적인 원가 구조상, 쇼핑 센터 방문당 지급받는 랜드사/가이드 커미션을 1회 방문당 총 상품 단가의 약 3% 수준으로 모델링했습니다.
        - **결론**: 본 대시보드에서는 이 가상 원가(Mock Cost) 지표를 통해 **'저마진-고평점(브랜드 견인 상품류)'**과 **'고마진-저평점(쇼핑 뺑뺑이 수익류)'**을 수학적으로 분리하여 포트폴리오 단종 및 가격 인상 등 직관적인 의사결정 지원을 가능하게 만듭니다.
        """)
        render_analysis_box(
            "상품 최적화 및 이탈 방지",
            "가상 원가 기반 마진 추정치와 평점을 4분면 맵핑, 상세조회-결제까지의 전환율(Mock Data) 반영.",
            "마진과 평점이 모두 부진한 좌하위(Low Margin, Low Rating) '레드오션' 상품은 쇼핑 횟수를 강제 조정하거나 단종 처리해야 합니다. 또한 예약 단계 퍼널 모델 상, 30%가 넘는 이탈이 발생하는 '정보 입력' 구간에서 고객이 겪는 폼의 복잡성을 간소화시켜 최종 결제 전환율(CVR) 방어가 시급합니다."
        )


     # ----------------------------------------------------
    # [NEW] 도시별 심층 분석 (EDA 보고서 기반)
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("📍 도시별 심층 분석 (EDA 보고서 기반)")
    
    # 1. 가격 및 평점 분포 (Box Plot)
    with st.expander("📊 1. 도시별 가격 및 평점 분포 분석", expanded=True):
        col_box1, col_box2 = st.columns(2)
        
        with col_box1:
            # 가격 분포 Boxplot
            fig_price_box = px.box(filtered_df, x="대상도시", y="성인가격", color="대상도시",
                                  title="도시별 성인가격 분포 (이상치 탐지)",
                                  points="outliers", color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_price_box, use_container_width=True)
            
        with col_box2:
            # 평점 분포 Boxplot
            fig_rating_box = px.box(filtered_df, x="대상도시", y="평점", color="대상도시",
                                   title="도시별 고객 평점 분포",
                                   points="all", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_rating_box, use_container_width=True)
            
        # 도시별 수치 요약 테이블 (평균 및 중위값) 추가
        st.write("#### 📊 도시별 가격 및 평점 요약 통계")
        summary_df = filtered_df.groupby('대상도시').agg({
            '성인가격': ['mean', 'median'],
            '평점': ['mean', 'median']
        })
        # 컬럼명 가독성 있게 변경
        summary_df.columns = ['가격(평균)', '가격(중위값)', '평점(평균)', '평점(중위값)']
        # 스타일 포맷팅 적용하여 출력
        st.dataframe(summary_df.style.format({
            '가격(평균)': '{:,.0f}원', 
            '가격(중위값)': '{:,.0f}원',
            '평점(평균)': '{:.2f}점', 
            '평점(중위값)': '{:.2f}점'
        }), use_container_width=True)
            
        render_analysis_box(
            "가격 및 평점 분포 해석",
            "박스플롯(Box Plot)을 활용하여 도시별 상품 가격 상하위 25% 구간 및 통계적 이상치를 추출함.",
            "싱가포르는 타 도시 대비 중위 가격대가 높게 형성되어 있으며, 고가 프리미엄 상품(마리나베이 등)으로 인한 상단 이상치가 뚜렷하게 관측됩니다. "
            "평점의 경우 다낭은 모객량이 많아 평점 편차가 큰 편이며, 나트랑은 전반적으로 높은 만족도를 유지하는 균질한 분포를 보입니다."
        )

    # 2. 쇼핑 영향도 및 키워드 마이닝
    with st.expander("🛍️ 2. 쇼핑 영향도 및 핵심 키워드 분석", expanded=False):
        col_shop1, col_shop2 = st.columns(2)
        
        with col_shop1:
            # 쇼핑 횟수 분포
            fig_shop_dist = px.histogram(filtered_df, x="쇼핑횟수", color="대상도시", barmode="group",
                                         title="도시별 쇼핑 횟수 분포",
                                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_shop_dist, use_container_width=True)
            
        with col_shop2:
            # [NEW] 산출 방식 선택 필터
            calc_mode = st.radio("📊 산출 방식 선택", ["인기/거래 가중", "고유 상품 기준"], 
                                 horizontal=True, help="인기 가중: 리뷰 빈도(시장 흐름) 반영 | 고유 상품: 중복 제외 상품 종류별 평균")
            mode_map = {"인기/거래 가중": "popularity", "고유 상품 기준": "unique"}
            
            # 쇼핑 횟수별 평균 가격
            shopping_impact = engine.get_shopping_impact_analysis(filtered_df, mode=mode_map[calc_mode])
            if not shopping_impact.empty:
                fig_shop_price = px.line(shopping_impact, x="쇼핑횟수", y="성인가격", 
                                        markers=True, title=f"쇼핑 횟수에 따른 가격 변화 ({calc_mode})",
                                        line_shape="spline", color_discrete_sequence=['#FF6B6B'])
                st.plotly_chart(fig_shop_price, use_container_width=True)
                
        st.divider()
        # [NEW] 키워드 마이닝 도시별 3개 열 배치
        st.markdown("#### 🔍 도시별 핵심 세일즈 키워드 마이닝 (TF-IDF)")
        kw_data = engine.get_keyword_mining_data(filtered_df)
        kw_col1, kw_col2, kw_col3 = st.columns(3)
        
        cities_list = ['다낭', '나트랑', '싱가포르']
        kw_cols = [kw_col1, kw_col2, kw_col3]
        
        for i, city in enumerate(cities_list):
            with kw_cols[i]:
                city_kw = kw_data[kw_data['대상도시'] == city].sort_values(by='가중치', ascending=True)
                if not city_kw.empty:
                    fig_city_kw = px.bar(city_kw, x="가중치", y="키워드", 
                                        orientation='h', title=f"[{city}] Top 10 키워드",
                                        color_discrete_sequence=[px.colors.qualitative.Vivid[i]])
                    st.plotly_chart(fig_city_kw, use_container_width=True)
            
        render_analysis_box(
            "쇼핑 및 키워드 전략 인사이트",
            "쇼핑 횟수와 상품 가격의 상관계수 분석 및 상세 상품명 기반 TF-IDF 가중치 연산 결과임.",
            "산출 방식에 따라 3회 쇼핑 상품의 가격이 다르게 나타날 수 있습니다(약 85만 원 vs 102만 원). "
            "'인기/거래 가중' 방식은 실제 시장의 실거래 흐름과 출발 횟수를 반영한 가중 평균이며, '고유 상품 기준'은 개별 상품 종류의 단가를 단순 평균한 수치입니다. "
            "데이터 분석 결과 저가형(3회 쇼핑) 패키지는 고유 상품 수는 적으나 공급량과 모객 기록이 압도적으로 많아 '실거래 가중' 시 시장 평균가를 대폭 하향 견인하는 특징을 보옵니다."
        )

    # 3. 클러스터링 및 브랜드 프리미엄
    with st.expander("🧬 3. 상품 클러스터링 및 브랜드 가치 분석", expanded=False):
        col_cluster, col_brand = st.columns(2)
        
        with col_cluster:
            # K-Means 클러스터링
            clustered_df = engine.get_clustered_segments(filtered_df)
            if 'Segment' in clustered_df.columns:
                # [FIX] 레이블 순서 보장을 위해 카테고리형으로 변환
                clustered_df['Segment'] = pd.Categorical(clustered_df['Segment'], categories=['실속형', '표준형', '고급형'])
                fig_cluster = px.scatter(clustered_df, x="성인가격", y="평점", color="Segment",
                                        size="쇼핑횟수", hover_name="대상도시",
                                        title="상품 속성 기반 3대 세그먼트 클러스터링",
                                        color_discrete_map={'실속형': '#FF6B6B', '표준형': '#4D96FF', '고급형': '#6BCB77'})
                st.plotly_chart(fig_cluster, use_container_width=True)
            else:
                st.info("클러스터링을 위한 데이터가 부족합니다.")
            
        with col_brand:
            # 호텔 브랜드 프리미엄
            brand_premium = engine.get_hotel_premium_analysis(filtered_df)
            if not brand_premium.empty:
                fig_brand = px.bar(brand_premium, x="유명브랜드여부", y="평균가격", color="유명브랜드여부",
                                  title="5성급 호텔 브랜드 포함 시 가격 프리미엄",
                                  text_auto='.0s', color_discrete_sequence=['#AEC6CF', '#FFB347'])
                st.plotly_chart(fig_brand, use_container_width=True)
            else:
                st.info("브랜드 분석 데이터가 없습니다.")
            
        render_analysis_box(
            "클러스터링 및 브랜드 시사점",
            "K-Means 군집 분석 엔진과 유명 호텔 브랜드 문자열 필터링을 통한 가격 프리미엄 산출 결과임.",
            "K-Means 군집 분석 결과 상품군은 크게 '실속형(저가/다쇼핑)', '표준형', '고급형(고가/노쇼핑)'의 3개 세그먼트로 뚜렷하게 구분됩니다. "
            "특히 호텔 브랜드 분석 시 글로벌 랜드마크(마리나베이 등)를 보강하고 패키지 상품군으로 한정하여 분석한 결과, 유명 브랜드 포함 상품이 일반 대비 뚜렷한 가격 프리미엄을 형성하고 있음을 통계적으로 입증했습니다."
        )




# ---------------------------------------------------------
# 탭 4: 리뷰 기반 데이터 인사이트 (REVIEW ANALYTICS)
# ---------------------------------------------------------
if selected_tab == "🔍 리뷰 및 전략 심층 분석":
    st.subheader("📝 리뷰 기반 고객 인사이트 및 리스크 탐지")
    
    # [KPI 요약] 상단 핵심 관리 지표 추가
    kpis = engine.get_kpi_indicators()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 평균 평점", f"{kpis['전체평균평점']:.2f}")
    m2.metric("총 리뷰수", f"{int(kpis['총리뷰건수']):,}건")
    m3.metric("평균 쇼핑 횟수", f"{kpis['평균쇼핑횟수']:.1f}회")
    m4.metric("분석 대상 도시", f"{filtered_df['대상도시'].nunique()}개")
    
    st.divider()
    
    # [Section 1] 도시별 리뷰 성과 및 통계 (1, 2, 10번)
    st.markdown("### 📊 1. 도시별 리뷰 성과 요약 (전체 마켓 기준)")
    # [FIX] 사이드바 필터(평점 4-5점 기본값)에 영향을 받지 않도록 전체 데이터를 기준으로 통계 산출
    rev_metrics = engine.get_city_review_metrics() # None 또는 engine.df 사용 효과
    rev_stats = engine.get_city_review_stats_table()
    
    col1, col2 = st.columns([2, 1.5])
    with col1:
        # [NEW] 이중 축(Dual-Axis) 차트 구현: 막대(리뷰수) + 꺾은선(평점)
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
        
        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 1. 막대 그래프 (리뷰수) - 왼쪽 Y축
        fig_dual.add_trace(
            go.Bar(x=rev_metrics['대상도시'], y=rev_metrics['리뷰수'], name="리뷰수(건)", 
                   marker_color='lightblue', opacity=0.7),
            secondary_y=False,
        )
        
        # 2. 꺾은선 그래프 (평균평점) - 오른쪽 Y축
        fig_dual.add_trace(
            go.Scatter(x=rev_metrics['대상도시'], y=rev_metrics['평균평점'], name="평균 평점",
                       line=dict(color='red', width=3), marker=dict(size=10)),
            secondary_y=True,
        )
        
        # 차트 레이아웃 설정
        fig_dual.update_layout(title_text="도시별 리뷰 화력 및 만족도 비교", hovermode="x unified")
        fig_dual.update_yaxes(title_text="리뷰 등록 수 (건)", secondary_y=False)
        fig_dual.update_yaxes(title_text="평균 평점 (0-5점)", range=[3.5, 5.0], secondary_y=True)
        
        st.plotly_chart(fig_dual, use_container_width=True)

    with col2:
        st.write("#### 도시별 리뷰 마스터 테이블 (저평점 비중 정밀 검증)")
        # 저평점비중(%)이 높은 순으로 하이라이트
        st.dataframe(rev_stats.style.background_gradient(subset=['저평점비중(%)'], cmap='OrRd')
                     .format({'평균평점': '{:.2f}', '저평점비중(%)': '{:.1f}%'}))
        st.caption("※ 저평점 비중: 전체 리뷰 중 1~3점 평점 데이터가 차지하는 비율(%)")

    render_analysis_box(
        "도시별 종합 성과 검증",
        "전체 리뷰 볼륨(막대)과 평균 평점(꺾은선)의 이중 축 비교, 그리고 하위 30% 저평점 발생의 집중도를 보여줍니다.",
        "다낭이 가장 높은 리뷰 화력을 보여주지만, 동시에 저평점 비중 통계에서도 높은 위험성을 내포하고 있습니다. 이는 방대한 물량 대비 품질 관문(QC)이 느슨함을 증명하므로, 볼륨에 취해 리스크를 전가하지 않도록 현지 랜드사별 밀착 관리가 시급합니다."
    )

    st.divider()

    # [Section 2] 트렌드 및 일정별 분석
    st.markdown("### 📈 2. 리뷰 등록 트렌드 및 일정성 분석")
    col3, col4 = st.columns(2)
    with col3:
        monthly_reviews = engine.get_monthly_review_volume(filtered_df)
        fig_monthly = px.line(monthly_reviews, x='월', y='리뷰수', title="월별 리뷰 등록 추이", markers=True)
        st.plotly_chart(fig_monthly, use_container_width=True)
    with col4:
        duration_reviews = engine.get_review_by_duration(filtered_df)
        fig_dur = px.pie(duration_reviews, values='리뷰수', names='일정', title="여행 일정별 리뷰 비중", hole=0.4)
        st.plotly_chart(fig_dur, use_container_width=True)

    render_analysis_box(
        "등록 트렌드 및 일정 비중 진단",
        "월별 리뷰 등록 포화도 및 3일~5일 투어 기간별 리뷰 분포를 정리했습니다.",
        "단기(3~4일) 일정이 압도적 비율을 차지하므로, 짧은 시간 내에 무리한 이동과 쇼핑을 압축시키는 관행이 성수기의 불만 폭주로 직결되는 현상을 경계해야 합니다."
    )

    st.divider()

    # [Section 3] 리뷰 감성 및 키워드 분석
    st.markdown("### 🔍 3. 리뷰 텍스트 감성 및 키워드 분석")
    st.write("#### 🏷️ 리뷰 요약 키워드 빈도 (상위 1~5순위)")
    tag_counts = engine.get_review_summary_ranking(filtered_df)
    st.bar_chart(tag_counts.set_index('키워드'))

    st.write("#### 🎭 긍정 vs 부정 핵심 키워드 비교 (TF-IDF)")
    sentiment_kw = engine.get_review_sentiment_keywords(filtered_df)
    sk_col1, sk_col2 = st.columns(2)
    with sk_col1:
        st.info("👍 **긍정 대표 키워드**")
        st.dataframe(sentiment_kw['positive'], hide_index=True, use_container_width=True)
    with sk_col2:
        st.error("👎 **부정 대표 키워드**")
        st.dataframe(sentiment_kw['negative'], hide_index=True, use_container_width=True)
        
    render_analysis_box(
        "텍스트 마이닝 감성 진단",
        "TF-IDF 알고리즘을 통해 긍정과 부정 리뷰에서 고빈도로 나타나는 특이 키워드들을 추출했습니다.",
        "긍정 부분엔 '가이드의 친절' 관련 단어가, 부정 부분엔 '쇼핑, 대기, 선택옵션'이 주를 이룹니다. 하나투어의 패키지 경쟁력이 현지 가이드 개인기에 종속된 구조를 탈피해야 함을 방증합니다."
    )

    st.divider()

    # [Section 4] 리뷰 길이 및 상관관계 분석
    st.markdown("### 📏 4. 리뷰 텍스트 길이 및 만족도 상관성")
    rev_len_df = engine.get_review_length_analysis(filtered_df)
    col_len1, col_len2 = st.columns(2)
    with col_len1:
        fig_len_dist = px.histogram(rev_len_df, x="리뷰길이", nbins=50, title="리뷰 텍스트 길이 분포",
                                    color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_len_dist, use_container_width=True)
    with col_len2:
        fig_len_corr = px.scatter(rev_len_df, x="리뷰길이", y="평점", color="평점",
                                  title="리뷰 길이 x 평점 상관관계", trendline="ols",
                                  color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_len_corr, use_container_width=True)

    render_analysis_box(
        "리뷰 길이와 만족도 관계 입증",
        "작성된 문장 길이(글자수)와 최종 부여된 평점 간의 선형 회귀 상관분석입니다.",
        "불만이 가득한 고객만이 긴 시간과 정성을 들여 분노 섞인 장문을 작성함이 정량적으로 증명되었습니다(반비례). 따라서 50자 이상 길이의 리뷰는 자동으로 긴급 CS 채널로 라우팅되어 보호 조치가 이뤄져야 합니다."
    )

    st.divider()

    # [Section 5] 쇼핑 및 다차원 상관분석
    st.markdown("### 🧩 5. 쇼핑 및 다차원 속성별 상관분석")
    corrs = engine.get_correlation_metrics(filtered_df)
    col_corr1, col_corr2 = st.columns(2)
    with col_corr1:
        fig_shop_corr = px.line(corrs['shop'], x="쇼핑횟수", y="평점", markers=True,
                                title="쇼핑 횟수 x 평균 평점 상관관계", line_shape="linear")
        st.plotly_chart(fig_shop_corr, use_container_width=True)
    with col_corr2:
        fig_city_box = px.box(corrs['city'], x="대상도시", y="평점", color="대상도시",
                              title="도시 x 평점 분포 상관관계 (Box Plot)")
        st.plotly_chart(fig_city_box, use_container_width=True)

    render_analysis_box(
        "쇼핑 강도 기반의 리스크 상관성",
        "상품의 쇼핑 횟수와 평점 간의 상관관계 추세선 및 평점 분포도입니다.",
        "쇼핑 횟수가 2~3회를 초과하는 시점부터 평점은 4.0 밑으로 곤두박질칩니다. 쇼핑이 단기 랜드 수익률은 끌어올릴지 언정 롱테일 관점의 브랜드 타격을 유발하는 부채임을 시사합니다."
    )

    st.divider()

    # [도시별 쇼핑횟수 기반 상품 공급량 분석 3열 배치] 시장 전체 흐름(버블맵)과 도시별 쇼핑 정책(공급량)을 비교합니다.
    # 섹션 6 타이틀 출력 (도시 및 쇼핑 아이콘 테마)
    st.markdown("### 🫧 6. 시장 포트폴리오 분석 및 도시별 쇼핑 횟수별 상품 공급량")
    
       
    # --- 제 1열: 시장 포트폴리오 거시 버블맵 (기존 유지) ---
    # 분석 엔진을 통해 도시별/쇼핑횟수별 리뷰 성과(버블 데이터) 수집
    bubble_data = engine.get_bubble_market_map(filtered_df)
    # 쇼핑횟수(X), 평점(Y), 리뷰수(Size)를 활용한 다차원 산점도 생성
    fig_bubble_market = px.scatter(bubble_data, x="쇼핑횟수", y="평균평점", size="리뷰수", color="대상도시",
                                   hover_name="대상도시", size_max=60, title="도시 x 쇼핑 x 리뷰 성과 매트릭스")
    st.plotly_chart(fig_bubble_market, use_container_width=True)

    # 분석 해석 박스 업데이트
    render_analysis_box(
        "도시/쇼핑 포트폴리오 거시맵",
        "전체 판매 상품들을 쇼핑 횟수(위험도)와 평점(건전성)의 X, Y 축에 띄워 규모를 가늠한 버블 차트입니다.",
        "지역별 평균 수익 지표(쇼핑)와 품질 지표(평점)를 버블 차트로 매핑하여 자원 배분의 우선순위를 결정함.",
        "우하단(고쇼핑, 저평점)에 침전된 세그먼트는 즉각적인 옵션 조율이나 단종 결정이 요구되며, 좌상단(노쇼핑, 고평점) 그룹으로 전략적 밀어주기(Promoting)가 진행되어야 합니다."
    )


    st.divider()

    # [Section 7] 부정 리뷰 심화 마이닝 (XAI)
    st.markdown("### 🧨 7. 부정 리뷰(Rating 3.0↓) 원인 심층 마이닝")
    neg_mining = engine.get_negative_cause_deep_mining(filtered_df)
    
    if neg_mining['total'] > 0:
        st.write(f"분석 대상: 평점 3.0 이하의 부정 리뷰 **{neg_mining['total']:,}건**")
        
        m_col1, m_col2 = st.columns([1.5, 1])
        with m_col1:
            fig_neg_cause = px.bar(neg_mining['data'], x="출현율(%)", y="원인분류", orientation='h',
                                   title="부정 리뷰 주요 원인 분류 (TF-IDF 출현율)",
                                   color="출현율(%)", color_continuous_scale="Reds")
            st.plotly_chart(fig_neg_cause, use_container_width=True)
        with m_col2:
            st.write("#### 📝 키워드별 분석 상세")
            st.table(neg_mining['data'].style.format({'출현율(%)': '{:.1f}%'}))
            
        render_analysis_box(
            "부정 원인 세분화 타격점",
            "평점 3.0 이하의 부정 리뷰들만 역추적하여 NLP 모델로 마이닝한 불만 원인입니다.",
            "주요 불만 원인이 '가이드 마찰'인지 '일정 스케줄'인지 즉각 파악 가능합니다. 랜드사의 품질 미달(가이드 불친절)이 치솟는 지역은 무조건적인 상품 리뉴얼보다 오퍼레이터 교체를 선행해야 효과적입니다."
        )
    
    st.divider()

    # [Section 8] 도시별 부정 키워드 히트맵
    st.markdown("### 🗺️ 8. 도시별 부정 핵심 키워드 히트맵")
    neg_kw_heatmap = engine.get_city_negative_keyword_heatmap(filtered_df)
    
    if not neg_kw_heatmap.empty:
        fig_neg_heat = px.imshow(neg_kw_heatmap, text_auto=True, aspect="auto",
                                 title="도시별 주요 불만(Pain Points) 키워드 빈도 현황",
                                 color_continuous_scale="Reds")
        st.plotly_chart(fig_neg_heat, use_container_width=True)
        
        render_analysis_box(
            "도시별 불만 지점 차별화 분석",
            "평점 3.0 이하의 부정 리뷰 내 주요 위험 키워드(가이드, 숙소, 강요 등)의 지역별 출현 빈도를 집계함.",
            "히트맵 분석 결과, **다낭**은 '가이드'와 '시간'에 대한 불만이 압도적으로 높게 나타나는 반면, "
            "**싱가포르**는 '비용'과 '숙소'의 퀄리티에 대한 민감도가 상대적으로 높습니다. "
            "**나트랑**은 '대기' 및 '일정' 빡빡함이 주된 원인으로 파악되므로, 지역별로 상이한 품질 관리 포인트(QC Point) 설정이 필요합니다."
        )
    else:
        st.success("해당 조건에서 분석할 부정 리뷰가 없습니다.")

    st.divider()

    # [Section 9] 인구통계학적 만족도 분석
    st.markdown("### 👥 9. 인구통계학적 심층 만족도 분석")
    col7, col8 = st.columns(2)
    with col7:
        demog = engine.get_review_demographics(filtered_df)
        fig_age = px.bar(demog['age'], x='연령대', y='리뷰수', color='평균평점',
                         title="연령대별 리뷰수 및 평균 평점", color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_age, use_container_width=True)
    with col8:
        fig_comp = px.bar(demog['companion'], x='동행', y='평균평점', color='평균평점',
                          title="동행 그룹별 평균 평점", color_continuous_scale='Viridis')
        st.plotly_chart(fig_comp, use_container_width=True)
    
    st.markdown("#### 🌡️ 연령대 x 동행별 평점 히트맵")
    heatmap_data = engine.get_rating_heatmap_data(filtered_df)
    fig_heat = px.imshow(heatmap_data, text_auto='.1f', aspect="auto",
                         title="연령대 및 동행 조합별 평균 평점 분포",
                         color_continuous_scale='YlOrRd')
    st.plotly_chart(fig_heat, use_container_width=True)

    render_analysis_box(
        "인구통계학적 세그먼트 공략점",
        "연령대 그룹 및 동행자 유무 교차에 따른 리뷰 체감 평점 스펙트럼 히트맵입니다.",
        "40대 이상 혹은 '가족/아이 동반' 그룹에서는 평점에 극히 보수적 성향을 보입니다. 가족 대상 상품은 빽빽한 관광 모듈을 포기하더라도 리조트 체류와 '자유/여유 타임'을 반드시 보장하는 기획이 설계 단계부터 적용되어야 합니다."
    )

    st.divider()

    # [Section 10] 포트폴리오 최적화 (Portfolio Optimization)
    st.markdown("### 🎯 10. 상위 레벨: 상품 포트폴리오 가치 분석")
    
    # 분석의 효율적인 시각화를 위해 화면을 3개의 열로 분할 (1.5 : 1 : 1 비율)
    b_col1, b_col2, b_col3 = st.columns([1.5, 1, 1])
    
    # --- 제 1열: 시장 포트폴리오 거시 버블맵 ---
    with b_col1:
        st.write("#### 🫧 수익성 vs 만족도 매트릭스")
        # 도시별 통합 요약 데이터를 가져옵니다.
        city_summary = engine.get_city_comparison_summary()
        # 쇼핑(수익)과 평점(품질)을 축으로 하고 리뷰수를 크기로 하는 버블 차트를 생성합니다.
        fig_bubble = px.scatter(city_summary, x="평균쇼핑횟수", y="평균평점", size="리뷰건수", color="대상도시",
                                hover_name="대상도시", title="도시별 포트폴리오 위치",
                                size_max=40)
        # 차트를 1열 내부에 표시합니다.
        st.plotly_chart(fig_bubble, use_container_width=True)

    # [데이터 분석 헬퍼 함수] 공급(상품수)과 수요(리뷰수)를 통합 집계합니다.
    @st.cache_data
    def get_supply_demand_stats(_df):
        """
        [Tab 4] 도시/쇼핑별 고유 상품 수(공급)와 리뷰 건수(수요)를 집계합니다.
        """
        temp_df = _df.copy()
        temp_df['쇼핑횟수'] = pd.to_numeric(temp_df['쇼핑횟수'], errors='coerce').fillna(0).astype(int)
        
        # 1. 수요(리뷰 건수) 집계
        demand = temp_df.groupby(['대상도시', '쇼핑횟수']).size().reset_index(name='리뷰건수')
        
        # 2. 공급(고유 상품 수) 집계 - 중복 제거된 상품코드 기준
        supply = temp_df.groupby(['대상도시', '쇼핑횟수'])['상품코드'].nunique().reset_index(name='상품수')
        
        # 3. 데이터 통합
        combined = pd.merge(demand, supply, on=['대상도시', '쇼핑횟수'], how='outer').fillna(0)
        return combined

    # 집계 데이터 준비
    comparison_stats = get_supply_demand_stats(filtered_df)

    # --- [10-A] 시장 반응 분석 (수요: 리뷰 건수) ---
    st.markdown("#### 📊 10-A. 시장 반응 분석 (수요: 리뷰 건수)")
    st.caption("실제 고객이 예약하고 리뷰를 남긴 '시장 화력' 지표입니다.")
    
    dem_col1, dem_col2 = st.columns([1, 2])
    
    with dem_col1:
        st.write("**리뷰 건수 통계표**")
        if not comparison_stats.empty:
            # 리뷰건수 기준 내림차순 정렬하여 표 표시
            st.dataframe(comparison_stats[['대상도시', '쇼핑횟수', '리뷰건수']].sort_values('리뷰건수', ascending=False), 
                         hide_index=True, use_container_width=True)
        else:
            st.info("데이터 부족")
            
    with dem_col2:
        if not comparison_stats.empty:
            # 리뷰 건수 시각화 (Sunburst 또는 Bar)
            fig_dem_bar = px.bar(comparison_stats, x='대상도시', y='리뷰건수', color='쇼핑횟수', 
                                title="도시별/쇼핑정책별 리뷰 발생 분포",
                                text_auto=True, color_continuous_scale=px.colors.sequential.OrRd)
            st.plotly_chart(fig_dem_bar, use_container_width=True)

    st.markdown("---")

    # --- [10-B] 상품 공급 분석 (공급: 상품 수) ---
    st.markdown("#### 📦 10-B. 상품 공급 분석 (공급: 상품 수)")
    st.caption("하나투어가 시장에 깔아놓은 '인벤토리(공급량)' 지표입니다.")
    
    sup_col1, sup_col2 = st.columns([1, 2])
    
    with sup_col1:
        st.write("**고유 상품 수 통계표**")
        if not comparison_stats.empty:
            # 상품수 기준 내림차순 정렬하여 표 표시
            st.dataframe(comparison_stats[['대상도시', '쇼핑횟수', '상품수']].sort_values('상품수', ascending=False), 
                         hide_index=True, use_container_width=True)
        else:
            st.info("데이터 부족")
            
    with sup_col2:
        if not comparison_stats.empty:
            # 상품 수 시각화
            fig_sup_bar = px.bar(comparison_stats, x='대상도시', y='상품수', color='쇼핑횟수', 
                                title="도시별/쇼핑정책별 고유 상품 공급 분포",
                                text_auto=True, color_continuous_scale=px.colors.sequential.Blues)
            st.plotly_chart(fig_sup_bar, use_container_width=True)

    # 통합 분석 해석 박스
    render_analysis_box(
        "수요와 공급의 불일치(Gap) 분석",
        "상단 '리뷰 건수(수요)'와 하단 '상품 수(공급)'를 수직으로 대조하여 시장의 효율성을 진단함.",
        "리뷰 건수가 폭발적인 쇼핑 횟수 구간(수요)과 실제 상품이 집중된 구간(공급)이 일치하지 않는다면, 이는 '고객이 원하는 상품'과 '회사가 팔고 싶은 상품' 사이의 간극을 의미합니다. "
        "예를 들어 싱가포르의 경우 상품 수 대비 리뷰가 압도적으로 높다면, 해당 도시의 공급량을 대폭 늘려야 하는 '기회 구간'임을 시사합니다."
    )

    # 분석 해석 박스 업데이트
    render_analysis_box(
        "도시별 쇼핑 정책 및 공급량 시사점",
        "각 도시별로 등록된 전체 상품 중 쇼핑이 포함된 비중과 그 절대량을 분석한 결과입니다.",
        "특정 도시에 '3회 쇼핑' 상품이 압도적으로 많다면 이는 저가 대량 모객 중심의 시장임을 의미합니다. 반면 '노쇼핑' 상품의 등록 비중이 높을수록 프리미엄 여행지로의 전환이 가속화되고 있음을 시사하므로, 버블맵의 수익성 지표와 연계하여 최적의 상품 믹스를 결정하십시오.\n\n"
        "싱가포르 노선은 높은 평점을 유지하고 있으나 수익률이 낮아 프리미엄 옵션 개발이 필요하며, 다낭은 수익성은 좋으나 리스크가 커 상품 리뉴얼이 시급한 상황임."
    )

    st.divider()

    # [Section 11] 세그먼트 전략 (Clustering)
    st.markdown("### 👥 11. 상위 레벨: AI 기반 상품 세그먼트 분류")
    segments = engine.get_clustered_segments()
    
    col_seg1, col_seg2 = st.columns([1, 2])
    with col_seg1:
        st.write("#### 군집별 특징 요약")
        summary = segments.groupby('Segment', observed=True).agg({
            '성인가격': 'mean',
            '평점': 'mean',
            '쇼핑횟수': 'mean'
        }).reset_index()
        st.dataframe(summary.style.highlight_max(axis=0, color='#AED9E0'))
    with col_seg2:
        if 'Segment' in segments.columns:
            segments['Segment'] = pd.Categorical(segments['Segment'], categories=['실속형', '표준형', '고급형'])
            fig_clus = px.scatter(segments, x="쇼핑횟수", y="평점", color="Segment", 
                                 title="K-Means 기반 상품 세그먼트 분포 (실속/표준/고급)",
                                 color_discrete_map={'실속형': '#FF6B6B', '표준형': '#4D96FF', '고급형': '#6BCB77'})
            st.plotly_chart(fig_clus, use_container_width=True)
        else:
            st.info("데이터가 부족하여 군집화가 수행되지 않았습니다.")
            
    render_analysis_box(
        "머신러닝 기반 고객 분류 근거",
        f"Scikit-learn의 K-Means 알고리즘을 사용하여 {len(engine.df)}건의 상품 객체를 독립된 {len(segments)}개의 세그먼트로 군집화함.",
        "Segment 0(가성비)은 쇼핑 위주 만족도가 낮고, Segment 2(프리미엄)는 노쇼핑 높은 만족도를 보임. 향후 마케팅 타겟팅 시 Segment 0 상품의 품질 개선이 브랜드 이미지 제고에 기여할 것임."
    )

# ---------------------------------------------------------
# 탭 5: 리스크 관리 (Gauges/Tables)
# ---------------------------------------------------------
if selected_tab == "🛡️ 리스크 모니터링":
    st.subheader("실시간 불만 관리 및 리스크 탐지")
    
    # [리스크 관리 섹션 2열 배치] 좌측에는 장기 지표, 우측에는 실시간 불만 리스트를 배치합니다.
    risk_col1, risk_col2 = st.columns(2)
    
    # 좌측 컬럼: 장기 모니터링 대시보드 지표
    with risk_col1:
        # 섹션 1 타이틀 출력 (돋보기 아이콘 사용)
        st.markdown("### 🔭 1. 모니터링 대시보드 지표")
        # 분석 엔진을 통해 장기 트래킹 지표 데이터 수집
        lt_metrics = engine.get_long_term_tracking_metrics(filtered_df)
        
        # 수집된 지표 데이터가 존재할 경우에만 렌더링
        if lt_metrics:
            # 내부 지표 가독성을 위해 다시 3개 열로 분할하여 메트릭 표시
            mt_col1, mt_col2, mt_col3 = st.columns(3)
            # 1번째 메트릭: 고위험 악성 리뷰 발생률 및 탐지 건수
            mt_col1.metric("🚨 고위험 발생률", f"{lt_metrics['high_risk_ratio']:.1f}%", f"{lt_metrics['high_risk_count']}건")
            # 2번째 메트릭: 프리미엄 옵션 전환율 지표
            mt_col2.metric("📈 프리미엄 전환", f"{lt_metrics['premium_conversion']}%")
            # 3번째 메트릭: 현재 가장 집중 대응이 필요한 페인포인트 분류
            mt_col3.metric("🎯 우선 대응", "가이드/일정")
            
            # 부정/불만 키워드 빈도를 보여주는 가로 막대 차트 생성
            fig_pain = px.bar(lt_metrics['pain_keywords'], x='출현횟수', y='키워드', orientation='h', 
                             title="부정/불만 키워드 트렌드", color='출현횟수', color_continuous_scale="Reds")
            # 생성된 차트를 대시보드에 표시
            st.plotly_chart(fig_pain, use_container_width=True)
            
            # 분석 결과에 대한 상세 해석 박스 렌더링
            render_analysis_box(
                "장기 트래킹 인사이트",
                "평점 3.0 이하 및 내용 50자 이상의 '분노의 리뷰'를 실시간 스캐닝한 결과입니다.",
                "고위험 리뷰 발생률이 주간 평균을 상회할 경우, 즉각적인 CS 개입 및 상품 품질 재검토가 필요함을 시사합니다."
            )

    # 우측 컬럼: 실시간 불만 모니터링 및 상세 리스트
    with risk_col2:
        # 섹션 4 타이틀 출력 (사이렌 아이콘 사용)
        st.markdown("### 🚨 실시간 불만 모니터링")
        
        # 전체 데이터에서 평점 2점 이하인 리뷰만 필터링하여 최신순으로 정렬
        risk_df = filtered_df[filtered_df['평점'] <= 2].sort_values(by='작성일', ascending=False)
        
        # 사용자에게 주의를 환기시키는 경고 메시지 표시
        st.warning("⚠️ 최근 접수된 위험 리뷰 리스트")
        # 위험 리뷰의 주요 정보를 테이블 형태로 표시 (상품명, 도시, 평점, 내용)
        st.dataframe(risk_df[['상품명', '대상도시', '평점', '내용']].head(10), use_container_width=True)
        
        # 실시간 불만 데이터에 대한 상세 분석 및 시사점 제공
        render_analysis_box(
            "리스크 감지 데이터 요약",
            f"최근 접수된 평점 2점 이하의 저만족도 리뷰 {len(risk_df)}건에 대한 실시간 필터링 결과입니다.",
            "가이드 불친절 및 숙소 위생 관련 키워드가 위험 리뷰의 대부분을 차지하고 있어, 현지 랜드사 품질 관리가 시급합니다."
        )

    st.divider()

    # [통합 분석 대시보드 2열 배치] 좌측에는 일회성 심층 보고서, 우측에는 고위험 상품 실시간 추적기를 배치합니다.
    main_col1, main_col2 = st.columns(2)
    
    # --- 좌측 컬럼: 📑 2. 일회성 보고서 지표 (One-off Report) ---
    with main_col1:
        # 섹션 2 타이틀 출력
        st.markdown("### 📑 2. 일회성 보고서 지표")
        # 분석 엔진을 통해 일회성 분석 리포트 데이터(가격 불일치, 일정 밀집도 등) 수집
        off_metrics = engine.get_one_off_report_metrics(filtered_df)
        
        # 수집된 리포트 지표 데이터가 존재할 경우 화면에 렌더링
        if off_metrics:
            # 1. 가격-쇼핑 기대 불일치 지수 분석
            st.write("#### 💸 가격-쇼핑 기대 불일치")
            # 데이터프레임 형식으로 불일치 상품 리스트 표시
            st.dataframe(off_metrics['price_mismatch'].style.format({'평점': '{:.2f}'}), use_container_width=True)
            # 지표에 대한 보충 설명
            st.caption("※ 상품 가격은 비싸지만 쇼핑 횟수가 많아 브랜드 가치를 훼손하는 상품군")
            
            # 2. 세그먼트별 일정 밀집도 타격량 분석
            st.write("#### 👨‍👩‍👧 세그먼트별 일정 피로도")
            # 일정 밀집도에 따른 만족도 하락을 보여주는 막대 차트 생성
            fig_density = px.bar(off_metrics['density_impact'], x='세그먼트', y='일정밀집도', color='평점', 
                                title="그룹별 일정 밀집도 타격량", color_continuous_scale="Viridis")
            # 생성된 차트를 대시보드에 렌더링
            st.plotly_chart(fig_density, use_container_width=True)
                
            # 시사점 해석 박스
            render_analysis_box(
                "구조적 의사결정 시사점",
                "가격을 상위 30% 수준으로 수용했음에도 쇼핑 3회 이상을 포함한 '기대 불일치' 상품을 식별함.",
                "아동 동반 그룹의 경우 일정 밀집도에 따른 만족도 하락폭이 크므로, 일정 20% 축소가 필수적임."
            )

    # --- 우측 컬럼: ⚠️ 3. 고위험 상품 리스크 관리 ---
    with main_col2:
        # 섹션 3 타이틀 출력
        st.markdown("### ⚠️ 3. 고위험 상품 리스크 관리")
        # 분석 엔진을 통해 고위험 상품 랭킹 데이터 수집
        risk_rank = engine.get_product_risk_ranking(filtered_df)
        
        # 1. 누적 저평점 비중 기반 TOP 10 요약 테이블 표시
        st.write("#### 📊 누적 저평점 비중 TOP 10")
        # 분석된 리스크 데이터가 비어있지 않은 경우에만 테이블을 렌더링함
        if not risk_rank.empty:
            # [수정] 엔진에서 반환하는 정확한 컬럼명인 '평균평점'과 '저평점비중(%)'을 사용하여 데이터프레임 출력
            st.dataframe(risk_rank[['상품명', '평균평점', '저평점비중(%)']].head(10), hide_index=True, use_container_width=True)
        else:
            # 데이터가 없는 경우 사용자에게 안내 메시지 표시
            st.info("현재 분석된 고위험 상품이 없습니다.")

        # 2. 특정 상품 상세 조사 및 일정 대조 도구
        st.write("#### 🔍 특정 상품 일정 정밀 역추적")
        # 조사를 원하는 상품 코드를 선택할 수 있는 셀렉트박스 생성
        selected_risk_code = st.selectbox(
            "조사할 고위험 상품 코드를 선택하세요", 
            options=risk_rank['상품코드'].tolist() if not risk_rank.empty else ["데이터 없음"],
            key="risk_search_box" # 유니크 키 설정
        )
        
        # 상품이 선택되었을 경우 상세 정보 표시
        if selected_risk_code != "데이터 없음":
            st.write(f"**📅 '{selected_risk_code}' 상세 일정 및 리뷰 대조**")
            # 해당 상품의 상세 일정 데이터 수집
            iti_data = engine.get_review_with_itinerary(selected_risk_code)
            if not iti_data.empty:
                # 상세 일정 및 내용 테이블 출력
                st.dataframe(
                    iti_data[['상세일정', '상세내용' if '상세내용' in iti_data.columns else '대표상품코드']].head(10),
                    use_container_width=True
                )
            else:
                st.info("해당 상품의 상세 일정 데이터가 존재하지 않습니다.")



# ---------------------------------------------------------
# 탭 6: 맞춤 추천 위저드 (Area 3)
# ---------------------------------------------------------
if selected_tab == "✨ 맞춤 추천 위저드":
    st.header("✨ 맞춤 상품 추천 위저드")
    
    with st.form("recommendation_form"):
        st.write("고객님의 여행 취향과 조건을 입력해주시면, 데이터 기반으로 최상의 상품을 제안해 드립니다. 🪄")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            budget = st.slider("1인당 최대 예산 (만원)", min_value=30, max_value=300, value=100, step=10)
        with col_w2:
            pref = st.radio("여행 시 가장 중요하게 생각하는 요소는?", 
                            ["가성비 투어 (다쇼핑 무관)", "쇼핑 없는 힐링 (노쇼핑)", "안전한 가족 여행 (평점 최우선)"])
        
        submitted = st.form_submit_button("맞춤 상품 추천받기 🚀")
        
    if submitted:
        recs = engine.get_persona_recommendations(max_budget=budget * 10000, preference=pref, df=filtered_df)
        
        if not recs.empty:
            st.success(f"🎉 조건에 완벽히 부합하는 최우수 추천 상품 {len(recs)}개를 찾았습니다!")
            for idx, row in recs.iterrows():
                rank_emoji = ["🥇", "🥈", "🥉"][idx] if idx < 3 else "🏅"
                with st.container():
                    st.markdown(f"#### {rank_emoji} [{row['대상도시']}] {row['상품명']}")
                    st.markdown(f"> **상품코드**: `{row['상품코드']}` | **상품군**: `{row['상품군']}`")
                    st.markdown(f"> ⭐ **신뢰 점수**: {row['추천점수']:.1f}점 (실제 평점 {row['평점']:.2f}점, 누적 리뷰 {row['리뷰ID']}건)")
                    st.markdown(f"> 💸 **예상 경비**: {int(row['성인가격']):,}원 | 🛍️ **안내 쇼핑**: {row['쇼핑횟수']:.0f}회")
                    st.divider()
        else:
            st.error("앗, 너무 까다로운 조건인가 봐요! 😥 예산을 조금 높이거나 다른 도시를 선택해 보시겠어요?")

st.markdown("---")
st.markdown("© 2026 HanaTour Travel Intelligence Center | 초보 분석가를 위한 데이터 분석 캠프")
