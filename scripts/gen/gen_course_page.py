# -*- coding: utf-8 -*-
"""
과정 페이지(courses/<cid>.html)를 한 템플릿에서 찍어낸다.

c1 과 c2 를 손으로 각각 고치다 보니 칸 구성이 갈라졌다.
과정을 늘릴 때마다 또 갈라질 자리라, 템플릿 하나만 두고 courses.js 의
과정 목록을 돌며 생성한다. 과정을 추가하면 courses.js 에 한 줄 넣고
이 스크립트를 돌리면 끝이다.

칸 구성 (모든 과정 동일)
  능력단위 | 코드 | 강사 | 시작일 | 종료일 | 본평가 | 가이드 | 학습하기 | 평가 자료 | 표준 교안

  - 능력단위명 자체가 상세 링크다. 상세 단추를 따로 두지 않는다.
  - 수준 · 시간 · 평가방법 · 결석자평가 · 재평가는 표에서 뺐다.
    수준 · 시간은 표준 강의 교안 ①교과개요에, 평가방법은 ⑤평가계획에 있다.
    표를 좁게 두고 자세한 것은 교안에서 본다.

  python NCS-CATALOG/scripts/gen/gen_course_page.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[2] / "COURSE-MANAGEMENT"
A = SITE / "assets"


def jsvar(path, var):
    s = (A / path).read_text(encoding="utf-8")
    m = re.search(rf"window\.{var}\s*=\s*(\[.*?\]|\{{.*?\}});\s*$", s, re.S | re.M)
    if not m:
        return None
    raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fixed = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:',
                       lambda x: x.group(1) + '"' + x.group(2) + '":', raw)
        fixed = re.sub(r",(\s*[}\]])", lambda x: x.group(1), fixed)
        return json.loads(fixed)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


TEMPLATE = """<meta charset="utf-8"><title>능력단위 모듈 목록</title>
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a><small id="brandSub"></small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div>
<div class="nav" id="nav"></div>
</div>
<script>EXAM_AUTH.paintTop("../");</script>
<style>
  td.c{text-align:center}
  .sumbar{display:flex;gap:20px;flex-wrap:wrap;border:1px solid #000;
          padding:10px 14px;margin:14px 0;font-size:12.5px;background:#fafafa}
  .sumbar b{font-size:16px;margin-left:4px}
  .tscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
</style>
<div class="wrap">
<h1>능력단위 모듈 목록</h1>
<p class="sub" id="sub"></p>

<div class="role" id="roleBox">
  <span class="now">보기 모드 &nbsp;<b id="roleNow">일반(학생)</b></span>
  <span class="sp"></span>
  <button id="bLogin">관리자 로그인</button>
  <button id="bStudent">일반으로 보기</button>
</div>
<div class="login" id="loginBox">
  <label>아이디 <input id="lu" autocomplete="off"></label>
  <label>비밀번호 <input id="lp" type="password" autocomplete="off"></label>
  <button id="bDo">확인</button>
  <span class="msg" id="lmsg"></span>
</div>

<div class="sumbar">
  <span>능력단위 <b id="kCnt">0</b></span>
  <span>NCS 능력단위 <b id="kNcs">0</b></span>
  <span>평가 완료 <b id="kEv">0</b></span>
  <span>표준 교안 <b id="kLp">0</b></span>
</div>

<div class="note admonly" id="mNote"><b>능력단위 관리</b> — 표에서 <b>수정 · 삭제</b> 하고,
각 행의 <b>잠김/열림</b> 으로 학생이 자료를 열 수 있는지 정합니다. 바꾼 것은 이 브라우저에만 남습니다.
<b>설정 파일 저장</b> 을 눌러 <code>assets/modules-__CID__.js</code> 와
<code>assets/locks-__CID__.js</code> 에 덮어쓴 뒤 git 에 올려야 모두에게 적용됩니다.
<form class="cform" id="mForm">
  <input id="mName" placeholder="능력단위명" required>
  <input id="mCode" placeholder="능력단위코드 (예: 2001070705_25v1)">
  <input id="mTc" placeholder="강사" style="max-width:110px">
  <span class="cdate">기간 <input type="date" id="mSd"> ~ <input type="date" id="mEd"></span>
  <button type="submit">능력단위 추가</button>
</form>
<div style="margin-top:8px">
  <button id="bSaveMods" type="button">설정 파일 저장</button>
  <button id="bResetMods" type="button">되돌리기</button>
  <span id="mMsg" style="margin-left:10px;font-size:12.5px"></span>
</div></div>

<div class="tscroll"><table id="mtable"></table></div>
<footer id="foot"></footer>
</div>

<script src="../assets/courses.js"></script>
<script src="../assets/locks-__CID__.js"></script>
<script src="../assets/modules-__CID__.js"></script>
<script src="../assets/items-__CID__.js"></script>
<script>
(function(){
  var CID = '__CID__';
  var MKEY = 'cm_modules_' + CID, LKEY = 'cm_locks_' + CID;
  /* 편집 칸. 표의 단추 칸(준비 교안 · 평가 자료)은 자료 파일에서 나오므로 여기 없다. */
  var COLS = [['name','능력단위','text'],['code','능력단위코드','text'],['tc','강사','text'],
              ['sd','시작일','date'],['ed','종료일','date'],['ev','본평가','date'],
              ['page','상세','text'],['lp','표준 교안','text']];
  var NCOL = 10;                        /* 표시 칸 수 */
  var editing = -1;

  var course = (window.CM_COURSES || []).filter(function(c){ return c.id === CID; })[0] || {};

  function esc(s){ return String(s == null ? '' : s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function ymd(d){ return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2); }
  function isDate(s){ return /^\\d{4}-\\d{2}-\\d{2}$/.test(String(s || '')); }

  function base(){ return (window.CM_MODULES || []).slice(); }
  function list(){
    try{ var d = localStorage.getItem(MKEY); if(d) return JSON.parse(d); }catch(e){}
    return base();
  }
  function save(v){
    try{ localStorage.setItem(MKEY, JSON.stringify(v)); }
    catch(e){ alert('저장 공간이 부족합니다.'); }
  }

  /* 잠금 : 기본값은 assets/locks-<과정>.js, 관리자가 바꾼 것은 이 브라우저에만 */
  function ovr(){ try{ return JSON.parse(localStorage.getItem(LKEY) || '{}'); }catch(e){ return {}; } }
  function locked(id){ var o = ovr(); return (id in o) ? o[id] : !!(window.CM_LOCKS || {})[id]; }
  function setLock(id, v){
    var o = ovr(); o[id] = v;
    try{ localStorage.setItem(LKEY, JSON.stringify(o)); }catch(e){}
  }
  function lockChanged(){
    var o = ovr(), b = (window.CM_LOCKS || {});
    return Object.keys(o).some(function(k){ return !!o[k] !== !!b[k]; });
  }

  function head(){
    document.getElementById('brandSub').textContent = course.name || '';
    document.getElementById('sub').textContent =
      [course.name, course.ncs, course.hours, course.period].filter(Boolean).join(' · ');
    document.getElementById('foot').textContent =
      [course.name, course.period, '담당 ' + (course.tc || '')].filter(Boolean).join(' · ');
  }

  function nav(){
    var adm = EXAM_AUTH.isAdmin();
    document.getElementById('nav').innerHTML = list().map(function(m){
      var shut = (!adm && locked(m.id));
      return (m.page && !shut)
        ? '<a href="../' + esc(m.page) + '">' + esc(m.name) + '</a>'
        : '<a class="na">' + esc(m.name) + '</a>';
    }).join('');
  }

  function summary(v){
    var ncs = 0, done = 0, lp = 0;
    v.forEach(function(m){
      if(m.code) ncs++;
      if(m.ev && m.ev !== '-') done++;
      if(m.lp) lp++;
    });
    document.getElementById('kCnt').textContent = v.length;
    document.getElementById('kNcs').textContent = ncs;
    document.getElementById('kEv').textContent = done + ' / ' + v.length;
    document.getElementById('kLp').textContent = lp + ' / ' + v.length;
  }

  function draw(){
    var v = list(), adm = EXAM_AUTH.isAdmin(), h = '';
    h += '<tr><th>능력단위</th><th>코드</th><th>강사</th>' +
         '<th>시작일</th><th>종료일</th><th>본평가</th>' +
         '<th>가이드</th><th>학습하기</th><th>평가 자료</th><th>표준 교안</th></tr>';

    v.forEach(function(m, i){
      if(adm && i === editing){
        var tds = '';
        COLS.forEach(function(c){
          var val = m[c[0]] == null ? '' : m[c[0]];
          var type = (c[2] === 'date' && (isDate(val) || val === '')) ? 'date' : 'text';
          tds += '<td><input class="mi" data-f="' + c[0] + '" type="' + type +
                 '" value="' + esc(val) + '" placeholder="' + esc(c[1]) + '"></td>';
        });
        h += '<tr class="med">' + tds + '</tr>' +
             '<tr class="med"><td colspan="' + NCOL + '" class="mrow">' +
             '<button class="mok" data-i="' + i + '" type="button">저장</button>' +
             '<button class="mno" type="button">취소</button>' +
             '<span class="mhint">날짜가 아닌 값(예: -)은 그대로 적습니다. ' +
             '표준 교안은 비워 두면 양식 보기로 갑니다</span></td></tr>';
        return;
      }
      var lk = locked(m.id), shut = (!adm && lk), pg = m.page || '';
      var nm = (pg && !shut)
        ? '<a class="mlink" href="../' + esc(pg) + '">' + esc(m.name) + '</a>'
        : '<span class="mlink d">' + esc(m.name) + '</span>';
      // 가이드 — 준비 교안 한 장이라 바로 연다
      var hasG = !!(window.CM_GUIDES || {})[m.id];
      var gbtn = (hasG && !shut)
        ? '<a class="btn" href="../guides/' + esc(m.id) + '.html">확인</a>'
        : (hasG ? '<a class="btn d">확인</a>' : '<span class="non">—</span>');
      // 평가 자료 — 여러 건이라 상세의 평가 자료 자리로 보낸다
      var nItem = ((window.CM_ITEMS || {})[m.id] || []).length;
      var ebtn = (nItem && pg && !shut)
        ? '<a class="btn" href="../' + esc(pg) + '">자료 ' + nItem + '</a>'
        : (nItem ? '<a class="btn d">자료 ' + nItem + '</a>' : '<span class="non">—</span>');
      // 학습하기 — 가이드의 세부항목을 카드로 펼친 페이지
      var nStep = (window.CM_STUDY || {})[m.id] || 0;
      var sbtn = nStep
        ? (!shut ? '<a class="btn" href="../study/' + CID + '-' + esc(m.id) + '.html">단계 ' + nStep + '</a>'
                 : '<a class="btn d">단계 ' + nStep + '</a>')
        : '<span class="non">—</span>';
      // 표준 강의 교안 — 이 교과 것이 있으면 그리로, 없으면 양식을 보여 준다
      var lpbtn = (m.lp && !shut)
        ? '<a class="btn" href="../' + esc(m.lp) + '">교안</a>'
        : (m.lp ? '<a class="btn d">교안</a>'
                : '<a class="btn" href="../docs/표준강의교안-샘플.html">양식</a>');
      var tools = adm
        ? '<button class="lk' + (lk ? ' on' : '') + '" data-m="' + esc(m.id) + '" type="button">' +
          (lk ? '잠김' : '열림') + '</button>' +
          '<button class="med2" data-i="' + i + '" type="button">수정</button>' +
          '<button class="mdel" data-i="' + i + '" type="button">삭제</button>'
        : '';
      h += '<tr' + (lk ? '' : ' class="open"') + '><td class="nm">' + nm + '</td>' +
           '<td class="pre">' + (m.code ? esc(m.code) : '<span class="non">비NCS</span>') + '</td>' +
           '<td class="c">' + esc(m.tc) + '</td>' +
           '<td class="c">' + esc(m.sd) + '</td><td class="c">' + esc(m.ed) + '</td>' +
           '<td class="c">' + esc(m.ev || '-') + '</td>' +
           '<td class="tdb">' + gbtn + '</td>' +
           '<td class="tdb">' + sbtn + '</td>' +
           '<td class="tdb">' + ebtn + '</td>' +
           '<td class="tdb">' + lpbtn + tools + '</td></tr>';
    });
    document.getElementById('mtable').innerHTML = h;
    var _t = document.getElementById('mtable');
    if(_t.rows.length > 1 && _t.rows[0].cells.length !== _t.rows[1].cells.length){
      console.error('[' + CID + '] 표 머리글 ' + _t.rows[0].cells.length +
                    '칸, 본문 ' + _t.rows[1].cells.length + '칸 — 칼럼이 어긋났습니다.');
    }
    summary(v);
    nav();

    document.querySelectorAll('.lk').forEach(function(b){
      b.onclick = function(){ setLock(b.dataset.m, !locked(b.dataset.m)); draw(); };
    });
    document.querySelectorAll('.med2').forEach(function(b){
      b.onclick = function(){ editing = +b.dataset.i; draw(); };
    });
    document.querySelectorAll('.mno').forEach(function(b){
      b.onclick = function(){ editing = -1; draw(); };
    });
    document.querySelectorAll('.mdel').forEach(function(b){
      b.onclick = function(){
        var w = list(), i = +b.dataset.i;
        if(!confirm('"' + w[i].name + '" 을(를) 삭제합니다. 계속할까요?')) return;
        w.splice(i, 1); save(w); editing = -1; draw();
        document.getElementById('mMsg').textContent = '지웠습니다. 설정 파일 저장을 눌러야 반영됩니다.';
      };
    });
    document.querySelectorAll('.mok').forEach(function(b){
      b.onclick = function(){
        var w = list(), i = +b.dataset.i, got = {};
        document.querySelectorAll('tr.med .mi').forEach(function(e){ got[e.dataset.f] = e.value.trim(); });
        if(!got.name){ alert('능력단위명은 비워 둘 수 없습니다.'); return; }
        COLS.forEach(function(c){ w[i][c[0]] = got[c[0]]; });
        save(w); editing = -1; draw();
        document.getElementById('mMsg').textContent = '고쳤습니다. 설정 파일 저장을 눌러야 반영됩니다.';
      };
    });
  }

  function setDefaultDates(){
    var a = document.getElementById('mSd'), b = document.getElementById('mEd');
    if(!a || !b) return;
    var s0 = new Date(), e0 = new Date(); e0.setDate(e0.getDate() + 7);
    a.value = ymd(s0); b.value = ymd(e0);
  }
  var mf = document.getElementById('mForm');
  if(mf) mf.addEventListener('submit', function(e){
    e.preventDefault();
    var v = list(), n = 1, used = {};
    v.forEach(function(x){ used[x.id] = 1; });
    while(used['m' + ('0' + n).slice(-2)]) n++;
    var id = 'm' + ('0' + n).slice(-2);
    v.push({ id: id, name: document.getElementById('mName').value.trim(),
             code: document.getElementById('mCode').value.trim(),
             tc: document.getElementById('mTc').value.trim(),
             sd: document.getElementById('mSd').value, ed: document.getElementById('mEd').value,
             ev: '-', page: '', lp: '' });
    save(v); mf.reset(); setDefaultDates(); draw();
    document.getElementById('mMsg').textContent =
      id + ' 을 추가했습니다. 상세 페이지가 있으면 수정에서 modules/' + CID + '-' + id +
      '.html 을 적습니다. 설정 파일 저장을 눌러야 남습니다.';
  });

  var br = document.getElementById('bResetMods');
  if(br) br.onclick = function(){
    if(!confirm('파일에 저장된 내용으로 되돌립니다. 계속할까요?')) return;
    try{ localStorage.removeItem(MKEY); localStorage.removeItem(LKEY); }catch(e){}
    editing = -1; draw(); document.getElementById('mMsg').textContent = '';
  };

  function locksText(){
    var NL = String.fromCharCode(10), out = {};
    list().forEach(function(m){ out[m.id] = locked(m.id); });
    return ['/* 모듈별 잠금 상태.  true = 잠김(일반은 자료를 못 엽니다)',
            ' * courses/' + CID + '.html 의 [설정 파일 저장] 이 이 파일을 덮어씁니다.',
            ' * 고친 뒤 git 에 올려야 학생 화면에 적용됩니다.',
            ' */',
            'window.CM_LOCKS = ' + JSON.stringify(out, null, 2) + ';',
            ''].join(NL);
  }
  async function put(name, txt){
    if(window.showSaveFilePicker){
      try{
        var h = await showSaveFilePicker({ suggestedName: name,
          types: [{ description: 'JavaScript', accept: { 'text/javascript': ['.js'] } }] });
        var w = await h.createWritable(); await w.write(txt); await w.close();
        return 'saved';
      }catch(e){ if(e.name === 'AbortError') return 'cancel'; }
    }
    var a = document.createElement('a');
    a.href = 'data:text/javascript;charset=utf-8,' + encodeURIComponent(txt);
    a.download = name; document.body.appendChild(a); a.click(); a.remove();
    return 'download';
  }
  var bs = document.getElementById('bSaveMods');
  if(bs) bs.onclick = async function(){
    var NL = String.fromCharCode(10);
    var txt = ['/* 과정의 능력단위 모듈 목록.',
               ' * courses/' + CID + '.html 의 [설정 파일 저장] 이 이 파일을 덮어씁니다.',
               ' * 고친 뒤 git 에 올려야 모두에게 적용됩니다.',
               ' */',
               'window.CM_MODULES = ' + JSON.stringify(list(), null, 2) + ';',
               ''].join(NL);
    var m = document.getElementById('mMsg');
    var r = await put('modules-' + CID + '.js', txt);
    if(r === 'cancel'){ m.textContent = ''; return; }
    if(lockChanged()){
      m.textContent = 'modules-' + CID + '.js 를 저장했습니다. 이어서 locks-' + CID + '.js 를 저장합니다.';
      var r2 = await put('locks-' + CID + '.js', locksText());
      m.textContent = (r2 === 'cancel')
        ? 'modules-' + CID + '.js 만 저장했습니다. 잠금을 반영하려면 다시 눌러 locks-' + CID + '.js 도 저장합니다.'
        : 'modules-' + CID + '.js · locks-' + CID + '.js 저장 완료. git add/commit/push 하면 적용됩니다.';
      return;
    }
    m.textContent = (r === 'saved')
      ? 'modules-' + CID + '.js 저장 완료. git add/commit/push 하면 적용됩니다.'
      : 'modules-' + CID + '.js 를 내려받았습니다. assets/ 에 덮어쓴 뒤 git 에 올립니다.';
  };

  head();
  setDefaultDates();
  window.__drawMods = draw;
})();
</script>

<script>
(function(){
  var box = document.getElementById('roleBox'), now = document.getElementById('roleNow'),
      login = document.getElementById('loginBox'), msg = document.getElementById('lmsg');
  function paint(){
    var adm = EXAM_AUTH.isAdmin();
    now.textContent = EXAM_AUTH.label();
    box.classList.toggle('adm', adm);
    document.body.classList.toggle('admin', adm);
    if(window.__drawMods) window.__drawMods();
    document.getElementById('bLogin').style.display = adm ? 'none' : '';
    document.getElementById('bStudent').textContent = adm ? '관리자 해제' : '일반으로 보기';
    if(adm) login.classList.remove('on');
  }
  document.getElementById('bLogin').onclick = function(){
    login.classList.toggle('on'); msg.textContent = ''; document.getElementById('lu').focus();
  };
  document.getElementById('bStudent').onclick = function(){ EXAM_AUTH.logout(); paint(); };
  document.getElementById('bDo').onclick = async function(){
    msg.className = 'msg';
    var ok = await EXAM_AUTH.login(document.getElementById('lu').value,
                                   document.getElementById('lp').value);
    if(ok){ document.getElementById('lp').value = ''; msg.textContent = '관리자로 전환했습니다.'; paint(); }
    else { msg.className = 'msg err'; msg.textContent = '아이디 또는 비밀번호가 맞지 않습니다.'; }
  };
  document.getElementById('lp').addEventListener('keydown', function(e){
    if(e.key === 'Enter') document.getElementById('bDo').click();
  });
  paint();
})();
</script>
"""


def main():
    courses = jsvar("courses.js", "CM_COURSES") or []
    (SITE / "courses").mkdir(exist_ok=True)
    for c in courses:
        cid = c["id"]
        # 자료 파일이 없는 과정도 있다 — 없으면 빈 파일을 만들어 로드가 깨지지 않게 한다
        it = A / f"items-{cid}.js"
        if not it.exists():
            it.write_text(
                "/* 능력단위 상세의 자료 카드 · 준비 교안.\n"
                " * 아직 등록된 것이 없습니다. 형식은 items-c2.js 를 보세요.\n */\n"
                "window.CM_ITEMS = {};\nwindow.CM_GUIDES = {};\n", encoding="utf-8")
            print(f"  assets/items-{cid}.js 새로 만듦 (빈 목록)")
        (SITE / "courses" / f"{cid}.html").write_text(
            TEMPLATE.replace("__CID__", cid), encoding="utf-8")
        print(f"  courses/{cid}.html")
    print(f"\n과정 페이지 {len(courses)}개를 같은 템플릿에서 생성했습니다.")


if __name__ == "__main__":
    main()
