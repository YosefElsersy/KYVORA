"""
StatusOverlay - Ekranin ust ortasinda surekli gorunen jest durumu seridi.
Kamera acik veya kapali her iki modda da calisir.

MIMARI:
  update() → self._pending'e yaz (thread-safe, lock ile)
  _tick()  → ana thread'de 33ms'de bir _pending'i oku ve _apply() cagir
  _apply() → tkinter widget'larini guncelle

Ozel:
  thumbs_up destegi
  action_flash: aksiyon tetiklenince 700ms yesil flas
"""

import tkinter as tk
import threading
import lang as _lang_mod

# Jest renkleri
_COLORS = {
    "pointing":  "#4ade80",
    "pinch":     "#fbbf24",
    "thumbs_up": "#ffd700",
    "v_sign":    "#60a5fa",
    "four":      "#c084fc",
    "three":     "#f472b6",
    "fist":      "#818cf8",
    "wolf":      "#fb923c",
    "none":      "#4b5563",
}

_LABEL_KEYS = {
    "pointing":  "hud_move",
    "pinch":     "hud_lclick",
    "thumbs_up": "hud_hold",
    "v_sign":    "hud_rclick",
    "four":      "hud_scroll",
    "three":     "hud_keyboard",
    "fist":      "hud_cam",
    "wolf":      "hud_wolf",
    "none":      "hud_none",
}

_TIP_KEYS = {
    "none":      "hud_tip_none",
    "pointing":  "hud_tip_pointing",
    "pinch":     "hud_tip_pinch",
    "thumbs_up": "hud_tip_thumbsup",
    "v_sign":    "hud_tip_vsign",
    "four":      "hud_tip_scroll",
    "three":     "hud_tip_three",
    "fist":      "hud_tip_fist",
    "wolf":      "hud_tip_wolf",
}

_BG        = "#0d0d1a"
_BG_FLASH  = "#0d1a0d"


class StatusOverlay:
    def __init__(self, root: tk.Tk):
        self._root       = root
        self._lock       = threading.Lock()
        self._pending    = None      # son gelen veri (lock ile korunan)
        self._win        = None
        self._container  = None
        self._lbl_main   = None
        self._lbl_sub    = None
        self._bar_canvas = None
        self._bar_fill   = None
        self._action_job = None
        self._in_flash   = False

    def build(self) -> None:
        """Ana thread'de cagrılır."""
        L = _lang_mod.get()

        win = tk.Toplevel(self._root)
        self._win = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        try:
            win.attributes("-alpha", 0.93)
        except Exception:
            pass

        win.update_idletasks()
        sw  = win.winfo_screenwidth()
        ww, wh = 340, 58
        win.geometry(f"{ww}x{wh}+{(sw-ww)//2}+6")

        self._container = tk.Frame(win, bg=_BG)
        self._container.pack(fill="both", expand=True)

        self._lbl_main = tk.Label(
            self._container,
            text=L.t("hud_none"),
            font=("Consolas", 13, "bold"),
            fg=_COLORS["none"],
            bg=_BG, pady=1,
        )
        self._lbl_main.pack(fill="x")

        self._lbl_sub = tk.Label(
            self._container,
            text=L.t("hud_tip_none"),
            font=("Consolas", 8),
            fg="#4b5563",
            bg=_BG, pady=0,
        )
        self._lbl_sub.pack(fill="x")

        self._bar_canvas = tk.Canvas(
            self._container, height=5,
            bg="#111122", highlightthickness=0,
        )
        self._bar_canvas.pack(fill="x", side="bottom")
        self._bar_fill = self._bar_canvas.create_rectangle(
            0, 0, 0, 5, fill=_COLORS["none"], outline="",
        )

        # Tick dongusunu baslat
        self._root.after(33, self._tick)

    def update(self, gesture: str, progress: float,
               scroll_active: bool = False,
               hold_active: bool = False,
               action_label: str = "",
               dwell_sec: float = 1.5) -> None:
        """Herhangi bir thread'den cagrilabilir."""
        with self._lock:
            self._pending = {
                "gesture":       gesture,
                "progress":      progress,
                "scroll_active": scroll_active,
                "hold_active":   hold_active,
                "action_label":  action_label,
                "dwell_sec":     dwell_sec,
            }

    def _tick(self) -> None:
        """Ana thread'de 33ms'de bir calisir."""
        try:
            with self._lock:
                data = self._pending
                self._pending = None
            if data is not None:
                self._apply(data)
        except Exception:
            pass
        try:
            self._root.after(33, self._tick)
        except Exception:
            pass

    def _apply(self, data: dict) -> None:
        """Tkinter widget'larini gunceller. SADECE ana thread."""
        if not self._win or not self._win.winfo_exists():
            return

        L             = _lang_mod.get()
        gesture       = data.get("gesture", "none")
        progress      = float(data.get("progress", 0.0))
        scroll_active = data.get("scroll_active", False)
        hold_active   = data.get("hold_active", False)
        action_label  = data.get("action_label", "")
        dwell_sec     = float(data.get("dwell_sec", 1.5))
        color         = _COLORS.get(gesture, _COLORS["none"])

        # Flash modu - aksiyon tetiklenince 700ms yesil
        if action_label and not self._in_flash:
            self._in_flash = True
            self._set_bg(_BG_FLASH)
            self._lbl_main.configure(
                text=f"  {action_label}  ",
                fg="#ffffff", font=("Consolas", 13, "bold"),
            )
            self._lbl_sub.configure(
                text=L.t("hud_tip_ready"), fg="#4ade80",
            )
            self._update_bar(1.0, "#4ade80")
            if self._action_job:
                try: self._root.after_cancel(self._action_job)
                except Exception: pass
            self._action_job = self._root.after(
                700, lambda g=gesture, p=progress, sa=scroll_active, ha=hold_active, ds=dwell_sec:
                    self._end_flash(g, p, sa, ha, ds)
            )
            return

        if self._in_flash:
            return   # Flash bitmeden guncelleme yapma

        # Normal mod
        self._set_bg(_BG)

        # Ana etiket
        if gesture == "four" and scroll_active:
            main_txt = L.t("hud_scroll_active")
        elif gesture == "thumbs_up" and hold_active:
            main_txt = L.t("hud_hold_active")
        else:
            main_txt = L.t(_LABEL_KEYS.get(gesture, "hud_none"))
        self._lbl_main.configure(text=main_txt, fg=color,
                                  font=("Consolas", 13, "bold"))

        # Alt ipucu
        if gesture == "thumbs_up" and hold_active:
            sub_txt, sub_col = L.t("hud_tip_holding"), "#ffd700"
        elif progress >= 1.0 and gesture not in ("none", "pointing"):
            sub_txt, sub_col = L.t("hud_tip_ready"), "#4ade80"
        elif progress > 0.0 and gesture not in ("none", "pointing"):
            remain = max(0.0, dwell_sec * (1.0 - progress))
            sub_txt = f"{L.t('hud_tip_dwell')}  {remain:.1f}s"
            sub_col = color
        else:
            sub_txt = L.t(_TIP_KEYS.get(gesture, "hud_tip_none"))
            sub_col = "#6b7280"
        self._lbl_sub.configure(text=sub_txt, fg=sub_col)

        bar_col = "#4ade80" if progress >= 1.0 else color
        self._update_bar(progress, bar_col)

    def _set_bg(self, bg: str) -> None:
        try:
            self._container.configure(bg=bg)
            self._lbl_main.configure(bg=bg)
            self._lbl_sub.configure(bg=bg)
        except Exception:
            pass

    def _update_bar(self, progress: float, color: str) -> None:
        try:
            w = self._bar_canvas.winfo_width()
            if w > 1:
                filled = int(min(progress, 1.0) * w)
                self._bar_canvas.coords(self._bar_fill, 0, 0, filled, 5)
                self._bar_canvas.itemconfig(self._bar_fill, fill=color)
        except Exception:
            pass

    def _end_flash(self, gesture, progress, scroll_active, hold_active, dwell_sec):
        self._in_flash   = False
        self._action_job = None
        self._apply({
            "gesture":       gesture,
            "progress":      progress,
            "scroll_active": scroll_active,
            "hold_active":   hold_active,
            "action_label":  "",
            "dwell_sec":     dwell_sec,
        })

    def destroy(self) -> None:
        if self._win and self._win.winfo_exists():
            try: self._win.destroy()
            except Exception: pass
