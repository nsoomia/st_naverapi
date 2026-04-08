import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

# 1. 환경 설정 및 데이터 로드 영역
# 초보 분석가를 위해 모든 과정에 상세한 주석을 추가합니다.

# 이미지 저장 폴더 생성 (보고서용 시각화 결과물)
os.makedirs('images', exist_ok=True)

# 2. 한글 폰트 환경 설정 및 캐시 삭제 (최종 강제 해결책)
import matplotlib.font_manager as fm
import shutil
import matplotlib

# 매번 실행 시 폰트 캐시를 삭제하여 인식 오류를 방지합니다.
try:
    shutil.rmtree(matplotlib.get_cachedir(), ignore_errors=True)
except:
    pass

def get_korean_font():
    """
    시스템 가용 폰트 중 가장 적합한 한글 폰트 객체를 반환합니다.
    """
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    target_keywords = ['Malgun Gothic', 'NanumGothic', 'HYGothic', 'Gothic', 'Dotum', 'Gulim']
    
    for keyword in target_keywords:
        matches = [f for f in available_fonts if keyword.lower() in f.lower()]
        if matches:
            font_name = matches[0]
            print(f"폰트 선택: {font_name}")
            return font_name
    return 'Malgun Gothic' # 기본값

# 전역 설정
SELECTED_FONT = get_korean_font()
plt.rcParams['font.family'] = SELECTED_FONT
plt.rcParams['axes.unicode_minus'] = False

def apply_font(title=None, xlabel=None, ylabel=None):
    """
    현재 활성화된 axes의 모든 텍스트 요소(제목, 축, 범례 등)에 폰트를 전수 적용합니다. 
    """
    ax = plt.gca()
    if title: ax.set_title(title, fontfamily=SELECTED_FONT, fontsize=14, fontweight='bold')
    if xlabel: ax.set_xlabel(xlabel, fontfamily=SELECTED_FONT)
    if ylabel: ax.set_ylabel(ylabel, fontfamily=SELECTED_FONT)
    
    # 1. 축 눈금 폰트
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(SELECTED_FONT)
    
    # 2. 범례 폰트 (Seaborn 등에서 자동 생성된 범례 포함)
    legend = ax.get_legend()
    if legend:
        for text in legend.get_texts():
            text.set_fontfamily(SELECTED_FONT)
        if legend.get_title():
            legend.get_title().set_fontfamily(SELECTED_FONT)
            
    # 3. 기타 일반 텍스트 객체들
    for text in ax.texts:
        text.set_fontfamily(SELECTED_FONT)

# 데이터 파일 경로 설정
DATA_DIR = 'data'
REVIEW_FILE = os.path.join(DATA_DIR, 'hanatour_reviews.csv')
AVIATION_FILE = os.path.join(DATA_DIR, 'filtered_aviation_performance.csv')
DANANG_MASTER = os.path.join(DATA_DIR, 'hanatour_danang_integrated.csv')
NHATRANG_MASTER = os.path.join(DATA_DIR, 'hanatour_nhatrang_integrated.csv')
SINGAPORE_MASTER = os.path.join(DATA_DIR, 'hanatour_singapore_integrated.csv')

def load_data():
    """
    분석에 필요한 모든 CSV 파일을 로드합니다.
    한국어 깨짐 방지를 위해 utf-8-sig 인코딩을 사용합니다.
    """
    reviews = pd.read_csv(REVIEW_FILE, encoding='utf-8-sig')
    aviation = pd.read_csv(AVIATION_FILE, encoding='utf-8-sig')
    # 컬럼명 공백 제거
    aviation.columns = aviation.columns.str.strip()
    
    # 도시별 상품 마스터 데이터 로드 (쇼핑횟수 정보 포함)
    danang = pd.read_csv(DANANG_MASTER, encoding='utf-8-sig')
    danang.columns = danang.columns.str.strip()
    nhatrang = pd.read_csv(NHATRANG_MASTER, encoding='utf-8-sig')
    nhatrang.columns = nhatrang.columns.str.strip()
    singapore = pd.read_csv(SINGAPORE_MASTER, encoding='utf-8-sig')
    singapore.columns = singapore.columns.str.strip()
    
    return reviews, aviation, danang, nhatrang, singapore

def preprocess_data(reviews, aviation, danang, nhatrang, singapore):
    """
    데이터 전처리 및 병합을 수행합니다.
    - 파생변수 생성: 리뷰길이, 편당승객, 평점대 등
    - 데이터 병합: 리뷰 + 상품마스터 + 항공통계
    """
    
    # 가) 리뷰 데이터 전처리
    # 작성일로부터 연도, 월 정보 추출 (항공 데이터와 병합 목적)
    reviews['작성일'] = pd.to_datetime(reviews['작성일'], errors='coerce')
    reviews['연도'] = reviews['작성일'].dt.year
    reviews['월'] = reviews['작성일'].dt.month
    
    # 리뷰 내용이 비어있는 경우 빈 문자열로 처리
    reviews['내용'] = reviews['내용'].fillna('')
    # 리뷰 길이 계산
    reviews['리뷰길이'] = reviews['내용'].str.len().astype(int)
    
    # 평점대 구분 (저평점: 1~3, 고평점: 4~5)
    reviews['평점대'] = reviews['평점'].apply(lambda x: '저평점(1-3)' if x <= 3 else '고평점(4-5)')
    
    # 나) 상품 마스터 통합 (다낭, 나트랑, 싱가포르 통합)
    # 대표상품코드와 쇼핑횟수를 연결하기 위해 평균값 산출 (같은 대표코드 내 쇼핑횟수는 동일함)
    cols = ['대표상품코드', '쇼핑횟수']
    master_combined = pd.concat([
        danang[cols],
        nhatrang[cols],
        singapore[cols]
    ], axis=0).drop_duplicates()
    
    # 대표상품코드별 평균 쇼핑횟수 (중복 제거용)
    master_avg = master_combined.groupby('대표상품코드')['쇼핑횟수'].mean().reset_index()
    
    # 리뷰 데이터와 상품마스터 병합 (상품코드 기준)
    df = pd.merge(reviews, master_avg, left_on='상품코드', right_on='대표상품코드', how='left')
    
    # 다) 항공 데이터 전처리
    # 도시별 IATA 코드 매핑
    city_map = {'다낭': 'DAD', '나트랑': 'CXR', '싱가포르': 'SIN'}
    df['IATA'] = df['대상도시'].map(city_map)
    
    # 항공 데이터에서 편당 승객 수 계산 (유임승객 / 운항편수)
    # 0으로 나누기 방지
    aviation['운항(편)'] = aviation['운항(편)'].replace(0, np.nan)
    aviation['편당승객'] = aviation['유임승객(명)'] / aviation['운항(편)']
    # 결측치 처리
    aviation['편당승객'] = aviation['편당승객'].fillna(0)
    
    # 항공 데이터 요약 (월별, 공항별 평균 편당승객 - 연도 무관하게 트렌드 반영)
    # 2026년 리뷰에 대응하기 위해 모든 연도의 월별 평균 사용
    aviation_avg = aviation.groupby(['월', '경유지공항'])['편당승객'].mean().reset_index()
    
    # 최종 데이터 병합 (월, IATA 기준)
    df = pd.merge(df, aviation_avg, left_on=['월', 'IATA'], right_on=['월', '경유지공항'], how='left')
    
    return df

def generate_visualizations(df):
    """
    분석.md의 가설 검증을 위한 10종 이상의 시각화를 생성합니다.
    """
    sns.set_style('whitegrid')
    
    # 1. 단변량 - 평점 분포
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='평점', palette='viridis')
    apply_font(title='전체 평점 분포 (고객 만족도 현황)', xlabel='평점', ylabel='리뷰 수')
    plt.savefig('images/01_rating_dist_v12.png')
    plt.close()
    
    # 2. 단변량 - 도시별 리뷰 비중 (파이 차트는 텍스트 객체 직접 제어 필요)
    plt.figure(figsize=(10, 6))
    counts = df['대상도시'].value_counts()
    patches, texts, autotexts = plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    
    # 파이 차트의 레이블과 퍼센트 글씨에 폰트 강제 적용
    for t in texts + autotexts:
        t.set_fontfamily(SELECTED_FONT)
        t.set_fontsize(11)

    apply_font(title='대상 도시별 리뷰 비중')
    plt.savefig('images/02_city_pie_v12.png')
    plt.close()
    
    # 3. 이변량 - 쇼핑 횟수 vs 평점 (사용자 요청: 박스플롯)
    plt.figure(figsize=(12, 6))
    if not df['쇼핑횟수'].dropna().empty:
        # 박스플롯과 스트립플롯을 함께 사용하여 분포와 개별 데이터 밀도를 동시에 표현 (프리미엄 디자인)
        sns.boxplot(data=df, x='쇼핑횟수', y='평점', palette='Pastel1', showfliers=False)
        sns.stripplot(data=df, x='쇼핑횟수', y='평점', color='black', alpha=0.1, jitter=True)
        apply_font(title='쇼핑 횟수별 평점 분포 (Boxplot + Density)', xlabel='쇼핑 횟수', ylabel='평점')
        plt.savefig('images/03_shopping_vs_rating_v12.png')
    plt.close()
    
    # 4. 이변량 - 항공 혼잡도(편당 승객) vs 평점
    plt.figure(figsize=(12, 6))
    if not df['편당승객'].dropna().empty and df['편당승객'].nunique() > 1:
        try:
            df['혼잡도구간'] = pd.qcut(df['편당승객'], q=5, labels=['매우저조', '저조', '보통', '혼잡', '매우혼잡'], duplicates='drop')
            sns.barplot(data=df, x='혼잡도구간', y='평점', palette='RdYlGn')
            apply_font(title='항공 혼잡도(편당 승객)에 따른 평균 평점', xlabel='혼잡도 구간', ylabel='평균 평점')
            plt.savefig('images/04_congestion_vs_rating_v12.png')
        except Exception as e:
            print(f"혼잡도 구간화 실패: {e}")
    plt.close()
    
    # 5. 이변량 - 리뷰 길이 vs 평점
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x='리뷰길이', y='평점', alpha=0.1, color='blue')
    apply_font(title='리뷰 길이와 평점의 상관관계', xlabel='리뷰 글자 수', ylabel='평점')
    plt.savefig('images/05_length_vs_rating_v12.png')
    plt.close()
    
    # 6. 다변량 - 도시별 쇼핑 횟수당 평균 평점 (보고서 내 표로 대체됨 - 시각적 오류 방지를 위해 제거)
    pass
    
    # 7. 다변량 - 동행 유형별 평점
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df, x='동행', y='평점', hue='평점대', palette='muted')
    plt.xticks(rotation=45)
    apply_font(title='동행 유형별 평점 거동', xlabel='동행자 유형', ylabel='평등 만족도')
    # 범례 폰트 강제 재적용
    leg = plt.legend(prop={'family': SELECTED_FONT}, title='평점대')
    if leg:
        for t in leg.get_texts(): t.set_fontfamily(SELECTED_FONT)
        if leg.get_title(): leg.get_title().set_fontfamily(SELECTED_FONT)
    plt.savefig('images/07_companion_rating_v12.png')
    plt.close()
    
    # 8. 시계열 - 월별 평균 평점 추이
    plt.figure(figsize=(14, 6))
    if not df['월'].dropna().empty:
        sns.lineplot(data=df, x='월', y='평점', hue='대상도시', marker='o')
        plt.xticks(range(1, 13))
        apply_font(title='도시별 월별 평균 평점 추이 (시즌별 만족도)', xlabel='월', ylabel='평균 평점')
        # 범례 폰트 강제 재적용
        leg = plt.legend(prop={'family': SELECTED_FONT}, title='대상도시')
        if leg:
            for t in leg.get_texts(): t.set_fontfamily(SELECTED_FONT)
            if leg.get_title(): leg.get_title().set_fontfamily(SELECTED_FONT)
        plt.savefig('images/08_monthly_trend_v12.png')
    plt.close()
    
    # 9. 텍스트 분석 - 저평점 리뷰 핵심 키워드
    try:
        negative_reviews = df[df['평점대'] == '저평점(1-3)']['내용']
        negative_reviews = negative_reviews[negative_reviews.str.strip().str.len() > 2]
        
        if len(negative_reviews) > 5:
            vectorizer = TfidfVectorizer(max_features=20, stop_words=['진짜', '너무', '정말', '것', '수', '데', '그냥', '좀'])
            tfidf_matrix = vectorizer.fit_transform(negative_reviews)
            words = vectorizer.get_feature_names_out()
            sums = tfidf_matrix.sum(axis=0)
            
            data_list = []
            for col, word in enumerate(words):
                data_list.append((word, sums[0, col]))
            
            ranking = pd.DataFrame(data_list, columns=['words', 'tfidf']).sort_values('tfidf', ascending=False)
            
            if not ranking.empty:
                plt.figure(figsize=(12, 8))
                sns.barplot(data=ranking, x='tfidf', y='words', palette='Reds_r')
                apply_font(title='저평점(1-3점) 리뷰 주요 불만 키워드 (TF-IDF)', xlabel='중요도(TF-IDF)', ylabel='불만 키워드')
                plt.savefig('images/09_negative_keywords_v12.png')
                plt.close()
    except Exception as e:
        print(f"텍스트 분석 시각화 중 에러 발생: {e}")
    
    # 10. 상관관계 분석 - 주요 수치형 변수 간의 관계
    plt.figure(figsize=(10, 8))
    numeric_df = df[['평점', '리뷰길이', '쇼핑횟수', '월']].dropna()
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    apply_font(title='주요 변수 간 상관관계 계수')
    plt.savefig('images/10_correlation_v12.png')
    plt.close()
    
    # 11. 추가 시각화 - 요일별 평균 평점
    plt.figure(figsize=(10, 6))
    df['요일'] = df['작성일'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sns.barplot(data=df, x='요일', y='평점', order=day_order, palette='spring')
    apply_font(title='리뷰 작성 요일별 평균 평점', xlabel='요일', ylabel='평균 평점')
    plt.savefig('images/11_day_of_week_rating_v12.png')
    plt.close()
    
    # 12. 추가 시각화 - 항공사별 평균 평점
    plt.figure(figsize=(12, 6))
    if '항공사' in df.columns:
        # 상위 10개 항공사만 필터링
        top_airlines = df['항공사'].value_counts().nlargest(10).index
        sns.barplot(data=df[df['항공사'].isin(top_airlines)], x='항공사', y='평점', palette='tab10')
        plt.title('주요 이용 항공사별 평균 평점')
        plt.xticks(rotation=45)
        plt.savefig('images/12_airline_rating.png')
    plt.close()

def main():
    print("데이터 로딩 중...")
    reviews, aviation, danang, nhatrang, singapore = load_data()
    
    print("데이터 전처리 및 병합 중...")
    df = preprocess_data(reviews, aviation, danang, nhatrang, singapore)
    
    # 전처리된 데이터 중간 저장 (보고서 작성 시 참조 가능)
    df.to_csv('data/preprocessed_eda_data.csv', index=False, encoding='utf-8-sig')
    
    print("시각화 생성 중 (10종)...")
    generate_visualizations(df)
    
    print("\n[EDA 완료]")
    print(f"총 분석 데이터 건수: {len(df)}건")
    print(f"시각화 이미지가 'images/' 폴더에 저장되었습니다.")

if __name__ == "__main__":
    main()
