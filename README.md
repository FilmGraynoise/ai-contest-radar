# AI Contest Radar

국내 공모전 사이트의 공개 공고를 주기적으로 확인하고, 생성형 AI 활용 가능 여부와 창작 분야를 분석해 한 화면에 보여주는 개인용 MVP입니다.

## MVP 구성

- 수집처: 씽굿, 위비티
- 수집기: Python + Requests + BeautifulSoup
- AI 분석: Gemini API Structured Output
- 데이터베이스: Supabase
- 자동 실행: GitHub Actions (매일 09:00 / 18:00 KST)
- 웹: 정적 HTML/CSS/JS
- 배포: Vercel 권장
- 화면 기능: 검색, 그림/영상/글/음악/기타 필터, AI 필수/가능 필터, 마감 임박순/신규순/상금순

## 폴더

```text
ai-contest-radar/
├─ .github/workflows/crawl.yml
├─ crawler/
│  ├─ main.py
│  ├─ analyzer.py
│  ├─ storage.py
│  ├─ utils.py
│  ├─ requirements.txt
│  └─ sources/
│     ├─ base.py
│     ├─ thinkcontest.py
│     └─ wevity.py
├─ sql/
│  ├─ schema.sql
│  └─ sample_data.sql
├─ web/
│  ├─ index.html
│  ├─ styles.css
│  ├─ app.js
│  └─ config.js
├─ .gitignore
└─ DEPLOY_GUIDE_KO.md
```

## 가장 먼저 할 일

`DEPLOY_GUIDE_KO.md`를 위에서부터 그대로 따라가면 됩니다.

## 중요한 운영 원칙

이 MVP는 원문 전체를 재배포하는 서비스가 아니라 공개 메타정보와 자체 AI 요약을 저장하고 원문으로 연결하는 구조입니다.

각 사이트의 이용약관, robots.txt, 접근 제한 정책이 바뀔 수 있습니다. 차단 회피, 로그인 우회, CAPTCHA 우회 기능은 넣지 않았습니다. 응답 코드가 403/429이거나 구조가 바뀌면 해당 수집처는 실패 로그만 남기고 종료하도록 설계했습니다.

실제 응모 전에는 반드시 주최사 공식 공고를 다시 확인하세요.
