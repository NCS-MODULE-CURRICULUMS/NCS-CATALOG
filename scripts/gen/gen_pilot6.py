# -*- coding: utf-8 -*-
"""
교안 템플릿을 표준 강의 교안(교과목 운영계획서) 6시트 구조로 전면 개편.

「파이썬_표준강의교안_샘플.xlsx」(코리아AI아카데미 표준안 v1.0)의 구성을 따른다.
  ① 교과개요  ② NCS매핑  ③ 주차별계획  ④ 차시별지도안  ⑤ 평가계획  ⑥ 훈련생안내

능력단위요소·수행준거는 ncs.go.kr 능력단위 정의서 원문(29차)이다.
차시 전개·평가 비중 등 운영 값은 담당강사가 채울 자리로 두되, 합계가 맞도록 초기값을 넣는다.
"""
import importlib.util
from pathlib import Path

ORG = Path(__file__).resolve().parents[3]
BASE = ORG / "CURRICULUM-AI-DATA" / "modules" / "20010707_생성형AI엔지니어링"
TODAY = "2026-09-16"

spec = importlib.util.spec_from_file_location("ncs", Path(__file__).parent / "ncs_20010707.py")
ncs = importlib.util.module_from_spec(spec); spec.loader.exec_module(ncs)
UNITS = ncs.UNITS

_ls = importlib.util.spec_from_file_location("ls", Path(__file__).parent / "lessons_20010707.py")
_lm = importlib.util.module_from_spec(_ls); _ls.loader.exec_module(_lm)
LESSONS = _lm.LESSONS

# 과정 공통 (①교과개요 · ⑥훈련생안내에 쓰인다)
COURSE = {
    "name": "생성형 AI 엔지니어 양성과정",
    "org": "NCS-MODULE-CURRICULUMS",
    "types": "☑ 과정평가형  ☑ 일반국비(계좌제)  ☑ KDT",
    "ncs_path": "20.정보통신 > 01.정보기술 > 07.인공지능 > 07.생성형AI엔지니어링",
    "period": "2026-10-06 ~ 2027-01-15",
    "tc": "정우균",
    "room": "(미정) 실습실 · GPU 실습 환경",
    "cap": "20명",
}

# 능력단위별 편성 시간 · 교과목 코드 (총 160시간)
PLAN = {
 "01": {"hr": 12, "cd": "GA-101", "sd": "2026-10-06", "ed": "2026-10-08", "ev": "2026-10-08"},
 "02": {"hr": 12, "cd": "GA-102", "sd": "2026-10-08", "ed": "2026-10-13", "ev": "2026-10-13"},
 "03": {"hr": 20, "cd": "GA-103", "sd": "2026-10-14", "ed": "2026-10-21", "ev": "2026-10-21"},
 "04": {"hr": 24, "cd": "GA-104", "sd": "2026-10-22", "ed": "2026-11-03", "ev": "2026-11-03"},
 "05": {"hr": 20, "cd": "GA-105", "sd": "2026-11-04", "ed": "2026-11-13", "ev": "2026-11-13"},
 "06": {"hr": 16, "cd": "GA-106", "sd": "2026-11-16", "ed": "2026-11-23", "ev": "2026-11-23"},
 "07": {"hr": 28, "cd": "GA-107", "sd": "2026-11-24", "ed": "2026-12-11", "ev": "2026-12-11"},
 "08": {"hr": 16, "cd": "GA-108", "sd": "2026-12-14", "ed": "2026-12-22", "ev": "2026-12-22"},
 "09": {"hr": 12, "cd": "GA-109", "sd": "2026-12-23", "ed": "2027-01-05", "ev": "2027-01-05"},
}

# 능력단위별 평가방법 구성 (⑤평가계획). 비중 합계 100%.
EVAL = {
 "01": [("사례연구", 40, "요소①②"), ("구두발표", 30, "요소③④"), ("평가자 질문", 30, "요소 전체")],
 "02": [("포트폴리오", 50, "요소①②③"), ("평가자 질문", 30, "요소④"), ("서술형시험", 20, "요소①②")],
 "03": [("포트폴리오", 40, "요소①③④"), ("평가자 체크리스트", 40, "요소②⑤"), ("서술형시험", 20, "요소 전체")],
 "04": [("작업장평가", 50, "요소①③④"), ("일지/저널", 30, "요소②③"), ("평가자 질문", 20, "요소④")],
 "05": [("포트폴리오", 60, "요소①②③④"), ("평가자 질문", 30, "요소 전체"), ("서술형시험", 10, "요소①②")],
 "06": [("포트폴리오", 40, "요소②③④"), ("문제해결 시나리오", 40, "요소①③"), ("평가자 질문", 20, "요소 전체")],
 "07": [("작업장평가", 50, "요소①③④"), ("평가자 체크리스트", 30, "요소②④"), ("포트폴리오", 20, "요소②")],
 "08": [("문제해결 시나리오", 40, "요소②③"), ("평가자 체크리스트", 40, "요소①④"), ("포트폴리오", 20, "요소④")],
 "09": [("작업장평가", 60, "요소②"), ("포트폴리오", 40, "요소①")],
}

# 단계별 기본 배분 (④차시별지도안) — 1차시 = 2시간(120분)
STAGE = [("도입", 15), ("전개", 90), ("정리", 15)]

PRE = {
 "01": ["요구공학 기초 (요구사항 수집 · 명세)", "LLM 개괄 — 무엇을 할 수 있고 무엇을 못 하는가"],
 "02": ["01 프로덕트 목표 수립", "토큰 · 컨텍스트 개념"],
 "03": ["데이터 전처리 기초", "개인정보보호법 개괄"],
 "04": ["03 데이터 준비", "파이썬 · 딥러닝 기초"],
 "05": ["01 목표 수립", "02 모델 선정"],
 "06": ["05 프롬프트 구현"],
 "07": ["05 프롬프트 구현", "06 프롬프트 최적화", "웹 애플리케이션 개발 기초"],
 "08": ["07 프로덕트 제작", "01 목표 수립(지표)"],
 "09": ["07 프로덕트 제작", "08 프로덕트 검증"],
}

NOTE = {
 "01": "수준 7 능력단위로 이 세분류에서 가장 높다. 기술 구현이 아니라 판단과 합의가 핵심이므로 "
       "코드 실습으로 채우면 수행준거를 못 맞춘다. 요소④는 이해관계자 합의라 역할연기·구두발표가 맞는다.",
 "02": "공개 벤치마크 점수만 인용하면 수행준거 2.3(성능지표 도출)을 충족하지 못한다. "
       "우리 과제에 맞는 자체 평가셋을 만드는 것이 이 능력단위의 핵심이다.",
 "03": "요소⑤ '데이터 검증하기'의 수행준거 5.1이 도메인 전문가 협업을 명시한다. "
       "검증 절차와 기록이 없으면 미충족이다. 실습에 외부 검토자 역할을 반드시 넣는다.",
 "04": "이 세분류에서 장비 요건이 가장 크다. GPU 확보 계획이 없으면 편성하지 말 것. "
       "소형 모델 + LoRA 로 범위를 좁히는 것이 현실적이다. 요소③ 사전학습은 시연 위주로 간다.",
 "05": "정의의 순서(요구 분석 → 목표 수립 → 구조 설계 → 작성)가 그대로 요소①②③④다. "
       "요령 나열식 수업이 되지 않도록 이 순서를 지킨다. 06 최적화와 겹치지 않게 '만드는 것'까지만 다룬다.",
 "06": "요소③ 수행준거가 '진단 → 수정 방안 → 개선'으로 이어진다. 한 번 고쳐서 좋아졌다는 식으로는 "
       "안 되고 반복 실험 기록이 산출물이다. 05 와의 경계를 과제·채점표에도 명시한다.",
 "07": "시간 배분이 가장 큰 능력단위다. 웹 개발 자체를 여기서 가르치려 들면 시간이 모자란다. "
       "프론트엔드 기초는 선수과목으로 두거나 스캐폴드를 제공한다.",
 "08": "요소③ '보안성 점검하기'가 별도 요소로 있다. 기능 테스트만 하고 끝내면 미충족이다. "
       "프롬프트 주입 · 정보 유출 시험을 반드시 포함한다.",
 "09": "요소는 둘뿐이지만 수행준거가 각각 5개로 촘촘하다. API 키를 코드에 넣은 채 배포하는 사고가 "
       "가장 흔하므로 비밀값 분리를 평가 항목에 넣는다.",
}


def sessions(hr):
    """1차시 = 2시간. 편성시간에서 차시 수를 낸다."""
    return hr // 2


def allocate(no, u):
    """요소별 차시 배분 — 수행준거 개수 비례(최대잉여법).

    합이 정확히 총 차시가 되게 한다. 차시를 먼저 나누고 시간을 2배로 내야
    ②NCS매핑과 ③주차별계획의 합계가 어긋나지 않는다.
    마크다운 교안과 사이트용 HTML 교안이 같은 값을 쓰도록 여기 한 곳에 둔다.
    """
    n_ses = sessions(PLAN[no]["hr"])
    elems = u["elems"]
    weights = [len(e[2]) for e in elems]
    tot_w = sum(weights)
    quota = [n_ses * w / tot_w for w in weights]
    alloc = [max(1, int(q)) for q in quota]
    rest = n_ses - sum(alloc)
    order = sorted(range(len(elems)), key=lambda i: quota[i] - int(quota[i]), reverse=True)
    i = 0
    while rest > 0:
        alloc[order[i % len(order)]] += 1; rest -= 1; i += 1
    while rest < 0:                      # 최소 1차시 보장 탓에 넘친 경우
        j = max(range(len(alloc)), key=lambda k: alloc[k])
        if alloc[j] > 1:
            alloc[j] -= 1; rest += 1
        else:
            break
    return n_ses, alloc, [a * 2 for a in alloc]


def md(no, u):
    p = PLAN[no]
    elems = u["elems"]
    n_ses, alloc, hours = allocate(no, u)

    # ② NCS매핑
    ncs_rows, ses_cursor = [], 1
    for (eno, ename, crits), h, a in zip(elems, hours, alloc):
        s_from = ses_cursor
        s_to = ses_cursor + a - 1
        ses_cursor = s_to + 1
        rng = f"{s_from}~{s_to}차시" if s_to > s_from else f"{s_from}차시"
        first = True
        for c in crits:
            cno, ctxt = c.split(" ", 1)
            if first:
                ncs_rows.append(
                    f"| `{u['code']}.{eno}`<br>{ename} | {cno} | {ctxt} | {rng} | {h} | "
                    f"{round(h / p['hr'] * 100)}% |")
                first = False
            else:
                ncs_rows.append(f"| | {cno} | {ctxt} | | | |")

    # ③ 주차별계획
    wk_rows, cur = [], 1
    for (eno, ename, crits), a in zip(elems, alloc):
        for j in range(a):
            ev = 2 if cur == n_ses else 0          # 마지막 차시는 본평가
            th = 0 if ev else (1 if j < a - 1 else 0.5)
            pr = 0 if ev else 2 - th
            wk_rows.append(
                f"| {(cur + 1) // 2} | {cur} | {ename} | (채울 자리) | {th} | {pr} | {ev} | 2 | "
                f"{'본평가' if ev else ''} | `{u['code']}.{eno}` |")
            cur += 1

    # ④ 차시별지도안 — 작성분이 있으면 그대로, 없으면 서식만
    HEAD = ('| 단계 | 시간(분) | 교수 · 학습 활동 (강사 ↔ 훈련생) | 교수자료 · 도구 | 평가 · 과제 |'
            '\n|---|---|---|---|---|\n')
    les = LESSONS.get(no)
    if les:
        blocks = []
        for L in les:
            rows = "\n".join(
                f"| {st} | {mi} | {act} | {mat} | {ev} |"
                for st, mi, act, mat, ev in L["stages"])
            tot = sum(x[1] for x in L["stages"])
            blocks.append(
                f"### {L['no']}차시 — {L['topic']}\n\n"
                f"**학습목표** {L['goal']}\n"
                f"**연계 수행준거** {L['crit']}\n\n"
                + HEAD + rows + f"\n| **소계** | **{tot}** | | | |")
        stage_rows = "\n\n".join(blocks)
    else:
        stage_rows = (HEAD + "\n".join(
            f"| {st} | {mi} | (교수 · 학습 활동) | (교수자료) | |" for st, mi in STAGE)
            + "\n| 소계 | 120 | | | |")

    # ⑤ 평가계획
    ev_rows = "\n".join(
        f"| {i + 1} | {m} | {w}% | {p['ev']} | (문항 구성) | {tgt} | (평가지 · 채점표) |"
        for i, (m, w, tgt) in enumerate(EVAL[no]))
    ev_sum = sum(w for _, w, _ in EVAL[no])

    elem_list = " / ".join(f"① ②③④⑤"[i] if False else f"{'①②③④⑤'[i]} {e[1]}"
                           for i, e in enumerate(elems))
    pre = "\n".join(f"- {x}" for x in PRE[no])

    return f"""---
unit_code: "{u['code']}"
unit_name: {u['name']}
ncs_code: "20010707"
subdivision: 생성형AI엔지니어링
course_code: {p['cd']}
hours: {p['hr']}
level: {u['lv']}
sessions: {n_ses}
status: draft
updated: {TODAY}
---

# {no}. {u['name']}

> **NCS 능력단위 정의** (ncs.go.kr 원문, 29차)
> {u['def']}

표준 강의 교안(교과목 운영계획서) 6시트 구조를 따른다.
양식 원문 — [표준 강의 교안 샘플](https://ncs-module-curriculums.github.io/COURSE-MANAGEMENT/docs/표준강의교안-샘플.html)

---

## ① 교과개요

| 항목 | 내용 | 항목 | 내용 |
|---|---|---|---|
| 훈련과정명 | {COURSE['name']} | 훈련유형 | {COURSE['types']} |
| 교과목명 | {u['name']} | 교과목 코드 | {p['cd']} |
| 훈련기간 | {p['sd']} ~ {p['ed']} | 교육시간 | (채울 자리) |
| 담당강사 | {COURSE['tc']} | 보조강사/멘토 | (채울 자리) |
| 훈련장소 | {COURSE['room']} | 정원 | {COURSE['cap']} |
| 총 훈련시간 | **{p['hr']}시간** ({n_ses}차시) | 이론 / 실습 | (③에서 자동 집계) |

**NCS 분류** {COURSE['ncs_path']}
**능력단위** {u['name']} (`{u['code']}`) — 수준 **{u['lv']}**
**능력단위요소** {elem_list}

### 교과 목표(총괄)
{u['def']}

### 세부 학습목표
{chr(10).join(f"{i + 1}) {e[1]} — {len(e[2])}개 수행준거를 충족할 수 있다." for i, e in enumerate(elems))}

### 선수학습 / 입과요건
{pre}

### 교수학습 방법
(채울 자리 — 이론 강의 / 실습 / 프로젝트 비중)

### 교재 · 장비 · 자료
- **NCS 학습모듈 없음** — 이 세분류는 2025년 신설(`25v1`)이라 한국직업능력연구원의 학습모듈이 아직 제작되지 않았다. 교재를 직접 만들어야 한다.
- 장비 (채울 자리)

---

## ② NCS매핑

능력단위요소 · 수행준거는 **ncs.go.kr 능력단위 정의서 원문**이다. 문장을 고치지 않는다.
평가 문항과 루브릭은 이 문장에서 도출한다.

| 능력단위요소(코드) | 수행준거 번호 | 수행준거 | 연계 차시 | 편성시간(h) | 비율 |
|---|---|---|---|---|---|
{chr(10).join(ncs_rows)}
| **합계** | | | | **{p['hr']}** | **100%** |

> 합계는 ③주차별계획의 총 훈련시간과 일치해야 한다.

---

## ③ 주차별계획

1차시 = 2시간(120분). 이론/실습 시간은 담당강사가 채운다.

| 일차 | 차시 | 단원(대주제) | 학습내용(소주제 · 활동) | 이론(h) | 실습(h) | 평가(h) | 소계(h) | 평가/과제 | NCS요소 |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(wk_rows)}
| **합계** | | | | | | | **{p['hr']}** | | |

---

## ④ 차시별지도안

차시마다 아래 표를 채운다. 1차시 = 120분 = 도입 15 + 전개 90 + 정리 15.
**실제 수업에서 무엇을 어떻게 했는지**가 드러나야 한다 — 현장 모니터링에서 훈련일지 · 출석부와 대조된다.

{stage_rows}

---

## ⑤ 평가계획

| No | 평가 방법 | 비중 | 시기 | 평가 내용 · 문항 구성 | 대상 능력단위요소 | 평가 도구/증빙 |
|---|---|---:|---|---|---|---|
{ev_rows}
| **합계** | | **{ev_sum}%** | | | | |

**합격 기준** 60점 · 미달 시 재평가

### 루브릭 (4단계)

| 척도 | 환산 | 판정 기준 |
|---|---|---|
| 매우 우수 | 90 ~ 100 | 수행준거를 모두 충족하고 지시 없이 스스로 판단해 처리한다 |
| 우수 | 80 ~ 89 | 수행준거를 모두 충족한다. 일부 보완이 필요하나 스스로 고칠 수 있다 |
| 보통 | 60 ~ 79 | 주요 수행준거를 충족한다. 지도를 받으면 완결할 수 있다 — **합격 하한** |
| 미흡 | 60 미만 | 수행준거를 충족하지 못한다 — 재평가 대상 |

### 사전 · 결석자 · 재평가

| 구분 | 시점 | 내용 |
|---|---|---|
| 사전평가 | 능력단위 시작 전 | 훈련 전 수준 확인. 본평가와 **같은 문항을 쓰지 않는다**. 성적 미반영 |
| 본평가 | {p['ev']} | 위 평가계획 |
| 결석자평가 | 본평가 직후 예비일 | 정당한 사유자 대상. **사유 증빙 보관** |
| 재평가 | 미흡 판정 후 | **다른 과제**로 시행 |

---

## ⑥ 훈련생안내

> 이 절만 PDF 로 출력해 훈련생에게 배포한다.

| 항목 | 내용 |
|---|---|
| 훈련과정 | {COURSE['name']} |
| 교과목 | {u['name']} |
| 훈련기간 | {p['sd']} ~ {p['ed']} ({p['hr']}시간 · {n_ses}차시) |
| 담당강사 | {COURSE['tc']} |
| 강의실 | {COURSE['room']} |

**이 교과를 마치면**
{chr(10).join(f"{i + 1}) {e[1]}" for i, e in enumerate(elems))}

**준비물 · 학습 환경** (채울 자리)
**평가** {' · '.join(m for m, _, _ in EVAL[no])} — 합격 기준 60점
**문의** (채울 자리)

---

## 교안 작성 메모

{NOTE[no]}

## 참고

- 능력단위 원문 — [ncs.go.kr](https://www.ncs.go.kr) > NCS 및 학습모듈 검색 > `20-01-07-07`
- 수행준거는 원문 그대로이며 **수정하지 않는다**. 개정 시 코드 · 버전과 함께 갱신한다.
"""


def main():
    n = 0
    for no, u in UNITS.items():
        d = next((c for c in BASE.glob(f"{no}_*") if c.is_dir()), None)
        if d is None:
            print(f"  폴더 없음: {no}"); continue
        (d / "teaching-plan.md").write_text(md(no, u), encoding="utf-8")
        (d / "lesson-plans").mkdir(exist_ok=True)
        gk = d / "lesson-plans" / ".gitkeep"
        if not gk.exists():
            gk.write_text("", encoding="utf-8")
        n += 1
        print(f"  {d.name}")
    tot = sum(PLAN[k]["hr"] for k in UNITS)
    ecnt = sum(len(u["elems"]) for u in UNITS.values())
    ccnt = sum(len(e[2]) for u in UNITS.values() for e in u["elems"])
    print(f"\n교안 {n}개 · 총 {tot}시간 · 능력단위요소 {ecnt}개 · 수행준거 {ccnt}개")


if __name__ == "__main__":
    main()
