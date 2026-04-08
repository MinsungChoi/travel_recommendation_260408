import streamlit as st

def apply_vacation_theme():
    """휴양지 분위기(Blue/Beige/White)를 위한 커스텀 CSS 적용"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Nanum Gothic', sans-serif;
    }

    /* v5.0 상용화 수준 다크 프리미엄 테마 */
    .stApp {
        background-color: #0E1117;
        background-image: radial-gradient(circle at 50% 10%, #1A1C24 0%, #0E1117 100%);
        color: #FFFFFF !important; /* 본문 텍스트 화이트 고정 */
    }

    /* 텍스트 시인성 전수 개선 */
    p, span, label, div {
        color: #FFFFFF !important;
        line-height: 1.6;
    }

    /* 네온 블루 3.0 액센트 */
    h1, h2, h3, h4 { 
        color: #00D4FF !important; 
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.6); 
        letter-spacing: -0.01em;
        font-weight: 800 !important;
    }

    /* 탭 메뉴 (Active 상태 강화) */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        opacity: 0.6;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        opacity: 1.0;
        color: #00D4FF !important;
        border-bottom: 2px solid #00D4FF !important;
    }

    /* 결과 프리미엄 카드 (보강) */
    .product-card {
        background: rgba(26, 28, 36, 0.98);
        border: 1px solid rgba(0, 212, 255, 0.4);
        border-radius: 20px;
        padding: 35px;
        margin-bottom: 30px;
        border-left: 10px solid #00D4FF;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }

    /* 순위 뱃지 (Rank Badge) */
    .rank-badge {
        position: absolute;
        top: -15px;
        left: -15px;
        background: linear-gradient(135deg, #00D4FF, #0055FF);
        color: white;
        padding: 5px 15px;
        border-radius: 10px;
        font-weight: 900;
        font-size: 1.2rem;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
        z-index: 10;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* 배지 디자인 (명확성 강화) */
    .badge-나트랑 { background: #1D9E75; color: white; padding: 6px 18px; border-radius: 30px; font-weight: 800; }
    .badge-다낭 { background: #378ADD; color: white; padding: 6px 18px; border-radius: 30px; font-weight: 800; }
    .badge-싱가포르 { background: #D85A30; color: white; padding: 6px 18px; border-radius: 30px; font-weight: 800; }

    /* 데이터 기준 및 가이드 푸터 */
    .footer-container {
        margin-top: 60px;
        padding: 30px;
        background: rgba(26, 28, 36, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        color: #BBBBBB;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    /* 버튼 프리미엄 스타일링 (v5.5 고도화) */
    .stButton > button {
        background-color: rgba(0, 212, 255, 0.05) !important;
        color: #00D4FF !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 15px !important;
        padding: 20px 10px !important;
        min-height: 80px !important;
        transition: all 0.3s ease-in-out !important;
        font-weight: 700 !important;
        white-space: pre-line !important; /* 줄바꿈 허용 */
        font-size: 1rem !important;
    }

    .stButton > button:hover {
        background-color: rgba(0, 212, 255, 0.15) !important;
        border-color: #00D4FF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4) !important;
        transform: translateY(-2px);
    }

    /* 버튼 내부 텍스트 강제 색상 지정 (버그 방지) */
    .stButton > button p, .stButton > button span {
        color: inherit !important;
    }

    .footer-title {
        color: #E0E0E0;
        font-weight: 700;
        margin-bottom: 10px;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)
