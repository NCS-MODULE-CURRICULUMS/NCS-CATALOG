# 생성 스크립트

`COURSE-MANAGEMENT` 사이트와 `CURRICULUM-*` 교안을 만들어 내는 스크립트입니다.
손으로 쓴 결과물이 아니라 여기서 찍어내므로, 결과물을 고치기 전에 이쪽을 먼저 봅니다.

| 스크립트 | 산출물 |
|---|---|
| `ncs_20010707.py` | (데이터) 생성형AI엔지니어링 능력단위요소 35 · 수행준거 128 — ncs.go.kr 원문 |
| `gen_pilot6.py` | `CURRICULUM-AI-DATA/modules/20010707_*/teaching-plan.md` 9개 (6시트 구조) |
| `gen_site.py` | `COURSE-MANAGEMENT` 의 c1 과정 데이터 · `modules/c1-mNN.html` |
| `gen_course2.py` | c2 과정 데이터 (`modules-c2.js` · `locks-c2.js` · `courses.js`) |
| `gen_c2_detail.py` | `modules/c2-mNN.html` 17개 (카드 UI) |
| `gen_xlsx_view.py` | `docs/표준강의교안-샘플.html` (xlsx → 정적 HTML) |

## 실행 위치

조직 루트(각 repo 의 부모 폴더)에서 돌립니다. 스크립트가 `parents[1]` 을 조직 루트로 잡습니다.

```
조직루트/
  NCS-CATALOG/scripts/gen/*.py   ← 여기
  COURSE-MANAGEMENT/
  CURRICULUM-AI-DATA/
```

```bash
python NCS-CATALOG/scripts/gen/gen_pilot6.py
python NCS-CATALOG/scripts/gen/gen_c2_detail.py
```

`gen_xlsx_view.py` 는 `openpyxl` 이 필요합니다.
