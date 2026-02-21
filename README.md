# githubmaster

AI 무료/할인 이벤트를 로컬에서 수집하고 변경점을 추적하는 MVP 프로젝트입니다.

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main run-once
streamlit run app/ui/dashboard.py
```

## 기능
- 공식 페이지 기반 이벤트/혜택 키워드 탐지
- SQLite 저장 (current/history)
- 신규/종료 이벤트 diff 계산
- Streamlit 로컬 대시보드

## 주의
- 실제 운영 전에는 수집 대상의 robots.txt / ToS 준수 여부를 확인하세요.
- 현재 파서는 MVP 수준의 키워드 탐지로 구현되어 있습니다.
