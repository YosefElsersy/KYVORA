"""
Kontrol Paneli - tum aksiyonlar tıklanabilir butonlarla.
Klavye kisayolu yok. Tkinter, tum platformlarda calisir.
"""

import tkinter as tk
import threading
import platform
import lang as _lang_mod

_OS = platform.system()

_BG     = "#0d0d1a"
_CARD   = "#1a1a2e"
_BORDER = "#2a2a4a"
_WHITE  = "#e8e8f0"
_DIM    = "#5a5a7a"
_GREEN  = "#4ade80"
_AMBER  = "#fbbf24"
_BLUE   = "#60a5fa"
_PURPLE = "#c084fc"
_RED    = "#f87171"
_PINK   = "#f472b6"


class ControlPanel:
    """
    Yan kontrol paneli. Singleton — sadece bir tane acilir.
    Butonlar: Kalibrasyon, El Degistir, Yardim, Kapat.
    """

    def __init__(self,
                 on_calibrate,
                 on_toggle_hand,
                 on_help,
                 on_quit,
                 get_state):
        """
        on_calibrate    : kalibrasyon baslat
        on_toggle_hand  : el degistir (sol/sag)
        on_help         : yardim ekranini ac
        on_quit         : programi kapat
        get_state()     : dict dondurir:
            {left_hand, calibrated, kb_visible, fps, cam_top, dwell_sec}
        """
        self._on_calibrate   = on_calibrate
        self._on_toggle_hand = on_toggle_hand
        self._on_help        = on_help
        self._on_quit        = on_quit
        self._get_state      = get_state

        self._root: tk.Tk | None = None
        self._lock  = threading.Lock()
        self._alive = False

        # UI referanslari (update icin)
        self._lbl_hand    = None
        self._lbl_cal     = None
        self._lbl_fps     = None
        self._lbl_kb      = None
        self._lbl_cam     = None
        self._lbl_dwell   = None
        self._after_id    = None

    def start(self) -> None:
        with self._lock:
            if self._alive:
                return
            self._alive = True
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def stop(self) -> None:
        with self._lock:
            self._alive = False
            root = self._root
        if root:
            try:
                root.after(0, root.destroy)
            except Exception:
                pass

    def _run(self) -> None:
        L = _lang_mod.get()
        is_tr = L.code == "tr"

        root = tk.Tk()
        with self._lock:
            self._root = root

        root.title("GestureMouse")
        root.configure(bg=_BG)
        root.resizable(False, False)
        root.attributes("-topmost", True)

        try:
            root.attributes("-alpha", 0.96)
        except Exception:
            pass

        # Ekranin sol tarafina konumlandir
        root.update_idletasks()
        scr_h = root.winfo_screenheight()
        win_w, win_h = 220, 520
        root.geometry(f"{win_w}x{win_h}+10+{(scr_h - win_h)//2}")

        # Kapatma protokolu → programi durdur
        root.protocol("WM_DELETE_WINDOW", self._on_quit)

        pad = 12

        # Baslik
        tk.Label(root, text="GestureMouse",
                 font=("Consolas", 12, "bold"),
                 fg=_GREEN, bg=_BG, pady=10).pack(fill="x")

        tk.Frame(root, height=1, bg=_BORDER).pack(fill="x", padx=pad)

        # Durum bilgileri
        state_frame = tk.Frame(root, bg=_CARD, padx=10, pady=8)
        state_frame.pack(fill="x", padx=pad, pady=(8, 0))

        def _stat_row(label_text, var_text, color):
            row = tk.Frame(state_frame, bg=_CARD)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=label_text, font=("Consolas", 8),
                     fg=_DIM, bg=_CARD, width=10, anchor="w").pack(side="left")
            lbl = tk.Label(row, text=var_text, font=("Consolas", 8, "bold"),
                           fg=color, bg=_CARD, anchor="w")
            lbl.pack(side="left")
            return lbl

        hand_lbl = "Sol El" if is_tr else "Left Hand"
        cal_lbl  = "Tamam"  if is_tr else "Done"
        self._lbl_hand  = _stat_row("El:"          if is_tr else "Hand:",   hand_lbl, _BLUE)
        self._lbl_cal   = _stat_row("Kal.:"        if is_tr else "Cal.:",   cal_lbl,  _GREEN)
        self._lbl_fps   = _stat_row("FPS:",                                  "0",     _DIM)
        self._lbl_kb    = _stat_row("Klavye:"      if is_tr else "Keyboard:","--",    _DIM)
        self._lbl_cam   = _stat_row("Kamera:"      if is_tr else "Camera:",  "--",    _DIM)
        self._lbl_dwell = _stat_row("Bekleme:"     if is_tr else "Dwell:",   "--",    _AMBER)

        tk.Frame(root, height=1, bg=_BORDER).pack(fill="x", padx=pad, pady=8)

        # Buton olusturma yardimcisi
        def _btn(parent, text, color, cmd, pady=4):
            b = tk.Button(
                parent, text=text,
                font=("Consolas", 10, "bold"),
                fg=_BG, bg=color,
                activebackground=color,
                activeforeground=_BG,
                relief="flat", bd=0,
                padx=0, pady=pady,
                cursor="hand2",
                command=cmd,
            )
            b.pack(fill="x", padx=pad, pady=3)
            # Hover efekti
            def _enter(e, b=b, c=color):
                b.configure(bg=self._lighten(c))
            def _leave(e, b=b, c=color):
                b.configure(bg=c)
            b.bind("<Enter>", _enter)
            b.bind("<Leave>", _leave)
            return b

        # Ana butonlar
        if is_tr:
            _btn(root, "  Kalibrasyon",  _AMBER,  self._click_calibrate)
            _btn(root, "  El Degistir",  _BLUE,   self._click_hand)
            _btn(root, "  Nasil Kullanilir?", _PURPLE, self._click_help, pady=6)
            _btn(root, "  Kapat",        _RED,    self._on_quit)
        else:
            _btn(root, "  Calibration",  _AMBER,  self._click_calibrate)
            _btn(root, "  Switch Hand",  _BLUE,   self._click_hand)
            _btn(root, "  How To Use?",  _PURPLE, self._click_help, pady=6)
            _btn(root, "  Quit",         _RED,    self._on_quit)

        # Periyodik guncelleme
        self._schedule_update(root)

        root.mainloop()

        with self._lock:
            self._alive = False
            self._root  = None

    def _schedule_update(self, root: tk.Tk) -> None:
        def _tick():
            if not self._alive:
                return
            self._refresh_state()
            self._after_id = root.after(500, _tick)
        _tick()

    def _refresh_state(self) -> None:
        try:
            state = self._get_state()
            L     = _lang_mod.get()
            is_tr = L.code == "tr"

            if self._lbl_hand:
                hand = (L.t("hand_left") if state.get("left_hand")
                        else L.t("hand_right"))
                self._lbl_hand.configure(text=hand, fg=_BLUE)

            if self._lbl_cal:
                cal_ok = state.get("calibrated", False)
                self._lbl_cal.configure(
                    text=(L.t("startup_cal_ok") if cal_ok
                          else L.t("startup_cal_no")),
                    fg=_GREEN if cal_ok else _RED,
                )

            if self._lbl_fps:
                self._lbl_fps.configure(
                    text=f"{state.get('fps', 0):.0f} fps")

            if self._lbl_kb:
                kb = state.get("kb_visible", False)
                self._lbl_kb.configure(
                    text=(L.t("hud_kb_on") if kb else L.t("hud_kb_off")),
                    fg=_GREEN if kb else _DIM,
                )

            if self._lbl_cam:
                ct = state.get("cam_top", True)
                self._lbl_cam.configure(
                    text=(L.t("hud_cam_top") if ct else L.t("hud_cam_back")),
                    fg=_GREEN if ct else _DIM,
                )

            if self._lbl_dwell:
                self._lbl_dwell.configure(
                    text=f"{state.get('dwell_sec', 1.5)}s")

        except Exception:
            pass

    def _click_calibrate(self) -> None:
        try:
            self._on_calibrate()
        except Exception:
            pass

    def _click_hand(self) -> None:
        try:
            self._on_toggle_hand()
        except Exception:
            pass

    def _click_help(self) -> None:
        try:
            self._on_help()
        except Exception:
            pass

    @staticmethod
    def _lighten(hex_color: str) -> str:
        """Rengi biraz acilar (hover efekti icin)."""
        try:
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            r = min(255, r + 30)
            g = min(255, g + 30)
            b = min(255, b + 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
