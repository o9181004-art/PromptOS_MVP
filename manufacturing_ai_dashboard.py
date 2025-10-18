import json, os, datetime, time
import streamlit as st
import pandas as pd
from jinja2 import Template

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
INDEX_PATH = os.path.join(TEMPLATE_DIR, "index.json")

# 로딩 UX 상수 정의
LOADING_STEPS = [
    "📊 ERP·MES 데이터를 불러오고 있습니다...",
    "🔎 품질검사 이력, 생산일지, 불량 데이터를 수집 중입니다...",
    "🧩 데이터 매핑 및 문서 템플릿을 준비 중입니다..."
]

DONE_MESSAGE = "✅ PromptOS가 제조 데이터를 분석하여 문서를 생성했습니다."
EMPTY_INPUT_WARNING = "먼저 작업 내용을 입력해주세요."

def show_loading_sequence(total_duration: float = 3.0):
    """ERP·MES 데이터 로딩 UX 시퀀스를 표시한다."""
    step_duration = max(0.6, total_duration / len(LOADING_STEPS))
    progress = st.progress(0)
    
    with st.spinner(LOADING_STEPS[0]):
        time.sleep(step_duration)
    progress.progress(33)
    
    with st.spinner(LOADING_STEPS[1]):
        time.sleep(step_duration)
    progress.progress(66)
    
    with st.spinner(LOADING_STEPS[2]):
        time.sleep(step_duration)
    progress.progress(100)
    
    # 프로그레스바가 너무 오래 남지 않도록 약간 쉬고 바로 지워지게 함
    time.sleep(0.2)

@st.cache_data
def load_index():
    """템플릿 인덱스 로드"""
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_template_by_key(key: str) -> str:
    """키로 템플릿 파일 로드"""
    idx = load_index()
    fname = idx["map"].get(key)
    if not fname:
        raise ValueError(f"템플릿 키를 찾을 수 없음: {key}")
    path = os.path.join(TEMPLATE_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def render_markdown(template_str: str, ctx: dict) -> str:
    """Jinja2 템플릿 렌더링"""
    ctx = {**ctx, "today": datetime.date.today().isoformat()}
    return Template(template_str).render(**ctx)

def get_sample_context(key: str) -> dict:
    """표준화된 샘플 컨텍스트 반환"""
    if key == "qir":
        return {
            "doc_no": "QIR-2025-001",
            "date": "2025-01-18",
            "item_code": "P-1001",
            "item_name": "알루미늄 브래킷",
            "lot_no": "LOT-250118-A",
            "inspector": "이상길",
            "results": [
                {"name": "외경", "spec": "50±0.2mm", "value": "49.98", "judgement": "합격"},
                {"name": "내경", "spec": "25±0.1mm", "value": "24.92", "judgement": "합격"},
                {"name": "표면거칠기", "spec": "Ra≤1.6", "value": "1.8", "judgement": "보류"}
            ],
            "final_judgement": "보류",
            "remarks": "표면거칠기 재가공 필요",
            "evidence": "MES Lot LOT-250118-A 검사데이터"
        }
    elif key == "defect":
        return {
            "doc_no": "DA-2025-001",
            "date": "2025-01-18",
            "item_code": "P-1001",
            "item_name": "알루미늄 브래킷",
            "lot_no": "LOT-250118-A",
            "analyst": "박품질",
            "defects": [
                {"type": "표면불량", "count": 5, "ratio": 50, "cause": "가공조건 부적절", "action": "가공속도 조정"},
                {"type": "치수불량", "count": 3, "ratio": 30, "cause": "공구 마모", "action": "공구 교체"},
                {"type": "기타", "count": 2, "ratio": 20, "cause": "작업자 실수", "action": "교육 강화"}
            ],
            "total_defects": 10,
            "defect_rate": "2.7",
            "main_cause": "가공조건 부적절",
            "improvement": "가공속도 최적화 및 공구 교체 주기 단축",
            "action_now": "현재 LOT 재가공 처리",
            "prevention": "가공조건 표준화",
            "verify_method": "다음 LOT 검사 강화",
            "evidence": "품질관리 시스템"
        }
    elif key == "delivery":
        lines = [
            {"item_code":"P-1001","item_name":"알루미늄 브래킷","qty":100,"price":1200,"amount":120000},
            {"item_code":"P-2002","item_name":"스테인리스 볼트","qty":300,"price":200,"amount":60000},
        ]
        total = sum(l["amount"] for l in lines)
        return {
            "doc_no":"DR-2025-010",
            "date":"2025-01-18",
            "customer":"한빛정밀",
            "po_no":"PO-2501-022",
            "lines": lines,
            "total_amount": f"{total:,} 원",
            "remarks":"검수 완료, 파렛트 2EA"
        }
    return {}

def csv_to_context(df: pd.DataFrame, template_key: str) -> dict:
    """CSV 데이터를 템플릿 컨텍스트로 변환"""
    if df.empty:
        return {}
    
    # 기본 샘플 컨텍스트 가져오기
    context = get_sample_context(template_key)
    
    # 첫 번째 행 데이터로 덮어쓰기
    row = df.iloc[0]
    
    # 공통 필드 매핑
    if 'item_code' in df.columns:
        context['item_code'] = str(row['item_code'])
    if 'item_name' in df.columns:
        context['item_name'] = str(row['item_name'])
    if 'lot_no' in df.columns:
        context['lot_no'] = str(row['lot_no'])
    if 'inspector' in df.columns:
        context['inspector'] = str(row['inspector'])
    
    # 템플릿별 특수 필드
    if template_key == "qir":
        if 'final_judgement' in df.columns:
            context['final_judgement'] = str(row['final_judgement'])
        if 'remarks' in df.columns:
            context['remarks'] = str(row['remarks'])
    elif template_key == "defect":
        if 'analyst' in df.columns:
            context['analyst'] = str(row['analyst'])
        if 'main_cause' in df.columns:
            context['main_cause'] = str(row['main_cause'])
    
    return context

def route_template_from_text(text: str) -> str:
    """자연어 입력을 키워드 기반으로 분류해 템플릿 키를 반환"""
    import unicodedata
    
    # 전처리
    text = text.strip()
    if not text:
        return ""
    
    # 유니코드 정규화 (NFC)
    text = unicodedata.normalize('NFC', text)
    
    # 소문자화 (영문만)
    text_lower = text.lower()
    
    # 특수문자/중복 공백 최소화
    import re
    text_clean = re.sub(r'\s+', ' ', text_lower)
    
    # 키워드 사전 (우선순위 순)
    defect_keywords = ["불량", "불량분석", "원인분석", "시정조치", "불량률", "반품", "대책"]
    qir_keywords = ["품질검사", "검사성적서", "성적서", "검사서", "qir"]
    delivery_keywords = ["납품", "납품보고서", "송장", "상업송장", "출고", "delivery"]
    
    # 우선순위 1: 불량/원인 분석류
    for keyword in defect_keywords:
        if keyword in text_clean:
            return "defect"
    
    # 우선순위 2: 검사/성적서류
    for keyword in qir_keywords:
        if keyword in text_clean:
            return "qir"
    
    # 우선순위 3: 납품/출고/송장류
    for keyword in delivery_keywords:
        if keyword in text_clean:
            return "delivery"
    
    # 기본값
    return "qir"

def natural_language_route(text: str) -> str:
    """기존 함수와의 호환성을 위한 래퍼"""
    return route_template_from_text(text)

# 페이지 설정
st.set_page_config(
    page_title="🏭 제조AI 솔루션 - PromptOS", 
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if 'output' not in st.session_state:
    st.session_state.output = None
if 'title' not in st.session_state:
    st.session_state.title = ""
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# 사이드바 디버그 토글
with st.sidebar:
    st.markdown("### 🔧 개발자 옵션")
    debug_mode = st.checkbox("디버그 모드", value=st.session_state.debug_mode)
    st.session_state.debug_mode = debug_mode
    
    if debug_mode:
        st.markdown("**매칭 정보 표시:**")
        st.markdown("- 템플릿 키: `qir`, `defect`, `delivery`")
        st.markdown("- 히트 키워드: 매칭된 키워드 표시")

# 헤더
st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">🏭 PromptOS</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">ERP·MES 데이터 기반 제조문서 자동화 및 보고서 생성 플랫폼</p>
</div>
""", unsafe_allow_html=True)

# 메인 컨텐츠
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 제조 현장 데이터를 입력하여 문서를 생성하세요")
    
    # 자연어 입력
    user_input = st.text_area(
        "자연어 입력",
        value=st.session_state.user_input,
        placeholder="예: 오늘 생산된 제품의 품질검사 성적서를 작성해줘...",
        height=100,
        key="main_input"
    )
    st.session_state.user_input = user_input
    
    # 버튼 영역
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("🔄 입력창 초기화", use_container_width=True, type="secondary"):
            st.session_state.user_input = ""
            st.session_state.output = None
            st.session_state.title = ""
            st.rerun()
    
    with btn_col2:
        generate_clicked = st.button("⚡ 제조문서 생성하기", use_container_width=True, type="primary")
    
    # 빠른 시작 예시
    st.markdown("### 🚀 빠른 시작 예시")
    
    try:
        idx = load_index()
        quick = {q["label"]: q["key"] for q in idx["quickstart"]}
        
        # 3열 그리드로 버튼 배치
        grid_cols = st.columns(3)
        for i, (label, key) in enumerate(quick.items()):
            col_idx = i % 3
            if grid_cols[col_idx].button(f"📋 {label}", key=f"quick_{key}", use_container_width=True):
                try:
                    template = load_template_by_key(key)
                    context = get_sample_context(key)
                    markdown_output = render_markdown(template, context)
                    st.session_state.output = markdown_output
                    st.session_state.title = f"{label} (샘플)"
                    st.success(f"✅ {label} 문서가 생성되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
    except Exception as e:
        st.error(f"템플릿 로드 오류: {str(e)}")
    
    # CSV 업로드 섹션
    st.markdown("### 📁 CSV/XLSX 업로드 (ERP 시뮬레이션)")
    
    uploaded_file = st.file_uploader(
        "제조 데이터 파일을 업로드하세요",
        type=['csv', 'xlsx'],
        help="필수 컬럼: item_code, item_name, lot_no, inspector"
    )
    
    if uploaded_file is not None:
        try:
            # 파일 읽기
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # 프리뷰 표시
            st.markdown("#### 📊 업로드 파일 프리뷰 (상위 5행)")
            st.dataframe(df.head(), use_container_width=True)
            
            # 필수 컬럼 확인
            required_cols = ['item_code', 'item_name', 'lot_no', 'inspector']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.warning(f"⚠️ 필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
            else:
                # QIR 생성 버튼
                if st.button("📋 이 파일로 QIR 생성", use_container_width=True, type="primary"):
                    try:
                        template = load_template_by_key("qir")
                        context = csv_to_context(df, "qir")
                        markdown_output = render_markdown(template, context)
                        st.session_state.output = markdown_output
                        st.session_state.title = "품질검사서 (CSV 업로드)"
                        st.success("✅ CSV 데이터로 품질검사서가 생성되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"문서 생성 오류: {str(e)}")
        
        except Exception as e:
            st.error(f"파일 읽기 오류: {str(e)}")

with col2:
    st.markdown("### 📊 AI가 생성한 제조 문서 초안")
    
    if st.session_state.output:
        st.markdown(st.session_state.output)
        
        # 다운로드 버튼
        filename = f"document_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        st.download_button(
            "📥 Markdown 파일 다운로드",
            st.session_state.output,
            file_name=filename,
            mime="text/markdown"
        )
    else:
        st.info("👈 왼쪽에서 입력하거나 빠른 시작 예시를 클릭하여 문서를 생성해보세요.")

# 자연어 처리
if generate_clicked:
    if not user_input.strip():
        st.warning(EMPTY_INPUT_WARNING)
        st.stop()
    
    try:
        # ① 로딩 UX
        show_loading_sequence(total_duration=5.0)
        
        # ② 완료 알림 (브랜딩 고정)
        st.success(DONE_MESSAGE)
        
        # ③ 자연어 라우팅 → 템플릿 키 결정
        template_key = route_template_from_text(user_input)
        
        if not template_key:
            st.warning("⚠️ 입력 내용을 작성해주세요.")
        else:
            # 디버그 정보 표시
            if st.session_state.debug_mode:
                # 매칭된 키워드 찾기
                import unicodedata, re
                text_clean = re.sub(r'\s+', ' ', unicodedata.normalize('NFC', user_input.lower()))
                
                defect_keywords = ["불량", "불량분석", "원인분석", "시정조치", "불량률", "반품", "대책"]
                qir_keywords = ["품질검사", "검사성적서", "성적서", "검사서", "qir"]
                delivery_keywords = ["납품", "납품보고서", "송장", "상업송장", "출고", "delivery"]
                
                hit_keywords = []
                for keyword in defect_keywords + qir_keywords + delivery_keywords:
                    if keyword in text_clean:
                        hit_keywords.append(keyword)
                
                with st.expander("🔍 디버그 정보", expanded=True):
                    st.write(f"**입력 텍스트:** `{user_input}`")
                    st.write(f"**매칭된 템플릿:** `{template_key}`")
                    st.write(f"**히트한 키워드:** `{', '.join(hit_keywords) if hit_keywords else '없음'}`")
            
            # ④ 컨텍스트 생성 (기존 샘플 컨텍스트 사용)
            context = get_sample_context(template_key)
            
            # ⑤ 템플릿 매핑 및 렌더링
            template = load_template_by_key(template_key)
            markdown_output = render_markdown(template, context)
            
            # ⑥ 세션/출력 업데이트
            st.session_state.output = markdown_output
            st.session_state.title = f"{template_key.upper()} (자연어 라우팅)"
            
            # 토스트 메시지
            template_names = {"qir": "품질검사서", "defect": "불량분석서", "delivery": "납품보고서"}
            template_name = template_names.get(template_key, template_key.upper())
            st.toast(f"자연어 라우팅: {template_name}", icon="✅")
            st.rerun()
    except Exception as e:
        st.error(f"문서 생성 중 오류 발생: {str(e)}")

# 푸터
st.markdown("---")
st.markdown(
    """
    <hr style="margin-top:40px; margin-bottom:10px;">
    <div style="text-align:center; font-size:14px; color:#666;">
        🧠 <b>PromptOS™ — 제조문서 자동화 AI 플랫폼</b><br>
        ERP·MES 연동으로 스마트 제조의 첫걸음을 시작하세요.<br><br>
        📜 <b>주요 특허 출원</b><br>
        • 범용 인공지능 거버넌스 시스템 및 그 작동 방법 — 출원번호: <b>특허-2025-0086532</b><br>
        • AI 기반 언어모델 오류 탐지 및 신뢰성 개선 시스템 및 그 방법 — 출원번호: <b>특허-2025-0068036</b><br>
        • 발화 기반 프롬프트 자동 생성 시스템 및 그 방법 — 출원번호: <b>특허-2025-0094464</b><br><br>
        © 2025 AI Insight. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)

# 특허 상세 보기 확장 옵션
with st.expander("📄 특허 상세 보기"):
    st.markdown("""
    **📋 특허 출원 상세 정보**
    
    **1. 범용 인공지능 거버넌스 시스템 및 그 작동 방법**
    - 출원번호: 특허-2025-0086532
    - 출원일: 2024-06-12
    - 출원인: 이상길
    - 특허청(KIPO) 출원 증명서 보유
    
    **2. AI 기반 언어모델 오류 탐지 및 신뢰성 개선 시스템 및 그 방법**
    - 출원번호: 특허-2025-0068036
    - 출원일: 2024-05-15
    - 출원인: 이상길
    - 특허청(KIPO) 출원 증명서 보유
    
    **3. 발화 기반 프롬프트 자동 생성 시스템 및 그 방법**
    - 출원번호: 특허-2025-0094464
    - 출원일: 2024-07-20
    - 출원인: 이상길
    - 특허청(KIPO) 출원 증명서 보유
    
    ---
    *모든 특허 출원은 특허청(KIPO)에 정식 제출되었으며, 출원 증명서를 보유하고 있습니다.*
    """)
