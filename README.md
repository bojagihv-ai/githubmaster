# githubmaster

AI 무료/할인 이벤트를 로컬에서 수집하고 변경점을 추적하는 MVP 프로젝트입니다.

## 진행 상태(현재)
- [x] 1단계: 프로젝트 골격/DB/스케줄러/기본 UI
- [x] 2단계: NEW/UPDATED/ENDED diff 추적
- [x] 3단계: 더블클릭 실행 파일 추가
- [ ] 4단계: 소스 확장(Claude/Perplexity/국내 서비스)
- [ ] 5단계: 알림 채널(텔레그램/디스코드/이메일)

## 빠른 시작

```bash
python -m app.main run-once
python -m app.main dashboard
```

> `run-once`는 표준 라이브러리 기반으로 동작합니다. (설정은 `config/sources.json` fallback 지원)

## 더블클릭 실행
- macOS/Linux: `run_dashboard.command`
- Windows: `run_dashboard.bat`

## UI 실행 방식
1. streamlit 설치되어 있으면 Streamlit 대시보드 실행
2. streamlit 미설치면 tkinter 대시보드로 자동 전환

## 기능
- 공식 페이지 기반 이벤트/혜택 탐지(정규식+키워드)
- SQLite 저장 (`events_current`, `events_history`)
- 신규/변경/종료(diff) 계산
- 더블클릭 실행 스크립트 제공

## 주의
- 실제 운영 전에는 수집 대상의 robots.txt / ToS 준수 여부를 확인하세요.
- 현재 파서는 MVP 수준이며 사이트 구조 변경 시 룰 보강이 필요합니다.
