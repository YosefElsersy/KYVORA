"""
Config — ~/.gesture_mouse/config.json üzerinde JSON tabanlı ayar yönetimi.
"""
import json
import pathlib

_DIR  = pathlib.Path(__file__).parent   # script ile aynı klasör
_FILE = _DIR / "config.json"

_DEFAULTS: dict = {
    # Kamera
    "cam_index":   0,
    "frame_w":     640,
    "frame_h":     480,
    "show_cam":    True,
    "low_perf":    False,

    # Cursor
    "kalman_process_noise":     0.008,
    "kalman_measurement_noise": 0.15,

    # Gesture
    "stable_n":       6,
    "dwell_sec":      1.5,
    "scroll_speed":   2,
    "scroll_deadzone":20,

    # Ses
    "sound_enabled": True,

    # Sol/sağ el
    "dominant_hand": "right",   # "right" | "left" | "auto"

    # Kalibrasyon (5 nokta)
    "calibrated": False,
    "cal_x_min":  100,
    "cal_x_max":  540,
    "cal_y_min":  80,
    "cal_y_max":  400,
    "pinch_threshold": 0.28,
}


class Config:
    def __init__(self):
        self._data: dict = dict(_DEFAULTS)
        self._load()

    # ── public ────────────────────────────────────────────────────────────────

    def get(self, key: str, default=None):
        return self._data.get(key, default if default is not None
                              else _DEFAULTS.get(key))

    def set(self, key: str, value) -> None:
        self._data[key] = value
        self._save()

    def update(self, d: dict) -> None:
        self._data.update(d)
        self._save()

    def reset_calibration(self) -> None:
        for k in ("calibrated","cal_x_min","cal_x_max",
                  "cal_y_min","cal_y_max","pinch_threshold"):
            self._data[k] = _DEFAULTS[k]
        self._save()

    # ── internal ──────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if _FILE.exists():
            try:
                saved = json.loads(_FILE.read_text(encoding="utf-8"))
                self._data.update(saved)
            except Exception as e:
                print(f"[Config] Okuma hatası: {e} — varsayılanlar kullanılıyor.")

    def _save(self) -> None:
        try:
            _FILE.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"[Config] Kayıt hatası: {e}")