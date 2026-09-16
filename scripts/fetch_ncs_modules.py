# -*- coding: utf-8 -*-
"""
NCS 학습모듈(LM) PDF 조회/다운로드

출처: https://www.ncs.go.kr  NCS 활용 > NCS 통합검색 > 학습모듈 파일검색
  POST /unity/th03/ncsModuleFileSearch.do        (ncsClCd=<코드 또는 접두사>&pageIndex=N)
  POST /unity/hth01/hth0101/downloadFile.do      (sysDstinCd, fileMstky, filedetlSeq, ...)

⚠️ 학습모듈은 한국직업능력연구원이 제작한 저작물입니다.
   NCS 사이트는 다운로드 시 [활용 대상 선택] + [지적재산권 관련 고지 동의]를 요구합니다.
   --download 사용은 그 고지에 동의한 것으로 간주합니다. 반드시 원문 고지를 먼저 확인하세요.

사용:
  python fetch_ncs_modules.py --list                 # 우리 도메인 세분류의 학습모듈 목록만 조사
  python fetch_ncs_modules.py --list --code 20010202 # 특정 세분류만
  python fetch_ncs_modules.py --download             # 실제 PDF 내려받기 (동의 필요)
  python fetch_ncs_modules.py --download --latest-only  # 세분류별 최신 버전만
"""
import csv, json, re, ssl, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORG = ROOT.parent
DATA = ROOT / "data"
UA = "Mozilla/5.0 (compatible; NCS-CATALOG/1.0)"
SLEEP = 0.4          # 파일이 크므로 넉넉히
BASE = "https://www.ncs.go.kr"

_CTX = ssl.create_default_context()
_CTX.set_ciphers("DEFAULT:@SECLEVEL=1")
if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
    _CTX.options |= ssl.OP_LEGACY_SERVER_CONNECT

def parse_rows(html):
    """<tr rowindex="N"> 블록별로 파싱. 속성 사이 공백이 불규칙해 개별 정규식으로 뽑는다."""
    rows = []
    for chunk in html.split('<tr rowindex="')[1:]:
        idx = chunk[:chunk.index('"')]
        cl = re.search(r'colid="ncsClCd">\s*(\d{10}_\d{2}v\d+)', chunk)
        nm = re.search(r'colid="compeUnitNm">(.*?)</td>', chunk, re.S)
        if not cl:
            continue
        def val(name):
            m = re.search(r'value="([^"]*)"\s+id="' + name + idx + '"', chunk)
            return m.group(1) if m else ""
        rows.append({"idx": idx, "cl": cl.group(1),
                     "nm": re.sub(r"\s+", " ", nm.group(1)).strip() if nm else "",
                     "sys": val("sysDstinCd"), "mst": val("fileMstky"),
                     "seq": val("filedetlSeq")})
    return rows


def post(path, body, binary=False):
    req = urllib.request.Request(
        BASE + path, data=body.encode("utf-8"), method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": UA, "Referer": BASE + "/unity/th03/ncsModuleFileSearch.do"})
    with urllib.request.urlopen(req, timeout=180, context=_CTX) as res:
        data = res.read()
        cd = res.headers.get("Content-Disposition", "")
    time.sleep(SLEEP)
    return (data, cd) if binary else data.decode("utf-8", "replace")


def search(code):
    """세분류코드(8자리) 접두사로 학습모듈 전체 페이지를 긁는다."""
    out, seen, page = [], set(), 0
    while page <= 60:
        html = post("/unity/th03/ncsModuleFileSearch.do",
                    f"ncsClCd={code}&ncsSubdCdnm=&pageIndex={page}")
        rows = parse_rows(html)
        fresh = [r for r in rows if r["cl"] not in seen and r["mst"]]
        if not fresh:
            break
        for r in fresh:
            seen.add(r["cl"])
            out.append(r)
        page += 1
    return out


def load_targets():
    """mapping-domain.yml의 primary 세분류 → (domain, code, name)"""
    txt = (DATA / "mapping-domain.yml").read_text(encoding="utf-8")
    res, dom, sect = [], None, None
    for line in txt.splitlines():
        if re.match(r"^  [a-z0-9-]+:\s*$", line):
            dom, sect = line.strip().rstrip(":"), None
        elif re.match(r"^    (primary|related):", line):
            sect = line.strip().rstrip(":")
        elif dom and sect == "primary" and "code:" in line:
            m = re.search(r'code:\s*"(\d+)".*?name:\s*([^\s}]+)', line)
            if m:
                res.append((dom, m.group(1), m.group(2)))
    return res


def safe(s):
    return re.sub(r'[\/:*?"<>|]', "-", s).strip()


def repo_of(dom):
    """repo 이름은 mapping-domain.yml의 repo: 값이 기준(조직 repo명과 동일)."""
    if not hasattr(repo_of, "_cache"):
        txt = (DATA / "mapping-domain.yml").read_text(encoding="utf-8")
        cache, cur = {}, None
        for line in txt.splitlines():
            if re.match(r"^  [a-z0-9-]+:\s*$", line):
                cur = line.strip().rstrip(":")
            elif cur and re.match(r"^    repo:", line):
                cache[cur] = line.split(":", 1)[1].strip()
        repo_of._cache = cache
    return ORG / repo_of._cache[dom]


def target_dir(dom, sub_code, sub_name, unit_no):
    base = repo_of(dom) / "modules" / f"{sub_code}_{safe(sub_name)}"
    for d in base.glob(f"{unit_no}_*"):
        return d / "reference"
    return base / "_unmatched" / "reference"


def main():
    do_dl = "--download" in sys.argv
    latest = "--latest-only" in sys.argv
    only = None
    if "--code" in sys.argv:
        only = sys.argv[sys.argv.index("--code") + 1]

    targets = [t for t in load_targets() if not only or t[1] == only]
    index, total, dl = [], 0, 0

    for dom, code, name in targets:
        rows = search(code)
        # 능력단위별 최신 버전만
        if latest:
            best = {}
            for r in rows:
                k = r["cl"][:10]
                if k not in best or r["cl"] > best[k]["cl"]:
                    best[k] = r
            rows = list(best.values())
        rows.sort(key=lambda r: r["cl"])
        total += len(rows)
        print(f"[{dom}] {code} {name} : 학습모듈 {len(rows)}건")
        for r in rows:
            rec = {"domain": dom, "ncs_code": code, "subdivision": name,
                   "module_code": r["cl"], "unit_name": r["nm"],
                   "sysDstinCd": r["sys"], "fileMstky": r["mst"],
                   "filedetlSeq": r["seq"], "saved_as": None}
            if do_dl:
                unit_no = r["cl"][8:10]
                outdir = target_dir(dom, code, name, unit_no)
                outdir.mkdir(parents=True, exist_ok=True)
                body = (f"sysDstinCd={r['sys']}&fileMstky={r['mst']}"
                        f"&filedetlSeq={r['seq']}&ncsCompeUnitCd={unit_no}"
                        f"&downlDstinCd=02&histYn=N")
                done = list(outdir.glob(f"LM{r['cl']}*.pdf"))
                if done:
                    rec["saved_as"] = str(done[0].relative_to(ORG))
                    print(f"    = 있음 {done[0].name}")
                    index.append(rec)
                    continue
                blob, cd = post("/unity/hth01/hth0101/downloadFile.do", body, binary=True)
                if not blob.startswith(b"%PDF"):
                    print(f"    ! PDF 아님: {r['cl']}")
                    continue
                m = re.search(r"filename=([^;]+)", cd)
                fn = urllib.parse.unquote_plus(m.group(1).strip()) if m else f"{r['cl']}.pdf"
                path = outdir / safe(fn)
                path.write_bytes(blob)
                rec["saved_as"] = str(path.relative_to(ORG))
                dl += 1
                print(f"    ↓ {fn}  ({len(blob)//1024}KB)")
            index.append(rec)

    DATA.mkdir(exist_ok=True)
    (DATA / "learning-modules.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    with (DATA / "learning-modules.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(index[0].keys()) if index else ["module_code"])
        w.writeheader(); w.writerows(index)
    print(f"\n학습모듈 총 {total}건" + (f" / 다운로드 {dl}건" if do_dl else " (목록만)"))
    print(f"-> {DATA/'learning-modules.csv'}")


if __name__ == "__main__":
    main()
