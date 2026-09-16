# -*- coding: utf-8 -*-
"""
NCS 분류체계 / 능력단위 수집 스크립트
출처: https://www.ncs.go.kr  (NCS 및 학습모듈 검색 화면의 내부 조회 API)

  POST /unity/th03/getLclassCd.do
  POST /unity/th03/getMclassCd.do?ncsLclasCd=..
  POST /unity/th03/getSclassCd.do?ncsLclasCd=..&ncsMclasCd=..
  POST /unity/th03/getSubdCd.do?...&ncsSclasCd=..
  POST /unity/th03/getCompeUnit.do?...&ncsSubdCd=..

사용:
  python fetch_ncs.py            # 기본: 대분류 20(정보통신)
  python fetch_ncs.py 20 19      # 대분류 여러 개
  python fetch_ncs.py --all      # 24개 대분류 전체
산출:
  data/raw/<대분류코드>.json
  data/taxonomy.csv
  data/competency-units.csv
"""
import csv
import json
import html
import sys
import time
import urllib.parse
import urllib.request
import ssl
from pathlib import Path

BASE = "https://www.ncs.go.kr/unity/th03"
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
UA = "Mozilla/5.0 (compatible; NCS-CATALOG/1.0; +https://github.com/NCS-MODULE-CURRICULUMS)"
SLEEP = 0.15  # 공공 사이트 예의상 요청 간 간격

# ncs.go.kr은 구형 TLS 설정이라 파이썬 기본 컨텍스트로는 handshake가 실패한다.
_CTX = ssl.create_default_context()
_CTX.set_ciphers("DEFAULT:@SECLEVEL=1")
if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
    _CTX.options |= ssl.OP_LEGACY_SERVER_CONNECT


def post(path: str, **params):
    url = f"{BASE}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, data=b"", method="POST",
        headers={"X-Requested-With": "XMLHttpRequest", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=30, context=_CTX) as res:
        body = json.loads(res.read().decode("utf-8"))
    time.sleep(SLEEP)
    return body.get("data") or []


def clean(s):
    return html.unescape((s or "").strip())


def fetch_lclas(code: str):
    """대분류 1개의 전체 트리를 내려받는다."""
    tree = {"ncsLclasCd": code, "mclas": []}
    for m in post("getMclassCd.do", ncsLclasCd=code):
        tree["ncsLclasCdnm"] = clean(m["ncsLclasCdnm"])
        tree["ncsDegr"] = m.get("ncsDegr")
        mnode = {"cd": m["ncsMclasCd"], "nm": clean(m["ncsMclasCdnm"]), "sclas": []}
        for s in post("getSclassCd.do", ncsLclasCd=code, ncsMclasCd=m["ncsMclasCd"]):
            snode = {"cd": s["ncsSclasCd"], "nm": clean(s["ncsSclasCdnm"]), "subd": []}
            for d in post("getSubdCd.do", ncsLclasCd=code,
                          ncsMclasCd=m["ncsMclasCd"], ncsSclasCd=s["ncsSclasCd"]):
                units = post("getCompeUnit.do", ncsLclasCd=code,
                             ncsMclasCd=m["ncsMclasCd"], ncsSclasCd=s["ncsSclasCd"],
                             ncsSubdCd=d["ncsSubdCd"])
                snode["subd"].append({
                    "cd": d["ncsSubdCd"],
                    "nm": clean(d["ncsSubdCdnm"]),
                    "units": [{
                        "cd": u["ncsCompeUnitCd"],
                        "nm": clean(u["compeUnitName"]),
                        "ncsClCd": u["ncsClCd"],       # 10자리 + _YYvN
                    } for u in units],
                })
                print(f"  {code}-{m['ncsMclasCd']}-{s['ncsSclasCd']}-{d['ncsSubdCd']} "
                      f"{clean(d['ncsSubdCdnm'])} ({len(units)})")
            mnode["sclas"].append(snode)
        tree["mclas"].append(mnode)
    return tree


def write_csv(trees):
    DATA.mkdir(parents=True, exist_ok=True)
    tax = DATA / "taxonomy.csv"
    unit = DATA / "competency-units.csv"
    with tax.open("w", encoding="utf-8-sig", newline="") as ft, \
         unit.open("w", encoding="utf-8-sig", newline="") as fu:
        wt = csv.writer(ft)
        wu = csv.writer(fu)
        wt.writerow(["세분류코드", "대분류코드", "대분류", "중분류코드", "중분류",
                     "소분류코드", "소분류", "세분류코드2", "세분류", "능력단위수", "개정차수"])
        wu.writerow(["능력단위코드", "능력단위명", "세분류코드", "세분류",
                     "소분류", "중분류", "대분류", "개발연도버전"])
        for t in trees:
            L, Ln, degr = t["ncsLclasCd"], t.get("ncsLclasCdnm", ""), t.get("ncsDegr", "")
            for m in t["mclas"]:
                for s in m["sclas"]:
                    for d in s["subd"]:
                        full = f"{L}{m['cd']}{s['cd']}{d['cd']}"
                        wt.writerow([full, L, Ln, m["cd"], m["nm"], s["cd"], s["nm"],
                                     d["cd"], d["nm"], len(d["units"]), degr])
                        for u in d["units"]:
                            ver = u["ncsClCd"].split("_")[-1] if "_" in u["ncsClCd"] else ""
                            wu.writerow([u["ncsClCd"], u["nm"], full, d["nm"],
                                         s["nm"], m["nm"], Ln, ver])
    print(f"\n-> {tax}\n-> {unit}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--all" in sys.argv:
        codes = [f"{i:02d}" for i in range(1, 25)]
    else:
        codes = args or ["20"]
    RAW.mkdir(parents=True, exist_ok=True)
    trees = []
    for c in codes:
        print(f"[대분류 {c}]")
        t = fetch_lclas(c)
        (RAW / f"{c}.json").write_text(
            json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
        trees.append(t)
    write_csv(trees)


if __name__ == "__main__":
    main()
