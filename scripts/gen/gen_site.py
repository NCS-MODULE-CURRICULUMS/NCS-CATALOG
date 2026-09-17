# -*- coding: utf-8 -*-
"""
COURSE-MANAGEMENT 의 과정 / 모듈 데이터와 모듈 상세 페이지를 만든다.

NCS_EXAM_PAGE 와 같은 3단 구조:
    index.html  →  courses/cN.html (능력단위 모듈 목록)  →  modules/mNN.html (상세)

데이터는 CURRICULUM-AI-DATA 의 파일럿(20010707 생성형AI엔지니어링) 9개 능력단위를 쓴다.
"""
import importlib.util
import json
from pathlib import Path

ORG = Path(__file__).resolve().parents[3]
SITE = ORG / "COURSE-MANAGEMENT"

spec = importlib.util.spec_from_file_location("gp", ORG / "_shared" / "gen_pilot.py")
gp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gp)
UNITS = gp.UNITS

COURSE = {
    "id": "c1",
    "name": "생성형 AI 엔지니어 양성과정",
    "ncs": "20010707 생성형AI엔지니어링",
    "period": "2026-10-06 ~ 2027-01-15",
    "hours": "160시간",
    "tc": "정*균",
    "page": "courses/c1.html",
}

# 능력단위별 평가 일정 — 시간 배분에 따라 순차 배치한 예시값
SCHEDULE = [
    ("2026-10-06", "2026-10-08", "2026-10-08"),
    ("2026-10-08", "2026-10-13", "2026-10-13"),
    ("2026-10-14", "2026-10-21", "2026-10-21"),
    ("2026-10-22", "2026-11-03", "2026-11-03"),
    ("2026-11-04", "2026-11-13", "2026-11-13"),
    ("2026-11-16", "2026-11-23", "2026-11-23"),
    ("2026-11-24", "2026-12-11", "2026-12-11"),
    ("2026-12-14", "2026-12-22", "2026-12-22"),
    ("2026-12-23", "2027-01-05", "2027-01-05"),
]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def js_header(title, writer):
    return [f"/* {title}",
            f" * {writer} 의 [설정 파일 저장] 이 이 파일을 덮어씁니다. 손으로 고쳐도 됩니다.",
            " * 고친 뒤 git 에 올려야 모두에게 적용됩니다.",
            " */"]


def write_courses():
    body = js_header("과정 목록.", "index.html") + [
        " *",
        " *   id     : 과정 구분자",
        " *   name   : 과정명",
        " *   ncs    : 앵커 NCS 세분류",
        " *   period : 기간      hours : 시간      tc : 담당",
        " *   page   : 들어갈 페이지. 비우면 '준비 중' 카드가 됩니다",
        " */",
        "window.CM_COURSES = " + json.dumps([COURSE], ensure_ascii=False, indent=2) + ";",
        "",
    ]
    # 위에서 주석 닫기가 두 번 들어가지 않게 첫 블록의 닫기를 지운다
    body = [l for i, l in enumerate(body) if not (i == 3 and l == " */")]
    (SITE / "assets" / "courses.js").write_text("\n".join(body), encoding="utf-8")


def write_modules():
    mods = []
    for i, u in enumerate(UNITS):
        sd, ed, ev = SCHEDULE[i]
        mods.append({
            "id": "m" + u["no"],
            "name": u["name"],
            "code": u["code"],
            "lv": u["lv"],
            "hr": u["hr"],
            "tc": COURSE["tc"],
            "sd": sd, "ed": ed, "ev": ev, "ab": "-", "re": "-",
            "ev_method": " · ".join(u["ev"]),
            "page": f"modules/c1-m{u['no']}.html",
            "lp": "",
        })
    body = js_header("과정의 능력단위 모듈 목록.", "courses/c1.html") + [
        " *",
        " *   id   : 모듈 구분자        code : NCS 능력단위코드",
        " *   lv   : NCS 수준           hr   : 편성 훈련시간",
        " *   tc   : 강사               sd/ed: 시작일 / 종료일",
        " *   ev   : 본평가   ab : 결석자평가   re : 재평가",
        " *   ev_method : 평가방법      page : 상세 페이지
 *   lp   : 표준 강의 교안 경로. 비우면 양식 보기로 갑니다",
        " */",
        "window.CM_MODULES = " + json.dumps(mods, ensure_ascii=False, indent=2) + ";",
        "",
    ]
    body = [l for i, l in enumerate(body) if not (i == 3 and l == " */")]
    (SITE / "assets" / "modules.js").write_text("\n".join(body), encoding="utf-8")
    return mods


def write_locks(mods):
    out = {m["id"]: (m["id"] != "m05") for m in mods}   # m05 만 공개(작성 예시 완성분)
    body = js_header("모듈별 잠금 상태.  true = 잠김(일반은 상세를 못 엽니다)",
                     "courses/c1.html") + [
        "window.CM_LOCKS = " + json.dumps(out, ensure_ascii=False, indent=2) + ";",
        "",
    ]
    (SITE / "assets" / "locks.js").write_text("\n".join(body), encoding="utf-8")


def module_page(u, i):
    sd, ed, ev = SCHEDULE[i]
    rows = "\n".join(
        f'      <tr><td class="c">{a}</td><td class="nm">{esc(b)}</td>'
        f'<td>{esc(c)}</td><td class="c">{d}</td></tr>'
        for a, b, c, d in u["plan"])
    goals = "\n".join(f"    <li>{esc(g)}</li>" for g in u["goal"])
    pres = "\n".join(f"    <li>{esc(p)}</li>" for p in u["pre"])
    evs = " · ".join(u["ev"])
    extra = ""
    if u["no"] == "05":
        extra = """
  <div class="note"><b>작성 예시</b> — 이 능력단위는 실습 과제와 평가기준까지 작성되어 있습니다.
  <code>CURRICULUM-AI-DATA</code> 의
  <code>modules/20010707_생성형AI엔지니어링/05_프롬프트 구현/</code> 아래
  <code>labs/과제.md</code> · <code>assessment/평가기준.md</code> 를 보세요.</div>
"""
    return f"""<meta charset="utf-8"><title>{esc(u['name'])} — 능력단위 상세</title>
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a>
  <small><a href="../courses/{COURSE['id']}.html">{esc(COURSE['name'])}</a> / {esc(u['name'])}</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div></div>
<script>EXAM_AUTH.paintTop("../");</script>
<style>
  .defbox{{border:1px solid #000;border-left-width:4px;padding:11px 14px;margin:16px 0;
          font-size:13.5px;line-height:1.75;background:#fafafa}}
  .facts{{display:flex;gap:20px;flex-wrap:wrap;border:1px solid #000;padding:10px 14px;
         margin:14px 0;font-size:12.5px}}
  .facts b{{font-size:15px;margin-left:4px}}
  td.c{{text-align:center}}
  h2{{font-size:15px;margin:26px 0 8px;padding-bottom:6px;border-bottom:1px solid #000}}
  ul{{font-size:13.5px;line-height:1.85;padding-left:20px}}
  .memo{{font-size:13px;line-height:1.8;color:#555}}
  .body{{font-size:13.5px;line-height:1.8}}
</style>
<div class="wrap">
<h1>{u['no']}. {esc(u['name'])}</h1>
<p class="sub">{esc(COURSE['name'])} · {esc(COURSE['ncs'])}</p>

<div class="defbox"><b>NCS 능력단위 정의</b> (ncs.go.kr 원문, 29차)<br>{esc(u['def'])}</div>

<div class="facts">
  <span>능력단위코드 <b class="pre">{u['code']}</b></span>
  <span>NCS 수준 <b>{u['lv']}</b></span>
  <span>편성 훈련시간 <b>{u['hr']}</b></span>
  <span>기간 <b>{sd} ~ {ed}</b></span>
  <span>본평가 <b>{ev}</b></span>
</div>
{extra}
<h2>학습목표</h2>
<ul>
{goals}
</ul>

<h2>선수지식</h2>
<ul>
{pres}
</ul>

<h2>차시별 전개</h2>
<table><thead><tr>
  <th style="width:56px">차시</th><th class="nm">내용</th>
  <th style="width:150px">방법</th><th style="width:66px">시간</th>
</tr></thead><tbody>
{rows}
</tbody></table>

<h2>실습</h2>
<p class="body">{esc(u['lab'])}</p>

<h2>평가</h2>
<p class="body"><b>평가방법</b> {esc(evs)}<br>
능력단위 정의의 수행 절차를 그대로 평가 항목으로 삼습니다.
루브릭 4단계(매우 우수 90~ / 우수 80~ / 보통 60~ / 미흡 60미만), 합격 하한 60점.</p>

<h2>교안 작성 메모</h2>
<p class="memo">{esc(u['note'])}</p>

<div class="note"><b>학습모듈 없음</b> — 이 세분류는 2025년 신설(<code>25v1</code>)이라
한국직업능력연구원의 NCS 학습모듈이 아직 제작되지 않았습니다. 교재를 직접 만들어야 합니다.</div>

<p style="margin-top:20px"><a class="btn" href="../courses/{COURSE['id']}.html">← 능력단위 목록으로</a></p>
<footer>{esc(COURSE['name'])} · {esc(COURSE['period'])} · 담당 {esc(COURSE['tc'])}</footer>
</div>
"""


def main():
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    (SITE / "courses").mkdir(exist_ok=True)
    (SITE / "modules").mkdir(exist_ok=True)
    write_courses()
    mods = write_modules()
    write_locks(mods)
    for i, u in enumerate(UNITS):
        (SITE / "modules" / f"c1-m{u['no']}.html").write_text(module_page(u, i), encoding="utf-8")
    print(f"courses.js · modules.js({len(mods)}) · locks.js")
    print(f"modules/c1-m01.html ~ c1-m{UNITS[-1]['no']}.html ({len(UNITS)}개)")


if __name__ == "__main__":
    main()
