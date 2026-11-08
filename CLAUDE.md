# CLAUDE.md — platinum-ai-demo

사내 경진대회용 시연 키트. 이 저장소는 **공개**이며 GitHub Pages로 배포된다: https://donghyun1park-web.github.io/platinum-ai-demo/ (보고서 QR이 이 주소를 가리킨다).

## 먼저 읽을 것

- 작업 맥락(지금까지의 결정, 현재 상태, 다음 할 일)은 비공개 저장소 `donghyun1park-web/platinum-ai-workspace`의 `HANDOFF.md`에 있다. 같은 상위 폴더에 clone해 두고 `../platinum-ai-workspace/HANDOFF.md`를 먼저 읽는다.
- 사용자와는 한국어로 대화한다.

## 규칙

- 코드는 `src/the_platinum_ai_simulator_v3.html`에서만 고친다. `index.html`은 빌드 산출물이다.
  ```bash
  python tools/build_offline.py src/the_platinum_ai_simulator_v3.html index.html
  ```
- `main`에 push하면 1~2분 안에 Pages에 반영된다. 저장소 이름을 바꾸지 않는다(주소가 바뀌면 보고서 QR이 깨진다).
- 내부 자료(예산, 제안자 실명·직급, 리뷰 결과, 보고서 원문)는 이 공개 저장소에 커밋하지 않는다. 비공개 저장소에 둔다.
- `<meta name="robots" content="noindex, nofollow">`를 유지한다.
- Gemini API 키는 코드·커밋·로그 어디에도 넣지 않는다. 시연 키트는 사용자가 화면에서 입력하는 방식만 쓴다.
- 서드파티 라이브러리 버전·해시는 `tools/build_offline.py`에 고정돼 있다. 바꾸면 `THIRD_PARTY_NOTICES.md`도 함께 고친다.

## 확인 방법

1. 저장소 폴더에서 `python -m http.server 8765`를 띄우고 `http://localhost:8765/`를 연다.
2. 모드 1: 로그에 "3D 대표 평면 5개 상태 렌더 완료"가 뜨고, 4개 탭(비포·애프터, 4대 테마, 걸어보기, X-Ray)이 모두 그려지는지 본다.
3. 모드 2: "지금 실행"을 눌러 자동 테스트 8개가 PASS인지 본다.
4. 375px 폭(휴대폰)에서도 화면이 가려지거나 겹치지 않는지 본다.
