"""
Ekran bildirimi — jest tetiklenince ekranın üstünde kısa süre gösterilir.
Singleton + throttle ile performans korumalı.
"""
import threading, time, platform
import lang as _lang_mod

_OS = platform.system()
_GESTURE_KEYS = {
    "pinch":  "notify_lclick",
    "v_sign": "notify_rclick",
    "four":   "notify_scroll",
    "three":  "notify_keyboard",
    "fist":   "notify_cam",
    "spider": "notify_spider",
}
_BG, _FG   = "#0f0f1a", "#00e676"
_FONT      = ("Consolas", 13, "bold")
_THROTTLE  = 1.0
_last: dict[str, float] = {}
_lock      = threading.Lock()
_active    = [False]


def show(gesture: str, duration: float = 1.0) -> None:
    key = _GESTURE_KEYS.get(gesture)
    if not key:
        return
    now = time.perf_counter()
    if now - _last.get(gesture, 0) < _THROTTLE:
        return
    _last[gesture] = now
    with _lock:
        if _active[0]:
            return
        _active[0] = True
    label = _lang_mod.get().t(key)
    threading.Thread(target=_popup, args=(f"  {label}  ", duration), daemon=True).start()


def _popup(text: str, duration: float) -> None:
    try:
        import tkinter as tk
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        try: root.attributes("-alpha", 0.88)
        except Exception: pass
        if _OS == "Linux":
            try: root.wm_attributes("-type", "notification")
            except Exception: pass
        tk.Label(root, text=text, font=_FONT, fg=_FG, bg=_BG,
                 padx=16, pady=10).pack()
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        root.geometry(f"+{(sw - root.winfo_width()) // 2}+24")
        root.after(int(duration * 1000), root.destroy)
        root.mainloop()
    except Exception:
        pass
    finally:
        with _lock:
            _active[0] = False
