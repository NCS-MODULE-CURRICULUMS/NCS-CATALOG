# NCS-CATALOG

**조직 전체의 단일 기준점(SSOT).** NCS 분류체계·능력단위 원천 데이터와 수집 스크립트만 둡니다.
교안·실습·평가문항은 여기 두지 않습니다 → `CURRICULUM-*` repo.

> 공개 범위: **public** (출처가 공공 데이터이고, 조직 얼굴 역할을 합니다)

## 무엇이 들어 있나

```
data/
  raw/20.json              # ncs.go.kr 원본 트리 (대분류별)
  taxonomy.csv             # 세분류 flat (대/중/소/세 + 능력단위수 + 개정차수)
  competency-units.csv     # 능력단위 flat (10자리코드_YYvN + 명 + 상위분류)
  mapping-domain.yml       # ★ 우리 판단: 도메인 ↔ 세분류 매핑
  hrdnet/                  # 고용24 훈련과정 수집 결과 (예정)
scripts/
  fetch_ncs.py             # NCS 수집 → raw/*.json + *.csv
  scaffold_modules.py      # mapping 기준으로 CURRICULUM-* 모듈 폴더 생성
docs/
  NCS-분류체계-20-정보통신.md
  국기훈련-과정개발-가이드.md
```

## 현재 데이터 (2026-09-16 수집, NCS 29차)

- 대분류 `20. 정보통신` : 중분류 3 / 소분류 22 / **세분류 123** / **능력단위 1,254**
- NCS 학습모듈(LM) PDF : **291건 / 약 3.0GB** (우리 도메인 primary 28개 세분류, 능력단위별 최신버전)
  - 인덱스: `data/learning-modules.csv` (파일 키 포함 → 누구나 재현 가능)
  - 실물 PDF는 `.gitignore` 처리. `scripts/fetch_ncs_modules.py --download --latest-only` 로 각자 내려받음

### 학습모듈이 없는 primary 세분류 (직접 개발 필요)

| 코드 | 세분류 | 상태 |
|---|---|---|
| `20010602` | 정보보호진단·분석 | **0건** — 모의해킹·취약점진단·ISMS 심사 전부 교재 없음 |
| `20010707` | 생성형AI엔지니어링 | **0건** — 25v1 신설, 프롬프트/파인튜닝 자체 개발 |
| `20010603` | 보안사고분석대응 | 7개 중 **1건**만 존재 |
| `20010708` | 로우코드 AI Agent | 능력단위 자체가 미공개(0개) → 편성 불가 |

## 사용법

```bash
python scripts/fetch_ncs.py              # 대분류 20
python scripts/fetch_ncs.py 20 19 15     # 여러 대분류
python scripts/fetch_ncs.py --all        # 24개 대분류 전체
python scripts/scaffold_modules.py       # 커리큘럼 모듈 폴더 스켈레톤 생성
```

`fetch_ncs.py`는 ncs.go.kr의 NCS 검색 화면이 쓰는 조회 API를 그대로 호출합니다
(`getMclassCd / getSclassCd / getSubdCd / getCompeUnit`). 인증키 불필요, 요청 간 0.15s 대기.

## 데이터 규칙

**능력단위코드 = 10자리 + `_YYvN`**

```
2001070705_25v1
└┬┘└┬┘└┬┘└┬┘└┬┘  └─┬─┘
 20 01 07 07  05    25v1
 대  중  소  세  능력단위  개발연도25년·v1
                        → 생성형AI엔지니어링 / 프롬프트 구현
```

앞 8자리(`20010707`)가 **세분류코드**이고, 이게 모든 폴더명·front-matter의 1급 키입니다.

## NCS 개정 대응

NCS는 매년 개정됩니다(현재 29차). 개정 시:
1. `fetch_ncs.py` 재실행 → CSV diff 발생
2. diff로 **신설/폐지/코드변경 능력단위** 확인
3. `mapping-domain.yml` 갱신
4. `CURRICULUM-*`의 CI가 존재하지 않는 코드를 참조하는 교안을 잡아냄

`.github/workflows/refresh.yml`이 매월 자동 실행 → 변경 시 PR 생성.
