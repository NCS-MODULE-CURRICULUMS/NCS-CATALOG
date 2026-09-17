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
| `gen_course_page.py` | `courses/cN.html` — 모든 과정 페이지를 한 템플릿에서 |
| `gen_lp_html.py` | `lesson-plans/c1-mNN.html` — 표준 강의 교안 6시트 |
| `gen_study.py` | `study/cN-mNN.html` — 준비 교안의 단계를 카드로 |
| `gen_xlsx_view.py` | `docs/표준강의교안-샘플.html` (xlsx → 정적 HTML) |
| `export_status.py` | `data/curriculum-status.json` — 비공개 교안의 **상태만** 공개 데이터로 |
| `gen_curriculum.py` | `assets/curriculum.js` · `curriculum/*.html` 32장 |

## 커리큘럼 페이지

조직의 커리큘럼 저장소 4종은 **비공개**고 사이트는 **공개**입니다. 그래서
교안 내용은 두고 상태만 뽑아 내보냅니다.

```bash
python NCS-CATALOG/scripts/gen/export_status.py    # 먼저 — 상태 수집
python NCS-CATALOG/scripts/gen/gen_curriculum.py   # 그 다음 — 페이지 생성
```

`export_status.py` 가 **조직에서 비공개 저장소를 읽는 유일한 자리**입니다.
나가는 것은 능력단위코드 · 시간 · 수준 · 차시 · 진척 단계 · 산출물 유무뿐이고,
교안 본문 · 평가 문항 · 모범답안은 나가지 않습니다.

진척은 파일 유무가 아니라 **4단계**로 잽니다 — 279바이트짜리 골격도 파일이라
`teaching-plan.md` 가 있다는 사실만으로는 아무것도 알 수 없기 때문입니다.

| 단계 | 뜻 |
|---|---|
| 골격 | 섹션 제목만 있는 틀 |
| 작성중 | 표준 강의 교안 6시트를 씌웠고 `(채울 자리)` 가 남음 |
| 완성 | 빈칸 없음 · 검수 전 |
| 검수 | frontmatter `status: ready` |

`mapping-domain.yml` 의 `primary` 세분류만 재고로 셉니다. 운영 과정이 `related`
세분류의 능력단위를 쓰고 있으면 **재고 밖 편성**으로 도메인 페이지에 경고가 뜹니다 —
집계가 조용히 어긋나는 것을 막습니다.

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
