import pandas as pd
import os

def verify_data(file_path):
    """
    hanatour_reviews.csv 데이터를 로드하여 주요 지표의 수치를 검증합니다.
    """
    # 데이터 로드
    df = pd.read_csv(file_path)
    
    print("--- 데이터 검증 시작 ---")
    
    # 2-1. 대상 도시별 리뷰 수 검증
    print("\n2-1. 대상 도시별 리뷰 수:")
    city_counts = df['대상도시'].value_counts()
    print(city_counts)
    
    # 2-2. 상품형태별 비중
    print("\n2-2. 상품형태별 비중:")
    product_type_counts = df['상품형태'].value_counts(normalize=True) * 100
    print(product_type_counts)
    
    # 2-3. 동행자별 분포 (상위 5개)
    print("\n2-3. 동행자별 분포 (상위 5개):")
    companion_counts = df['동행'].value_counts()
    print(companion_counts.head(5))
    
    # 2-4. 연령대별 리뷰 분포
    print("\n2-4. 연령대별 리뷰 분포:")
    age_counts = df['연령대'].value_counts().sort_index()
    print(age_counts)
    
    # 2-6. 도시별 평균 평점
    print("\n2-6. 도시별 평균 평점:")
    city_avg_rating = df.groupby('대상도시')['평점'].mean()
    print(city_avg_rating)
    
    # 2-8. 동행별 평균 평점
    print("\n2-8. 동행별 평균 평점 (상위 5개):")
    companion_avg_rating = df.groupby('동행')['평점'].mean().sort_values(ascending=False)
    print(companion_avg_rating.head(5))
    
    # 2-10. 연령대별 평균 평점
    print("\n2-10. 연령대별 평균 평점:")
    age_avg_rating = df.groupby('연령대')['평점'].mean().sort_index()
    print(age_avg_rating)
    
    print("\n--- 데이터 검증 완료 ---")

if __name__ == "__main__":
    base_path = "c:/Users/Administrator/Desktop/fcicb6/pj2/pj2-3-3"
    csv_file = os.path.join(base_path, "data/hanatour_reviews.csv")
    verify_data(csv_file)
