# -*- coding: utf-8 -*-
"""
학습 가이드를 만든다 — 훈련생이 읽고 이해하고 실습하는 한 장짜리 문서.

표준 강의 교안(6시트)은 심사 서류고, 이것은 수업에서 쓰는 문서다.
한 꼭지(학습내용)마다 네 덩어리로 간다.

  무엇을 할 수 있게 되나   학습목표 (학습모듈 원문)
  알아야 할 것            개념 — 필요 지식의 제목과 요지 (원문 인용)
  해 보기                실습 — 준비물과 수행 순서 (원문 인용)
  스스로 확인             학습목표를 체크리스트로

원문 본문을 통째로 옮기지 않는다. 요지와 절차만 옮기고, 자세한 설명과 표·그림은
꼭지마다 있는 [원문 N쪽] 단추로 학습모듈을 그 자리에서 펼쳐 본다.
출처는 쪽마다 밝힌다(공공누리 제2유형 · 출처표시 · 상업적 이용 금지).

  python NCS-CATALOG/scripts/gen/lm_extract.py 20010202         # 먼저
  python NCS-CATALOG/scripts/gen/gen_guides.py 20010202         # 세분류 전체
  python NCS-CATALOG/scripts/gen/gen_guides.py 2001020201_23v5  # 한 건만
"""
import csv
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deep  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "NCS-CATALOG" / "data"
LM = DATA / "learning-modules"
OUT = ROOT / "COURSE-MANAGEMENT" / "guides"


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


CSS = """<style>
  /* 학습 가이드 — 개념 / 실습 / 확인 세 덩어리가 눈으로 구분되어야 한다 */
  .bd h4{margin:22px 0 8px;font-size:14px;padding-bottom:5px;border-bottom:1px solid #000}
  .bd h4:first-child{margin-top:0}
  .bd h5{margin:16px 0 5px;font-size:13px;font-weight:700}
  .bd blockquote{margin:5px 0 12px;padding:9px 13px;border-left:3px solid #999;
                 background:#fafafa;font-size:13px;line-height:1.8;color:#333}
  .cc{margin:0 0 6px}
  .cc dt{font-weight:700;font-size:13.5px;margin:14px 0 0}
  .cc dd{margin:4px 0 0}
  .doh{display:flex;gap:9px;align-items:baseline;margin:16px 0 4px;font-size:13.5px;
       font-weight:700}
  .doh b{flex:0 0 auto;width:21px;height:21px;line-height:19px;text-align:center;
         border:1px solid #000;font-size:11.5px}
  ol.dos{margin:2px 0 0 30px;padding:0;font-size:13px;line-height:1.85}
  ol.dos li{margin:3px 0}
  .prep{display:grid;grid-template-columns:76px 1fr;gap:3px 10px;font-size:12.5px;
        border:1px solid #ccc;padding:10px 13px;margin:6px 0 2px;background:#fafafa}
  .prep b{color:#555;font-weight:400}
  ul.goal{margin:6px 0 0;padding-left:20px;font-size:13.5px;line-height:1.9}
  ul.chk{margin:6px 0 0;padding:0;list-style:none;font-size:13.5px;line-height:1.95}
  ul.chk li::before{content:"\\2610  "}
  .none{color:#888;font-size:12.5px}
  .srcline{font-size:11.5px;color:#888;margin:8px 0 0}
  .tools{display:grid;gap:8px;margin:8px 0 4px}
  .tool{border:1px solid #000;padding:10px 13px}
  .tool b{font-size:13.5px}
  .tool span{margin-left:8px;font-size:12px}
  .tool p{margin:5px 0 0;font-size:12.5px;color:#444;line-height:1.75}
  p.tip{margin:6px 0 0 30px;font-size:12.5px;color:#444;line-height:1.75}
  p.tip b{border:1px solid #000;padding:0 5px;font-size:11px;margin-right:6px}
  ul.miss{margin:8px 0 0;padding-left:20px;font-size:13px;line-height:1.85}
  ul.miss li{margin:5px 0}
  .ci{margin:0 0 22px;padding:0 0 0 13px;border-left:2px solid #ddd}
  .ci h5{margin:0 0 6px;font-size:14px}
  .ci p{margin:9px 0;font-size:13.5px;line-height:1.85}
  .mini{border:1px solid #000;padding:11px 14px;margin:12px 0 0}
  .mini b.t{display:inline-block;border:1px solid #000;padding:0 7px;
            font-size:11px;margin-right:8px}
  .mini ol.dos{margin:8px 0 0 22px}
</style>"""

SPY = """<script>
/* 빠른 이동 — 지금 보는 꼭지를 표시하고, 좁은 화면에서는 여닫습니다. */
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
</script>"""


def pdf_btn(code, printed, front):
    if not printed:
        return '<span class="non">&mdash;</span>'
    return (f'<a class="btn" href="#" data-pdf="{esc(code)}" '
            f'data-page="{printed + front}">원문 {printed}쪽</a>')


def concepts(topics, notes=None):
    """알아야 할 것 — 항목마다 원문 정리 · 풀어 설명 · 그 항목의 실습.

    원문 정리는 학습모듈에서 뽑은 것이고, 풀어 설명과 실습은 우리가 쓴 것이다
    (deep/ 원고). 원고가 없는 항목은 원문 정리만 나온다."""
    notes = notes or {}
    if not topics:
        return '<p class="none">이 꼭지는 실습 중심입니다. 바로 해 보기로 갑니다.</p>'
    out, bare = [], []
    for t in topics:
        note = notes.get(t["t"])
        if not t.get("s") and not note:
            bare.append(t["t"])
            continue
        out.append(f"<div class='ci'><h5>{esc(t['t'])}</h5>")
        if t.get("s"):
            out.append(f"<blockquote>{esc(t['s'])}</blockquote>")
        if note:
            for para in note.get("more", []):
                out.append(f"<p>{para}</p>")
            if note.get("table"):
                head, *rows = note["table"]
                out.append("<table class='wide'><tr>"
                           + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr>")
                for r in rows:
                    out.append("<tr>" + "".join(f"<td>{esc(v)}</td>" for v in r) + "</tr>")
                out.append("</table>")
            d = note.get("do")
            if d:
                out.append(f"<div class='mini'><b class='t'>해 보기</b> {esc(d['h'])}"
                           + "<ol class='dos'>"
                           + "".join(f"<li>{x}</li>" for x in d["steps"]) + "</ol>"
                           + (f"<p class='tip'><b>tip</b> {d['tip']}</p>"
                              if d.get("tip") else "") + "</div>")
        out.append("</div>")
    if bare:
        out.append("<p class='none'>함께 나오는 것 — " + esc(" · ".join(bare)) + "</p>")
    return "".join(out)


def practice(dos):
    """해 보기 — 준비물과 수행 순서. 원문 절차를 그대로 옮긴다."""
    if not dos:
        return ('<p class="none">학습모듈이 이 꼭지에 따로 제시한 실습 절차가 '
                '없습니다. 앞 꼭지의 절차를 이어서 씁니다.</p>')
    out = []
    for d in dos:
        if d["title"]:
            out.append(f"<h5>{esc(d['title'])}</h5>")
        rows = []
        for key, lab in (("재료", "재료·자료"), ("기기", "기기·도구"), ("유의", "유의 사항")):
            if d[key]:
                rows.append(f"<b>{lab}</b><span>{esc(' / '.join(d[key]))}</span>")
        if rows:
            out.append(f"<div class='prep'>{''.join(rows)}</div>")
        for i, st in enumerate(d["steps"], 1):
            out.append(f"<div class='doh'><b>{i}</b><span>{esc(st['h'])}</span></div>")
            if st["items"]:
                out.append("<ol class='dos'>"
                           + "".join(f"<li>{esc(x)}</li>" for x in st["items"])
                           + "</ol>")
    return "".join(out)


def checklist(goals):
    return ("<ul class='chk'>"
            + ("".join(f"<li>{esc(g)}</li>" for g in goals) or "<li>&mdash;</li>")
            + "</ul>")



def deep_why(d):
    """왜 하는가 — 개념보다 먼저 와야 한다. 이유를 모르고 외우면 남지 않는다."""
    if not d or not d.get("why"):
        return ""
    return "<h4>왜 하는가</h4>" + "".join(f"<p>{x}</p>" for x in d["why"])


def deep_blocks(d):
    """혼자 할 수 있게 쓴 원고 — 도구 · 따라 하기 · 예제 · 흔한 실수 · 산출물."""
    if not d:
        return ""
    out = []

    if d.get("tools"):
        out.append("<h4>쓰는 도구</h4><div class='tools'>")
        for t in d["tools"]:
            link = (f'<a href="{esc(t["url"])}">{esc(t["url"])}</a>'
                    if t.get("url") else "")
            out.append(f"<div class='tool'><b>{esc(t['name'])}</b>"
                       f"{'<span>' + link + '</span>' if link else ''}"
                       f"<p>{t['note']}</p></div>")
        out.append("</div>")

    if d.get("walk"):
        out.append("<h4>따라 하기</h4>")
        for i, w in enumerate(d["walk"], 1):
            out.append(f"<div class='doh'><b>{i}</b><span>{esc(w['h'])}</span></div>")
            out.append("<ol class='dos'>"
                       + "".join(f"<li>{x}</li>" for x in w["steps"]) + "</ol>")
            if w.get("tip"):
                out.append(f"<p class='tip'><b>tip</b> {w['tip']}</p>")

    ex = d.get("example")
    if ex:
        out.append(f"<h4>{esc(ex['title'])}</h4>")
        if ex.get("intro"):
            out.append(f"<p>{ex['intro']}</p>")
        if ex.get("table"):
            head, *rows = ex["table"]
            out.append("<table class='wide'><tr>"
                       + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr>")
            for r in rows:
                out.append("<tr>" + "".join(
                    f"<td{' class=\'nm\'' if k else ''}>{esc(v)}</td>"
                    for k, v in enumerate(r)) + "</tr>")
            out.append("</table>")
        if ex.get("note"):
            out.append(f"<p class='srcline'>{ex['note']}</p>")

    if d.get("mistakes"):
        out.append("<h4>흔한 실수</h4><ul class='miss'>"
                   + "".join(f"<li>{x}</li>" for x in d["mistakes"]) + "</ul>")

    if d.get("output"):
        out.append("<h4>내야 할 것</h4><ul class='chk'>"
                   + "".join(f"<li>{x}</li>" for x in d["output"]) + "</ul>")

    return "".join(out)


def section(n, e, c, code, front, deep_d=None):
    """한 꼭지 = 학습내용 하나."""
    n_do = sum(len(s["items"]) for d in c["do"] for s in d["steps"])
    return f"""
    <div class="step" id="st{n}">
      <h3><i>{n}</i>{esc(c['no'])}. {esc(c['title'])}</h3>
      <aside class="side">
        <p class="pt">{esc(c['goals'][0] if c['goals'] else e['name'])}</p>
        <b class="sh">능력단위요소</b>
        <p class="v">{esc(e['name'])}</p>
        <b class="sh">학습모듈</b>
        <p class="v">{pdf_btn(code, c['printed'], front)}</p>
        <b class="sh">분량</b>
        <p class="src">개념 {len(c['topics'])}항목 · 실습 {n_do}절차</p>
      </aside>
      <div class="bd">
<h4>이 꼭지를 마치면</h4>
<ul class="goal">{"".join(f"<li>{esc(g)}</li>" for g in c["goals"]) or "<li>&mdash;</li>"}</ul>

{deep_why(deep_d)}
<h4>알아야 할 것</h4>
{concepts(c["topics"], (deep_d or {}).get("topics"))}

{deep_blocks(deep_d)}
<h4>학습모듈이 제시한 실습 절차</h4>
{practice(c["do"])}

<h4>스스로 확인</h4>
{checklist([st["h"] for d in c["do"] for st in d["steps"]] + c["goals"])}
<p class="srcline">평가 방법 — {esc(" · ".join(e["eval"]["methods"]) or "—")}</p>
<div class="try">
  <b class="t">막히면</b>
  옆의 <b>원문 {c['printed']}쪽</b> 단추를 누르십시오.
  이 꼭지의 자세한 설명과 표·그림이 그 자리에 있습니다.
</div>
      </div>
    </div>
"""


def page(unit, lm, lv, hours, deep_d=None):
    elems, front = lm["elements"], lm.get("front", 0)
    deep_d = deep_d or {}
    nav, body, n = [], [], 0
    for e in elems:
        nav.append(f'<i class="qg">{esc(e["name"])}</i>')
        steps = []
        for c in e["contents"]:
            n += 1
            nav.append(f'<a href="#st{n}"><b>{n}</b><span>{esc(c["title"])}</span></a>')
            steps.append(section(n, e, c, unit["code"], front,
                                 deep_d.get(c["no"])))
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
    n_top = sum(len(c["topics"]) for e in elems for c in e["contents"])
    n_do = sum(len(s["items"]) for e in elems for c in e["contents"]
               for d in c["do"] for s in d["steps"])
    rows = "\n".join(
        f'  <tr><td class="c">{i}</td><td>{esc(c["no"])}. {esc(c["title"])}</td>'
        f'<td>{esc(e["name"])}</td><td class="c">{len(c["topics"])}</td>'
        f'<td class="c">{sum(len(s["items"]) for d in c["do"] for s in d["steps"])}</td>'
        f'<td class="c">{"있음" if c["no"] in deep_d else "—"}</td></tr>'
        for i, (e, c) in enumerate(((e, c) for e in elems for c in e["contents"]), 1))

    return f"""<meta charset="utf-8"><title>{esc(unit["name"])} — 학습 가이드</title>
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/guide.css">
{CSS}
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<script>window.CM_BASE="../";</script>
<script src="../assets/modules-pdf.js"></script>
<script defer src="../assets/pdfview.js"></script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a><small>커리큘럼 /
  <a href="../curriculum/{esc(unit["dom"])}-{esc(unit["ncs"])}.html">{esc(unit["subd"])}</a>
  / {esc(unit["name"])} / 학습 가이드</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div></div>
<script>EXAM_AUTH.paintTop("../");</script>

<button id="qbtn" type="button" aria-label="빠른 이동">목차</button>

<nav id="qnav" aria-label="빠른 이동">
  <a class="qt" href="#top"><b>&uarr;</b><span>맨 위로</span></a>
  {"".join(nav)}
</nav>

<div class="wrap" id="top">

<h1>{esc(unit["name"])} — 학습 가이드</h1>
<p class="sub">능력단위 <code>{esc(unit["code"])}</code> · {lv or "-"}수준 ·
{hours}시간 · 꼭지 {n}개 · 개념 {n_top}항목 · 실습 {n_do}절차</p>

<h2 class="sec" id="g0">0. 시작하기 전에</h2>
<div class="sect">
  <aside class="side">
    <p class="pt">{esc(lm["goal"])}</p>
    <b class="sh">먼저 알아야 할 것</b>
    <p class="v">{esc(lm.get("prereq") or "—")}</p>
    <b class="sh">평가</b>
    <p class="src">{esc(" · ".join(methods) or "—")}</p>
  </aside>
  <div class="bd">
<h4>이 문서를 쓰는 법</h4>
<p>꼭지마다 <b>무엇을 할 수 있게 되나 → 알아야 할 것 → 해 보기 → 스스로 확인</b>
   순서입니다. 읽고 끝내지 말고 <b>해 보기</b>를 손으로 따라 하십시오.
   마지막 <b>스스로 확인</b>을 전부 «할 수 있다» 고 말할 수 있으면 다음 꼭지로 갑니다.</p>
<p>자세한 설명과 표·그림은 <b>학습모듈 원문</b>에 있습니다. 꼭지마다 있는
   <b>[원문 N쪽]</b> 단추를 누르면 그 자리가 바로 펼쳐집니다.</p>

<h4>핵심 용어</h4>
<p>{esc(", ".join(lm.get("keywords") or []) or "—")}</p>

<h4>차례</h4>
<table class="wide">
  <tr><th style="width:44px">꼭지</th><th style="width:250px">학습 내용</th>
      <th>능력단위요소</th><th style="width:58px">개념</th><th style="width:58px">실습</th>
      <th style="width:70px">실습원고</th></tr>
{rows}
</table>
  </div>
</div>

{"".join(body)}
<footer>담당 정우균 · 개념과 절차는 <b>NCS 학습모듈 {esc(lm["src"])}</b> 에서
옮긴 것입니다 — 한국직업능력연구원 · 공공누리 제2유형(출처표시 · 상업적 이용 금지)</footer>
</div>
{SPY}"""


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    ncs = {r["능력단위코드"]: r for r in
           csv.DictReader(open(DATA / "competency-units.csv", encoding="utf-8-sig"))}
    st = json.loads((DATA / "curriculum-status.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    made = 0
    for uc, u in sorted(st["units"].items(), key=lambda kv: (kv[1]["s"], kv[1]["seq"])):
        if arg and arg not in (u["s"], uc):
            continue
        f = LM / f"{uc}.json"
        if not f.exists():
            continue
        lm = json.loads(f.read_text(encoding="utf-8"))
        r = ncs.get(uc, {})
        lv = int(r["수준"]) if r.get("수준", "").isdigit() else None
        unit = {"code": uc, "name": u["n"], "ncs": u["s"], "dom": u["d"],
                "subd": r.get("세분류", "")}
        htm = page(unit, lm, lv, u.get("hr") or 0, deep.load(uc))
        (OUT / f"lm-{uc}.html").write_text(htm, encoding="utf-8")
        made += 1
        n_t = sum(len(c["topics"]) for e in lm["elements"] for c in e["contents"])
        n_d = sum(len(s["items"]) for e in lm["elements"] for c in e["contents"]
                  for d in c["do"] for s in d["steps"])
        print(f"{u['seq']} {u['n'][:22]:24} 꼭지 {htm.count('class=\"step\"'):2} · "
              f"개념 {n_t:3} · 실습 {n_d:3} · {len(htm) // 1024:3}KB")

    print(f"\n학습 가이드 {made}건 -> COURSE-MANAGEMENT/guides/lm-*.html")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
