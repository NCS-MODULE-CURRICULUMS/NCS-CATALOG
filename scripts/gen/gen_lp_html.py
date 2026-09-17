# -*- coding: utf-8 -*-
"""
표준 강의 교안(교과목 운영계획서)을 사이트에서 볼 수 있게 HTML 로 찍어낸다.

마크다운 교안(gen_pilot6.py)과 같은 데이터·같은 배분 함수를 쓴다.
마크다운을 변환하는 것이 아니라 원천에서 각각 찍으므로 둘이 갈라지지 않는다.

공개 범위는 양식이 정해 둔 대로 따른다 (assets/lesson-plan.js 의 student 값).
  훈련생도 본다   ③ 주차별계획 · ⑤ 평가계획 · ⑥ 훈련생안내
  강사(관리자)만  ① 교과개요 · ② NCS매핑 · ④ 차시별지도안
강사 전용 절은 site.css 의 .sc 로 감춘다 — body:not(.admin) .sc {display:none}

  python NCS-CATALOG/scripts/gen/gen_lp_html.py
"""
import html
import importlib.util
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORG = HERE.parents[2]
SITE = ORG / "COURSE-MANAGEMENT"
OUT = SITE / "lesson-plans"

spec = importlib.util.spec_from_file_location("gp", HERE / "gen_pilot6.py")
gp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gp)
LESSONS = gp.LESSONS

COURSE_ID = "c1"
SHEET_STUDENT = {"3", "5", "6"}          # 양식의 '훈련생 배포' 대상


def esc(s):
    return html.escape(str(s), quote=True)


def sheet(no, name, body, student):
    """절 하나. 훈련생 배포 대상이 아니면 .sc 로 감싼다."""
    cls = "" if student else " sc"
    tag = "" if student else '<span class="tag">강사용</span>'
    return (f'<section class="sheet{cls}">\n'
            f'  <h2 class="sub2" id="s{no}">{no}. {esc(name)}{tag}</h2>\n{body}\n</section>')


def page(no, u):
    p = gp.PLAN[no]
    elems = u["elems"]
    n_ses, alloc, hours = gp.allocate(no, u)
    mid = f"m{no}"

    # ② NCS매핑
    rows, cur = [], 1
    for (eno, ename, crits), h, a in zip(elems, hours, alloc):
        rng = f"{cur}~{cur + a - 1}차시" if a > 1 else f"{cur}차시"
        cur += a
        for i, c in enumerate(crits):
            cno, ctxt = c.split(" ", 1)
            if i == 0:
                rows.append(
                    f'<tr><td class="nm" rowspan="{len(crits)}"><span class="pre">'
                    f'{esc(u["code"])}.{eno}</span><br>{esc(ename)}</td>'
                    f'<td class="c">{cno}</td><td class="nm">{esc(ctxt)}</td>'
                    f'<td class="c" rowspan="{len(crits)}">{rng}</td>'
                    f'<td class="c" rowspan="{len(crits)}">{h}</td>'
                    f'<td class="c" rowspan="{len(crits)}">{round(h / p["hr"] * 100)}%</td></tr>')
            else:
                rows.append(f'<tr><td class="c">{cno}</td><td class="nm">{esc(ctxt)}</td></tr>')
    ncs_tbl = ('<div class="tscroll"><table><thead><tr>'
               '<th>능력단위요소(코드)</th><th>수행준거 번호</th><th class="nm">수행준거</th>'
               '<th>연계 차시</th><th>편성시간</th><th>비율</th></tr></thead><tbody>'
               + "\n".join(rows)
               + f'<tr class="on"><td colspan="4" class="nm"><b>합계</b></td>'
                 f'<td class="c"><b>{p["hr"]}</b></td><td class="c"><b>100%</b></td></tr>'
               '</tbody></table></div>')

    # ③ 주차별계획
    wk, cur = [], 1
    for (eno, ename, _), a in zip(elems, alloc):
        for j in range(a):
            ev = 2 if cur == n_ses else 0
            th = 0 if ev else (1 if j < a - 1 else 0.5)
            pr = 0 if ev else 2 - th
            wk.append(f'<tr><td class="c">{(cur + 1) // 2}</td><td class="c">{cur}</td>'
                      f'<td class="nm">{esc(ename)}</td><td class="nm fill">(채울 자리)</td>'
                      f'<td class="c">{th}</td><td class="c">{pr}</td><td class="c">{ev}</td>'
                      f'<td class="c">2</td><td class="c">{"본평가" if ev else ""}</td>'
                      f'<td class="c pre">{esc(u["code"])}.{eno}</td></tr>')
            cur += 1
    wk_tbl = ('<div class="tscroll"><table><thead><tr>'
              '<th>일차</th><th>차시</th><th class="nm">단원</th><th class="nm">학습내용</th>'
              '<th>이론</th><th>실습</th><th>평가</th><th>소계</th><th>평가/과제</th>'
              '<th>NCS요소</th></tr></thead><tbody>' + "\n".join(wk)
              + f'<tr class="on"><td colspan="7" class="nm"><b>합계</b></td>'
                f'<td class="c"><b>{p["hr"]}</b></td><td colspan="2"></td></tr>'
              '</tbody></table></div>')

    # ④ 차시별지도안 — 서식
    HEAD = ('<div class="tscroll"><table><thead><tr><th>단계</th><th>시간(분)</th>'
            '<th class="nm">교수 · 학습 활동 (강사 ↔ 훈련생)</th>'
            '<th class="nm">교수자료 · 도구</th><th class="nm">평가 · 과제</th></tr></thead><tbody>')
    les = LESSONS.get(no)
    if les:
        parts = ['<p class="memo">1차시 = 120분 = 도입 · 전개 · 정리. '
                 '<b>실제 수업에서 무엇을 어떻게 했는지</b>가 드러나야 한다 — '
                 '현장 모니터링에서 훈련일지 · 출석부와 대조된다.</p>']
        for L in les:
            rows = "".join(
                f'<tr><td class="c">{esc(st)}</td><td class="c">{mi}</td>'
                f'<td class="nm">{esc(act)}</td><td class="nm">{esc(mat)}</td>'
                f'<td class="nm">{esc(ev)}</td></tr>'
                for st, mi, act, mat, ev in L["stages"])
            tot = sum(x[1] for x in L["stages"])
            parts.append(
                f'<h3>{L["no"]}차시 — {esc(L["topic"])}</h3>'
                f'<p class="memo"><b>학습목표</b> {esc(L["goal"])}<br>'
                f'<b>연계 수행준거</b> {esc(L["crit"])}</p>'
                + HEAD + rows
                + f'<tr class="on"><td class="c"><b>소계</b></td>'
                  f'<td class="c"><b>{tot}</b></td><td colspan="3"></td></tr>'
                  '</tbody></table></div>')
        lesson_tbl = "".join(parts)
    else:
        stage = "".join(f'<tr><td class="c">{st}</td><td class="c">{mi}</td>'
                        f'<td class="nm fill">(교수 · 학습 활동)</td>'
                        f'<td class="nm fill">(교수자료)</td><td class="fill"></td></tr>'
                        for st, mi in gp.STAGE)
        lesson_tbl = ('<p class="memo">차시마다 아래 표를 채운다. 1차시 = 120분.</p>'
                      + HEAD + stage
                      + '<tr class="on"><td class="c">소계</td><td class="c">120</td>'
                        '<td colspan="3"></td></tr></tbody></table></div>'
                      f'<p class="memo">총 {n_ses}차시. 차시별 작성분은 아직 비어 있습니다 '
                      f'(<b>status: draft</b>).</p>')

    # ⑤ 평가계획
    ev_rows = "".join(
        f'<tr><td class="c">{i + 1}</td><td class="nm">{esc(m)}</td><td class="c">{w}%</td>'
        f'<td class="c">{p["ev"]}</td><td class="nm fill">(문항 구성)</td>'
        f'<td class="nm">{esc(t)}</td><td class="nm fill">(평가지 · 채점표)</td></tr>'
        for i, (m, w, t) in enumerate(gp.EVAL[no]))
    ev_sum = sum(w for _, w, _ in gp.EVAL[no])
    rub = [("매우 우수", "90 ~ 100", "수행준거를 모두 충족하고 지시 없이 스스로 판단해 처리한다"),
           ("우수", "80 ~ 89", "수행준거를 모두 충족한다. 일부 보완이 필요하나 스스로 고칠 수 있다"),
           ("보통", "60 ~ 79", "주요 수행준거를 충족한다. 지도를 받으면 완결할 수 있다 — <b>합격 하한</b>"),
           ("미흡", "60 미만", "수행준거를 충족하지 못한다 — 재평가 대상")]
    eval_body = (
        '<div class="tscroll"><table><thead><tr><th>No</th><th class="nm">평가 방법</th>'
        '<th>비중</th><th>시기</th><th class="nm">평가 내용 · 문항 구성</th>'
        '<th class="nm">대상 요소</th><th class="nm">평가 도구/증빙</th></tr></thead><tbody>'
        + ev_rows + f'<tr class="on"><td colspan="2" class="nm"><b>합계</b></td>'
        f'<td class="c"><b>{ev_sum}%</b></td><td colspan="4"></td></tr></tbody></table></div>'
        '<p class="memo"><b>합격 기준</b> 60점 · 미달 시 재평가</p>'
        '<h3>루브릭 (4단계)</h3><table><thead><tr><th>척도</th><th>환산</th>'
        '<th class="nm">판정 기준</th></tr></thead><tbody>'
        + "".join(f'<tr{" class=\"on\"" if a == "보통" else ""}><td class="nm">{a}</td>'
                  f'<td class="c">{b}</td><td class="nm">{c}</td></tr>' for a, b, c in rub)
        + '</tbody></table>'
        '<h3>사전 · 결석자 · 재평가</h3><table><thead><tr><th class="nm">구분</th>'
        '<th class="nm">시점</th><th class="nm">내용</th></tr></thead><tbody>'
        '<tr><td class="nm">사전평가</td><td class="nm">능력단위 시작 전</td>'
        '<td class="nm">훈련 전 수준 확인. 본평가와 <b>같은 문항을 쓰지 않는다</b>. 성적 미반영</td></tr>'
        f'<tr><td class="nm">본평가</td><td class="nm">{p["ev"]}</td><td class="nm">위 평가계획</td></tr>'
        '<tr><td class="nm">결석자평가</td><td class="nm">본평가 직후 예비일</td>'
        '<td class="nm">정당한 사유자 대상. <b>사유 증빙 보관</b></td></tr>'
        '<tr><td class="nm">재평가</td><td class="nm">미흡 판정 후</td>'
        '<td class="nm"><b>다른 과제</b>로 시행</td></tr></tbody></table>')

    # ① 교과개요
    elem_list = " / ".join(f"{'①②③④⑤'[i]} {esc(e[1])}" for i, e in enumerate(elems))
    goals = "".join(f"<li>{esc(e[1])} — {len(e[2])}개 수행준거를 충족할 수 있다.</li>"
                    for e in elems)
    pre = "".join(f"<li>{esc(x)}</li>" for x in gp.PRE[no])
    outline = (
        '<table><tbody>'
        f'<tr><td class="lb">훈련과정명</td><td class="nm">{esc(gp.COURSE["name"])}</td>'
        f'<td class="lb">훈련유형</td><td class="nm">{esc(gp.COURSE["types"])}</td></tr>'
        f'<tr><td class="lb">교과목명</td><td class="nm">{esc(u["name"])}</td>'
        f'<td class="lb">교과목 코드</td><td class="nm">{esc(p["cd"])}</td></tr>'
        f'<tr><td class="lb">훈련기간</td><td class="nm">{p["sd"]} ~ {p["ed"]}</td>'
        f'<td class="lb">정원</td><td class="nm">{esc(gp.COURSE["cap"])}</td></tr>'
        f'<tr><td class="lb">담당강사</td><td class="nm">{esc(gp.COURSE["tc"])}</td>'
        f'<td class="lb">훈련장소</td><td class="nm">{esc(gp.COURSE["room"])}</td></tr>'
        f'<tr><td class="lb">총 훈련시간</td><td class="nm"><b>{p["hr"]}시간</b> ({n_ses}차시)</td>'
        f'<td class="lb">이론 / 실습</td><td class="nm fill">(③에서 집계)</td></tr>'
        '</tbody></table>'
        f'<p class="memo"><b>NCS 분류</b> {esc(gp.COURSE["ncs_path"])}<br>'
        f'<b>능력단위</b> {esc(u["name"])} (<span class="pre">{esc(u["code"])}</span>) — 수준 {u["lv"]}<br>'
        f'<b>능력단위요소</b> {elem_list}</p>'
        f'<h3>교과 목표(총괄)</h3><p class="body">{esc(u["def"])}</p>'
        f'<h3>세부 학습목표</h3><ol class="body">{goals}</ol>'
        f'<h3>선수학습 / 입과요건</h3><ul class="body">{pre}</ul>'
        '<h3>교재 · 장비 · 자료</h3>'
        '<p class="body"><b>NCS 학습모듈 없음</b> — 이 세분류는 2025년 신설(<span class="pre">25v1</span>)이라 '
        '한국직업능력연구원의 학습모듈이 아직 제작되지 않았다. 교재를 직접 만들어야 한다.</p>')

    # ⑥ 훈련생안내
    notice = (
        '<table><tbody>'
        f'<tr><td class="lb">훈련과정</td><td class="nm">{esc(gp.COURSE["name"])}</td></tr>'
        f'<tr><td class="lb">교과목</td><td class="nm">{esc(u["name"])}</td></tr>'
        f'<tr><td class="lb">훈련기간</td><td class="nm">{p["sd"]} ~ {p["ed"]} '
        f'({p["hr"]}시간 · {n_ses}차시)</td></tr>'
        f'<tr><td class="lb">담당강사</td><td class="nm">{esc(gp.COURSE["tc"])}</td></tr>'
        f'<tr><td class="lb">강의실</td><td class="nm">{esc(gp.COURSE["room"])}</td></tr>'
        '</tbody></table>'
        f'<h3>이 교과를 마치면</h3><ol class="body">'
        + "".join(f"<li>{esc(e[1])}</li>" for e in elems) + '</ol>'
        f'<h3>평가</h3><p class="body">{esc(" · ".join(m for m, _, _ in gp.EVAL[no]))}'
        ' — 합격 기준 60점</p>')

    return f"""<meta charset="utf-8"><title>{esc(u['name'])} — 표준 강의 교안</title>
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a>
  <small><a href="../courses/{COURSE_ID}.html">{esc(gp.COURSE['name'])}</a> /
  {esc(u['name'])} / 표준 강의 교안</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div></div>
<script>EXAM_AUTH.paintTop("../");</script>
<style>
  .sub2{{font-size:15px;margin:30px 0 8px;padding-bottom:6px;border-bottom:1px solid #000;font-weight:700}}
  h3{{font-size:13.5px;margin:20px 0 6px}}
  .facts{{display:flex;gap:20px;flex-wrap:wrap;border:1px solid #000;padding:10px 14px;
         margin:14px 0;font-size:12.5px}}
  .facts b{{font-size:15px;margin-left:4px}}
  .body{{font-size:13.5px;line-height:1.8}}
  ol.body,ul.body{{padding-left:20px}}
  .memo{{font-size:12.5px;line-height:1.7;color:#555}}
  .tscroll{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
  td.c{{text-align:center}}
  td.lb{{background:#f0f0f0;font-weight:700;white-space:nowrap;width:104px}}
  td.fill{{color:#888}}
  .tag{{display:inline-block;border:1px solid #000;padding:0 5px;font-size:10.5px;margin-left:6px;
       font-weight:400}}
  .bar{{display:flex;gap:6px;flex-wrap:wrap;margin:20px 0 0}}
  .bar a{{border:1px solid #000;background:#fff;color:#000;padding:5px 14px;
         font-size:12.5px;text-decoration:none}}
  .bar a:hover{{background:#000;color:#fff}}
  @media print{{.top,.bar,.note{{display:none}} .sheet{{break-inside:avoid}}}}
</style>
<div class="wrap">
<h1>{esc(u['name'])}</h1>
<p class="sub">표준 강의 교안 (교과목 운영계획서) · {esc(gp.COURSE['name'])}</p>

<div class="facts">
  <span>능력단위코드 <b class="pre">{esc(u['code'])}</b></span>
  <span>NCS 수준 <b>{u['lv']}</b></span>
  <span>편성 훈련시간 <b>{p['hr']}</b></span>
  <span>차시 <b>{n_ses}</b></span>
  <span>본평가 <b>{p['ev']}</b></span>
</div>

<div class="note"><b>공개 범위</b> — 양식이 정한 대로 나뉩니다.
<b>③ 주차별계획 · ⑤ 평가계획 · ⑥ 훈련생안내</b>는 훈련생에게 배포하는 절이고,
<b>① 교과개요 · ② NCS매핑 · ④ 차시별지도안</b>은 심사 증빙용이라 강사에게만 보입니다.
<br>② 의 수행준거는 <b>ncs.go.kr 능력단위 정의서 원문</b>입니다. 문장을 고치지 않습니다.</div>

{sheet('1', '교과개요', outline, '1' in SHEET_STUDENT)}
{sheet('2', 'NCS매핑', ncs_tbl, '2' in SHEET_STUDENT)}
{sheet('3', '주차별계획', wk_tbl, '3' in SHEET_STUDENT)}
{sheet('4', '차시별지도안', lesson_tbl, '4' in SHEET_STUDENT)}
{sheet('5', '평가계획', eval_body, '5' in SHEET_STUDENT)}
{sheet('6', '훈련생안내', notice, '6' in SHEET_STUDENT)}

<section class="sheet sc">
  <h2 class="sub2">교안 작성 메모<span class="tag">강사용</span></h2>
  <p class="memo">{esc(gp.NOTE[no])}</p>
</section>

<p class="bar">
  <a href="../courses/{COURSE_ID}.html">← 능력단위 모듈 목록으로</a>
  <a href="../docs/표준강의교안-샘플.html">표준 강의 교안 양식</a>
</p>
<footer>{esc(gp.COURSE['name'])} · {esc(gp.COURSE['period'])} · 담당 {esc(gp.COURSE['tc'])}</footer>
</div>
<script>
(function(){{ document.body.classList.toggle('admin', EXAM_AUTH.isAdmin()); }})();
</script>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for no, u in gp.UNITS.items():
        f = OUT / f"{COURSE_ID}-m{no}.html"
        f.write_text(page(no, u), encoding="utf-8")
        made.append(f"lesson-plans/{f.name}")

    # modules-c1.js 의 lp 를 이 교안으로 잇는다
    p = SITE / "assets" / f"modules-{COURSE_ID}.js"
    s = p.read_text(encoding="utf-8")
    m = re.search(r"window\.CM_MODULES = (\[.*\]);", s, re.S)
    mods = json.loads(m.group(1))
    for x in mods:
        cand = f"lesson-plans/{COURSE_ID}-{x['id']}.html"
        if (SITE / cand).exists():
            x["lp"] = cand
    p.write_text(s[:m.start()] + "window.CM_MODULES = " +
                 json.dumps(mods, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    print(f"표준 강의 교안 {len(made)}개 — {made[0]} ~ {made[-1]}")
    print(f"modules-{COURSE_ID}.js 의 lp 연결 완료")


if __name__ == "__main__":
    main()
