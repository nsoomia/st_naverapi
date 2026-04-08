import pandas as pd
import os
import numpy as np
from typing import Tuple, Dict
# 데이터 디렉토리 경로 설정 (상대 경로로 변경하여 배포 환경 호환성 확보)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
def load_all_data() -> Dict[str, pd.DataFrame]:
    """
    모든 분석에 필요한 CSV 파일들을 로드합니다 (패키지, 에어텔, 투어/티켓 포함).
    """
    data = {}
    # 1. 기본 데이터 로드
    data['reviews'] = pd.read_csv(os.path.join(DATA_DIR, 'hanatour_reviews.csv'), encoding='utf-8-sig')
    data['aviation'] = pd.read_csv(os.path.join(DATA_DIR, 'processed_aviation_performance.csv'), encoding='utf-8-sig')
    data['itineraries'] = pd.read_csv(os.path.join(DATA_DIR, 'hanatour_all_itineraries.csv'), encoding='utf-8-sig')
    
    # 2. 도시별/유형별 통합 데이터 로드
    cities = ['danang', 'nhatrang', 'singapore']
    types = {'': '패키지', '_airtel': '에어텔', '_tour_ticket': '투어/티켓'}
    
    for city in cities:
        for t_suffix, t_label in types.items():
            key = f"{city}{t_suffix}"
            filename = f"hanatour_{city}{t_suffix}_integrated.csv"
            try:
                df = pd.read_csv(os.path.join(DATA_DIR, filename), encoding='utf-8-sig')
                df['상품군'] = t_label
                data[key] = df
            except FileNotFoundError:
                print(f"Warning: {filename} not found.")
                
    return data
def preprocess_and_merge(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    데이터프레임들을 하나의 분석용 통합 데이터셋으로 병합합니다.
    방어적 로직을 추가하여 KeyError 발생을 원천 차단합니다.
    """
    # 1. 리뷰 데이터 기본 전처리
    reviews = data['reviews'].copy()
    
    # [방어 로직] 병합 전 '상품군' 컬럼을 기본값으로 초기화하여 무결성 보장
    if '상품군' not in reviews.columns:
        reviews['상품군'] = '정보없음'
        
    reviews['작성일'] = pd.to_datetime(reviews['작성일'], errors='coerce')
    reviews['연도'] = reviews['작성일'].dt.year
    reviews['월'] = reviews['작성일'].dt.month
    
    # 2. 상품별 추가 정보(상품군, 쇼핑횟수 등) 병합
    target_cols = ['대표상품코드', '쇼핑횟수', '가이드동행', '상품군', '성인가격']
    
    city_infos = []
    cities = ['danang', 'nhatrang', 'singapore']
    types = ['', '_airtel', '_tour_ticket']
    
    for city in cities:
        for suffix in types:
            key = f"{city}{suffix}"
            if key in data:
                df_city = data[key].copy()
                df_city.columns = df_city.columns.str.strip()
                
                # '성인가격'이 없는 경우(투어/티켓 등)는 '정상가격' 지원
                if '성인가격' not in df_city.columns and '정상가격' in df_city.columns:
                    df_city.rename(columns={'정상가격': '성인가격'}, inplace=True)
                
                # 데이터가 실제 존재하는 컬럼만 선별하여 추출
                existing_cols = [c for c in target_cols if c in df_city.columns]
                if existing_cols:
                    city_infos.append(df_city[existing_cols].drop_duplicates())
    
    # 상품 마스터 통합 (데이터가 없는 경우 방어)
    if city_infos:
        product_master = pd.concat(city_infos, axis=0).drop_duplicates('대표상품코드')
    else:
        # 데이터가 아예 없는 경우 빈 스키마 생성
        product_master = pd.DataFrame(columns=target_cols)
    
    # 리뷰 데이터와 상품 마스터를 병합합니다 (상품군 정보가 리뷰의 기본값을 덮어씁니다).
    # 병합 전 reviews에서 '상품군'을 삭제하여 product_master의 데이터가 우선되게 합니다.
    if '상품군' in reviews.columns and '상품군' in product_master.columns:
        reviews_temp = reviews.drop(columns=['상품군'])
    else:
        reviews_temp = reviews
        
    df = pd.merge(reviews_temp, product_master, left_on='상품코드', right_on='대표상품코드', how='left')
    
    # 병합 후에도 '상품군'이 결측치인 경우 다시 기본값 처리
    if '상품군' in df.columns:
        df['상품군'] = df['상품군'].fillna('정보없음')
    else:
        df['상품군'] = '정보없음'
    
    # 3. 항공 실적 데이터와 병합
    aviation = data['aviation'].copy()
    city_to_iata = {'다낭': 'DAD', '나트랑': 'CXR', '싱가포르': 'SIN'}
    df['IATA'] = df['대상도시'].map(city_to_iata)
    aviation.columns = aviation.columns.str.strip()
    
    aviation_monthly = aviation.groupby(['IATA', '월'])['유임승객(명)'].mean().reset_index()
    aviation_monthly.rename(columns={'유임승객(명)': '평균항공객수'}, inplace=True)
    
    df = pd.merge(df, aviation_monthly, on=['IATA', '월'], how='left')
    
    # 4. 평점대 컬럼 생성 및 수치 데이터 정형화
    df['평점대'] = df['평점'].apply(lambda x: f"{int(x)}점대" if pd.notnull(x) else "정보없음")
    df['성인가격'] = pd.to_numeric(df['성인가격'], errors='coerce').fillna(0).astype(int)
    
    # [FIX] 쇼핑횟수가 문자열로 로드되어 Plotly에서 오류가 발생하는 것을 방지
    if '쇼핑횟수' in df.columns:
        df['쇼핑횟수'] = pd.to_numeric(df['쇼핑횟수'], errors='coerce').fillna(0).astype(int)
    else:
        df['쇼핑횟수'] = 0
        
    return df
if __name__ == "__main__":
    # 스크립트 단독 실행 시 데이터 로드 및 병합 테스트를 진행합니다.
    print("데이터 로딩 시작...")
    raw_data = load_all_data()
    print("데이터 병합 및 전처리 시작...")
    final_df = preprocess_and_merge(raw_data)
    print(f"완성된 데이터 셋 크기: {final_df.shape}")
    print("상위 5건 데이터 확인:")
    print(final_df.head())