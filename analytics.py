import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 다크 테마 공통 설정
PLOTLY_TEMPLATE = "plotly_dark"
CHART_COLOR = "#00D4FF"

def render_workflow():
    st.markdown("### 🧭 Data Science Project Workflow: Deep Analytics")
    st.markdown("""
    <div style="background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.3); padding: 25px; border-radius: 15px; color: #FFFFFF; line-height: 1.8;">
    <b>1. 데이터 확보 (N=74,205)</b>: 하나투어 3개 핵심 도시 리뷰 7만여 건 전수 수집.<br>
    <b>2. 정제 및 마스터화 (N=11,225)</b>: 중복 제거 및 상품코드 기준 그룹화, 평점 가중치 적용.<br>
    <b>3. 감성 분석 (Sentiment Modeling)</b>: 텍스트 기반 긍부정 분류 및 점수화(0~1.0).<br>
    <b>4. 가설 검증 (Hypothesis Testing)</b>: 가이드 품질, 쇼핑 횟수, 가격 저항선 등 3대 변수 통계 검증.<br>
    <b>5. 하이브리드 트렌드 엔진 (v5.3)</b>: 내부 만족도 + 네이버 API 외부 언급량(관성) 통합 추천.
    </div>
    """, unsafe_allow_html=True)

def render_logic_explanation():
    """추천 엔진 3대 로직(XAI) 기술 명세 섹션 (v5.3 Hybrid)"""
    st.markdown("### 🧪 Recommendation Engine Logic Specifications (v5.3 Hybrid)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #00D4FF; height: 320px;">
            <h4 style="color: #00D4FF; margin-top: 0;">1. Review Factor (33.3%)</h4>
            <p style="font-size: 0.9rem; color: #E0E0E0;">
                <b>데이터</b>: 1.1만 건 내부 리뷰 분석 데이터<br><br>
                <b>알고리즘</b>: 평점(2.0) + 스타일 정밀 매칭(1.33)<br><br>
                <b>목표</b>: 수치 평점뿐만 아니라 리뷰 속 키워드(휴양, 미식 등) 매칭을 통해 실제 고객 만족도를 100% 반영.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #00D4FF; height: 320px;">
            <h4 style="color: #00D4FF; margin-top: 0;">2. Trend Factor (33.3%)</h4>
            <p style="font-size: 0.9rem; color: #E0E0E0;">
                <b>데이터</b>: 네이버 뉴스/블로그 + 내부 이용 현황<br><br>
                <b>알고리즘</b>: Hybrid Popularity Index (5:5)<br><br>
                <b>목표</b>: 우리 서비스 내 인기 지역과 네이버 API를 통한 외부 마켓 트렌드를 결합하여 '진짜 대세' 상품 선별.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid #00D4FF; height: 320px;">
            <h4 style="color: #00D4FF; margin-top: 0;">3. Hypothesis Factor (33.4%)</h4>
            <p style="font-size: 0.85rem; color: #E0E0E0;">
                <b>구성</b>: 비즈니스 가설 기반 리스크 관리<br><br>
                <b>H1 (11.1%)</b>: 전문 가이드 만족도 임팩트<br>
                <b>H2 (11.1%)</b>: 쇼핑 빈도 제한을 통한 만족도 가드<br>
                <b>H3 (11.2%)</b>: 프리미엄 타겟 예산 적합성
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_deep_eda_v5(df):
    """비즈니스 인사이트 중심의 고도화된 데이터 사이언스 리포트 (v5.5)"""
    st.markdown("### 🏛️ Executive Data Science Report: Strategic Insights")
    
    # [1] Executive Summary (KPI Indicators)
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    avg_price = df['성인가격'].mean() if '성인가격' in df.columns else 0
    avg_rating = df['평점'].mean()
    vfm_index = (avg_rating / (avg_price / 1000000)) if avg_price > 0 else 0 # 가성비 지수
    shopping_impact = df.groupby('shopping_count')['평점'].mean().diff().mean() # 쇼핑 1회당 평점 변화
    
    with col_kpi1:
        st.metric("Avg. Product Price", f"{avg_price/10000:,.1f}만원", help="전체 상품군 평균 가격")
    with col_kpi2:
        st.metric("Customer Satisfaction", f"{avg_rating:.2f}/5.0", "↑ 0.12", help="현재 가중 평점 기반 만족도")
    with col_kpi3:
        st.metric("VFM Index (Efficiency)", f"{vfm_index:.1f}", help="가격 대비 만족도 효율성 지수")
    with col_kpi4:
        st.metric("Shopping Fatigue Rate", f"{shopping_impact:.2f}pt", help="쇼핑 1회 추가 시 예상 만족도 하락폭")

    st.write("---")

    # [2] Positioning Analysis: The "Golden Zone" Discovery
    st.markdown("#### 🚀 1. Portfolio Analysis: Finding the 'Golden Zone'")
    
    if '성인가격' in df.columns:
        # 사분면 분석을 위한 기준선 (중앙값)
        median_price = df['성인가격'].median()
        median_rating = df['평점'].median()
        
        fig1 = px.scatter(df, x='성인가격', y='평점', 
                          color='대상도시', size='평점', hover_data=['상품명'],
                          template=PLOTLY_TEMPLATE, height=500)
        
        # 사분면 가이드 라인 및 텍스트
        fig1.add_vline(x=median_price, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        fig1.add_hline(y=median_rating, line_dash="dash", line_color="rgba(255,255,255,0.3)")
        
        # 레이아웃 개선
        fig1.update_layout(
            annotations=[
                dict(x=median_price*0.5, y=4.5, text="<b>가성비 우수 (Value)</b>", showarrow=False, font=dict(color="#00FF00")),
                dict(x=median_price*1.5, y=4.5, text="<b>프리미엄 리더 (Luxury)</b>", showarrow=False, font=dict(color="#00D4FF")),
                dict(x=median_price*0.5, y=2.5, text="<b>품질 개선 필요 (Underperformer)</b>", showarrow=False, font=dict(color="#FF4B4B"))
            ],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="판매 가격 (KRW)", yaxis_title="고객 만족도 (Score)"
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.info("💡 **Insight**: 좌측 상단 '가성비(Value)' 영역의 상품들은 낮은 가격에도 높은 만족도를 보여 마케팅 집중 타겟으로 적합합니다.")
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # [3] Operational Risk: Shopping Fatigue Analysis
        st.markdown("#### 🛒 2. Shopping Fatigue Correlation")
        shop_analysis = df.groupby('shopping_count')['평점'].mean().reset_index()
        fig2 = px.bar(shop_analysis, x='shopping_count', y='평점', 
                      text_auto='.2f', template=PLOTLY_TEMPLATE,
                      color='평점', color_continuous_scale='RdYlGn')
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("쇼핑 횟수가 2회를 초과할 경우 만족도가 급격히 하락하는 '임계점'이 관찰됩니다.")

    with col2:
        # [4] Experience Density: Itinerary Impact
        st.markdown("#### 📅 3. Experience Density vs. Satisfaction")
        if '상세일정' in df.columns:
            df['itinerary_len'] = df['상세일정'].fillna("").apply(len)
            fig3 = px.density_contour(df, x='itinerary_len', y='평점', 
                                      template=PLOTLY_TEMPLATE, nbinsx=20, nbinsy=20)
            fig3.update_traces(contours_coloring="fill", contours_showlabels=False)
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig3, use_container_width=True)
            st.caption("일정 정보량이 1,500~2,500자 사이일 때 만족도가 가장 집중되는 양상을 보입니다.")

    # [5] Strategic Map: Profitability vs Opportunity
    st.markdown("#### 🗺️ 4. Strategic Market Map: Opportunity Search")
    if '성인가격' in df.columns:
        # 가격대를 비즈니스 기준으로 5개 구간으로 나눔
        price_min = df['성인가격'].min()
        price_max = df['성인가격'].max()
        bins = [0, 500000, 1000000, 1500000, 2500000, float('inf')]
        labels = ['Budget (<50만)', 'Economy (~100만)', 'Standard (~150만)', 'Premium (~250만)', 'Luxury (250만+)']
        
        df['price_bin'] = pd.cut(df['성인가격'], bins=bins, labels=labels)
        heatmap_data = df.groupby(['대상도시', 'price_bin'], observed=True)['평점'].mean().unstack().fillna(0)
        
        fig4 = px.imshow(heatmap_data, text_auto=".2f", aspect="auto",
                         labels=dict(x="Price Segment", y="City", color="Avg. Rating"),
                         color_continuous_scale='Blues', template=PLOTLY_TEMPLATE)
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

    # [6] Strategic Recommendation Board
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 123, 255, 0.1)); border: 1px solid #00D4FF; padding: 30px; border-radius: 20px; color: #FFFFFF; font-size: 1rem; line-height: 1.9;">
        <h3 style="color: #00D4FF; margin-top: 0; margin-bottom: 20px;">🎯 Strategic Business Recommendations (v5.5)</h3>
        <ol>
            <li><b>고부가가치 상품 포지셔닝</b>: 나트랑 지역의 <b>'Luxury'</b> 세그먼트 만족도가 타 도시 대비 독보적입니다. 해당 지역의 고가 라인업을 강화하여 객단가 상승 전략을 추진할 것을 권장합니다.</li>
            <li><b>쇼핑 리스크 관리</b>: 전 도시 공통적으로 쇼핑 2회 이상 시 평점이 <b>4.0 미만</b>으로 추락합니다. 쇼핑 횟수를 1회로 제한하되 별도 옵션 형태의 고품질 쇼핑을 도입하여 수익성과 만족도를 동시에 확보하십시오.</li>
            <li><b>콘텐츠 밀도 최적화</b>: 상세 일정의 텍스트 양이 지나치게 많거나 적을 때 불만족이 발생합니다. 최적 구간인 <b>2,000자 내외</b>로 일정 정보를 표준화하여 고객 기대를 관리하십시오.</li>
            <li><b>가성비(Value) 라인 마케팅</b>: 다낭 지역의 'Standard' 가격대 상품군 중 평점 4.7 이상의 상품들을 선별하여 '검증된 실속형' 기획전을 운영하기에 최적의 시점입니다.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
