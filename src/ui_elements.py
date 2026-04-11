import streamlit as st
from typing import Optional, List, Any
# 하나투어 대시보드 색상 테마 정의 (Pastel Blue & Sand Beige)
PRIMARY_COLOR = "#AED9E0"  # 부드러운 하늘색 (휴양지 느낌)
SECONDARY_COLOR = "#F5E6BE" # 따뜻한 모래색 (해변 느낌)
TEXT_COLOR = "#2C3E50"      # 가시성 높은 다크 그린/블루
CARD_BG = "#FFFFFF"         # 카드 배경색 (Clean White)
def apply_custom_style():
    """
    모던한 카드형 UI와 색상 테마를 반영한 전용 CSS를 적용합니다.
    Streamlit의 기본 레이아웃을 하나투어 브랜드 맞춤형으로 변경합니다.
    """
    st.markdown(f"""
        <style>
            /* 메인 배경색 설정 */
            .main {{
                background-color: #F9FBFF;
                color: {TEXT_COLOR};
            }}
            /* 카드 스타일 정의 */
            .metric-card {{
                background-color: {CARD_BG};
                padding: 1.5rem;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border-left: 5px solid {PRIMARY_COLOR};
                margin-bottom: 1rem;
            }}
            /* 데이터 근거 및 해석 레이블 스타일 */
            .data-basis-label {{
                font-weight: bold;
                color: #5D6D7E;
                font-size: 0.85rem;
                margin-top: 0.5rem;
            }}
            .interpretation-label {{
                font-weight: bold;
                color: #1E8449;
                font-size: 0.85rem;
                margin-top: 0.3rem;
            }}
            /* 탭 텍스트 스타일 */
            .stTabs [data-baseweb="tab"] {{
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
        </style>
    """, unsafe_allow_html=True)
def render_analysis_box(title: str, basis: str, interpretation: str, extra: Optional[str] = None):
    """
    기획서에 명시된 '데이터 근거(Data Basis)'와 '분석 결과(Interpretation)'를
    하단에 포함하는 분석 전용 박스를 생성합니다.
    
    Args:
        title (str): 분석의 제목
        basis (str): 데이터 근거 (데이터 소스 및 수치)
        interpretation (str): 첫 번째 결과 해석 (비즈니스 인사이트)
        extra (str, optional): 추가적인 상세 분석 결과 또는 인사이트
    """
    # 추가 해석이 있는 경우 기존 해석 뒤에 개행 후 붙여줍니다.
    full_interpretation = interpretation
    if extra:
        full_interpretation += f"\n\n{extra}"

    st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin-top:0;">📊 {title}</h4>
            <div class="data-basis-label">📍 데이터 근거 (Data Basis)</div>
            <p style="font-size: 0.9rem; color: #5D6D7E; line-height: 1.5; white-space: pre-wrap;">{basis}</p>
            <div class="interpretation-label">💡 그래프 해석 (Interpretation)</div>
            <p style="font-size: 0.9rem; color: #2C3E50; line-height: 1.5; font-style: italic; white-space: pre-wrap;">{full_interpretation}</p>
        </div>
    """, unsafe_allow_html=True)
def render_xai_card(label: str, value: Any, delta: Optional[str] = None):
    """
    핵심 KPI를 표시하는 인터랙티브 메트릭 카드를 생성합니다.
    """
    with st.container():
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label=label, value=value, delta=delta)
        st.markdown('</div>', unsafe_allow_html=True)
def display_sidebar_filters(cities: List[str]):
    """
    대시보드 좌측에 필터 시스템을 구축합니다.
    지역, 기간, 평점 수준 등을 선택할 수 있습니다.
    """
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/ko/c/c5/Hanatour_logo.png", width=150)
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 분석 필터")
    
    selected_city = st.sidebar.multiselect("대상 지역 선택", options=cities, default=cities)
    selected_period = st.sidebar.slider("분석 기간(월)", 1, 12, (1, 12))
    min_rating = st.sidebar.selectbox("최소 만족도(평점)", options=[1, 2, 3, 4, 5], index=3)
    
    return selected_city, selected_period, min_rating
