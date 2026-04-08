import numpy as np
import pandas as pd
from datetime import datetime

class TravelRecommender:
    def __init__(self, master_df, cosine_sim, external_trends=None):
        self.master = master_df
        self.cosine_sim = cosine_sim
        self.external_trends = external_trends or {}
        self.current_month = datetime.now().month

    def rule_based_recommend(self, persona):
        """v5.5 Hybrid Engine: 실데이터(가격, 일정) 기반 가중치 시스템"""
        scores = pd.Series(0.0, index=self.master.index)
        reasons = {}
        
        target_style = persona.get('style', '휴양·힐링')
        user_budget = persona.get('budget', 150) * 10000 # 만원 단위를 원 단위로 변환 (예: 150 -> 1,500,000)

        # [v5.3/5.5] Trend Factor 구성 요소 계산
        city_counts = self.master['대상도시'].value_counts()
        max_internal = city_counts.max() if not city_counts.empty else 1
        
        # 외부 데이터 최댓값이 0일 경우(데이터 로드 실패 등)를 대비해 최소 1로 고정하여 ZeroDivisionError 방지
        ext_values = self.external_trends.values()
        max_external = max(max(ext_values) if ext_values else 1, 1)

        city_trend_map = {}
        for city in city_counts.index:
            internal_idx = city_counts[city] / max_internal
            external_idx = self.external_trends.get(city, 0) / max_external
            hybrid_idx = (internal_idx * 0.5) + (external_idx * 0.5)
            # 트렌드 가중치 (Max 3.33)
            city_trend_map[city] = 2.0 + (hybrid_idx * 1.33)

        STYLE_KEYWORDS = {
            '휴양·힐링': ['리조트', '수영장', '바다', '편안', '조용', '휴식', '힐링', '스파', '마사지'],
            '관광·명소': ['명소', '역사', '가이드', '투어', '구경', '일정', '박물관', '유적지', '사원'],
            '미식·맛집': ['맛집', '식당', '요리', '현지식', '조식', '카페', '저녁', '맛있', '음식'],
            '쇼핑·도심': ['쇼핑', '마트', '기념품', '백화점', '시장', '시내', '도심', '브랜드', '구매']
        }
        keywords = STYLE_KEYWORDS.get(target_style, [])
        
        for idx, row in self.master.iterrows():
            item_reasons = []
            review_content = str(row.get('내용', ''))
            city = row['대상도시']
            price = row.get('성인가격', 0)
            
            # [1] Review Factor (33.3% Weight) -> Max 3.33 pts
            rating_score = (row['평점'] / 5.0) * 2.0
            match_count = sum(1 for kw in keywords if kw in review_content)
            keyword_score = min((match_count / 3) * 1.33, 1.33)
            review_total = rating_score + keyword_score
            item_reasons.append(f"⭐ 만족도 분석: 평점({row['평점']:.1f})과 '{target_style}' 테마 매칭.")

            # [2] Trend Factor (33.3% Weight) -> Max 3.33 pts
            trend_score = city_trend_map.get(city, 2.0)
            item_reasons.append(f"📈 트렌드 분석: {city} 지역 시장 언급량 및 인기도 반영.")

            # [3] Hypothesis Factor (33.4% Weight) -> Max 3.34 pts
            # H1: 가이드 (1.11 pts)
            h1_score = min(row.get('guide_impact', 2.5) / 5.0 * 1.11, 1.11)
            item_reasons.append(f"👨‍🏫 H1(가이드): 전문 가이드 영향력 지수 반영.")

            # H2: 쇼핑 리스크 (1.11 pts) - 실제 쇼핑 횟수 기반
            shop_count = row.get('shopping_count', 3)
            if shop_count <= 0: h2_score = 1.11
            elif shop_count <= 2: h2_score = 0.8
            else: h2_score = 0.5
            item_reasons.append(f"🛒 H2(쇼킹 케어): 실제 쇼핑 횟수({shop_count}회) 기반 만족도 보정.")

            # H3: 가격 적합성 (1.12 pts) - 실제 가격 기반
            if price > 0:
                # 예산 대비 가격 차이 분석 (적을수록 좋음)
                price_diff_ratio = abs(price - user_budget) / user_budget
                h3_score = max(0, 1.12 * (1 - price_diff_ratio))
                item_reasons.append(f"💎 H3(예산): 고객님 예산 대비 상품 가격({price:,.0f}원) 적합성 검증.")
            else:
                h3_score = 0.6
                item_reasons.append(f"⚠️ H3(예산): 가격 정보 확인 중 (표준 점수 부여).")

            # 최종 합산
            total_score = review_total + trend_score + h1_score + h2_score + h3_score
            scores[idx] = total_score
            reasons[row['상품코드']] = {
                'reasons': item_reasons,
                'breakdown': {
                    'Review (Internal)': review_total,
                    'Trend (Hybrid)': trend_score,
                    'H1 (Guide)': h1_score,
                    'H2 (Shopping)': h2_score,
                    'H3 (Risk)': h3_score
                }
            }
            
        top_indices = scores.sort_values(ascending=False).head(5).index
        results = self.master.loc[top_indices].copy()
        
        results['reasons'] = [reasons.get(code, {}).get('reasons', []) for code in results['상품코드']]
        results['breakdown'] = [reasons.get(code, {}).get('breakdown', {}) for code in results['상품코드']]
        results['total_score'] = scores.loc[top_indices].values
        
        return results



    def content_based_recommend(self, product_code, top_n=5):
        """2번 탭용: TF-IDF 코사인 유사도 기반 유사 상품 추천"""
        try:
            target_idx = self.master[self.master['상품코드'] == product_code].index[0]
            sim_scores = list(enumerate(self.cosine_sim[target_idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            similar_indices = [i[0] for i in sim_scores[1:top_n+1]]
            
            results = self.master.loc[similar_indices].copy()
            results['similarity'] = [i[1] for i in sim_scores[1:top_n+1]]
            return results
        except (IndexError, KeyError):
            return pd.DataFrame()

    def collaborative_recommend(self, persona, raw_df, top_n=5):
        """v5.1 신규: 취향 유사 고객(Cluster-based CF) 추천 엔진"""
        try:
            # 1. 페르소나를 클러스터에 매핑
            age_map = {'20대': 0, '30대': 1, '40대': 2, '50대 이상': 3}
            comp_map = {'혼자': 0, '커플·연인': 1, '가족': 2, '친구·지인': 3}
            
            p_age = age_map.get(persona.get('age', '30대'), 1)
            p_comp = comp_map.get(persona.get('companion', '가족'), 2)
            
            # 2. 페르소나와 가장 일치하는 클러스터 찾기 (가장 빈번한 클러스터)
            matched_cluster = raw_df[(raw_df['age_cat'] == p_age) & (raw_df['comp_cat'] == p_comp)]['cluster'].mode()[0]
            cluster_size = len(raw_df[raw_df['cluster'] == matched_cluster])
            
            # 3. 해당 클러스터 내 우수 상품 집계
            cluster_df = raw_df[raw_df['cluster'] == matched_cluster]
            best_items = cluster_df.groupby('상품코드').agg({'평점': 'mean', '상품명': 'count'}).rename(columns={'상품명': 'review_count'})
            best_items = best_items[best_items['review_count'] >= 2].sort_values('평점', ascending=False)
            
            # 4. 결과 매칭
            target_codes = best_items.head(top_n).index
            results = self.master[self.master['상품코드'].isin(target_codes)].copy()
            
            # 개인화 설명 문구 생성
            p_age_str = persona.get('age', '30대')
            p_style = persona.get('style', '휴양')
            results['cf_reason'] = f"✨ {p_age_str} {p_style} 취향의 고객 {cluster_size:,}명이 검증한 인기 상품입니다."
            
            return results
        except (IndexError, KeyError, ValueError):
            # 매칭 실패 시 평점 상위 노출 및 기본 사유 제공
            fallback_res = self.master.sort_values('평점', ascending=False).head(top_n).copy()
            fallback_res['cf_reason'] = "🔍 현재 페르소나와 일치하는 고객 그룹의 데이터를 정밀 분석 중입니다. (평점 기반 추천 수행)"
            return fallback_res
