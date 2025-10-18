# 제조_PromptOS — Manufacturing AI Document Automation Platform

🏭 **ERP·MES 기반 제조문서 자동화 및 보고서 생성 플랫폼**

## 📌 개요
PromptOS는 제조기업의 ERP·MES·QMS 데이터를 기반으로  
품질검사서, 납품보고서, SOP 등 제조문서를 자동 생성하는  
AI 거버넌스 기반 문서 자동화 솔루션입니다.

## 🚀 주요 기능
- **자연어 입력 기반 문서 생성**: "품질검사서 작성해줘" 등 자연어로 문서 요청
- **ERP/MES 데이터 자동 매핑**: CSV/Excel 업로드로 실시간 데이터 연동
- **AI 거버넌스 기반 검증**: 도메인 특화 규칙 엔진으로 Zero Hallucination 보장
- **3단계 로딩 UX**: ERP·MES 데이터 수집 과정을 시각적으로 표시
- **즉시 다운로드**: 생성된 문서를 Markdown 형식으로 즉시 다운로드

## 🧠 기술 구조
```
ERP/MES → Data Adapter → PromptOS Engine → LLM + Rule Engine → 검증/출력
```

### 핵심 컴포넌트
- **Intent Analyzer**: 자연어 입력을 제조 문서 유형으로 분류
- **Rule Engine**: 도메인 특화 검증 규칙 적용
- **Template System**: Jinja2 기반 동적 문서 생성
- **Governance Layer**: AI 출력 신뢰성 보장

## 🏭 지원 문서 유형
- **품질검사성적서 (QIR)**: 검사 결과, 판정, 특이사항
- **불량분석서**: 불량 유형, 원인 분석, 시정조치
- **납품보고서**: 납품 내역, 거래처 정보, 금액 정산
- **생산일지**: 생산 수량, 불량 현황, 특이사항
- **원가계산서**: 재료비, 노무비, 간접비 산출

## 🧩 실행 방법

### 1. 환경 설정
```bash
# 프로젝트 디렉토리로 이동
cd "C:\Users\LeeSG\Desktop\제조_PromptOS"

# 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 애플리케이션 실행
```bash
# Streamlit 앱 실행
streamlit run manufacturing_ai_dashboard.py --server.port 8515

# 브라우저에서 접속
# http://localhost:8515
```

### 3. 사용 방법
1. **자연어 입력**: "품질검사서 작성해줘" 등 입력
2. **빠른 시작**: 품질검사서, 불량분석서, 납품보고서 버튼 클릭
3. **CSV 업로드**: 제조 데이터 파일 업로드하여 문서 생성
4. **결과 확인**: 우측 패널에서 생성된 문서 확인 및 다운로드

## 📊 기술 특징

### AI 거버넌스
- **Zero Hallucination**: 도메인 특화 규칙으로 AI 출력 검증
- **Traceability**: 모든 데이터의 출처와 변환 과정 추적
- **Audit Trail**: 완전한 감사 추적 로그 제공

### 하이브리드 AI 엔진
- **Rule Engine**: 제조 도메인 규칙 기반 검증
- **LLM Integration**: 자연어 이해 및 문서 생성
- **Validation Layer**: 다중 검증 단계로 신뢰성 보장

## 🏆 특허 출원 현황
- **범용 인공지능 거버넌스 시스템** (특허-2025-0086532)
- **AI 기반 언어모델 오류 탐지 시스템** (특허-2025-0068036)
- **발화 기반 프롬프트 자동 생성 시스템** (특허-2025-0094464)

## 🎯 공모전 활용
이 솔루션은 **한국 제조AI 솔루션 공모전** 제출용으로 개발되었으며,  
실제 제조 현장에서 즉시 적용 가능한 문서 자동화 기능을 제공합니다.

### 평가 포인트
- ✅ **기술 혁신성**: AI 거버넌스 기반 Zero Hallucination
- ✅ **실용성**: 실제 제조 문서 자동 생성 데모
- ✅ **확장성**: ERP/MES 연동 가능한 아키텍처
- ✅ **신뢰성**: 특허 출원 기술 기반

## 📁 프로젝트 구조
```
제조_PromptOS/
├── manufacturing_ai_dashboard.py    # 메인 Streamlit 애플리케이션
├── templates/                       # Jinja2 템플릿 파일들
│   ├── index.json                   # 템플릿 인덱스
│   ├── qir_ko.md.j2                # 품질검사서 템플릿
│   ├── defect_analysis.md.j2       # 불량분석서 템플릿
│   └── delivery_report.md.j2       # 납품보고서 템플릿
├── components/                      # UI 컴포넌트
├── static/                         # 정적 파일
├── requirements.txt                # Python 의존성
├── README.md                       # 프로젝트 문서
└── .gitignore                      # Git 제외 파일
```

## 🔧 개발 환경
- **Python**: 3.8+
- **Streamlit**: 1.39.0
- **Jinja2**: 3.1.4
- **Pandas**: 2.0.3
- **OpenPyXL**: 3.1.2

## 📞 문의
- **개발자**: 이상길
- **이메일**: [연락처]
- **프로젝트**: PromptOS Manufacturing AI Solution

---
**© 2025 AI Insight. All rights reserved.**  
**Patent Applications: PromptOS | Governance Engine | Universal Governance**