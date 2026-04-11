import pandas as pd
import os
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# 1. 환경 설정 및 데이터 로드
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
FILE_PATH = os.path.join(DATA_DIR, 'hanatour_reviews.csv')

def load_negative_reviews():
    if not os.path.exists(FILE_PATH):
        print(f"Error: {FILE_PATH} not found.")
        return pd.DataFrame()
    
    df = pd.read_csv(FILE_PATH, encoding='utf-8-sig')
    # 평점 3점 이하 필터링
    neg_df = df[df['평점'] <= 3].copy()
    return neg_df

def preprocess_text(text):
    # 한글만 남기기
    text = re.sub(r'[^가-힣\s]', '', str(text))
    # 불용어 정의 (기존 리스트 활용 및 시스템 안내문구 대폭 제외)
    STOPWORDS = set(['에서', '하고', '으로', '하는', '입니다', '있습니다', '정말', '너무', '좋아요', '자체가', '같아요', '습니다', '했고', '해서', '있어서', '있는', '있고', '한다', '있다', '것이', '것은', '등의', '한', '때문에', '위한', '대해', '대한', '모든', '통해', '같은', '함께', '전체', '가장', '다양한', '위해', '매우', '진짜', '좀', '그', '건', '들', '이', '가', '은', '는', '도', '를', '을', '의', '에', '와', '과', '나', '다', '로', '고', '지', '아', '오', '요', '이런', '저런', '그런', '하나', '건데', '때', '번', '함께', '보고', '갔는데', '많이', '정말', '매우', '아주', '조금', '특히', '다시', '꼭', '근데', '하지만', '그래도', '그래서', '그런데', '그냥', '조금', '약간', '거의', '모두', '전부', '진짜', '완전', '대박', '진심', '진짜로', '덕분에', '여행', '여행이',
                     '네이버블로그', '티스토리', '외부', '복사해서', '이미지가', '깨지는', '현상이', '발생하니', '첨부하여', '올려주시기', '바라며', '모바일', '상품평에는', '이미지', '올리실', '경우는', '부탁', '드립니다',
                     '정보가', '제공되지', '참고', '게시판에', '글쓰기를', '경우본문또는', '첨부파일내에', '개인정보주민등록번호', '성명', '개인정보가', '어플로', '남겨주시면', '확인이', '가능합니다', '안내', '드립니다', '작성하신', '글은', '삭제될', '수', '있으니'])
    
    # 특정 시스템 키워드가 포함된 문장 통째로 필터링 (개인정보 관련 자동 메시지 대응)
    if '개인정보' in text or '게시판' in text or '블로그' in text:
        return ""

    words = text.split()
    filtered = [w for w in words if len(w) >= 2 and w not in STOPWORDS]
    return " ".join(filtered)

def run_ngram_analysis(texts, n=2):
    # CountVectorizer를 이용한 N-gram 추출
    vectorizer = CountVectorizer(ngram_range=(n, n), max_features=20)
    ngrams = vectorizer.fit_transform(texts)
    count_values = ngrams.toarray().sum(axis=0)
    vocab = vectorizer.vocabulary_
    
    df_ngram = pd.DataFrame([{'ngram': k, 'count': count_values[v]} for k, v in vocab.items()])
    return df_ngram.sort_values(by='count', ascending=False)

def run_lda_topic_modeling(texts, n_topics=3):
    # LDA 고도화: 너무 흔한 단어(가이드, 패키지 등)는 토픽 구분을 방해하므로 max_df를 낮춰서 필터링
    # 추가적으로 LDA용 엔진에서만 제외할 '너무 일반적인' 단어들
    LDA_STOPWORDS = ['가이드', '패키지', '하나투어', '여행을', '베트남', '다낭', '가이드가', '시간', '다른', '그리고']
    
    vectorizer = CountVectorizer(max_df=0.5, min_df=5, stop_words=LDA_STOPWORDS)
    dtm = vectorizer.fit_transform(texts)
    
    if dtm.shape[1] == 0:
        return pd.DataFrame([{'Topic': 1, 'Keywords': '분석할 단어가 부족합니다.'}])

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, learning_method='online')
    lda.fit(dtm)
    
    words = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        # 각 토픽별로 가장 비중이 높은 단어 8개 추출
        top_words = [words[i] for i in topic.argsort()[:-9:-1]]
        topics.append({'Topic': topic_idx + 1, 'Keywords': ", ".join(top_words)})
    
    return pd.DataFrame(topics)

def run_service_quality_analysis(df):
    # 서비스 품질 3대 차원 키워드 정의
    dimensions = {
        'Tangibles (유형성 - 호텔/식사/항공)': ['호텔', '숙소', '식사', '음식', '항공', '비행기', '기내식', '객실', '조식', '석식', '뷔페', '침구', '청소'],
        'Empathy (공감성 - 가족/아이/배려)': ['아이', '어린이', '가족', '아이들', '배려', '키즈', '노인', '부모님', '동반', '친절', '상황', '요청', '불편함', '가이드가'],
        'Reliability (신뢰성 - 일정/쇼핑)': ['일정', '시간', '쇼핑', '지연', '강요', '옵션', '선택관광', '코스', '변경', '조율', '약속', '설명', '대기', '빠듯', '촉박']
    }
    
    results = {}
    for dim_name, keywords in dimensions.items():
        # 해당 키워드 중 하나라도 포함된 리뷰 필터링
        pattern = '|'.join(keywords)
        dim_df = df[df['내용'].str.contains(pattern, na=False, case=False)]
        
        if not dim_df.empty:
            # 해당 차원 내 상위 키워드 추출
            dim_texts = dim_df['cleaned'].tolist()
            dim_keywords = get_top_keywords_simple(dim_texts, top_n=10)
            results[dim_name] = {
                'count': len(dim_df),
                'top_keywords': dim_keywords
            }
        else:
            results[dim_name] = {'count': 0, 'top_keywords': []}
            
    return results

def get_top_keywords_simple(texts, top_n=10):
    all_words = " ".join(texts).split()
    return Counter(all_words).most_common(top_n)

if __name__ == "__main__":
    print("=== HanaTour Advanced Review Analysis (Service Quality Focused) ===")
    df = load_negative_reviews()
    if not df.empty:
        print(f"Total Negative Reviews (Rating <= 3): {len(df)}")
        
        # 텍스트 전처리
        df['cleaned'] = df['내용'].apply(preprocess_text)
        processed_texts = [t for t in df['cleaned'].tolist() if t != ""]
        
        # 1. 서비스 품질 3대 차원 분석
        print("\n[Analysis 1] Service Quality Dimensions (Categorized)")
        sq_results = run_service_quality_analysis(df)
        for dim, res in sq_results.items():
            print(f"\n--- {dim} (Reviews: {res['count']}) ---")
            kw_str = ", ".join([f"{k}({v})" for k, v in res['top_keywords']])
            print(f"Top Keywords: {kw_str}")
            
        # 2. N-gram 분석 (맥락 파악용)
        print("\n[Analysis 2] Top 10 Bi-grams (Overall)")
        bigrams = run_ngram_analysis(processed_texts, n=2)
        print(bigrams.head(10).to_string(index=False))
        
        # 3. LDA 토픽 모델링 (탐색용)
        print("\n[Analysis 3] Refined LDA Topic Modeling")
        topics = run_lda_topic_modeling(processed_texts, n_topics=3)
        for i, row in topics.iterrows():
            print(f"Topic {row['Topic']}: {row['Keywords']}")
    else:
        print("No negative reviews found to analyze.")
