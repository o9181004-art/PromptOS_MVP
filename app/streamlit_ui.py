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
    # today 헬퍼 주입
    ctx = {**ctx, "today": datetime.date.today().isoformat()}
    return Template(template_str).render(**ctx)

def example_context(key: str) -> dict:
    # 퀵스타트 누르면 이 예시 컨텍스트로 바로 생성
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
    if key == "prodlog":
        return {
            "doc_no": "PL-2025-001",
            "date": "2025-01-18",
            "work_team": "A조",
            "worker": "김제조",
            "production": [
                {"time": "09:00-10:00", "item_code": "P-1001", "item_name": "알루미늄 브래킷", "prod_qty": 50, "defect_qty": 2, "status": "완료", "remarks": "정상"},
                {"time": "10:00-11:00", "item_code": "P-1001", "item_name": "알루미늄 브래킷", "prod_qty": 48, "defect_qty": 1, "status": "완료", "remarks": "정상"},
                {"time": "11:00-12:00", "item_code": "P-2002", "item_name": "스테인리스 볼트", "prod_qty": 200, "defect_qty": 5, "status": "완료", "remarks": "정상"}
            ],
            "total_prod_qty": 298,
            "total_defect_qty": 8,
            "yield_rate": "97.3",
            "daily_remarks": "전반적으로 양호한 생산성",
            "evidence": "MES 생산 데이터"
        }
    if key == "defect":
        return {
            "doc_no": "DA-2025-001",
            "date": "2025-01-18",
            "item_code": "P-1001",
            "item_name": "알루미늄 브래킷",
            "lot_no": "LOT-250118-A",
            "analyst": "박품질",
            "defects": [
                {"type": "표면불량", "qty": 5, "rate": 50, "cause": "가공조건 부적절", "action": "가공속도 조정"},
                {"type": "치수불량", "qty": 3, "rate": 30, "cause": "공구 마모", "action": "공구 교체"},
                {"type": "기타", "qty": 2, "rate": 20, "cause": "작업자 실수", "action": "교육 강화"}
            ],
            "total_defect_qty": 10,
            "defect_rate": "2.7",
            "main_cause": "가공조건 부적절",
            "improvement_plan": "가공속도 최적화 및 공구 교체 주기 단축",
            "immediate_action": "현재 LOT 재가공 처리",
            "prevention_action": "가공조건 표준화",
            "verification_method": "다음 LOT 검사 강화",
            "evidence": "품질관리 시스템"
        }
    if key == "cost":
        return {
            "doc_no": "CS-2025-001",
            "date": "2025-01-18",
            "item_code": "P-1001",
            "item_name": "알루미늄 브래킷",
            "quantity": 1000,
            "calculator": "최원가",
            "costs": [
                {"item": "재료비", "unit_price": 800, "qty": 1000, "amount": 800000, "ratio": 64},
                {"item": "인건비", "unit_price": 200, "qty": 1000, "amount": 200000, "ratio": 16},
                {"item": "제조간접비", "unit_price": 150, "qty": 1000, "amount": 150000, "ratio": 12},
                {"item": "기타비용", "unit_price": 100, "qty": 1000, "amount": 100000, "ratio": 8}
            ],
            "total_manufacturing_cost": "1,250,000 원",
            "manufacturing_overhead": "150,000 원",
            "total_cost": "1,250,000 원",
            "unit_cost": "1,250 원",
            "selling_price": "1,500 원",
            "target_margin": "20",
            "expected_profit": "250,000 원",
            "evidence": "ERP 원가 데이터"
        }
    return {}

st.set_page_config(page_title="PromptOS – 제조 문서 자동화", layout="wide")
st.title("PromptOS")
st.caption("ERP·MES 데이터 기반 제조문서 자동화 및 보고서 생성 플랫폼")

# 세션 상태 초기화
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'last_output' not in st.session_state:
    st.session_state.last_output = None
if 'last_title' not in st.session_state:
    st.session_state.last_title = ""

idx = load_index()
quick = {q["label"]: q["key"] for q in idx["quickstart"]}

# 좌/우 2컬럼
c1, c2 = st.columns([1,1])
with c1:
    st.subheader("제조 현장 데이터를 입력하여 문서를 생성하세요")
    
    # 텍스트 입력 (세션 상태와 연동)
    user_text = st.text_area(
        "자연어 입력", 
        value=st.session_state.user_input,
        placeholder="예: 오늘 생산된 제품의 품질검사 성적서를 작성해줘...", 
        height=160,
        key="user_input_text"
    )
    
    # 입력값을 세션 상태에 저장
    st.session_state.user_input = user_text
    
    colA, colB = st.columns([1,1])
    with colA:
        if st.button("입력창 초기화", use_container_width=True):
            st.session_state.user_input = ""
            st.session_state.last_output = None
            st.session_state.last_title = ""
            st.rerun()
    with colB:
        gen_clicked = st.button("제조문서 생성하기", type="primary", use_container_width=True)

    st.markdown("#### 빠른 시작 예시")
    qcols = st.columns(len(quick))
    for i, (label, key) in enumerate(quick.items()):
        if qcols[i].button(label, key=f"quick_{key}"):
            # 예시 컨텍스트로 즉시 렌더
            t = load_template_by_key(key)
            md = render_markdown(t, example_context(key))
            st.session_state["last_output"] = md
            st.session_state["last_title"] = f"{label} (샘플)"
            st.toast(f"{label} 샘플을 생성했습니다.", icon="✅")
            st.rerun()

with c2:
    st.subheader("AI가 생성한 제조 문서 초안")
    output = st.session_state.get("last_output")
    if output:
        st.markdown(output)
        st.download_button("Markdown 다운로드", output, file_name="document.md")
    else:
        st.info("왼쪽에서 입력하거나 '빠른 시작 예시'를 눌러 문서를 생성해보세요.")

# 자연어 → 기본 템플릿 라우팅 (아주 단순 라우팅)
if gen_clicked:
    if user_text.strip():
        # 키워드로 간단 매핑 (임시 라우팅)
        route = "qir" if "검사" in user_text or "성적서" in user_text else \
                "delivery" if "납품" in user_text else "prodlog"
        t = load_template_by_key(route)
        # 실제로는 LLM 파싱/폼 입력으로 context 생성해야 하나, MVP용으로 기본 예시 사용
        ctx = example_context(route)
        md = render_markdown(t, ctx)
        st.session_state["last_output"] = md
        st.session_state["last_title"] = f"{route} (자연어 라우팅)"
        st.toast("문서를 생성했습니다.", icon="✨")
        st.rerun()
    else:
        st.warning("먼저 작업 내용을 입력해주세요.")
