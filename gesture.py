"""
KYVORA - Gesture Recognition
====================================
21 MediaPipe landmark noktasindan jest tanir.

Jest haritasi:
  pointing  : SADECE isaret acik                        -> fare imleci
  pinch     : basparmak + isaret yakin (histerezis)    -> sol tik
  thumbs_up : basparmak yukari, 4 parmak kapali         -> basili surdur
  v_sign    : isaret + orta acik                        -> sag tik
  three     : isaret + orta + yuzuk acik                -> klavye
  four      : isaret + orta + yuzuk + serce acik        -> scroll
  fist      : tum parmaklar kapali                      -> kamera toggle
  wolf      : isaret + serce yukari, orta + yuzuk thumb -> alt+tab
  none      : tanimsiz / 5 parmak

FIST ALGILAMA IYILESTIRMESI:
  Onceki sirum sadece PIP bazli _up() kontrolu kullaniyordu.
  Yumruk yaparken parmaklar MCP etrafinda bukuldugu icin
  PIP yukarida kalabiliyordu -> false "none".
  
  Yeni yaklasim: IKILI KONTROL
    - PIP bazli: parmak ucu PIP'in ALTINDA mi?  (not _up)
    - MCP bazli: parmak ucu MCP'nin ALTINDA mi? (toleransli)
  En az biri True olunca kapali sayilir -> daha toleranli, 
  yumruk her bicimde algilanir.
"""

import math
from hand_tracker import HandTracker as HT

_PINCH_ENTER  = 0.26
_PINCH_EXIT   = 0.35
_PINCH_RATIO  = _PINCH_EXIT / _PINCH_ENTER
_pinch_active = False


def _dist(a, b) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _up(lm, tip: int, pip: int) -> bool:
    """Parmak acik mi? (standart PIP bazli)"""
    return lm[tip][1] < lm[pip][1]


def _closed(lm, tip: int, pip: int, mcp: int) -> bool:
    """
    Parmak kapali mi? PIP VEYA MCP bazli — daha toleranli.
    Yumruk yaparken her iki esikten birini gecmesi yeterli.
    """
    # Tip, PIP'in altinda mi?
    pip_closed = lm[tip][1] >= lm[pip][1]
    # Tip, MCP'ye yakin mi? (MCP + 20px tolerans)
    mcp_near   = lm[tip][1] >= lm[mcp][1] - 20
    return pip_closed or mcp_near


def _thumb_open(lm, left_hand: bool = False) -> bool:
    if left_hand:
        return lm[HT.THUMB_TIP][0] > lm[HT.THUMB_IP][0]
    return lm[HT.THUMB_TIP][0] < lm[HT.THUMB_IP][0]


def _thumb_up_vertical(lm) -> bool:
    """Basparmak duzce yukari mi? (thumbs_up icin)"""
    # Tip, MCP'nin en az 20px ustunde olmali
    above_mcp = lm[HT.THUMB_TIP][1] < lm[HT.THUMB_MCP][1] - 20
    # Tip, IP ekleminin de ustunde olmali
    above_ip  = lm[HT.THUMB_TIP][1] < lm[HT.THUMB_IP][1]
    return above_mcp and above_ip


def _near(lm, tip_a: int, tip_b: int, threshold: float) -> bool:
    palm = _dist(lm[HT.WRIST], lm[HT.MIDDLE_MCP]) + 1e-6
    return _dist(lm[tip_a], lm[tip_b]) / palm < threshold


def _pinky_closed(lm) -> bool:
    """Serce kapali mi? (three/four ayrimi icin MCP bazli)"""
    return lm[HT.PINKY_TIP][1] > lm[HT.PINKY_MCP][1] + 15


GESTURES = frozenset({
    "none", "pointing", "pinch", "thumbs_up",
    "v_sign", "three", "four", "fist", "wolf", "open_palm",
})


def reset_pinch() -> None:
    global _pinch_active
    _pinch_active = False


def set_pinch_threshold(threshold: float, hysteresis: float | None = None) -> None:
    """
    Pinch esigini ayarla (histerezis ile).
    threshold = giris esigi (enter), hysteresis = exit/enter orani.
    """
    global _PINCH_ENTER, _PINCH_EXIT
    try:
        t = float(threshold)
    except Exception:
        return
    # Mantikli aralikta tut
    t = max(0.05, min(0.80, t))
    ratio = _PINCH_RATIO if hysteresis is None else float(hysteresis)
    ratio = max(1.05, ratio)
    exit_val = t * ratio
    # exit > enter olmali, asinma olmasin
    if exit_val <= t:
        exit_val = t * 1.20
    _PINCH_ENTER = t
    _PINCH_EXIT  = min(0.95, exit_val)


def get_gesture(lm: list | None, left_hand: bool = False) -> str:
    global _pinch_active

    if not lm:
        reset_pinch()
        return "none"

    # PIP bazli acik/kapali (4 parmak)
    idx = _up(lm, HT.INDEX_TIP,  HT.INDEX_PIP)
    mid = _up(lm, HT.MIDDLE_TIP, HT.MIDDLE_PIP)
    rng = _up(lm, HT.RING_TIP,   HT.RING_PIP)
    pnk = _up(lm, HT.PINKY_TIP,  HT.PINKY_PIP)
    thm = _thumb_open(lm, left_hand)

    # FIST icin toleranli kapali kontrol
    idx_c = _closed(lm, HT.INDEX_TIP,  HT.INDEX_PIP,  HT.INDEX_MCP)
    mid_c = _closed(lm, HT.MIDDLE_TIP, HT.MIDDLE_PIP, HT.MIDDLE_MCP)
    rng_c = _closed(lm, HT.RING_TIP,   HT.RING_PIP,   HT.RING_MCP)
    pnk_c = _closed(lm, HT.PINKY_TIP,  HT.PINKY_PIP,  HT.PINKY_MCP)

    # ── 1. Pinch (histerezis, en yuksek oncelik) ──────────────────────────────
    palm  = _dist(lm[HT.WRIST], lm[HT.MIDDLE_MCP]) + 1e-6
    ratio = _dist(lm[HT.THUMB_TIP], lm[HT.INDEX_TIP]) / palm
    if _pinch_active:
        _pinch_active = ratio < _PINCH_EXIT
    else:
        _pinch_active = ratio < _PINCH_ENTER
    if _pinch_active:
        return "pinch"

    # ── 2. Thumbs Up (fist'ten once — daha kati kontrol) ─────────────────────
    if idx_c and mid_c and rng_c and pnk_c and _thumb_up_vertical(lm):
        return "thumbs_up"

    # ── 3. Fist (toleranli — yumruk her bicimde algilansin) ───────────────────
    # thumbs_up kontrol edildi ve match etmedi → basparmak yukari degil
    if idx_c and mid_c and rng_c and pnk_c:
        return "fist"

    # ── 4. Wolf ───────────────────────────────────────────────────────────────
    if (idx and not mid and not rng and pnk
            and _near(lm, HT.MIDDLE_TIP, HT.THUMB_TIP, 0.30)
            and _near(lm, HT.RING_TIP,   HT.THUMB_TIP, 0.30)
            and not _near(lm, HT.INDEX_TIP, HT.THUMB_TIP, 0.42)):
        return "wolf"

    # ── 5. 5 parmak = open palm (duraklat/devam) ────────────────────────────
    if thm and idx and mid and rng and pnk:
        return "open_palm"

    # ── 6. 4 parmak = scroll ──────────────────────────────────────────────────
    if not thm and idx and mid and rng and pnk:
        return "four"

    # ── 7. 3 parmak = klavye ──────────────────────────────────────────────────
    if idx and mid and rng and _pinky_closed(lm) and not thm:
        return "three"

    # ── 8. V isareti = sag tik ────────────────────────────────────────────────
    if idx and mid and not rng and not pnk and not thm:
        return "v_sign"

    # ── 9. Tek isaret = cursor ────────────────────────────────────────────────
    if idx and not mid and not rng and not pnk:
        return "pointing"

    return "none"


def get_cursor_point(lm: list) -> tuple[int, int]:
    if not lm or len(lm) <= HT.INDEX_TIP:
        return (0, 0)
    return lm[HT.INDEX_TIP]


def get_scroll_ref(lm: list) -> tuple[int, int]:
    if not lm or len(lm) <= HT.WRIST:
        return (0, 0)
    return lm[HT.WRIST]


def get_palm_center(lm: list) -> tuple[int, int]:
    """
    Avuc merkezi — thumbs_up hareket modu icin referans nokta.
    Basparmak hareket ederken geri kalan elin konumunu temsil eder.
    Bilek ile orta parmak MCP ortalaması.
    """
    if not lm:
        return (0, 0)
    wx, wy = lm[HT.WRIST]
    mx, my = lm[HT.MIDDLE_MCP]
    return ((wx + mx) // 2, (wy + my) // 2)
