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

# 2. 데이터 로드 및 필터링
def load_and_filter_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')
    
    # 평점 3점 이하 필터링 (사용자 요청)
    neg_df = df[df['평점'] <= 3].copy()
    print(f"전체 {len(df)}건 중 평점 3점 이하 리뷰 {len(neg_df)}건을 대상으로 분석을 진행합니다.")
    return neg_df

# 3. EDA 및 시각화
def perform_eda(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='평점', palette='Reds_r')
    plt.title('부정 리뷰(Rating <= 3) 평점 분포')
    plt.savefig(os.path.join(IMAGE_DIR, 'rating_dist.png'))
    plt.close()

    plt.figure(figsize=(10, 6))
    df['대상도시'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=sns.color_palette('Reds'))
    plt.title('부정 리뷰 도시별 비중')
    plt.ylabel('')
    plt.savefig(os.path.join(IMAGE_DIR, 'city_dist.png'))
    plt.close()

# 4. 텍스트 전처리
def preprocess_text(text):
    text = re.sub(r'[^가-힣\s]', '', str(text))
    # 특정 시스템 키워드가 포함된 문장 통째로 필터링 (이미 확인된 boilerplate 대응)
    if '개인정보' in text or '게시판' in text or '블로그' in text:
        return ""
        
    STOPWORDS = set(['에서', '하고', '으로', '하는', '입니다', '있습니다', '정말', '너무', '좋아요', '자체가', '같아요', '습니다', '했고', '해서', '있어서', '있는', '있고', '한다', '있다', '것이', '것은', '등의', '한', '때문에', '위한', '대해', '대한', '모든', '통해', '같은', '함께', '전체', '가장', '다양한', '위해', '매우', '진짜', '좀', '그', '건', '들', '이', '가', '은', '는', '도', '를', '을', '의', '에', '와', '과', '나', '다', '로', '고', '지', '아', '오', '요', '이런', '저런', '그런', '하나', '건데', '때', '번', '함께', '보고', '갔는데', '많이', '정말', '매우', '아주', '조금', '특히', '다시', '꼭', '근데', '하지만', '그래도', '그래서', '그런데', '그냥', '조금', '약간', '거의', '모두', '전부', '진짜', '완전', '대박', '진심', '진짜로', '덕분에', '여행', '여행이', '가이드', '가이드가', '패키지', '하나투어', '베트남', '다낭', '시간', '다른', '그리고'])
    words = text.split()
    return " ".join([w for w in words if len(w) >= 2 and w not in STOPWORDS])

# 5. 토픽 모델링
def run_modeling(df, n_topics=5):
    df['cleaned'] = df['내용'].apply(preprocess_text)
    # 빈 문자열 제외
    valid_df = df[df['cleaned'] != ''].copy()
    texts = valid_df['cleaned'].tolist()
    
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

    return lda, lda_output, nmf, nmf_output, feature_names, valid_df

# 6. 보고서 생성
def generate_report(valid_df, lda_output, nmf_output):
    # 전수 데이터 확률 결합
    full_result = valid_df.copy()
    full_result['내용_요약'] = full_result['내용'].apply(lambda x: str(x)[:50] + "...")
    
    for i in range(5):
        full_result[f'LDA_Topic_{i+1}'] = lda_output[:, i]
        full_result[f'NMF_Topic_{i+1}'] = nmf_output[:, i]

    # 전수 결과 저장 (CSV)
    full_result.to_csv(os.path.join(DOC_DIR, 'negative_review_topic_analysis.csv'), index=False, encoding='utf-8-sig')

    # Markdown 작성
    report_content = f"""# 하나투어 부정 리뷰(평점 3이하) 통합 분석 보고서

## 1. 데이터 개요
- **분석 대상**: 하나투어 평점 3점 이하 리뷰 전체
- **총 분석 수**: {len(valid_df)}건

## 2. EDA (Exploratory Data Analysis) - 부정 리뷰 중심
### 2.1 평점 분포 (1-3점)
![평점 분포](file:///{os.path.join(IMAGE_DIR, 'rating_dist.png').replace('\\', '/')})

### 2.2 도시별 부정 리뷰 비중
![도시별 비중](file:///{os.path.join(IMAGE_DIR, 'city_dist.png').replace('\\', '/')})

## 3. 토픽 모델링 결과 요약 (5 Topics)
- **부정 리뷰를 5개의 핵심 테마로 분류하였습니다.**
- 상세 키워드 30개는 `lda_top_30_keywords.txt`, `nmf_top_30_keywords.txt` 파일에 저장되었습니다.

## 4. 리뷰 전수 분석 결과 (상위 20개 샘플 노출)
*전체 {len(valid_df)}건에 대한 분석 결과는 [negative_review_topic_analysis.csv](./negative_review_topic_analysis.csv)에서 확인하실 수 있습니다.*

"""
    # 표 형태 추가 (상위 20개만 요역 노출)
    cols_to_show = ['내용_요약'] + [f'LDA_Topic_{i+1}' for i in range(5)]
    report_content += full_result[cols_to_show].head(20).to_markdown(index=False)
    
    with open(os.path.join(DOC_DIR, 'eda_report.md'), 'w', encoding='utf8') as f:
        f.write(report_content)
    
    return full_result

if __name__ == "__main__":
    print("부정 리뷰 집중 분석을 시작합니다...")
    df = load_and_filter_data()
    perform_eda(df)
    lda_model, lda_out, nmf_model, nmf_out, features, valid_df = run_modeling(df)
    results_df = generate_report(valid_df, lda_out, nmf_out)
    print("분석 완료. 부정 리뷰 전수 분석 결과 및 보고서가 생성되었습니다.")
    
    # 터미널 출력 (샘플)
    print("\n=== 부정 리뷰 전수 분석 결과 (상위 5건 샘플) ===")
    cols_out = ['내용_요약'] + [f'LDA_Topic_{i+1}' for i in range(5)]
    print(results_df[cols_out].head(5).to_string(index=False))
