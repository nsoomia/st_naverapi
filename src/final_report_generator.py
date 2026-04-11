import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF

# 1. 환경 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'hanatour_reviews.csv')
IMAGE_DIR = os.path.join(BASE_DIR, 'images', 'eda')
DOC_DIR = os.path.join(BASE_DIR, 'docs')

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

# 2. 데이터 로드
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
    return df

# 3. EDA 및 시각화
def perform_eda(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='평점', palette='viridis')
    plt.title('평점 분포 현황')
    plt.savefig(os.path.join(IMAGE_DIR, 'rating_dist.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    df['대상도시'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    plt.title('도시별 리뷰 비중')
    plt.ylabel('')
    plt.savefig(os.path.join(IMAGE_DIR, 'city_dist.png'))
    plt.close()

# 4. 텍스트 전처리
def preprocess_text(text):
    text = re.sub(r'[^가-힣\s]', '', str(text))
    STOPWORDS = set(['에서', '하고', '으로', '하는', '입니다', '있습니다', '정말', '너무', '좋아요', '자체가', '같아요', '습니다', '했고', '해서', '있어서', '있는', '있고', '한다', '있다', '것이', '것은', '등의', '한', '때문에', '위한', '대해', '대한', '모든', '통해', '같은', '함께', '전체', '가장', '다양한', '위해', '매우', '진짜', '좀', '그', '건', '들', '이', '가', '은', '는', '도', '를', '을', '의', '에', '와', '과', '나', '다', '로', '고', '지', '아', '오', '요', '이런', '저런', '그런', '하나', '건데', '때', '번', '함께', '보고', '갔는데', '많이', '정말', '매우', '아주', '조금', '특히', '다시', '꼭', '근데', '하지만', '그래도', '그래서', '그런데', '그냥', '조금', '약간', '거의', '모두', '전부', '진짜', '완전', '대박', '진심', '진짜로', '덕분에', '여행', '여행이', '가이드', '가이드가', '패키지', '하나투어', '베트남', '다낭', '시간', '다른', '그리고'])
    words = text.split()
    return " ".join([w for w in words if len(w) >= 2 and w not in STOPWORDS])

# 5. 토픽 모델링
def run_modeling(df, n_topics=5):
    df['cleaned'] = df['내용'].apply(preprocess_text)
    texts = df[df['cleaned'] != '']['cleaned'].tolist()
    
    tfidf_vec = TfidfVectorizer(max_df=0.5, min_df=5, max_features=2000)
    tfidf = tfidf_vec.fit_transform(texts)
    feature_names = tfidf_vec.get_feature_names_out()

    # LDA
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda_output = lda.fit_transform(tfidf)
    
    # NMF
    nmf = NMF(n_components=n_topics, random_state=42)
    nmf_output = nmf.fit_transform(tfidf)

    # 상위 키워드 30개 저장
    def save_keywords(model, name):
        with open(os.path.join(BASE_DIR, f'{name}_top_30_keywords.txt'), 'w', encoding='utf8') as f:
            for i, topic in enumerate(model.components_):
                top_indices = topic.argsort()[:-31:-1]
                top_words = [feature_names[idx] for idx in top_indices]
                f.write(f"Topic {i+1}: {', '.join(top_words)}\n\n")

    save_keywords(lda, 'lda')
    save_keywords(nmf, 'nmf')

    return lda, lda_output, nmf, nmf_output, feature_names

# 6. 보고서 생성
def generate_report(df, lda_output, nmf_output):
    # 상위 5개 행 확률 결합
    sample_df = df.head(5).copy()
    sample_df['내용_요약'] = sample_df['내용'].apply(lambda x: str(x)[:50] + "...")
    
    # LDA 확률 추가
    for i in range(5):
        sample_df[f'LDA_Topic_{i+1}'] = lda_output[:5, i]
        sample_df[f'NMF_Topic_{i+1}'] = nmf_output[:5, i]

    # Markdown 작성
    report_content = f"""# 하나투어 리뷰 통합 분석 보고서

## 1. 데이터 개요
- **분석 대상**: 하나투어 다낭/나트랑/싱가포르 리뷰 데이터
- **총 리뷰 수**: {len(df)}건

## 2. EDA (Exploratory Data Analysis)
### 2.1 평점 분포
![평점 분포](file:///{os.path.join(IMAGE_DIR, 'rating_dist.png').replace('\\', '/')})

### 2.2 도시별 리뷰 비중
![도시별 비중](file:///{os.path.join(IMAGE_DIR, 'city_dist.png').replace('\\', '/')})

## 3. 토픽 모델링 결과 요약 (5 Topics)
- **LDA**: 각 테마별 확률 분포 기반의 클러스터링을 수행함.
- **NMF**: 행렬 분해 기법을 활용하여 보다 변별력 있는 키워드 셋을 도출함.
- *상세 키워드 30개는 개별 텍스트 파일(lda_top_30_keywords.txt, nmf_top_30_keywords.txt) 참조.*

## 4. 리뷰 샘플 및 토픽 확률
"""
    # 표 형태 추가
    cols_to_show = ['내용_요약'] + [f'LDA_Topic_{i+1}' for i in range(5)]
    report_content += sample_df[cols_to_show].to_markdown(index=False)
    
    with open(os.path.join(DOC_DIR, 'eda_report.md'), 'w', encoding='utf8') as f:
        f.write(report_content)
    
    return sample_df

if __name__ == "__main__":
    print("분석을 시작합니다...")
    df = load_data()
    perform_eda(df)
    lda_model, lda_out, nmf_model, nmf_out, features = run_modeling(df)
    results_df = generate_report(df, lda_out, nmf_out)
    print("분석 완료. 보고서 및 키워드 파일이 생성되었습니다.")
    
    # 터미널 출력용 (50자 요약 + 토픽 확률)
    print("\n=== 상위 5개 행 토픽 모델링 결과 (LDA) ===")
    cols_out = ['내용_요약'] + [f'LDA_Topic_{i+1}' for i in range(5)]
    print(results_df[cols_out].to_string(index=False))
