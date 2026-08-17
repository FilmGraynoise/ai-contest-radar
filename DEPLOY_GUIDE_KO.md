# AI Contest Radar 초보자용 배포 가이드

이 문서는 코딩을 모르는 사람 기준입니다. 아래 순서만 따라가면 됩니다.

---

## 0. 준비할 계정 4개

1. GitHub
2. Supabase
3. Google AI Studio
4. Vercel

모두 무료 계정으로 시작할 수 있습니다.

---

## 1. Supabase 데이터베이스 만들기

### 1-1. 프로젝트 생성

Supabase에 로그인 → `New project`

프로젝트 이름 예시:

`ai-contest-radar`

Database Password는 반드시 따로 저장해 두세요.

### 1-2. 테이블 생성

Supabase 왼쪽 메뉴 → `SQL Editor` → `New query`

이 프로젝트의 아래 파일 내용을 전부 복사해서 실행합니다.

`sql/schema.sql`

성공하면 `contests` 테이블이 생깁니다.

### 1-3. 테스트 데이터 넣기

화면부터 확인하고 싶다면:

`sql/sample_data.sql`

내용을 SQL Editor에서 한 번 실행합니다.

나중에 테스트 데이터는 Table Editor에서 삭제해도 됩니다.

---

## 2. Supabase 키 3개 확인

Supabase 프로젝트의 Settings / API 관련 화면에서 다음 값을 확인합니다.

1. Project URL
2. Publishable key 또는 anon/public key
3. Secret key 또는 service_role key

용도가 완전히 다릅니다.

- Publishable/anon 키: 웹 화면 읽기용
- service_role/secret 키: 크롤러가 DB에 쓰는 용도

`service_role` 또는 Secret key는 절대로 `web/config.js`에 넣지 마세요.

---

## 3. 웹페이지용 config.js 수정

`web/config.js`를 열면 아래처럼 되어 있습니다.

```js
window.APP_CONFIG = {
  SUPABASE_URL: "YOUR_SUPABASE_URL",
  SUPABASE_PUBLIC_KEY: "YOUR_SUPABASE_PUBLISHABLE_KEY"
};
```

두 값만 바꿉니다.

예:

```js
window.APP_CONFIG = {
  SUPABASE_URL: "https://abcdefgh.supabase.co",
  SUPABASE_PUBLIC_KEY: "sb_publishable_xxxxxxxxx"
};
```

Publishable/anon 키는 공개 웹 클라이언트에서 사용하는 키입니다. 이 프로젝트는 RLS 정책으로 읽기만 허용합니다.

---

## 4. GitHub에 프로젝트 올리기

GitHub → `New repository`

Repository name:

`ai-contest-radar`

처음에는 Public으로 만드는 것이 가장 간단합니다.

그 다음 압축을 푼 `ai-contest-radar` 폴더의 파일들을 저장소에 업로드합니다.

중요:

`.github` 폴더도 반드시 올라가야 합니다.

---

## 5. Gemini API Key 만들기

Google AI Studio에서 API Key를 생성합니다.

이 키는 웹페이지에 넣지 않습니다.

GitHub에 비밀값으로 저장합니다.

---

## 6. GitHub Secrets 등록

GitHub 저장소 → `Settings` → `Secrets and variables` → `Actions`

`New repository secret`를 눌러 다음 3개를 각각 만듭니다.

### Secret 1

Name:

`GEMINI_API_KEY`

Value:

Google AI Studio에서 발급받은 Gemini API Key

### Secret 2

Name:

`SUPABASE_URL`

Value:

Supabase Project URL

### Secret 3

Name:

`SUPABASE_SERVICE_ROLE_KEY`

Value:

Supabase Secret/service_role key

주의: public/anon 키가 아닙니다.

---

## 7. 크롤러 첫 실행

GitHub 저장소 → `Actions`

왼쪽에서:

`AI Contest Crawl`

선택

→ `Run workflow`

→ 다시 `Run workflow`

실행 로그 마지막에 대략 다음 형태가 보이면 정상입니다.

```text
=== AI Contest Radar ===
discovered: ...
analyzed: ...
saved: ...
errors: ...
```

Supabase → `Table Editor` → `contests`

공모전 데이터가 들어왔는지 확인합니다.

### 데이터가 0건이어도 바로 고장이라고 판단하지 마세요

다음 상황이면 0건일 수 있습니다.

- 최근 목록에 AI 관련 창작 공모전이 없음
- 사이트 HTML 구조가 변경됨
- 해당 사이트가 자동 접근을 제한함
- Gemini 무료 한도/키 설정 문제

Actions 로그의 `[WARN]`, `[ERROR]`를 보면 원인을 확인할 수 있습니다.

---

## 8. Vercel에 웹페이지 올리기

Vercel 로그인 → `Add New` → `Project`

GitHub의 `ai-contest-radar` 저장소를 선택합니다.

Root Directory를:

`web`

으로 지정합니다.

Framework Preset은 `Other` 또는 자동 감지된 정적 사이트 설정을 사용하면 됩니다.

그 다음 `Deploy`.

배포가 끝나면 다음과 비슷한 주소가 생깁니다.

```text
https://ai-contest-radar-xxxx.vercel.app
```

이 주소가 실제 웹사이트 주소입니다.

---

## 9. 자동 업데이트

`.github/workflows/crawl.yml`에는 한국시간 기준으로 다음 두 시각에 실행되도록 UTC cron이 들어 있습니다.

- 09:00 KST
- 18:00 KST

컴퓨터를 꺼도 GitHub Actions가 실행합니다.

원할 때는 GitHub Actions에서 `Run workflow`로 수동 실행할 수도 있습니다.

---

## 10. 사이트에서 보이는 AI 상태

- AI 필수: 생성형 AI 사용이 응모 조건에 명시됨
- AI 가능: AI 사용이 허용되지만 필수는 아님
- 조건부: 일부 사용만 허용되거나 별도 표기/증빙 조건 존재
- 확인 필요: 공고 내용만으로 명확히 판단하기 어려움
- AI 금지: AI 사용 불가

기본 화면은 AI 필수/가능/조건부/확인 필요 항목을 보여주고 AI 금지는 숨깁니다.

---

## 11. 문제 발생 시 가장 먼저 확인할 것

### 웹은 열리는데 카드가 안 나옴

1. `web/config.js` URL/키 확인
2. Supabase `contests` 테이블에 데이터가 있는지 확인
3. 브라우저 개발자도구 Console 확인

### GitHub Actions가 빨간색

Actions → 실패한 실행 → `crawl` → 로그 확인

가장 흔한 원인:

- Secret 이름 오타
- Gemini API Key 오류
- Supabase service_role/secret key 오류
- 사이트에서 403/429 반환
- 사이트 HTML 구조 변경

### 특정 사이트만 계속 실패

수집처 사이트 정책이나 HTML 변경 가능성이 큽니다.

`crawler/sources/` 안의 해당 파일만 수정하면 됩니다.

---

## 12. 다음 업그레이드 추천 순서

1. 링커리어는 이용정책/허용 범위를 별도로 확인한 뒤 추가
2. 동일 공모전 중복 판정 강화
3. D-7 / D-3 마감 알림
4. 즐겨찾기
5. 개인 역량 기반 추천 점수
6. 공모전 원문 변경 감지
7. 관리자 화면

MVP를 먼저 안정적으로 돌린 뒤 추가하는 것을 권장합니다.
