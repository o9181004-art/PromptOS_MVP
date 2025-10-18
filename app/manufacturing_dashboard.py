import json, os, datetime
import streamlit as st
from jinja2 import Template

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
INDEX_PATH = os.path.join(TEMPLATE_DIR, "index.json")

@st.cache_data
def load_index():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_template_by_key(key: str) -> str:
    idx = load_index()
    fname = idx["map"].get(key)
    if not fname:
        raise ValueError(f"템플릿 키를 찾을 수 없음: {key}")
    path = os.path.join(TEMPLATE_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def render_markdown(template_str: str, ctx: dict) -> str:
    ctx = {**ctx, "today": datetime.date.today().isoformat()}
    return Template(template_str).render(**ctx)

def example_context(key: str) -> dict:
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
    if key == "delivery":
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

# 페이지 설정
st.set_page_config(
    page_title="🏭 제조AI 솔루션 - PromptOS", 
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'last_output' not in st.session_state:
    st.session_state.last_output = None

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
    
    # 입력 영역
    user_input = st.text_area(
        "자연어 입력",
        value=st.session_state.user_input,
        placeholder="예: 오늘 생산된 제품의 품질검사 성적서를 작성해줘...",
        height=120,
        key="main_input"
    )
    
    st.session_state.user_input = user_input
    
    # 버튼 영역
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("🔄 입력창 초기화", use_container_width=True, type="secondary"):
            st.session_state.user_input = ""
            st.session_state.last_output = None
            st.rerun()
    
    with btn_col2:
        generate_clicked = st.button("⚡ 제조문서 생성하기", use_container_width=True, type="primary")
    
    # 빠른 시작 예시
    st.markdown("### 🚀 빠른 시작 예시")
    
    idx = load_index()
    quick = {q["label"]: q["key"] for q in idx["quickstart"]}
    
    # 2x3 그리드로 버튼 배치
    grid_cols = st.columns(3)
    for i, (label, key) in enumerate(quick.items()):
        col_idx = i % 3
        if grid_cols[col_idx].button(f"📋 {label}", key=f"quick_{key}", use_container_width=True):
            try:
                template = load_template_by_key(key)
                context = example_context(key)
                markdown_output = render_markdown(template, context)
                st.session_state.last_output = markdown_output
                st.success(f"✅ {label} 문서가 생성되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")

with col2:
    st.markdown("### 📊 AI가 생성한 제조 문서 초안")
    
    if st.session_state.last_output:
        st.markdown(st.session_state.last_output)
        
        # 다운로드 버튼
        st.download_button(
            "📥 Markdown 파일 다운로드",
            st.session_state.last_output,
            file_name=f"제조문서_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    else:
        st.info("👈 왼쪽에서 입력하거나 빠른 시작 예시를 클릭하여 문서를 생성해보세요.")

# 자연어 처리
if generate_clicked:
    if user_input.strip():
        # 키워드 기반 라우팅
        if "검사" in user_input or "성적서" in user_input or "qir" in user_input.lower():
            route = "qir"
        elif "납품" in user_input or "delivery" in user_input.lower():
            route = "delivery"
        elif "생산" in user_input or "일지" in user_input:
            route = "prodlog"
        elif "불량" in user_input or "분석" in user_input:
            route = "defect"
        elif "원가" in user_input or "비용" in user_input:
            route = "cost"
        else:
            route = "qir"  # 기본값
        
        try:
            template = load_template_by_key(route)
            context = example_context(route)
            markdown_output = render_markdown(template, context)
            st.session_state.last_output = markdown_output
            st.success(f"✅ {route.upper()} 문서가 생성되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"문서 생성 중 오류 발생: {str(e)}")
    else:
        st.warning("⚠️ 먼저 작업 내용을 입력해주세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>🏭 PromptOS</strong> - 제조기업의 문서작업을 자동화하는 AI 솔루션</p>
    <p>ERP·MES 연동으로 스마트 제조의 첫걸음 시작하세요</p>
</div>
""", unsafe_allow_html=True)
