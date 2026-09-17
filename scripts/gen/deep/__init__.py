# -*- coding: utf-8 -*-
"""
꼭지별 '혼자서 할 수 있는' 실습 원고.

학습모듈 PDF 는 개념과 추상적인 절차까지만 준다 — "자료를 수집한다", "결정한다".
훈련생이 강사 없이 혼자 해내려면 그 사이가 채워져야 한다.
어떤 도구를 쓰는지, 어디를 눌러야 하는지, 결과가 어떻게 생겼는지.
그것은 뽑아낼 수 없고 써야 한다. 여기가 그 원고가 사는 자리다.

파일 하나가 능력단위 하나다.  deep/lm_<능력단위코드 앞 10자리>.py
그 안에 DEEP 이라는 사전을 두고, 열쇠는 학습내용 번호("2-1")다.

  DEEP = {
    "2-1": {
      "why":   [문단, 문단]              왜 하는가 — 쉬운 말로
      "tools": [{"name","url","note"}]   쓰는 도구 (실제로 쓰는 것만)
      "walk":  [{"h": 단계 제목,
                 "steps": [지시, 지시],   눌러야 할 곳까지 구체적으로
                 "tip": 한 줄}]
      "example": {"title","intro","table":[[머리],[행]],"note"}
      "mistakes": [흔한 실수]
      "output":   [산출물 체크 항목]
    }
  }

원고가 없는 꼭지는 학습모듈에서 뽑은 것만 나온다. 있으면 그 자리에 끼워 넣는다.
그래서 한 꼭지씩 채워 나갈 수 있고, 채운 만큼 진척으로 잡힌다.
"""
import importlib


def load(unit_code):
    """능력단위코드 -> DEEP 사전. 없으면 빈 사전."""
    mod = "deep.lm_" + unit_code.split("_")[0]
    try:
        return importlib.import_module(mod).DEEP
    except ModuleNotFoundError:
        return {}
