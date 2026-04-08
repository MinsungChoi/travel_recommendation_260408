import pandas as pd
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# 1. 데이터 경로를 찾는 슈퍼 로버스트 로직
def get_data_path():
    """배포 환경(리눅스) 및 로컬 환경 어디서든 데이터 파일을 찾아내는 강력한 탐색 로직"""
    import os
    
    # 찾고자 하는 파일명
    target_file = 'hanatour_sentiment_result (2).csv.gz'
    
    # 현재 파일의 위치 기준
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 탐색 지점 설정
    search_dirs = [
        current_dir,                                # 현재 폴더
        os.path.join(current_dir, 'data'),          # 현재 폴더/data
        os.path.dirname(current_dir),               # 상위 폴더
        os.path.join(os.path.dirname(current_dir), 'data'), # 상위 폴더/data
        os.getcwd(),                                # 작업 디렉토리 루트
        os.path.join(os.getcwd(), 'data')           # 작업 디렉토리 루트/data
    ]
    
    # 1. 명시적 후보지 탐색
    for d in search_dirs:
        potential_path = os.path.join(d, target_file)
        if os.path.exists(potential_path):
            print(f"✅ 데이터 발견: {potential_path}")
            return potential_path
            
    # 2. 최후의 수단: 현재 디렉토리부터 하위 모든 폴더 전수 조사
    print("⚠️ 후보지에서 미발견. 전수 조사를 시작합니다...")
    for root, dirs, files in os.walk(os.getcwd()):
        if target_file in files:
            full_path = os.path.join(root, target_file)
            print(f"✅ 전수 조사로 데이터 발견: {full_path}")
            return full_path
            
    # 모든 시도 실패 시 기본값 반환 (이후 pd.read_csv에서 명시적 에러 발생)
    print(f"❌ '{target_file}' 파일을 어디에서도 찾을 수 없습니다.")
    return os.path.join(current_dir, 'data', target_file)

DATA_PATH = get_data_path()

def load_processed_data():
    """11,225행의 리뷰 데이터를 로드하고 실제 가격 및 일정 데이터를 병합"""
    df = pd.read_csv(DATA_PATH)
    data_dir = os.path.dirname(DATA_PATH)
    
    # 1. 실제 여행 일정 데이터 로드 (상품코드 기준)
    itinerary_path = os.path.join(data_dir, 'hanatour_all_itineraries (2).csv.gz')
    if os.path.exists(itinerary_path):
        df_it = pd.read_csv(itinerary_path, encoding='utf-8-sig', compression='gzip')
        # 대표상품코드 기준으로 상세일정 병합
        df = pd.merge(df, df_it[['대표상품코드', '상세일정']], left_on='상품코드', right_on='대표상품코드', how='left')
        df.drop(columns=['대표상품코드'], inplace=True)
    
    # 2. 도시별 실제 가격 통합 데이터 로드
    price_files = [
        'hanatour_danang_airtel_integrated.csv.gz', 'hanatour_danang_integrated (2).csv.gz', 'hanatour_danang_tour_ticket_integrated.csv.gz',
        'hanatour_nhatrang_airtel_integrated (1).csv.gz', 'hanatour_nhatrang_integrated (1).csv.gz', 'hanatour_nhatrang_tour_ticket_integrated.csv.gz',
        'hanatour_singapore_airtel_integrated.csv.gz', 'hanatour_singapore_integrated (4).csv.gz', 'hanatour_singapore_tour_ticket_integrated.csv.gz'
    ]
    
    price_dfs = []
    for f in price_files:
        p_path = os.path.join(data_dir, f)
        if os.path.exists(p_path):
            try:
                # 메모리 효율을 위해 필요한 컬럼만 로드
                cols = ['대표상품코드', '성인가격', '쇼핑횟수', '쇼핑매장내역']
                df_p = pd.read_csv(p_path, encoding='utf-8-sig', usecols=lambda x: x in cols)
                price_dfs.append(df_p)
            except Exception: continue
            
    if price_dfs:
        df_price_all = pd.concat(price_dfs).drop_duplicates('대표상품코드')
        df = pd.merge(df, df_price_all, left_on='상품코드', right_on='대표상품코드', how='left')
        df.drop(columns=['대표상품코드'], inplace=True)

    # 가격대(Real Price based) 및 쇼핑 횟수 보정
    def classify_price_real(price):
        if pd.isna(price) or price == 0: return 'Standard'
        if price >= 2500000: return 'Premium'
        elif price <= 1200000: return 'Budget'
        return 'Standard'

    # 기존 상품명 기반 추출도 보조적으로 유지 (가격 데이터 없을 경우 대비)
    def classify_price_ext(name):
        name = str(name)
        if any(kw in name for kw in ['프리미엄', '5성', '특급', '노쇼핑', '고품격']): return 'Premium'
        elif any(kw in name for kw in ['실속', '특가', '최저가', '4성', '세미팩']): return 'Budget'
        return 'Standard'

    df['price_group'] = df.apply(lambda x: classify_price_real(x['성인가격']) if '성인가격' in x and not pd.isna(x['성인가격']) else classify_price_ext(x['상품명']), axis=1)
    
    # 쇼핑 횟수: 실제 데이터 우선, 없으면 상품명에서 추출
    def extract_shopping_ext(name):
        name = str(name)
        if '노쇼핑' in name: return 0
        match = re.search(r'쇼핑(\d+)회', name)
        return int(match.group(1)) if match else 3

    df['shopping_count'] = df.apply(lambda x: int(x['쇼핑횟수']) if '쇼핑횟수' in x and not pd.isna(x['쇼핑횟수']) else extract_shopping_ext(x['상품명']), axis=1)
    
    # [v5.1] 가이드 임팩트 지수 선행 계산
    guide_keywords = ['가이드', '친절', '전문', '설명', '배려', '매너']
    def calculate_guide_score(text):
        text = str(text)
        count = sum(1 for kw in guide_keywords if kw in text)
        return min(count / 3 * 5.0, 5.0) 
    
    df['review_guide_score'] = df['내용'].apply(calculate_guide_score)
    
    return df

def get_product_master(df):
    """상품코드 기준 마스터 테이블 생성 (실제 가격 및 일정 포함)"""
    
    # 마스터 테이블 집계
    agg_dict = {
        '상품명': 'first',
        '대상도시': 'first',
        '평점': 'mean',
        'price_group': 'first',
        'shopping_count': 'max', # 실제 쇼핑 횟수 반영
        '성인가격': 'median',     # 기간별 변동이 있을 수 있으므로 중앙값 사용
        '상세일정': 'first',
        '쇼핑매장내역': 'first',
        'review_guide_score': 'mean',
        '내용': lambda x: " ".join(str(i) for i in x[:5])
    }
    
    # 존재하지 않는 컬럼 제외
    actual_agg = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    master = df.groupby('상품코드').agg(actual_agg).reset_index()
    master.rename(columns={'review_guide_score': 'guide_impact'}, inplace=True)
    
    return master

def build_content_engine(master):
    """TF-IDF 및 코사인 유사도 행렬 구축 (일정 텍스트 추가)"""
    tfidf = TfidfVectorizer(max_features=500, stop_words=['있는', '대한', '함께', '여행'])
    # 상품명 + 도시 + 상세일정 일부 결합하여 유사도 측정
    text_data = master['상품명'] + " " + master['대상도시'] + " " + master['상세일정'].fillna("").str[:200]
    tfidf_matrix = tfidf.fit_transform(text_data)
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return tfidf, cosine_sim

def build_collaborative_clusters(df):
    """사용자 클러스터링 고도화 (v5.1: 연령/동행 기반)"""
    # 1. 범주형 데이터 인코딩 (Label Mapping) - 연령대 및 동행 형태
    age_map = {'20대': 0, '30대': 1, '40대': 2, '50대 이상': 3}
    comp_map = {'혼자': 0, '커플·연인': 1, '가족': 2, '친구·지인': 3}
    
    df['age_cat'] = df['연령대'].map(age_map).fillna(1) # 기본값 30대
    df['comp_cat'] = df['동행'].map(comp_map).fillna(2) # 기본값 가족

    # 2. 클러스터링 피처 고도화 (평점, 감성, 가이드 만족도, 쇼핑 빈도, 연령, 동행)
    features = ['평점', 'sentiment_score', 'review_guide_score', 'shopping_count', 'age_cat', 'comp_cat']
    # 리뷰ID 기준 피벗 테이블 생성
    pivot = df.pivot_table(index='리뷰ID', values=features).fillna(0)
    
    # 3. K-Means 기반 세그먼트 분류 (5개 군집)
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(pivot)
    
    # 4. 리뷰별 클러스터 할당 데이터프레임에 맵핑
    review_to_cluster = pd.Series(clusters, index=pivot.index)
    df['cluster'] = df['리뷰ID'].map(review_to_cluster).fillna(-1).astype(int)
    
    return df

def load_external_trends():
    """네이버 API 수집 외부 트렌드 데이터(뉴스/블로그 볼륨) 로드"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(base_path), "data")
    
    external_trends = {}
    city_files = {
        '나트랑': 'historical_나트랑_20260322.csv.gz',
        '다낭': 'historical_다낭_20260322.csv.gz',
        '싱가포르': 'historical_싱가포르_20260322.csv.gz'
    }
    
    for city, filename in city_files.items():
        file_path = os.path.join(data_dir, filename)
        if os.path.exists(file_path):
            try:
                # 데이터 양이 많으므로 단순히 행 수만 카운트하여 '관심도 Volume'으로 활용
                df_ext = pd.read_csv(file_path)
                external_trends[city] = len(df_ext)
            except Exception as e:
                # 오류 발생 시 0으로 처리
                external_trends[city] = 0
        else:
            external_trends[city] = 0
            
    return external_trends
