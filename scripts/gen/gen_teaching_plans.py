# -*- coding: utf-8 -*-
"""
표준 강의 교안(6시트)을 세분류 단위로 찍어낸다.

지어내지 않는다. 능력단위요소·학습내용·학습목표·필요지식 제목·평가방법·피드백은
전부 NCS 학습모듈 원문(lm_extract.py 가 뽑아 둔 JSON)에서 온다.
우리가 정하는 것은 셋뿐이다.

  1. 편성 시간   운영 과정에 이미 들어간 능력단위는 그 과정의 실제 일정에서 가져온다.
                 아직 안 들어간 것은 학습내용 1개당 8시간을 기본값으로 둔다.
  2. 차시 배분   시간 / 2 = 차시. 능력단위요소에 최대잉여법으로 나눈다.
                 round() 를 쓰면 은행가 반올림 때문에 합이 어긋난다(파일럿에서 겪었다).
  3. 평가 비중   학습모듈이 제시한 평가방법을 그대로 쓰되 비중은 우리가 정한다(합 100%).

과정마다 달라져야 하는 칸(훈련기간·강사·훈련장소 등)은 '(채울 자리)' 로 남긴다.
남은 칸 수가 교안의 진척도가 된다(export_status.py 가 센다).

  python NCS-CATALOG/scripts/gen/lm_extract.py 20010202        # 먼저
  python NCS-CATALOG/scripts/gen/gen_teaching_plans.py 20010202
"""
import csv
import datetime
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "NCS-CATALOG" / "data"
LM = DATA / "learning-modules"
SITE = ROOT / "COURSE-MANAGEMENT"
TODAY = datetime.date.today().isoformat()

HOURS_PER_CONTENT = 8           # 미편성 능력단위의 기본 편성 시간
SESSION_H = 2                   # 1차시 = 2시간(120분)
STAGE = [("도입", 15), ("전개", 90), ("정리", 15)]
FILL = "(채울 자리)"

# 평가방법별 기본 비중. 학습모듈이 제시한 방법만 쓰고, 없는 방법은 만들지 않는다.
WEIGHT = {
    "포트폴리오": 30, "문제해결 시나리오": 25, "서술형시험": 20, "논술형시험": 20,
    "사례연구": 20, "평가자 질문": 15, "평가자 체크리스트": 20, "피평가자 체크리스트": 10,
    "일지/저널": 15, "역할연기": 15, "구두발표": 15, "작업장 평가": 25,
    "기타": 10,
}


def jsvar(path, var):
    p = SITE / "assets" / path
    if not p.exists():
        return None
    m = re.search(rf"window\.{var}\s*=\s*(\[.*?\]|\{{.*?\}});\s*$",
                  p.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        return None
    raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fixed = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:',
                       lambda x: x.group(1) + '"' + x.group(2) + '":', raw)
        return json.loads(re.sub(r",(\s*[}\]])", lambda x: x.group(1), fixed))


def placed_hours():
    """운영 과정에 이미 편성된 능력단위의 실제 시간(근무일 x 8)."""
    out = {}
    for c in (jsvar("courses.js", "CM_COURSES") or []):
        for m in (jsvar(f"modules-{c['id']}.js", "CM_MODULES") or []):
            code, sd, ed = m.get("code"), m.get("sd"), m.get("ed")
            if not (code and sd and ed):
                continue
            try:
                a = datetime.date.fromisoformat(sd)
                b = datetime.date.fromisoformat(ed)
            except ValueError:
                continue
            days = sum(1 for i in range((b - a).days + 1)
                       if (a + datetime.timedelta(i)).weekday() < 5)
            if days:
                out[code] = (days * 8, c["id"], c["name"])
    return out


def allocate(total, weights):
    """최대잉여법. 각 몫은 최소 1이고 합은 반드시 total 이다."""
    n = len(weights)
    if n == 0:
        return []
    if total < n:
        total = n
    tot_w = sum(weights) or n
    quota = [total * w / tot_w for w in weights]
    alloc = [max(1, int(q)) for q in quota]
    rest = total - sum(alloc)
    order = sorted(range(n), key=lambda i: quota[i] - int(quota[i]), reverse=True)
    i = 0
    while rest > 0:
        alloc[order[i % n]] += 1
        rest -= 1
        i += 1
    while rest < 0:
        j = max(range(n), key=lambda k: alloc[k])
        if alloc[j] <= 1:
            break
        alloc[j] -= 1
        rest += 1
    return alloc


def spread(items, k):
    """소재 items 를 k 개 차시로 고르게 나눈다. 모자라면 빈 차시가 생긴다."""
    if k <= 0:
        return []
    if not items:
        return [[] for _ in range(k)]
    base, extra = divmod(len(items), k)
    out, i = [], 0
    for s in range(k):
        n = base + (1 if s < extra else 0)
        out.append(items[i:i + n])
        i += n
    return out


def eval_plan(methods):
    """학습모듈이 제시한 평가방법에 비중을 매긴다. 합은 100%."""
    ms = []
    for m in methods:
        if m not in ms:
            ms.append(m)
    if not ms:
        ms = ["포트폴리오", "평가자 체크리스트"]
    w = [WEIGHT.get(m, WEIGHT["기타"]) for m in ms]
    pct = allocate(100, w)
    return list(zip(ms, pct))


def md(seq, unit, lm, hours, lv, src_note):
    n_ses = max(1, round(hours / SESSION_H))
    elems = lm["elements"]
    weights = [max(1, sum(len(c["topics"]) or 1 for c in e["contents"])) for e in elems]
    alloc = allocate(n_ses, weights)
    e_hours = [a * SESSION_H for a in alloc]

    # ② NCS매핑
    rows, s_no = [], 0
    for e, a, h in zip(elems, alloc, e_hours):
        first = s_no + 1
        s_no += a
        goals = " / ".join(g for c in e["contents"] for g in c["goals"]) or FILL
        conts = " · ".join(c["title"] for c in e["contents"])
        rows.append(f"| {e['no']}. {e['name']}<br>`{e['code'] or FILL}` | {conts} | "
                    f"{goals} | {first}~{s_no} | {h} | {round(h / hours * 100)}% |")

    # ③ 주차별계획 (1주 = 20시간 기준으로 묶는다)
    per_week = max(1, 20 // SESSION_H)
    weeks, s = [], 0
    while s < n_ses:
        k = min(per_week, n_ses - s)
        weeks.append((len(weeks) + 1, s + 1, s + k, k * SESSION_H))
        s += k

    # ④ 차시별지도안
    plans, s_no = [], 0
    for e, a in zip(elems, alloc):
        topics = [t["t"] for c in e["contents"] for t in c["topics"]]
        if not topics:
            topics = [c["title"] for c in e["contents"]]
        for k, chunk in enumerate(spread(topics, a)):
            s_no += 1
            title = chunk[0] if chunk else f"{e['name']} ({k + 1})"
            body = "\n".join(
                f"| {st} | {mn} | " +
                ({"도입": f"지난 차시 확인 · 오늘 다룰 것 제시 — {title}",
                  "전개": ("· " + "<br>· ".join(chunk)) if chunk else FILL,
                  "정리": "핵심 정리 · 산출물 확인 · 다음 차시 예고"}[st]) +
                f" | {'학습모듈 ' + lm['src'][:24] if st == '전개' else '판서 · 슬라이드'} | "
                f"{'관찰' if st != '정리' else '질의'} |"
                for st, mn in STAGE)
            plans.append(f"### {s_no}차시 — {title}\n\n"
                         f"학습 {e['no']}. {e['name']} · {SESSION_H}시간(120분)\n\n"
                         "| 단계 | 분 | 활동 | 자료 | 평가 |\n|---|---:|---|---|---|\n"
                         + body + "\n")

    ev = eval_plan([m for e in elems for m in e["eval"]["methods"]])
    ev_rows = "\n".join(f"| {m} | {p}% | {FILL} |" for m, p in ev)
    fb = [f for e in elems for f in e["eval"]["feedback"]][:3]

    goals_all = [f"{i + 1}) {c['title']} — {g}"
                 for i, (c, g) in enumerate(
                     (c, g) for e in elems for c in e["contents"] for g in c["goals"])]

    return f"""---
unit_code: "{unit['code']}"
unit_name: {unit['name']}
ncs_code: "{unit['ncs']}"
subdivision: {unit['subd']}
hours: {hours}
level: {lv or ''}
sessions: {n_ses}
status: draft
updated: {TODAY}
---

# {seq}. {unit['name']}

> **NCS 능력단위 정의**
> {lm['goal']}

표준 강의 교안(교과목 운영계획서) 6시트 구조를 따른다.
내용은 **NCS 학습모듈 원문**에서 옮긴 것이다 — 문장을 고치지 않는다.
양식 원문 — [표준 강의 교안 샘플](https://ncs-module-curriculums.github.io/COURSE-MANAGEMENT/docs/표준강의교안-샘플.html)

---

## ① 교과개요

| 항목 | 내용 | 항목 | 내용 |
|---|---|---|---|
| 훈련과정명 | {FILL} | 훈련유형 | ☐ 과정평가형  ☐ 일반국비(계좌제)  ☐ KDT |
| 교과목명 | {unit['name']} | 능력단위코드 | `{unit['code']}` |
| 훈련기간 | {FILL} | 교육시간 | **{hours}시간** ({n_ses}차시) |
| 담당강사 | {FILL} | 보조강사/멘토 | {FILL} |
| 훈련장소 | {FILL} | 정원 | {FILL} |
| NCS 수준 | {lv or FILL} | 이론 / 실습 | ③에서 집계 |

**NCS 분류** {unit['tree']}
**능력단위요소** {' / '.join(f"{e['no']}. {e['name']}" for e in elems)}

### 교과 목표(총괄)
{lm['goal']}

### 세부 학습목표
{chr(10).join(goals_all) if goals_all else FILL}

### 선수학습 / 입과요건
{lm.get('prereq') or FILL}

### 핵심 용어
{', '.join(lm.get('keywords') or []) or FILL}

### 교재 · 장비 · 자료
- NCS 학습모듈 `{lm['src']}` ({lm['pages']}쪽) — 한국직업능력연구원
- 장비 · 실습 환경 {FILL}

---

## ② NCS매핑

능력단위요소·학습내용·학습목표는 **NCS 학습모듈 원문**이다. 문장을 고치지 않는다.
평가 문항과 루브릭은 이 문장에서 도출한다.

| 능력단위요소 | 학습 내용 | 학습 목표 | 연계 차시 | 편성시간(h) | 비율 |
|---|---|---|---|---:|---:|
{chr(10).join(rows)}
| **합계** | | | **{n_ses}차시** | **{sum(e_hours)}** | **100%** |

---

## ③ 주차별계획

1주 = 20시간(10차시) 기준으로 묶은 것이다. 실제 과정 일정에 맞춰 조정한다.

| 주차 | 차시 | 시간 | 내용 |
|---:|---|---:|---|
{chr(10).join(f"| {w} | {a}~{b} | {h} | {FILL} |" for w, a, b, h in weeks)}
| **합계** | **{n_ses}차시** | **{sum(x[3] for x in weeks)}** | |

---

## ④ 차시별지도안

1차시 = {SESSION_H}시간(120분) · 도입 15 / 전개 90 / 정리 15분

{chr(10).join(plans)}
---

## ⑤ 평가계획

평가방법은 학습모듈이 제시한 것을 그대로 쓴다. 비중은 과정에서 정한다.

| 평가방법 | 비중 | 평가 시점 |
|---|---:|---|
{ev_rows}
| **합계** | **100%** | |

### 루브릭 (4단계)

| 수준 | 기준 |
|---|---|
| A (90~100) | 수행준거를 모두 충족하고 근거를 들어 설명할 수 있다 |
| B (80~89) | 수행준거를 대부분 충족한다 |
| C (70~79) | 도움을 받아 수행준거를 충족한다 |
| D (~69) | 재평가 대상 |

### 피드백 (학습모듈 원문)
{chr(10).join('- ' + f for f in fb) if fb else '- ' + FILL}

### 사전 · 결석자 · 재평가
- 사전평가 {FILL}
- 결석자평가 {FILL}
- 재평가 {FILL}

---

## ⑥ 훈련생안내

- **무엇을 할 수 있게 되나** — {lm['goal']}
- **준비물** {FILL}
- **평가** {' · '.join(f'{m} {p}%' for m, p in ev)}
- **유의사항** {FILL}

---

## 교안 작성 메모

{src_note}
차시 배분은 학습내용의 분량(필요 지식 제목 수)에 비례해 최대잉여법으로 나눴다.
`(채울 자리)` 는 과정마다 달라지는 값이라 편성할 때 채운다.

## 참고
- NCS 학습모듈 `{lm['src']}` — 한국직업능력연구원 (공공누리 제2유형)
- ncs.go.kr 능력단위 `{unit['code']}` · 수준 {lv or '-'}
"""


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    tax = {r["세분류코드"]: r for r in
           csv.DictReader(open(DATA / "taxonomy.csv", encoding="utf-8-sig"))}
    ncs = {r["능력단위코드"]: r for r in
           csv.DictReader(open(DATA / "competency-units.csv", encoding="utf-8-sig"))}
    placed = placed_hours()

    st = json.loads((DATA / "curriculum-status.json").read_text(encoding="utf-8"))
    made = skip = 0
    for uc, u in sorted(st["units"].items(), key=lambda kv: (kv[1]["s"], kv[1]["seq"])):
        if only and u["s"] != only:
            continue
        f = LM / f"{uc}.json"
        if not f.exists():
            print(f"  ! {u['n']} — 학습모듈 추출본이 없다 (lm_extract.py 먼저)")
            skip += 1
            continue
        lm = json.loads(f.read_text(encoding="utf-8"))
        r, t = ncs.get(uc, {}), tax.get(u["s"], {})

        n_cont = sum(len(e["contents"]) for e in lm["elements"]) or 1
        if uc in placed:
            hours, cid, cname = placed[uc]
            note = (f"편성 시간 {hours}시간은 운영 과정 **{cname}**({cid})의 "
                    f"실제 일정에서 가져왔다.")
        else:
            hours = min(80, max(24, HOURS_PER_CONTENT * n_cont))
            note = (f"아직 어느 과정에도 편성되지 않았다. 편성 시간 {hours}시간은 "
                    f"학습내용 {n_cont}개 × {HOURS_PER_CONTENT}시간의 기본값이고, "
                    f"과정을 짤 때 조정한다.")

        unit = {"code": uc, "name": u["n"], "ncs": u["s"], "subd": r.get("세분류", ""),
                "tree": " > ".join(x for x in (
                    f"{t.get('대분류코드','')}.{t.get('대분류','')}",
                    f"{t.get('중분류코드','')}.{t.get('중분류','')}",
                    f"{t.get('소분류코드','')}.{t.get('소분류','')}",
                    f"{t.get('세분류코드2','')}.{t.get('세분류','')}") if x.strip("."))}
        lv = int(r["수준"]) if r.get("수준", "").isdigit() else None

        repo = st["domains"][u["d"]]["repo"]
        base = ROOT / repo / "modules"
        folder = next(base.glob(f"{u['s']}_*"), None)
        if folder is None:
            print(f"  ! {u['n']} — 모듈 폴더 없음")
            skip += 1
            continue
        d = next((x for x in folder.iterdir()
                  if x.is_dir() and x.name.startswith(u["seq"] + "_")), None)
        if d is None:
            print(f"  ! {u['n']} — {u['seq']}_ 폴더 없음")
            skip += 1
            continue

        (d / "teaching-plan.md").write_text(
            md(u["seq"], unit, lm, hours, lv, note), encoding="utf-8")
        made += 1
        n_ses = max(1, round(hours / SESSION_H))
        tag = "편성" if uc in placed else "기본"
        print(f"{u['seq']} {u['n'][:22]:24} {hours:3}h · {n_ses:2}차시 · "
              f"요소 {len(lm['elements'])} · {tag}")

    print(f"\n교안 {made}건 작성 · 건너뜀 {skip}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
