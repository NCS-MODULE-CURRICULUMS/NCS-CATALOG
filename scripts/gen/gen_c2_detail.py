# -*- coding: utf-8 -*-
"""
c2 능력단위 상세 페이지 — 카드 UI 로 재생성.

섹션
  1. 평가 자료      포트폴리오 제출서 · 채점판 · 평가도구 · 샘플 문제지 (exam/)
  2. 준비 교안      guides/mNN.html (17개)
  3. 표준 강의 교안  「파이썬_표준강의교안_샘플.xlsx」의 6개 시트 구성

카드 마크업은 원본 site.css 의 .cards / .card / .card .d / .card dl / .card .go 를 그대로 쓴다.
"""
import json
import re
from pathlib import Path

ORG = Path(__file__).resolve().parents[3]
SITE = ORG / "COURSE-MANAGEMENT"

COURSE = {"id": "c2",
          "name": "(디지털 컨버전스) 공공데이터 융합 풀스택 개발자 양성과정E",
          "period": "2026-02-24 ~ 2026-08-12", "tc": "정우균"}

DETAIL = {
 "m01": {"meta": "평가일 2026-03-05 (09:00~18:00) · 포트폴리오 100점",
         "unit": "화면 설계 (2001020224_23v6) / 5수준",
         "method": "포트폴리오 (100점) · 합격선 60점",
         "desc": "[팀별제출] 웹기획을 위한 각 단계를 이행합니다. "
                 "유스케이스 다이어그램 · 명세서 → 스타일가이드 → 프로토타입 구현.",
         "score": "① UI 요구사항 확인하기 60점 (과제1 30 + 과제2 30) + ② UI 설계하기 40점 (과제3 40)",
         "submit": "스타일가이드 PDF · 프로토타입 Figma 링크 및 캡처 PDF · 유스케이스 문서"},
 "m16": {"meta": "평가일 2026-07-21 (09:00~18:00) · 문제해결시나리오 100점",
         "unit": "(비NCS 실기) — NCS 능력단위에 대응하지 않는 자체 실기 과목",
         "method": "문제해결 시나리오 (100점) · 합격선 60점",
         "desc": "공공데이터포털에서 확보한 데이터로 이진분류 모델을 학습하고, 그 모델을 API 로 "
                 "서비스한 뒤 인증이 적용된 웹 화면에서 예측하고 이력을 DB 로 관리(CRUD)하는 "
                 "서비스를 구축합니다.",
         "score": "공공데이터 융합 기초 30점 + 공공데이터 융합 DBMS 구축 70점",
         "submit": "PPT(실행화면 캡처 포함) · 소스 폴더(01 / 02 / 03) GITHUB REPO 링크"},
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def load_mods():
    t = (SITE / "assets" / "modules-c2.js").read_text(encoding="utf-8")
    return json.loads(re.search(r"window\.CM_MODULES = (\[.*\]);", t, re.S).group(1))


MODS = load_mods()


def page(m):
    d = DETAIL.get(m["id"])
    nav = "".join(
        (f'<a class="act" href="#">{esc(x["name"])}</a>' if x["id"] == m["id"]
         else f'<a class="na" href="../{x["page"]}">{esc(x["name"])}</a>')
        for x in MODS)

    facts = (f'<span>능력단위코드 <b class="pre">{esc(m["code"])}</b></span>'
             f'<span>세분류 <b>{esc(m["sub"])}</b></span>') if m["code"] else \
            '<span><b>NCS 능력단위에 대응하지 않는 자체 실기 과목</b></span>'

    overview = ""
    if d:
        overview = f"""<div class="note"><b>평가 개요</b><br>
능력단위 {esc(d['unit'])} · 평가방법 <b>{esc(d['method'])}</b><br>
{esc(d['desc'])}<br>
배점 — {esc(d['score'])}<br>
제출 — {esc(d['submit'])}</div>
<p class="memo">{esc(d['meta'])}</p>"""

    return f"""<meta charset="utf-8"><title>{esc(m['name'])}</title>
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a>
  <small><a href="../courses/{COURSE['id']}.html">{esc(COURSE['name'])}</a> / {esc(m['name'])}</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div>
<div class="nav">{nav}</div>
</div>
<script>EXAM_AUTH.paintTop("../");</script>
<style>
  .facts{{display:flex;gap:20px;flex-wrap:wrap;border:1px solid #000;padding:10px 14px;
         margin:14px 0;font-size:12.5px}}
  .facts b{{font-size:15px;margin-left:4px}}
  .sub2{{font-size:15px;margin:30px 0 8px;padding-bottom:6px;border-bottom:1px solid #000;font-weight:700}}
  .sub2 span{{font-weight:400;font-size:12px;color:#555;margin-left:8px}}
  .memo{{font-size:12.5px;line-height:1.7;color:#555}}
  .card .d{{min-height:0}}
  .tag{{display:inline-block;border:1px solid #000;padding:0 5px;font-size:10.5px;margin-left:5px}}
  .tag.off{{border-color:#bbb;color:#888}}
</style>
<div class="wrap">
<h1>{esc(m['name'])}</h1>
<p class="sub">{esc(COURSE['name'])}</p>

<div class="facts">
  {facts}
  <span>강사 <b>{esc(m['tc'])}</b></span>
  <span>기간 <b>{m['sd']} ~ {m['ed']}</b></span>
  <span>본평가 <b>{m['ev']}</b></span>
</div>
{overview}

<h2 class="sub2">평가 자료</h2>
<div class="cards" id="examCards"></div>

<h2 class="sub2">준비 교안</h2>
<div class="cards" id="guideCards"></div>

<h2 class="sub2">표준 강의 교안 <span id="lpSrc"></span></h2>
<p class="memo">교과목 운영계획서 6개 시트. 심사·인증 증빙과 훈련생 배포에 그대로 쓰는 양식입니다.
아래 카드의 항목을 이 교과에 맞게 채우면 됩니다.</p>
<div class="cards" id="lpCards"></div>
<div class="note"><b>작성 원칙</b><ul id="lpRules" style="margin:8px 0 0 18px;padding:0;font-size:12.5px;line-height:1.8"></ul></div>

<p style="margin-top:20px"><a class="btn" href="../courses/{COURSE['id']}.html">← 능력단위 모듈 목록으로</a></p>
<footer>{esc(COURSE['name'])} · {esc(COURSE['period'])} · 담당 {esc(COURSE['tc'])}</footer>
</div>

<script src="../assets/items-c2.js"></script>
<script src="../assets/lesson-plan.js"></script>
<script>
(function(){{
  var MID = '{m["id"]}';
  function esc(s){{ return String(s == null ? '' : s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }}
  function card(title, desc, meta, links){{
    var dl = (meta || []).map(function(x){{
      return '<dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd>';
    }}).join('');
    return '<div class="card"><h3>' + title + '</h3>' +
           (desc ? '<p class="d">' + esc(desc) + '</p>' : '') +
           (dl ? '<dl>' + dl + '</dl>' : '') +
           '<div class="go">' + links + '</div></div>';
  }}

  var adm = EXAM_AUTH.isAdmin();
  document.body.classList.toggle('admin', adm);

  /* 1. 평가 자료 */
  var items = (window.CM_ITEMS || {{}})[MID] || [];
  var vis = items.filter(function(it){{ return adm || !it.adm; }});
  document.getElementById('examCards').innerHTML = vis.length
    ? vis.map(function(it){{
        return card(esc(it.title) + (it.adm ? '<span class="tag">강사용</span>' : ''),
          it.desc, it.meta,
          '<a class="btn" href="' + encodeURI(it.link) + '">' + esc(it.btn || '열기') + '</a>');
      }}).join('')
    : '<div class="empty">평가 자료가 아직 등록되지 않았습니다.</div>';

  /* 2. 준비 교안 */
  var g = (window.CM_GUIDES || {{}})[MID];
  document.getElementById('guideCards').innerHTML = g
    ? card(esc(g) + ' 준비 교안',
        '평가를 처음 준비한다면 여기부터. 알아야 할 개념과 실습 순서를 난이도 4레벨로 정리했습니다.',
        [['형태', '단계별 지도안 (도입 → 전개 → 정리)'], ['난이도', '4레벨 구성']],
        '<a class="btn" href="../guides/' + MID + '.html">준비 교안 열기</a>')
    : '<div class="empty">준비 교안이 없습니다.</div>';

  /* 3. 표준 강의 교안 6개 시트 */
  var LP = window.CM_LESSON_PLAN || {{sheets:[], rules:[]}};
  document.getElementById('lpSrc').textContent = LP.src || '';
  document.getElementById('lpCards').innerHTML = LP.sheets.map(function(s, i){{
    var tags = (s.simsa ? '<span class="tag">심사 증빙</span>' : '') +
               (s.student ? '<span class="tag">훈련생 배포</span>' : '');
    return card(esc(s.no + ' ' + s.name) + tags, s.what,
      [['핵심 항목', s.keys.join(' / ')], ['작성 주체', s.who]],
      '<a class="btn" href="' + LP.view + '#s' + (i + 1) + '">양식 보기</a>' +
      '<a class="btn" href="' + LP.file + '" download>xlsx</a>');
  }}).join('');
  document.getElementById('lpRules').innerHTML =
    (LP.rules || []).map(function(r){{ return '<li>' + esc(r) + '</li>'; }}).join('');
}})();
</script>
"""


def main():
    md = SITE / "modules"
    for m in MODS:
        (md / f"c2-{m['id']}.html").write_text(page(m), encoding="utf-8")
    print(f"modules/c2-m01.html ~ c2-m{MODS[-1]['id'][1:]}.html ({len(MODS)}개) 카드 UI 로 재생성")


if __name__ == "__main__":
    main()
