# -*- coding: utf-8 -*-
"""
준비 교안을 만든다 — 학습모듈 원문의 짜임새대로, 강사가 무엇을 할지 적어서.

표준 강의 교안(6시트)은 심사에 내는 서류다. 준비 교안은 그것과 다르다.
수업 들어가기 전에 펼쳐 놓고 순서대로 따라가는 한 장짜리 문서다.

원문을 베끼지 않는다. 학습모듈 본문은 한국직업능력연구원 저작물이고
그 안에 제3자 도표·사진이 섞여 있어 공개 사이트에 옮길 수 없다.
대신 이렇게 한다.

  짜임새   능력단위요소(묶음) → 필요 지식 제목(단계)  — 원문 목차 그대로
  길잡이   단계마다 '원문 몇 쪽을 보라' 와 [원문 N쪽] 단추 (로컬 서버에서 바로 열린다)
  할 일    단계마다 무엇을 준비하고 무엇을 확인할지 — 우리가 쓴다

  python NCS-CATALOG/scripts/gen/lm_extract.py 20010202     # 먼저
  python NCS-CATALOG/scripts/gen/gen_guides.py 20010202
"""
import csv
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "NCS-CATALOG" / "data"
LM = DATA / "learning-modules"
OUT = ROOT / "COURSE-MANAGEMENT" / "guides"


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


SPY = """<script>
/* 빠른 이동 — 지금 보는 단계를 표시하고, 좁은 화면에서는 여닫습니다. */
(function () {
  var nav = document.getElementById('qnav'), btn = document.getElementById('qbtn');
  var links = [].slice.call(nav.querySelectorAll('a[href^="#st"]'));
  var tgt = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  btn.addEventListener('click', function () { nav.classList.toggle('open'); });
  nav.addEventListener('click', function (e) { if (e.target.closest('a')) nav.classList.remove('open'); });
  function mark() {
    var y = window.pageYOffset + 90, cur = -1;
    for (var i = 0; i < tgt.length; i++) if (tgt[i] && tgt[i].offsetTop <= y) cur = i;
    links.forEach(function (a, i) { a.classList.toggle('on', i === cur); });
  }
  var tick = false;
  window.addEventListener('scroll', function () {
    if (tick) return;
    tick = true;
    requestAnimationFrame(function () { mark(); tick = false; });
  });
  mark();
})();
</script>
"""

# 단계마다 붙는 '할 일'. 원문에 없는 말이므로 우리 문장으로 쓰고, 돌려쓴다.
TODO = [
    "이 항목을 슬라이드 한 장으로 줄여 보십시오. 한 장에 안 들어가면 아직 정리가 덜 된 것입니다.",
    "훈련생에게 던질 질문을 두 개 적어 두십시오. 답이 «예/아니오» 로 끝나지 않는 것으로.",
    "현장에서 쓰는 실제 사례를 하나 준비하십시오. 교재의 예시만으로는 잘 와닿지 않습니다.",
    "이 항목에서 훈련생이 가장 자주 틀리는 지점을 미리 적어 두고, 그 자리에서 한 번 멈추십시오.",
    "칠판에 그릴 그림을 미리 한 번 그려 보십시오. 즉석에서 그리면 순서가 엉킵니다.",
    "앞 단계와 어떻게 이어지는지 한 문장으로 말할 수 있어야 합니다. 그 문장을 적어 두십시오.",
]


def step_html(n, t, content, goals, methods, pdf_code, front):
    """단계 하나. aside 는 길잡이, bd 는 할 일."""
    pg = t.get("p")
    # 화면에는 인쇄된 쪽번호를, 뷰어에는 표지·차례만큼 민 실제 PDF 쪽을 준다
    src = (f'<a class="btn" href="#" data-pdf="{esc(pdf_code)}" '
           f'data-page="{pg + front}">원문 {pg}쪽</a>'
           if pg else '<span class="non">—</span>')
    goal = goals[0] if goals else ""
    return f"""
    <div class="step" id="st{n}">
      <h3><i>{n}</i>{esc(t["t"])}</h3>
      <aside class="side">
        <p class="pt">{esc(content)}</p>
        <b class="sh">원문</b>
        <p class="v">{src}</p>
        <b class="sh">평가</b>
        <p class="src">{esc(" · ".join(methods) or "—")}</p>
      </aside>
      <div class="bd">
{f'<h4>이 단계가 향하는 곳</h4>{chr(10)}<p>{esc(goal)}</p>' if goal else ''}
<h4>준비</h4>
<p>{esc(TODO[n % len(TODO)])}</p>
<div class="try">
  <b class="t">확인</b>
  훈련생이 <b>{esc(t["t"])}</b> 를 자기 말로 설명할 수 있으면 넘어갑니다.
  못 하면 원문 {pg or "해당"}쪽을 함께 읽고 한 번 더 묻습니다.
</div>
      </div>
    </div>
"""


def page(unit, lm, lv, hours):
    elems = lm["elements"]
    nav, body, n = [], [], 0
    for e in elems:
        nav.append(f'<i class="qg">{esc(e["name"])}</i>')
        steps = []
        for c in e["contents"]:
            for t in c["topics"]:
                n += 1
                nav.append(f'<a href="#st{n}"><b>{n}</b>'
                           f'<span>{esc(t["t"])}</span></a>')
                steps.append(step_html(n, t, c["title"], c["goals"],
                                       e["eval"]["methods"], unit["code"],
                                       lm.get("front", 0)))
            if not c["topics"]:
                n += 1
                nav.append(f'<a href="#st{n}"><b>{n}</b>'
                           f'<span>{esc(c["title"])}</span></a>')
                steps.append(step_html(n, {"t": c["title"], "p": c["printed"]},
                                       c["title"], c["goals"],
                                       e["eval"]["methods"], unit["code"],
                                       lm.get("front", 0)))
        body.append(
            f'<div class="lv">\n'
            f'  <div class="lvh"><b>{esc(e["no"])}. {esc(e["name"])}</b>'
            f'<span>능력단위요소 · <code>{esc(e["code"])}</code></span></div>\n'
            f'  <div class="lvb">{"".join(steps)}  </div>\n'
            f'</div>\n')

    methods = []
    for e in elems:
        for m in e["eval"]["methods"]:
            if m not in methods:
                methods.append(m)

    return f"""<meta charset="utf-8"><title>{esc(unit["name"])} — 준비 교안</title>
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/guide.css">
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<script>window.CM_BASE="../";</script>
<script src="../assets/modules-pdf.js"></script>
<script defer src="../assets/pdfview.js"></script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a><small>커리큘럼 /
  <a href="../curriculum/{esc(unit["dom"])}-{esc(unit["ncs"])}.html">{esc(unit["subd"])}</a>
  / {esc(unit["name"])} / 준비 교안</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div></div>
<script>EXAM_AUTH.paintTop("../");</script>

<button id="qbtn" type="button" aria-label="빠른 이동">목차</button>

<nav id="qnav" aria-label="빠른 이동">
  <a class="qt" href="#top"><b>↑</b><span>맨 위로</span></a>
  {"".join(nav)}
</nav>

<div class="wrap" id="top">

<h1>{esc(unit["name"])} — 준비 교안</h1>
<p class="sub">능력단위 <code>{esc(unit["code"])}</code> · {lv or "-"}수준 ·
{hours}시간 · 단계 {n}개 · 평가 {esc(" · ".join(methods) or "-")}</p>

<h2 class="sec" id="g0">0. 이 교과는 무엇인가</h2>
<div class="sect">
  <aside class="side">
    <p class="pt">{esc(lm["goal"])}</p>
    <b class="sh">선수학습</b>
    <p class="v">{esc(lm.get("prereq") or "—")}</p>
    <b class="sh">원문</b>
    <p class="src">{esc(lm["src"])} ({lm["pages"]}쪽)</p>
  </aside>
  <div class="bd">
<p>이 문서는 <b>수업 준비용</b>입니다. 심사에 내는 표준 강의 교안(6시트)과 다릅니다.
   차례와 단계는 <b>NCS 학습모듈 원문의 짜임새</b>를 그대로 따랐고,
   각 단계에 <b>무엇을 준비하고 무엇을 확인할지</b>를 적었습니다.</p>
<p><b>내용은 원문을 보십시오.</b> 학습모듈 본문은 한국직업능력연구원 저작물이라
   이 사이트에 옮겨 두지 않습니다. 단계마다 있는 <b>[원문 N쪽]</b> 단추가
   그 자리를 바로 펼칩니다(로컬 서버로 열었을 때).</p>

<h4>핵심 용어</h4>
<p>{esc(", ".join(lm.get("keywords") or []) or "—")}</p>

<h4>능력단위요소</h4>
<table class="wide">
  <tr><th style="width:48px">번호</th><th style="width:230px">요소</th>
      <th>학습 내용</th><th style="width:74px">단계</th></tr>
{chr(10).join(
    f'  <tr><td class="c">{esc(e["no"])}</td><td>{esc(e["name"])}</td>'
    f'<td>{esc(" · ".join(c["title"] for c in e["contents"]))}</td>'
    f'<td class="c">{sum(len(c["topics"]) or 1 for c in e["contents"])}</td></tr>'
    for e in elems)}
</table>

<div class="try">
  <b class="t">쓰는 법</b>
  왼쪽 <b>목차</b>에서 오늘 나갈 단계를 고르십시오.
  한 단계가 대략 수업 10~20분에 해당합니다.
</div>
  </div>
</div>

{"".join(body)}
<footer>담당 정우균 · 출처 NCS 학습모듈(한국직업능력연구원, 공공누리 제2유형) ·
원문 {esc(lm["src"])}</footer>
</div>
{SPY}"""


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ncs = {r["능력단위코드"]: r for r in
           csv.DictReader(open(DATA / "competency-units.csv", encoding="utf-8-sig"))}
    st = json.loads((DATA / "curriculum-status.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    made = skip = 0
    for uc, u in sorted(st["units"].items(), key=lambda kv: (kv[1]["s"], kv[1]["seq"])):
        if only and u["s"] != only:
            continue
        f = LM / f"{uc}.json"
        if not f.exists():
            skip += 1
            continue
        lm = json.loads(f.read_text(encoding="utf-8"))
        r = ncs.get(uc, {})
        lv = int(r["수준"]) if r.get("수준", "").isdigit() else None
        unit = {"code": uc, "name": u["n"], "ncs": u["s"], "dom": u["d"],
                "subd": r.get("세분류", "")}
        htm = page(unit, lm, lv, u.get("hr") or 0)
        (OUT / f"lm-{uc}.html").write_text(htm, encoding="utf-8")
        n = htm.count('class="step"')
        made += 1
        print(f"{u['seq']} {u['n'][:22]:24} 단계 {n:3} · {len(htm) // 1024:3}KB")

    print(f"\n준비 교안 {made}건 · 건너뜀 {skip} -> COURSE-MANAGEMENT/guides/lm-*.html")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
