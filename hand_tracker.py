"""
HandTracker - mediapipe el tespiti.

KRITIK BUG DUZELTME:
  Tasks API (0.11+) onceden IMAGE modunda calisiyordu.
  IMAGE modu: her frame icin bastan palm detection - tracking YOK.
  Sonuc: landmark'lar frame'den frame'e zipliyor, baska parmaklara kayiyor.

  DUZELTME: VIDEO modu ile detect_for_video() kullaniliyor.
  VIDEO modu: onceki frame'in bounding box'ini kullanarak takip yapar.
  Sadece takip basarisiz olunca palm detection tetiklenir.
  Sonuc: cok daha stabil, duzgun landmark takibi.
"""

import cv2
import time
import mediapipe as mp

# ── API versiyonu tespiti ─────────────────────────────────────────────────────

_USE_TASKS = False

try:
    _hands_sol   = mp.solutions.hands
    _drawing_sol = mp.solutions.drawing_utils
    _DrawingSpec = mp.solutions.drawing_utils.DrawingSpec
    _USE_TASKS   = False
    print("[HandTracker] API: solutions (eski/0.10.x)")
except AttributeError:
    from mediapipe.tasks import python as _mp_tasks
    from mediapipe.tasks.python.vision import (
        HandLandmarker, HandLandmarkerOptions, RunningMode
    )
    _USE_TASKS = True
    print("[HandTracker] API: tasks (yeni/0.11+) - VIDEO modu")

# ── Tasks API model dosyasi ───────────────────────────────────────────────────

if _USE_TASKS:
    import urllib.request, pathlib

    _MODEL_PATH = pathlib.Path(__file__).parent / "hand_landmarker.task"

    if not _MODEL_PATH.exists():
        _URL = (
            "https://storage.googleapis.com/mediapipe-models/"
            "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        )
        print("[HandTracker] Model indiriliyor (~8MB)...")
        urllib.request.urlretrieve(_URL, _MODEL_PATH)
        print("[HandTracker] Model hazir.")


# ── Sabitler - MediaPipe landmark indeksleri ──────────────────────────────────
# Kaynak: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
# 0=WRIST, 1=THUMB_CMC, 2=THUMB_MCP, 3=THUMB_IP, 4=THUMB_TIP
# 5=INDEX_MCP, 6=INDEX_PIP, 7=INDEX_DIP, 8=INDEX_TIP
# 9=MIDDLE_MCP, 10=MIDDLE_PIP, 11=MIDDLE_DIP, 12=MIDDLE_TIP
# 13=RING_MCP, 14=RING_PIP, 15=RING_DIP, 16=RING_TIP
# 17=PINKY_MCP, 18=PINKY_PIP, 19=PINKY_DIP, 20=PINKY_TIP


class HandTracker:
    # Landmark indeksleri (resmi dokumantasyona gore)
    WRIST      = 0
    THUMB_CMC  = 1
    THUMB_MCP  = 2
    THUMB_IP   = 3
    THUMB_TIP  = 4
    INDEX_MCP  = 5
    INDEX_PIP  = 6
    INDEX_DIP  = 7
    INDEX_TIP  = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP   = 13
    RING_PIP   = 14
    RING_DIP   = 15
    RING_TIP   = 16
    PINKY_MCP  = 17
    PINKY_PIP  = 18
    PINKY_DIP  = 19
    PINKY_TIP  = 20

    LANDMARK_COUNT = 21

    def __init__(self, max_hands: int = 1,
                 detect_conf: float = 0.7,
                 track_conf: float  = 0.5,
                 low_perf: bool     = False):
        self._closed      = False
        self._frame_idx   = 0         # VIDEO modu icin timestamp

        if not _USE_TASKS:
            # Solutions API - zaten VIDEO gibi davranir (static_image_mode=False)
            self._hands = _hands_sol.Hands(
                static_image_mode        = False,  # tracking aktif
                max_num_hands            = max_hands,
                min_detection_confidence = detect_conf,
                min_tracking_confidence  = track_conf,
                model_complexity         = 0 if low_perf else 1,
            )
            self._draw_spec   = _DrawingSpec(color=(0,255,120), thickness=2, circle_radius=4)
            self._conn_spec   = _DrawingSpec(color=(200,200,200), thickness=1)
            self._connections = _hands_sol.HAND_CONNECTIONS

        else:
            # Tasks API - VIDEO modu ile - tracking aktif!
            opts = HandLandmarkerOptions(
                base_options = _mp_tasks.BaseOptions(
                    model_asset_path=str(_MODEL_PATH)),
                running_mode  = RunningMode.VIDEO,   # KRITIK: IMAGE degil VIDEO
                num_hands     = max_hands,
                min_hand_detection_confidence = detect_conf,
                min_hand_presence_confidence  = detect_conf,
                min_tracking_confidence       = track_conf,
            )
            self._hands = HandLandmarker.create_from_options(opts)
            # Cizim icin connections
            try:
                self._connections = _hands_sol.HAND_CONNECTIONS
            except Exception:
                self._connections = None

    def process(self, frame):
        """BGR frame'i isle, sonuc dondurir."""
        if self._closed:
            return None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False

        if not _USE_TASKS:
            # Solutions API - dogrudan kullan
            return self._hands.process(rgb)
        else:
            # Tasks API - VIDEO modu: timestamp zorunlu ve monoton artmali
            self._frame_idx += 1
            timestamp_ms = self._frame_idx * 33   # ~30fps = 33ms/frame
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            return self._hands.detect_for_video(mp_img, timestamp_ms)

    def draw(self, frame, results) -> None:
        """El iskeletini frame uzerine cizer."""
        if not results:
            return

        if not _USE_TASKS:
            if results.multi_hand_landmarks:
                for lm in results.multi_hand_landmarks:
                    _drawing_sol.draw_landmarks(
                        frame, lm, self._connections,
                        self._draw_spec, self._conn_spec)
        else:
            if results.hand_landmarks:
                h, w = frame.shape[:2]
                for hand in results.hand_landmarks:
                    pts = [(int(p.x*w), int(p.y*h)) for p in hand]
                    if self._connections:
                        for a, b in self._connections:
                            cv2.line(frame, pts[a], pts[b], (200,200,200), 1)
                    for pt in pts:
                        cv2.circle(frame, pt, 4, (0,255,120), -1)

    def get_landmarks(self, results, frame_shape) -> list | None:
        """(x,y) piksel koordinatlari listesi dondurir (21 nokta) veya None."""
        if not results:
            return None
        h, w = frame_shape[:2]

        if not _USE_TASKS:
            if not results.multi_hand_landmarks:
                return None
            lm = results.multi_hand_landmarks[0].landmark
        else:
            if not results.hand_landmarks:
                return None
            lm = results.hand_landmarks[0]

        if len(lm) < self.LANDMARK_COUNT:
            return None

        return [(int(p.x*w), int(p.y*h)) for p in lm]

    def close(self) -> None:
        """MediaPipe kaynaklarini serbest birak (bellek/GPU leak onler)."""
        if not self._closed:
            self._closed = True
            try:
                self._hands.close()
            except Exception:
                pass
