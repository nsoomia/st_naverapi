import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from matplotlib import font_manager, rc

def setup_korean_font():
    """
    한글 폰트 설정을 위한 함수입니다.
    Windows 환경의 맑은 고딕(Malgun Gothic)을 기본으로 설정합니다.
    """
    # 한글 폰트 경로 설정 (맑은 고딕)
    font_path = "C:/Windows/Fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)
    # 마이너스 기호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
    print(f"한글 폰트 설정 완료: {font_name}")

def analyze_reviews(file_path, output_dir):
    """
    리뷰 데이터를 분석하고 10가지 시각화 지표를 생성합니다.
    
    Args:
        file_path (str): 리뷰 CSV 파일 경로
        output_dir (str): 결과 이미지를 저장할 디렉토리
    """
    # 디렉토리가 없으면 생성합니다.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"디렉토리 생성: {output_dir}")

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # 작성일 컬럼을 datetime으로 변환 (2026.03.19 형식 처리)
    df['작성일'] = pd.to_datetime(df['작성일'], format='%Y.%m.%d', errors='coerce')
    df['작성월'] = df['작성일'].dt.month

    # 1. 대상 도시별 리뷰 수 (막대 그래프)
    plt.figure(figsize=(10, 6))
    city_counts = df['대상도시'].value_counts()
    sns.barplot(x=city_counts.index, y=city_counts.values, palette='viridis')
    plt.title('대상 도시별 리뷰 수 (데이터 규모 확인)')
    plt.xlabel('도시')
    plt.ylabel('리뷰 수')
    for i, v in enumerate(city_counts.values):
        plt.text(i, v + 50, str(v), ha='center')
    plt.savefig(os.path.join(output_dir, 'review_1_city_counts.png'))
    plt.close()

    # 2. 상품형태별 비중 (파이 차트)
    plt.figure(figsize=(8, 8))
    product_counts = df['상품형태'].value_counts()
    plt.pie(product_counts, labels=product_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('상품형태별 비중 (Product Type Distribution)')
    plt.savefig(os.path.join(output_dir, 'review_2_product_type.png'))
    plt.close()

    # 3. 동행자별 분포 (막대 차트)
    plt.figure(figsize=(12, 6))
    companion_counts = df['동행'].value_counts()
    sns.barplot(x=companion_counts.index, y=companion_counts.values, palette='magma')
    plt.title('동행자별 분포 (Companion Distribution)')
    plt.xticks(rotation=45)
    plt.xlabel('동행자 유형')
    plt.ylabel('리뷰 수')
    plt.savefig(os.path.join(output_dir, 'review_3_companion_dist.png'))
    plt.close()

    # 4. 연령대별 리뷰 분포 (막대 그래프)
    plt.figure(figsize=(10, 6))
    # 연령대 데이터가 숫자로 되어 있을 수 있으므로 처리
    df['연령대_str'] = df['연령대'].astype(str) + '대'
    age_counts = df['연령대_str'].value_counts().sort_index()
    sns.barplot(x=age_counts.index, y=age_counts.values, palette='coolwarm')
    plt.title('연령대별 리뷰 분포 (Age Group Distribution)')
    plt.xlabel('연령대')
    plt.ylabel('리뷰 수')
    plt.savefig(os.path.join(output_dir, 'review_4_age_dist.png'))
    plt.close()

    # 5. 평점 분포 (막대 그래프)
    plt.figure(figsize=(10, 6))
    rating_counts = df['평점'].value_counts().sort_index()
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette='YlGnBu')
    plt.title('평점 분포 (Rating Distribution)')
    plt.xlabel('평점')
    plt.ylabel('리뷰 수')
    plt.savefig(os.path.join(output_dir, 'review_5_rating_dist.png'))
    plt.close()

    # 6. 도시별 평균 평점 (막대 그래프)
    plt.figure(figsize=(10, 6))
    city_avg_rating = df.groupby('대상도시')['평점'].mean().sort_values(ascending=False)
    sns.barplot(x=city_avg_rating.index, y=city_avg_rating.values, palette='Spectral')
    plt.title('도시별 평균 평점 (Avg Rating by City)')
    plt.ylim(4.0, 5.0)
    plt.xlabel('도시')
    plt.ylabel('평균 평점')
    for i, v in enumerate(city_avg_rating.values):
        plt.text(i, v + 0.01, f"{v:.2f}", ha='center')
    plt.savefig(os.path.join(output_dir, 'review_6_city_avg_rating.png'))
    plt.close()

    # 7. 핵심 키워드 분석 (TF-IDF 기반)
    # 간단한 TF-IDF 분석 (내용 컬럼 사용)
    # 한글 불용어 처리가 필요하지만 여기서는 기본적인 구현만 함
    review_content = df['내용'].dropna().astype(str)
    tfidf = TfidfVectorizer(max_features=20, stop_words=None) # 한글 형태소 분석기 없이 띄어쓰기 기준으로 처리
    tfidf_matrix = tfidf.fit_transform(review_content)
    
    # 가점 합산
    word_scores = tfidf_matrix.sum(axis=0).A1
    words = tfidf.get_feature_names_out()
    keyword_df = pd.DataFrame({'Word': words, 'Score': word_scores}).sort_values(by='Score', ascending=False)

    plt.figure(figsize=(12, 8))
    sns.barplot(x='Score', y='Word', data=keyword_df, palette='rocket')
    plt.title('핵심 키워드 분석 (Top Keywords - TF-IDF)')
    plt.xlabel('TF-IDF 점수 합계')
    plt.ylabel('키워드')
    plt.savefig(os.path.join(output_dir, 'review_7_top_keywords.png'))
    plt.close()

    # 8. 동행별 평균 평점 (막대 그래프)
    plt.figure(figsize=(12, 6))
    companion_avg_rating = df.groupby('동행')['평점'].mean().sort_values(ascending=False)
    sns.barplot(x=companion_avg_rating.index, y=companion_avg_rating.values, palette='autumn')
    plt.title('동행별 평균 평점 (Avg Rating by Companion)')
    plt.xticks(rotation=45)
    plt.ylim(4.5, 5.0)
    plt.xlabel('동행자 유형')
    plt.ylabel('평균 평점')
    plt.savefig(os.path.join(output_dir, 'review_8_companion_avg_rating.png'))
    plt.close()

    # 9. 월별 리뷰 작성 추이 (시계열 라인 차트)
    plt.figure(figsize=(12, 6))
    monthly_trend = df['작성월'].value_counts().sort_index()
    sns.lineplot(x=monthly_trend.index, y=monthly_trend.values, marker='o', linewidth=2, color='green')
    plt.title('월별 리뷰 작성 추이 (Monthly Review Trend)')
    plt.xlabel('월')
    plt.ylabel('리뷰 수')
    plt.xticks(range(1, 13))
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_dir, 'review_9_monthly_trend.png'))
    plt.close()

    # 10. 연령대별 평균 평점 (막대 그래프)
    plt.figure(figsize=(10, 6))
    age_avg_rating = df.groupby('연령대_str')['평점'].mean().sort_index()
    sns.barplot(x=age_avg_rating.index, y=age_avg_rating.values, palette='cubehelix')
    plt.title('연령대별 평균 평점 (Avg Rating by Age Group)')
    plt.ylim(4.5, 5.0)
    plt.xlabel('연령대')
    plt.ylabel('평균 평점')
    for i, v in enumerate(age_avg_rating.values):
        plt.text(i, v + 0.01, f"{v:.2f}", ha='center')
    plt.savefig(os.path.join(output_dir, 'review_10_age_avg_rating.png'))
    plt.close()

    print("모든 시각화 이미지 생성 완료.")

if __name__ == "__main__":
    # 폰트 설정
    setup_korean_font()
    
    # 경로 설정
    base_path = "c:/Users/Administrator/Desktop/fcicb6/pj2/pj2-3-3"
    csv_file = os.path.join(base_path, "data/hanatour_reviews.csv")
    output_images = os.path.join(base_path, "image/reviews")
    
    # 분석 실행
    analyze_reviews(csv_file, output_images)
