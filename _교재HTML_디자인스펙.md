# 한국어 교재 HTML 디자인 스펙 (확정본)

> 기준 샘플: `Stanford CME295_Lecture 3/섹션3_한국어교재.html` (2026-06-02 승인)
> 목적: 9개 강의 × 전 섹션 md → 가독성 높은 HTML. 동료 공무원 공유용.

## 기술 스택
- **정적 사전 렌더링** — md를 직접 HTML로 변환(런타임 마크다운 파서 안 씀). 오프라인에서 본문이 JS 없이 뜸.
- **CSS 단일 파일 내장** — 외부 프레임워크 0. 파일 하나로 공유.
- **영문 토글** — 순수 HTML `<details>/<summary>`. 기본 접힘, JS 불필요.
- **폰트** — Pretendard (CDN) + 시스템 폰트 폴백.
- **수식** — KaTeX (CDN, auto-render). `$$...$$` 디스플레이, `\(...\)` 인라인.
- **도식** — Mermaid (CDN, ESM). 오프라인이면 코드로 표시(graceful).
- **목차** — 사전 생성 + IntersectionObserver로 현재 위치 강조.

## 색상 (CSS 변수)
```
--bg:#FBF9F6  --paper:#fff  --ink:#1a1a1a  --ink-soft:#4a4744  --muted:#7a756f
--accent:#8C1515 (Stanford 카디널)  --accent-soft:#b9554f
--tint:#f6ebe9  --tint-2:#f3efe9  --line:#e7e1d9  --line-strong:#d8d0c5
--maxw:760px  --sidew:268px
```

## 콘텐츠 패턴 → HTML 매핑
| md 요소 | HTML 처리 |
|---|---|
| `> 원문 출처:` | 상단 `.source-banner` (📄, 타임스탬프 칩) |
| `### 블록 N — 제목` | `<h3><span class="badge">블록 N</span>제목</h3>` |
| `**영문 원문**` + blockquote | `<details class="en">` 기본 접힘. 타임스탬프 `(37:18)` → `<span class="ts">37:18</span>` |
| `**한국어 번역**` 단락 | `.ko` 카드 (좌측 카디널 보더) |
| `**용어 설명**` 목록 | `.terms` 의 `<dl>`. 영문 용어는 `.en-term` |
| 표 | `.table-wrap > table` (헤더 카디널, 줄무늬, 모바일 가로스크롤) |
| 복습 문제 | `.callout.review` (✏️) |
| 부록 실무 포인트 | `.callout.practice` (💡) |
| 강한 주의 단락 | `.callout.note` (⚠️) |
| 다음 섹션 예고 | `.next` 박스 |

## 보강 규칙 (원문에 없으면 선택 추가)
- softmax/온도 등 산문으로 풀린 공식 → KaTeX로 병기. **원문 산문도 함께 유지**(삭제 금지).
- 트리/흐름 설명 → Mermaid 도식. **수치가 원문에 없으면 "개념도"임을 캡션에 명시**(임의값 오해 방지).

## 반응형 / 인쇄
- ≤900px: 사이드바 → ☰ 드로어, 본문 1단 풀폭.
- `@media print`: 사이드바·영문 토글 숨김. 한국어 위주 PDF 출력.

## 파일 규칙
- 출력 위치: 원본 md와 **같은 폴더**, 확장자만 `.html`.
- 원본 md는 **수정하지 않음**.
