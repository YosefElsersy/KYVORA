"""
KYVORA — Modular UI Manager
============================
Single-window Tkinter application with embedded camera preview.
Supports detachable / dockable panels for flexible workspace arrangement.

Architecture:
  Main thread  : Tkinter mainloop (this class)
  Camera thread: Sends BGR frames via queue — displayed as embedded preview
  Queue system : Thread-safe communication from camera → UI

Panels (all detachable):
  A. Camera Preview   — live webcam + hand-tracking overlay
  B. System Status    — ACTIVE/PAUSED, FPS, calibration, hand, camera
  C. Gesture Monitor  — recognized gesture, dwell progress
  D. Actions/Activity — recent executed actions log
  E. Notifications    — timestamped info / warning / error log
  F. Controls         — calibrate, hand switch, pause, dwell slider, help
"""

import tkinter as tk
import threading
import queue
import time
import os
import cv2
from PIL import Image, ImageTk
import lang as _lang_mod

# ── KYVORA Color Palette ─────────────────────────────────────────────────────

_BG        = "#0a0e1a"
_BG_HEADER = "#080c16"
_CARD      = "#111827"
_BORDER    = "#1e293b"
_CYAN      = "#06b6d4"
_BLUE      = "#3b82f6"
_GREEN     = "#22c55e"
_AMBER     = "#f59e0b"
_RED       = "#ef4444"
_PURPLE    = "#a855f7"
_PINK      = "#ec4899"
_ORANGE    = "#f97316"
_INDIGO    = "#6366f1"
_GOLD      = "#eab308"
_WHITE     = "#e2e8f0"
_DIM       = "#64748b"
_DIMMER    = "#475569"

_GESTURE_COLORS = {
    "pointing": _GREEN, "pinch": _AMBER, "thumbs_up": _GOLD,
    "v_sign": _BLUE, "four": _PURPLE, "three": _PINK,
    "fist": _INDIGO, "wolf": _ORANGE, "open_palm": _CYAN,
    "none": _DIMMER,
}

_GESTURE_LABEL_KEYS = {
    "pointing": "hud_move", "pinch": "hud_lclick", "thumbs_up": "hud_hold",
    "v_sign": "hud_rclick", "four": "hud_scroll", "three": "hud_keyboard",
    "fist": "hud_cam", "wolf": "hud_wolf", "open_palm": "hud_open_palm",
    "none": "hud_none",
}

_GESTURE_TIP_KEYS = {
    "none": "hud_tip_none", "pointing": "hud_tip_pointing",
    "pinch": "hud_tip_pinch", "thumbs_up": "hud_tip_thumbsup",
    "v_sign": "hud_tip_vsign", "four": "hud_tip_scroll",
    "three": "hud_tip_three", "fist": "hud_tip_fist",
    "wolf": "hud_tip_wolf", "open_palm": "hud_tip_open_palm",
}

_NOTIFY_KEYS = {
    "pinch": "notify_lclick", "v_sign": "notify_rclick",
    "four": "notify_scroll", "three": "notify_keyboard",
    "fist": "notify_cam", "wolf": "notify_wolf",
    "thumbs_up_hold": "notify_hold", "thumbs_up_release": "notify_release",
    "paused": "notify_paused", "resumed": "notify_resumed",
}

_SEV_COLORS = {"success": _GREEN, "info": _CYAN, "warning": _AMBER, "error": _RED}


# ══════════════════════════════════════════════════════════════════════════════
#  Detachable Section Helper
# ══════════════════════════════════════════════════════════════════════════════

class _DetachableSection:
    """Wraps a UI section so it can be detached into a floating window."""

    def __init__(self, mgr, parent, panel_id, title, build_fn,
                 min_w=300, min_h=180):
        self._mgr = mgr
        self._id = panel_id
        self._title = title
        self._build_fn = build_fn
        self._min_w = min_w
        self._min_h = min_h
        self._floating = False
        self._toplevel = None
        self._topmost = False

        # Container in main layout
        self.frame = tk.Frame(parent, bg=_CARD)

        # Title bar
        tbar = tk.Frame(self.frame, bg=_CARD)
        tbar.pack(fill="x")
        tk.Label(tbar, text=title, font=("Consolas", 8, "bold"),
                 fg=_CYAN, bg=_CARD, anchor="w"
                 ).pack(side="left", padx=(12, 0), pady=(6, 2))
        self._btn = tk.Button(
            tbar, text="\u2b1c", font=("Consolas", 7),
            fg=_DIM, bg=_CARD, activebackground=_CARD, activeforeground=_CYAN,
            relief="flat", bd=0, cursor="hand2", command=self._toggle)
        self._btn.pack(side="right", padx=(0, 8), pady=(6, 2))

        # Content area
        self._content = tk.Frame(self.frame, bg=_CARD)
        self._content.pack(fill="both", expand=True)

        # Initial build
        self._build_fn(self._content)

    @property
    def is_floating(self):
        return self._floating

    def _toggle(self):
        if self._floating:
            self.dock()
        else:
            self.detach()

    def detach(self):
        if self._floating:
            return
        self._clear_refs()
        for w in self._content.winfo_children():
            w.destroy()
        # Placeholder
        ph = tk.Label(self._content, text=f"\u25a3 {self._title}",
                      font=("Consolas", 8), fg=_DIM, bg=_CARD,
                      cursor="hand2", pady=4)
        ph.pack(fill="x", padx=12)
        ph.bind("<Button-1>", lambda e: self.dock())
        self._btn.configure(text="\u25a3")
        # Floating window
        root = self._mgr._root
        self._toplevel = tk.Toplevel(root)
        self._toplevel.title(f"KYVORA \u2014 {self._title}")
        self._toplevel.configure(bg=_BG)
        self._toplevel.minsize(self._min_w, self._min_h)
        self._toplevel.geometry(f"{self._min_w + 60}x{self._min_h + 40}")
        self._toplevel.protocol("WM_DELETE_WINDOW", self.dock)
        try:
            if hasattr(root, "_icon_ref"):
                self._toplevel.iconphoto(True, root._icon_ref)
        except Exception:
            pass
        # Top-bar in floating window with Always on Top + Dock
        fbar = tk.Frame(self._toplevel, bg=_BG_HEADER)
        fbar.pack(fill="x")
        tk.Label(fbar, text=self._title, font=("Consolas", 9, "bold"),
                 fg=_CYAN, bg=_BG_HEADER).pack(side="left", padx=8, pady=4)
        self._top_var = tk.BooleanVar(value=self._topmost)
        cb = tk.Checkbutton(fbar, text=_lang_mod.get().t("panel_always_top"),
                            variable=self._top_var, font=("Consolas", 7),
                            fg=_DIM, bg=_BG_HEADER, selectcolor=_CARD,
                            activebackground=_BG_HEADER, activeforeground=_DIM,
                            command=self._toggle_topmost)
        cb.pack(side="right", padx=8)
        tk.Button(fbar, text=_lang_mod.get().t("panel_dock"),
                  font=("Consolas", 8, "bold"), fg=_BG, bg=_CYAN,
                  relief="flat", bd=0, padx=6, pady=1,
                  cursor="hand2", command=self.dock).pack(side="right", padx=4)
        tk.Frame(self._toplevel, height=1, bg=_BORDER).pack(fill="x")
        # Content
        fc = tk.Frame(self._toplevel, bg=_CARD)
        fc.pack(fill="both", expand=True, padx=2, pady=2)
        self._build_fn(fc)
        if self._topmost:
            try:
                self._toplevel.attributes("-topmost", True)
            except Exception:
                pass
        self._floating = True

    def dock(self):
        if not self._floating:
            return
        self._clear_refs()
        if self._toplevel:
            try:
                self._toplevel.destroy()
            except Exception:
                pass
            self._toplevel = None
        for w in self._content.winfo_children():
            w.destroy()
        self._build_fn(self._content)
        self._btn.configure(text="\u2b1c")
        self._floating = False

    def _toggle_topmost(self):
        self._topmost = self._top_var.get()
        if self._toplevel:
            try:
                self._toplevel.attributes("-topmost", self._topmost)
            except Exception:
                pass

    def _clear_refs(self):
        """Null out widget refs before rebuild."""
        self._mgr._null_panel_refs(self._id)


# ══════════════════════════════════════════════════════════════════════════════
#  UIManager
# ══════════════════════════════════════════════════════════════════════════════

class UIManager:
    """Unified KYVORA application window with detachable panels."""

    def __init__(self):
        self._q       = queue.Queue()
        self._frame_q = queue.Queue(maxsize=2)
        self._root    = None
        self._running = False
        self._state: dict = {}

        # Callbacks (set by main.py)
        self.on_calibrate    = None
        self.on_toggle_hand  = None
        self.on_quit         = None
        self.on_toggle_pause = None
        self.on_dwell_change = None

        # ── Widget references (set by panel builders, may be None) ────────
        # Camera
        self._camera_label = None
        self._camera_photo = None

        # Header
        self._cam_dot = None
        self._lbl_cam_status = None
        self._lbl_fps = None
        self._lbl_cal = None
        self._cal_dot = None
        self._lbl_header_status = None
        self._header_status_dot = None

        # Status panel (B)
        self._v_hand = None
        self._v_cal = None
        self._v_dwell = None
        self._v_kb = None
        self._v_cam = None
        self._v_status = None
        self._v_hand_det = None

        # Controls panel (F)
        self._btn_pause = None
        self._dwell_scale = None
        self._lbl_dwell_val = None

        # Gesture panel (C)
        self._gesture_bar = None
        self._gesture_bar_fill = None
        self._lbl_gesture = None
        self._lbl_gesture_tip = None
        self._dwell_canvas = None
        self._dwell_fill = None
        self._lbl_dwell_time = None

        # Actions panel (D)
        self._action_labels = []
        self._action_log = []

        # Notifications panel (E)
        self._notif_labels = []
        self._notif_log = []       # list of (time_str, severity, msg)

        # Footer
        self._lbl_tip = None
        self._lbl_kb_status = None
        self._lbl_cam_pos = None

        # Flash state
        self._in_flash = False
        self._flash_job = None

        # Help / Topmost / Logo
        self._help_win = None
        self._prev_topmost = None
        self._logo_photo = None

        # Detachable sections
        self._sections: dict[str, _DetachableSection] = {}

    # ══════════════════════════════════════════════════════════════════════════
    #  Null-out helpers (called before panel rebuild)
    # ══════════════════════════════════════════════════════════════════════════

    def _null_panel_refs(self, panel_id):
        """Set widget refs to None for a panel about to be rebuilt."""
        _MAP = {
            "camera":  ["_camera_label"],
            "status":  ["_v_hand", "_v_cal", "_v_dwell", "_v_kb",
                        "_v_cam", "_v_status", "_v_hand_det"],
            "gesture": ["_gesture_bar", "_gesture_bar_fill", "_lbl_gesture",
                        "_lbl_gesture_tip", "_dwell_canvas", "_dwell_fill",
                        "_lbl_dwell_time"],
            "actions": ["_action_labels"],
            "notif":   ["_notif_labels"],
            "controls":["_btn_pause", "_dwell_scale", "_lbl_dwell_val"],
        }
        for attr in _MAP.get(panel_id, []):
            if attr == "_action_labels":
                self._action_labels = []
            elif attr == "_notif_labels":
                self._notif_labels = []
            else:
                setattr(self, attr, None)

    # ══════════════════════════════════════════════════════════════════════════
    #  Main Loop
    # ══════════════════════════════════════════════════════════════════════════

    def run(self) -> None:
        self._root = tk.Tk()
        self._root.title("KYVORA")
        self._root.configure(bg=_BG)
        self._root.minsize(960, 580)
        self._root.geometry("1140x720")
        self._root.protocol("WM_DELETE_WINDOW", self._on_quit_click)
        self._running = True

        try:
            logo_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "Logo.png")
            if os.path.exists(logo_path):
                icon = ImageTk.PhotoImage(
                    Image.open(logo_path).resize((64, 64), Image.LANCZOS))
                self._root.iconphoto(True, icon)
                self._root._icon_ref = icon
        except Exception:
            pass

        self._build_header()
        self._build_footer()
        self._build_content()

        self._root.after(33, self._update_camera)
        self._root.after(50, self._process_queue)
        self._root.mainloop()

    def stop(self) -> None:
        self._running = False
        try:
            self._root.after(0, self._root.quit)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════════════
    #  Thread-safe API
    # ══════════════════════════════════════════════════════════════════════════

    def update_frame(self, frame_bgr) -> None:
        try:
            self._frame_q.put_nowait(frame_bgr)
        except queue.Full:
            try:
                self._frame_q.get_nowait()
                self._frame_q.put_nowait(frame_bgr)
            except Exception:
                pass

    def update_state(self, state: dict) -> None:
        self._q.put(("state", state))

    def update_gesture(self, gesture: str, progress: float,
                       scroll_active: bool = False,
                       hold_active: bool = False,
                       action_label: str = "",
                       dwell_sec: float | None = None) -> None:
        if dwell_sec is None:
            dwell_sec = float(self._state.get("dwell_sec", 1.5))
        self._q.put(("gesture", {
            "gesture": gesture, "progress": progress,
            "scroll_active": scroll_active, "hold_active": hold_active,
            "action_label": action_label, "dwell_sec": dwell_sec,
        }))

    def show_notify(self, gesture: str) -> None:
        self._q.put(("notify", gesture))

    def add_notification(self, msg: str, severity: str = "info") -> None:
        self._q.put(("notif_log", (severity, msg)))

    def request_quit(self) -> None:
        self._q.put(("quit", None))

    # ══════════════════════════════════════════════════════════════════════════
    #  UI Building
    # ══════════════════════════════════════════════════════════════════════════

    def _build_header(self):
        L = _lang_mod.get()
        header = tk.Frame(self._root, bg=_BG_HEADER, height=52)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Left: Logo + Title
        left = tk.Frame(header, bg=_BG_HEADER)
        left.pack(side="left", padx=(16, 0))
        try:
            logo_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "Logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path).resize((34, 34), Image.LANCZOS)
                self._logo_photo = ImageTk.PhotoImage(logo_img)
                tk.Label(left, image=self._logo_photo,
                         bg=_BG_HEADER).pack(side="left", padx=(0, 10))
        except Exception:
            pass
        tk.Label(left, text="KYVORA", font=("Consolas", 18, "bold"),
                 fg=_CYAN, bg=_BG_HEADER).pack(side="left")
        tk.Label(left, text=L.t("startup_title"), font=("Consolas", 9),
                 fg=_DIMMER, bg=_BG_HEADER
                 ).pack(side="left", padx=(12, 0), pady=(4, 0))

        # Right: indicators
        right = tk.Frame(header, bg=_BG_HEADER)
        right.pack(side="right", padx=(0, 16))

        self._cal_dot = tk.Label(right, text="\u25cf", font=("Consolas", 8),
                                 fg=_DIMMER, bg=_BG_HEADER)
        self._cal_dot.pack(side="right", padx=(4, 0))
        self._lbl_cal = tk.Label(right, text=L.t("hud_cal_no"),
                                 font=("Consolas", 8, "bold"),
                                 fg=_DIMMER, bg=_BG_HEADER)
        self._lbl_cal.pack(side="right")
        tk.Frame(right, width=16, bg=_BG_HEADER).pack(side="right")

        self._lbl_fps = tk.Label(right, text="0 fps", font=("Consolas", 9),
                                 fg=_DIM, bg=_BG_HEADER)
        self._lbl_fps.pack(side="right")
        tk.Frame(right, width=16, bg=_BG_HEADER).pack(side="right")

        self._cam_dot = tk.Label(right, text="\u25cf", font=("Consolas", 10),
                                 fg=_GREEN, bg=_BG_HEADER)
        self._cam_dot.pack(side="right", padx=(0, 4))
        self._lbl_cam_status = tk.Label(right, text="Camera",
                                         font=("Consolas", 8, "bold"),
                                         fg=_GREEN, bg=_BG_HEADER)
        self._lbl_cam_status.pack(side="right")
        tk.Frame(right, width=16, bg=_BG_HEADER).pack(side="right")

        self._header_status_dot = tk.Label(right, text="\u25cf",
                                           font=("Consolas", 10),
                                           fg=_GREEN, bg=_BG_HEADER)
        self._header_status_dot.pack(side="right", padx=(0, 4))
        self._lbl_header_status = tk.Label(right, text="ACTIVE",
                                           font=("Consolas", 8, "bold"),
                                           fg=_GREEN, bg=_BG_HEADER)
        self._lbl_header_status.pack(side="right")

        tk.Frame(self._root, height=1, bg=_BORDER).pack(fill="x", side="top")

    def _build_footer(self):
        L = _lang_mod.get()
        tk.Frame(self._root, height=1, bg=_BORDER).pack(fill="x", side="bottom")
        footer = tk.Frame(self._root, bg=_BG_HEADER, height=30)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self._lbl_tip = tk.Label(footer, text=L.t("hud_tip_none"),
                                 font=("Consolas", 8), fg=_DIM,
                                 bg=_BG_HEADER, anchor="w")
        self._lbl_tip.pack(side="left", padx=(16, 0), fill="x", expand=True)

        # Restore Layout button
        tk.Button(footer, text=L.t("panel_restore"),
                  font=("Consolas", 7, "bold"), fg=_DIM, bg=_BG_HEADER,
                  activebackground=_BG_HEADER, activeforeground=_CYAN,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._restore_layout
                  ).pack(side="right", padx=(8, 16))

        self._lbl_cam_pos = tk.Label(footer, text=L.t("hud_cam_front"),
                                     font=("Consolas", 8, "bold"),
                                     fg=_DIM, bg=_BG_HEADER)
        self._lbl_cam_pos.pack(side="right", padx=(8, 0))

        self._lbl_kb_status = tk.Label(footer, text=L.t("hud_kb_off"),
                                       font=("Consolas", 8, "bold"),
                                       fg=_DIM, bg=_BG_HEADER)
        self._lbl_kb_status.pack(side="right", padx=(8, 0))

    def _build_content(self):
        content = tk.Frame(self._root, bg=_BG)
        content.pack(fill="both", expand=True)

        # ── Left sidebar ──────────────────────────────────────────────────────
        left_sb = tk.Frame(content, bg=_CARD, width=220)
        left_sb.pack(side="left", fill="y")
        left_sb.pack_propagate(False)

        sec_b = _DetachableSection(self, left_sb, "status",
                                   _lang_mod.get().t("panel_status_title"),
                                   self._build_status_panel, 260, 200)
        sec_b.frame.pack(fill="x")
        self._sections["status"] = sec_b

        tk.Frame(left_sb, height=1, bg=_BORDER).pack(fill="x", padx=12, pady=4)

        sec_f = _DetachableSection(self, left_sb, "controls",
                                   _lang_mod.get().t("panel_controls_title"),
                                   self._build_controls_panel, 260, 320)
        sec_f.frame.pack(fill="x")
        self._sections["controls"] = sec_f

        # Spacer + fixed bottom buttons
        tk.Frame(left_sb, bg=_CARD).pack(fill="both", expand=True)
        self._make_button(left_sb, _lang_mod.get().t("panel_restore"),
                          _DIMMER, self._restore_layout, 12)
        self._make_button(left_sb, _lang_mod.get().t("panel_quit"),
                          _RED, self._on_quit_click, 12)
        tk.Frame(left_sb, height=8, bg=_CARD).pack()

        tk.Frame(content, width=1, bg=_BORDER).pack(side="left", fill="y")

        # ── Right sidebar ─────────────────────────────────────────────────────
        right_sb = tk.Frame(content, bg=_CARD, width=230)
        right_sb.pack(side="right", fill="y")
        right_sb.pack_propagate(False)

        sec_c = _DetachableSection(self, right_sb, "gesture",
                                   _lang_mod.get().t("panel_gesture_title"),
                                   self._build_gesture_panel, 280, 200)
        sec_c.frame.pack(fill="x")
        self._sections["gesture"] = sec_c

        tk.Frame(right_sb, height=1, bg=_BORDER).pack(fill="x", padx=12, pady=4)

        sec_d = _DetachableSection(self, right_sb, "actions",
                                   _lang_mod.get().t("panel_actions_title"),
                                   self._build_actions_panel, 280, 180)
        sec_d.frame.pack(fill="x")
        self._sections["actions"] = sec_d

        tk.Frame(right_sb, height=1, bg=_BORDER).pack(fill="x", padx=12, pady=4)

        sec_e = _DetachableSection(self, right_sb, "notif",
                                   _lang_mod.get().t("panel_notif_title"),
                                   self._build_notif_panel, 320, 200)
        sec_e.frame.pack(fill="both", expand=True)
        self._sections["notif"] = sec_e

        tk.Frame(content, width=1, bg=_BORDER).pack(side="right", fill="y")

        # ── Center: Camera ────────────────────────────────────────────────────
        center = tk.Frame(content, bg="#000000")
        center.pack(fill="both", expand=True)

        sec_a = _DetachableSection(self, center, "camera",
                                   _lang_mod.get().t("panel_cam_title"),
                                   self._build_camera_panel, 480, 360)
        sec_a.frame.pack(fill="both", expand=True)
        self._sections["camera"] = sec_a

    # ══════════════════════════════════════════════════════════════════════════
    #  Panel Builders (called by DetachableSection — accept parent frame)
    # ══════════════════════════════════════════════════════════════════════════

    def _build_camera_panel(self, parent):
        self._camera_label = tk.Label(
            parent, bg="#050510", text="KYVORA",
            font=("Consolas", 24, "bold"), fg="#1a1a3a", compound="center")
        self._camera_label.pack(fill="both", expand=True)

    def _build_status_panel(self, parent):
        L = _lang_mod.get()
        pad = 10
        sf = tk.Frame(parent, bg=_CARD, padx=6, pady=4)
        sf.pack(fill="x", padx=pad, pady=(0, 4))
        self._v_status   = self._status_row(sf, L.t("panel_status_lbl"), L.t("hud_active"), _GREEN)
        self._v_hand     = self._status_row(sf, L.t("panel_hand_lbl"),   "--", _BLUE)
        self._v_cal      = self._status_row(sf, L.t("panel_cal_lbl"),    "--", _GREEN)
        self._v_dwell    = self._status_row(sf, L.t("panel_dwell_lbl"),  "--", _AMBER)
        self._v_kb       = self._status_row(sf, L.t("panel_kb_lbl"),     "--", _DIM)
        self._v_cam      = self._status_row(sf, L.t("panel_cam_lbl"),    "--", _DIM)
        self._v_hand_det = self._status_row(sf, L.t("panel_hand_det_lbl"), "--", _DIM)

    def _build_controls_panel(self, parent):
        L = _lang_mod.get()
        pad = 10

        self._make_button(parent, L.t("panel_calibrate"),
                          _AMBER, self._on_cal_click, pad)
        self._make_button(parent, L.t("panel_hand"),
                          _BLUE, self._on_hand_click, pad)
        self._make_button(parent, L.t("panel_how_to"),
                          _PURPLE, self._open_help, pad)
        self._btn_pause = self._make_button(
            parent, L.t("panel_pause"), _CYAN, self._on_pause_click, pad)

        # ── Dwell slider ──────────────────────────────────────────────────────
        tk.Frame(parent, height=1, bg=_BORDER).pack(fill="x", padx=pad, pady=6)

        dwell_hdr = tk.Frame(parent, bg=_CARD)
        dwell_hdr.pack(fill="x", padx=pad)
        tk.Label(dwell_hdr, text=L.t("panel_dwell_delay"),
                 font=("Consolas", 8, "bold"), fg=_AMBER, bg=_CARD
                 ).pack(anchor="w")
        tk.Label(dwell_hdr, text=L.t("panel_dwell_time"),
                 font=("Consolas", 7), fg=_DIMMER, bg=_CARD
                 ).pack(anchor="w")

        cur = float(self._state.get("dwell_sec", 1.5))
        self._lbl_dwell_val = tk.Label(
            parent, text=f"{cur:.1f}s", font=("Consolas", 11, "bold"),
            fg=_AMBER, bg=_CARD)
        self._lbl_dwell_val.pack(padx=pad, pady=(2, 0))

        self._dwell_scale = tk.Scale(
            parent, from_=0.3, to=3.0, resolution=0.1,
            orient="horizontal", length=170,
            bg=_CARD, fg=_AMBER, troughcolor="#1a1a2e",
            activebackground=_AMBER, highlightthickness=0,
            font=("Consolas", 7), showvalue=False,
            command=self._on_dwell_slider)
        self._dwell_scale.set(cur)
        self._dwell_scale.pack(padx=pad, pady=(0, 6))

    def _build_gesture_panel(self, parent):
        L = _lang_mod.get()
        pad = 10

        self._gesture_bar = tk.Canvas(parent, height=3, bg="#1a1a2e",
                                      highlightthickness=0)
        self._gesture_bar.pack(fill="x", padx=pad, pady=(0, 6))
        self._gesture_bar_fill = self._gesture_bar.create_rectangle(
            0, 0, 0, 3, fill=_DIMMER, outline="")

        self._lbl_gesture = tk.Label(parent, text=L.t("hud_none"),
                                     font=("Consolas", 13, "bold"),
                                     fg=_DIMMER, bg=_CARD, anchor="w")
        self._lbl_gesture.pack(fill="x", padx=pad)

        self._lbl_gesture_tip = tk.Label(
            parent, text=L.t("hud_tip_none"), font=("Consolas", 8),
            fg=_DIM, bg=_CARD, anchor="w", wraplength=200, justify="left")
        self._lbl_gesture_tip.pack(fill="x", padx=pad, pady=(2, 8))

        # Dwell progress
        df = tk.Frame(parent, bg=_CARD)
        df.pack(fill="x", padx=pad)
        tk.Label(df, text="DWELL", font=("Consolas", 7, "bold"),
                 fg=_DIMMER, bg=_CARD).pack(anchor="w")
        self._dwell_canvas = tk.Canvas(df, height=6, bg="#1a1a2e",
                                       highlightthickness=0)
        self._dwell_canvas.pack(fill="x", pady=(2, 0))
        self._dwell_fill = self._dwell_canvas.create_rectangle(
            0, 0, 0, 6, fill=_DIMMER, outline="")
        self._lbl_dwell_time = tk.Label(parent, text="", font=("Consolas", 8),
                                        fg=_DIM, bg=_CARD, anchor="w")
        self._lbl_dwell_time.pack(fill="x", padx=pad, pady=(2, 0))

    def _build_actions_panel(self, parent):
        pad = 10
        self._action_labels = []
        for _ in range(6):
            lbl = tk.Label(parent, text="", font=("Consolas", 8),
                           fg=_DIMMER, bg=_CARD, anchor="w")
            lbl.pack(fill="x", padx=pad)
            self._action_labels.append(lbl)
        # Re-render existing log
        self._render_action_log()

    def _build_notif_panel(self, parent):
        pad = 10
        self._notif_labels = []
        for _ in range(8):
            lbl = tk.Label(parent, text="", font=("Consolas", 7),
                           fg=_DIMMER, bg=_CARD, anchor="w",
                           wraplength=200, justify="left")
            lbl.pack(fill="x", padx=pad, pady=0)
            self._notif_labels.append(lbl)
        self._render_notif_log()

    # ══════════════════════════════════════════════════════════════════════════
    #  Widget Helpers
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _section_label(parent, text, padx=12):
        tk.Label(parent, text=text, font=("Consolas", 8, "bold"),
                 fg=_CYAN, bg=_CARD, anchor="w"
                 ).pack(fill="x", padx=padx, pady=(10, 4))

    @staticmethod
    def _status_row(parent, label, value, color):
        row = tk.Frame(parent, bg=_CARD)
        row.pack(fill="x", pady=1)
        tk.Label(row, text=label, font=("Consolas", 8),
                 fg=_DIM, bg=_CARD, width=12, anchor="w").pack(side="left")
        val = tk.Label(row, text=value, font=("Consolas", 8, "bold"),
                       fg=color, bg=_CARD, anchor="w")
        val.pack(side="left")
        return val

    def _make_button(self, parent, text, color, command, padx=12):
        btn = tk.Button(parent, text=f"  {text}",
                        font=("Consolas", 10, "bold"),
                        fg=_BG, bg=color, activebackground=color,
                        activeforeground=_BG, relief="flat", bd=0,
                        padx=0, pady=5, cursor="hand2",
                        command=command, anchor="w")
        btn.pack(fill="x", padx=padx, pady=3)
        lighter = self._lighten(color)
        btn.bind("<Enter>", lambda e, b=btn, c=lighter: b.configure(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))
        return btn

    # ══════════════════════════════════════════════════════════════════════════
    #  Update Loops
    # ══════════════════════════════════════════════════════════════════════════

    def _update_camera(self):
        try:
            frame_bgr = None
            while True:
                try:
                    frame_bgr = self._frame_q.get_nowait()
                except queue.Empty:
                    break
            if frame_bgr is not None and self._camera_label is not None:
                frame_rgb = frame_bgr[:, :, ::-1].copy()
                pil = Image.fromarray(frame_rgb)
                try:
                    lw = self._camera_label.winfo_width()
                    lh = self._camera_label.winfo_height()
                except Exception:
                    lw = lh = 0
                if lw > 10 and lh > 10:
                    iw, ih = pil.size
                    scale = min(lw / iw, lh / ih)
                    nw = max(1, int(iw * scale))
                    nh = max(1, int(ih * scale))
                    if nw != iw or nh != ih:
                        pil = pil.resize((nw, nh), Image.BILINEAR)
                photo = ImageTk.PhotoImage(pil)
                self._camera_label.configure(image=photo, text="")
                self._camera_photo = photo
        except Exception:
            pass
        if self._running:
            self._root.after(33, self._update_camera)

    def _process_queue(self):
        try:
            batch = 0
            while batch < 30:
                msg, data = self._q.get_nowait()
                batch += 1
                if msg == "state":
                    self._state = data
                    self._refresh_state()
                elif msg == "gesture":
                    self._refresh_gesture(data)
                elif msg == "notify":
                    self._show_notification(data)
                elif msg == "notif_log":
                    sev, text = data
                    self._add_notif_entry(sev, text)
                elif msg == "quit":
                    if self.on_quit:
                        self.on_quit()
                    self._root.quit()
        except queue.Empty:
            pass
        if self._running:
            self._root.after(50, self._process_queue)

    # ── State Refresh ─────────────────────────────────────────────────────────

    def _refresh_state(self):
        L = _lang_mod.get()
        st = self._state
        try:
            lh = st.get("left_hand", False)
            if self._v_hand:
                self._v_hand.configure(
                    text=L.t("hand_left") if lh else L.t("hand_right"), fg=_BLUE)

            cal = st.get("calibrated", False)
            if self._v_cal:
                self._v_cal.configure(
                    text=L.t("startup_cal_ok") if cal else L.t("startup_cal_no"),
                    fg=_GREEN if cal else _RED)

            dw = st.get("dwell_sec", 1.5)
            if self._v_dwell:
                self._v_dwell.configure(text=f"{dw}s")

            kb = st.get("kb_visible", False)
            if self._v_kb:
                self._v_kb.configure(
                    text=L.t("hud_kb_on") if kb else L.t("hud_kb_off"),
                    fg=_GREEN if kb else _DIM)

            ct = st.get("cam_top", False)
            if self._v_cam:
                self._v_cam.configure(
                    text=L.t("hud_cam_top") if ct else L.t("hud_cam_back"),
                    fg=_GREEN if ct else _DIM)

            hd = st.get("hand_detected", False)
            if self._v_hand_det:
                self._v_hand_det.configure(
                    text=L.t("hud_hand_yes") if hd else L.t("hud_hand_no"),
                    fg=_GREEN if hd else _DIM)

            # Header
            fps = st.get("fps", 0)
            if self._lbl_fps:
                self._lbl_fps.configure(text=f"{fps:.0f} fps")
            if self._lbl_cal:
                self._lbl_cal.configure(
                    text=L.t("hud_cal_ok") if cal else L.t("hud_cal_no"),
                    fg=_GREEN if cal else _AMBER)
            if self._cal_dot:
                self._cal_dot.configure(fg=_GREEN if cal else _AMBER)

            # Footer
            if self._lbl_kb_status:
                self._lbl_kb_status.configure(
                    text=L.t("hud_kb_on") if kb else L.t("hud_kb_off"),
                    fg=_GREEN if kb else _DIM)
            if self._lbl_cam_pos:
                self._lbl_cam_pos.configure(
                    text=L.t("hud_cam_front") if ct else L.t("hud_cam_back"),
                    fg=_GREEN if ct else _DIM)

            # Always-on-top
            if ct != self._prev_topmost:
                self._prev_topmost = ct
                self._root.attributes("-topmost", ct)

            # Pause state
            paused = st.get("paused", False)
            if paused:
                if self._v_status:
                    self._v_status.configure(text=L.t("hud_paused"), fg=_RED)
                if self._btn_pause:
                    self._btn_pause.configure(
                        text=f"  {L.t('panel_resume')}", bg=_GREEN,
                        activebackground=_GREEN)
                    lt = self._lighten(_GREEN)
                    self._btn_pause.bind("<Enter>",
                        lambda e, b=self._btn_pause, c=lt: b.configure(bg=c))
                    self._btn_pause.bind("<Leave>",
                        lambda e, b=self._btn_pause, c=_GREEN: b.configure(bg=c))
                if self._lbl_header_status:
                    self._lbl_header_status.configure(text="PAUSED", fg=_RED)
                if self._header_status_dot:
                    self._header_status_dot.configure(fg=_RED)
            else:
                if self._v_status:
                    self._v_status.configure(text=L.t("hud_active"), fg=_GREEN)
                if self._btn_pause:
                    self._btn_pause.configure(
                        text=f"  {L.t('panel_pause')}", bg=_CYAN,
                        activebackground=_CYAN)
                    lt = self._lighten(_CYAN)
                    self._btn_pause.bind("<Enter>",
                        lambda e, b=self._btn_pause, c=lt: b.configure(bg=c))
                    self._btn_pause.bind("<Leave>",
                        lambda e, b=self._btn_pause, c=_CYAN: b.configure(bg=c))
                if self._lbl_header_status:
                    self._lbl_header_status.configure(text="ACTIVE", fg=_GREEN)
                if self._header_status_dot:
                    self._header_status_dot.configure(fg=_GREEN)

            # Sync dwell slider display
            if self._dwell_scale:
                try:
                    if abs(self._dwell_scale.get() - dw) > 0.05:
                        self._dwell_scale.set(dw)
                except Exception:
                    pass
            if self._lbl_dwell_val:
                self._lbl_dwell_val.configure(text=f"{dw:.1f}s")
        except Exception:
            pass

    # ── Gesture Refresh ───────────────────────────────────────────────────────

    def _refresh_gesture(self, data):
        if self._in_flash:
            return
        L = _lang_mod.get()
        gesture = data.get("gesture", "none")
        progress = float(data.get("progress", 0.0))
        scroll_active = data.get("scroll_active", False)
        hold_active = data.get("hold_active", False)
        dwell_sec = float(data.get("dwell_sec", 1.5))
        color = _GESTURE_COLORS.get(gesture, _DIMMER)

        try:
            if self._gesture_bar:
                w = self._gesture_bar.winfo_width()
                if w > 1:
                    self._gesture_bar.coords(self._gesture_bar_fill, 0, 0, w, 3)
                    self._gesture_bar.itemconfig(self._gesture_bar_fill, fill=color)

            if gesture == "four" and scroll_active:
                name = L.t("hud_scroll_active")
            elif gesture == "thumbs_up" and hold_active:
                name = L.t("hud_hold_active")
            else:
                name = L.t(_GESTURE_LABEL_KEYS.get(gesture, "hud_none"))
            if self._lbl_gesture:
                self._lbl_gesture.configure(text=name, fg=color)

            if gesture == "thumbs_up" and hold_active:
                tip, tip_col = L.t("hud_tip_holding"), _GOLD
            elif progress >= 1.0 and gesture not in ("none", "pointing"):
                tip, tip_col = L.t("hud_tip_ready"), _GREEN
            elif progress > 0.0 and gesture not in ("none", "pointing"):
                remain = max(0.0, dwell_sec * (1.0 - progress))
                tip = f"{L.t('hud_tip_dwell')}  {remain:.1f}s"
                tip_col = color
            else:
                tip = L.t(_GESTURE_TIP_KEYS.get(gesture, "hud_tip_none"))
                tip_col = _DIM
            if self._lbl_gesture_tip:
                self._lbl_gesture_tip.configure(text=tip, fg=tip_col)

            if self._dwell_canvas:
                dw = self._dwell_canvas.winfo_width()
                if dw > 1:
                    filled = int(min(progress, 1.0) * dw)
                    bar_col = _GREEN if progress >= 1.0 else color
                    self._dwell_canvas.coords(self._dwell_fill, 0, 0, filled, 6)
                    self._dwell_canvas.itemconfig(self._dwell_fill, fill=bar_col)

            if self._lbl_dwell_time:
                if gesture in ("none", "pointing"):
                    self._lbl_dwell_time.configure(text="")
                elif progress >= 1.0:
                    self._lbl_dwell_time.configure(
                        text=L.t("hud_tip_ready"), fg=_GREEN)
                else:
                    remain = max(0.0, dwell_sec * (1.0 - progress))
                    self._lbl_dwell_time.configure(text=f"{remain:.1f}s", fg=color)

            if self._lbl_tip:
                self._lbl_tip.configure(text=tip, fg=tip_col)
        except Exception:
            pass

    # ── Notification / Action ─────────────────────────────────────────────────

    def _show_notification(self, gesture):
        L = _lang_mod.get()
        key = _NOTIFY_KEYS.get(gesture)
        if not key:
            return
        text = L.t(key)

        # Action log
        self._action_log.insert(0, text)
        self._action_log = self._action_log[:6]
        self._render_action_log()

        # Also add to notification log
        sev = "success"
        if gesture in ("paused",):
            sev = "warning"
        elif gesture in ("resumed",):
            sev = "info"
        self._add_notif_entry(sev, text)

        # Flash
        self._in_flash = True
        try:
            if self._lbl_gesture:
                self._lbl_gesture.configure(text=f"\u2713 {text}", fg=_GREEN)
            if self._lbl_gesture_tip:
                self._lbl_gesture_tip.configure(text=L.t("hud_tip_ready"), fg=_GREEN)
            if self._dwell_canvas:
                dw = self._dwell_canvas.winfo_width()
                if dw > 1:
                    self._dwell_canvas.coords(self._dwell_fill, 0, 0, dw, 6)
                    self._dwell_canvas.itemconfig(self._dwell_fill, fill=_GREEN)
            if self._gesture_bar:
                w = self._gesture_bar.winfo_width()
                if w > 1:
                    self._gesture_bar.coords(self._gesture_bar_fill, 0, 0, w, 3)
                    self._gesture_bar.itemconfig(self._gesture_bar_fill, fill=_GREEN)
            if self._lbl_dwell_time:
                self._lbl_dwell_time.configure(text="", fg=_GREEN)
            if self._lbl_tip:
                self._lbl_tip.configure(text=f"\u2713 {text}", fg=_GREEN)
        except Exception:
            pass
        if self._flash_job:
            try:
                self._root.after_cancel(self._flash_job)
            except Exception:
                pass
        self._flash_job = self._root.after(700, self._end_flash)

    def _end_flash(self):
        self._in_flash = False
        self._flash_job = None

    def _render_action_log(self):
        _fade = [_GREEN, "#60a0a0", _DIM, _DIMMER, _DIMMER, _DIMMER]
        for i, lbl in enumerate(self._action_labels):
            try:
                if i < len(self._action_log):
                    lbl.configure(
                        text=f"\u25b8 {self._action_log[i]}",
                        fg=_fade[min(i, len(_fade) - 1)])
                else:
                    lbl.configure(text="")
            except Exception:
                pass

    def _add_notif_entry(self, severity, msg):
        ts = time.strftime("%H:%M:%S")
        self._notif_log.insert(0, (ts, severity, msg))
        self._notif_log = self._notif_log[:20]
        self._render_notif_log()

    def _render_notif_log(self):
        for i, lbl in enumerate(self._notif_labels):
            try:
                if i < len(self._notif_log):
                    ts, sev, msg = self._notif_log[i]
                    col = _SEV_COLORS.get(sev, _DIM)
                    lbl.configure(text=f"{ts}  {msg}", fg=col)
                else:
                    lbl.configure(text="")
            except Exception:
                pass

    # ══════════════════════════════════════════════════════════════════════════
    #  Help Dialog
    # ══════════════════════════════════════════════════════════════════════════

    def _open_help(self):
        if self._help_win and self._help_win.winfo_exists():
            self._help_win.lift()
            return

        L = _lang_mod.get()
        is_tr = L.code == "tr"

        win = tk.Toplevel(self._root)
        self._help_win = win
        win.title("KYVORA \u2014 " + (
            "Nasil Kullanilir?" if is_tr else "How To Use?"))
        win.configure(bg=_BG)
        win.resizable(False, False)
        win.transient(self._root)
        try:
            win.attributes("-topmost", True)
            win.attributes("-alpha", 0.97)
        except Exception:
            pass

        ww, wh = 500, 820
        rx = self._root.winfo_x()
        ry = self._root.winfo_y()
        rw = self._root.winfo_width()
        rh = self._root.winfo_height()
        x = rx + (rw - ww) // 2
        y = ry + (rh - wh) // 2
        win.geometry(f"{ww}x{wh}+{max(0, x)}+{max(0, y)}")

        f_head = ("Consolas", 14, "bold")
        f_lbl  = ("Consolas", 10, "bold")
        f_sm   = ("Consolas", 9)
        f_desc = ("Consolas", 8)

        canvas = tk.Canvas(win, bg=_BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg=_BG)
        canvas.create_window((0, 0), window=inner, anchor="nw", width=ww)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"))

        pad = 14
        tk.Label(inner, text="KYVORA \u2014 " + (
            "NASIL KULLANILIR?" if is_tr else "HOW TO USE?"),
                 font=f_head, fg=_CYAN, bg=_BG, pady=12).pack(fill="x", padx=pad)

        df = tk.Frame(inner, bg=_CARD, padx=10, pady=8)
        df.pack(fill="x", padx=pad, pady=(0, 6))
        tk.Label(df, text="DWELL " + ("SISTEMI" if is_tr else "SYSTEM"),
                 font=f_lbl, fg=_AMBER, bg=_CARD).pack(anchor="w")
        dwell_txt = (
            "Isaret parmagi haric tum jestler bekleme sistemi kullanir.\n"
            "Jesti yap ve halka dolana kadar bekle \u2014 islem o zaman tetiklenir.\n"
            "Bekleme suresini kontrol panelindeki kaydirici ile ayarlayabilirsiniz."
            if is_tr else
            "All gestures except pointing use the dwell system.\n"
            "Hold the gesture until the ring fills \u2014 action fires then.\n"
            "Adjust the dwell time with the slider in the Controls panel."
        )
        tk.Label(df, text=dwell_txt, font=f_desc, fg=_DIM, bg=_CARD,
                 justify="left").pack(anchor="w")

        if is_tr:
            items = [
                ("[1]", "IMLEC", "Isaret Parmagi",
                 "Sadece isaret parmagi yukari, diger parmaklar kapali.\n"
                 "Fareyi dogrudan hareket ettirir \u2014 bekleme yok.", _GREEN),
                ("[2]", "SOL TIK", "Pinch",
                 "Basparmak ucu ile isaret parmagi ucunu birlestir.\n"
                 "Halka dolunca sol tik yapar.", _AMBER),
                ("[3]", "SAG TIK", "V Isareti",
                 "Isaret ve orta parmak acik, yuzuk ve serce kapali.\n"
                 "Halka dolunca sag tik yapar.", _BLUE),
                ("[4]", "KAYDIRMA", "4 Parmak",
                 "Isaret, orta, yuzuk, serce acik \u2014 basparmak kapali.\n"
                 "Halka dolunca aktif: el yukari/asagi hareketiyle kaydir.", _PURPLE),
                ("[5]", "KLAVYE", "3 Parmak",
                 "Isaret, orta, yuzuk acik \u2014 serce ve basparmak kapali.\n"
                 "Halka dolunca ekran klavyesini acar/kapatir.", _PINK),
                ("[6]", "PENCERE", "Yumruk",
                 "Tum parmaklar kapali, siki yumruk.\n"
                 "Halka dolunca pencereyi one/arkaya alir.", _RED),
                ("[7]", "ALT+TAB", "Kurt",
                 "Orta ve yuzuk parmak basparmaga deger,\n"
                 "isaret ve serce duz yukari.\n"
                 "Halka dolunca pencere degistirir.", _ORANGE),
                ("[8]", "BASILI TUT", "Basparmak Yukari",
                 "Elini yumruk yapip basparmagi yukari tut.\n"
                 "Halka dolunca sol tus basili kalir.\n"
                 "Elini hareket ettirerek surukle.\n"
                 "Baska jest yapinca birakir.", _GOLD),
                ("[9]", "DURAKLAT / DEVAM", "Avuc Acma",
                 "Bes parmak acik avuc gosterin.\n"
                 "1 saniye bekleyin \u2014 jest kontrolu duraklar.\n"
                 "Ayni hareketi tekrar yapinca devam eder.\n"
                 "Duraklat veya Devam ettikten sonra elinizi\n"
                 "nötr pozisyona getirin (yumruk veya kameradan\n"
                 "cikarin). Surekli avuc acik tutmak tekrarli\n"
                 "gecis yapmaz.\n"
                 "GUI butonuyla da duraklat/devam edebilirsiniz.", _CYAN),
            ]
        else:
            items = [
                ("[1]", "CURSOR", "Index Finger",
                 "Only index finger raised, others closed.\n"
                 "Moves mouse directly \u2014 no dwell needed.", _GREEN),
                ("[2]", "L-CLICK", "Pinch",
                 "Bring thumb tip and index fingertip together.\n"
                 "When ring fills: left click.", _AMBER),
                ("[3]", "R-CLICK", "V Sign",
                 "Index and middle up, ring and pinky closed.\n"
                 "When ring fills: right click.", _BLUE),
                ("[4]", "SCROLL", "4 Fingers",
                 "Index, middle, ring, pinky up \u2014 thumb closed.\n"
                 "When ready: move hand up/down to scroll.", _PURPLE),
                ("[5]", "KEYBOARD", "3 Fingers",
                 "Index, middle, ring up \u2014 pinky and thumb closed.\n"
                 "When ring fills: toggles on-screen keyboard.", _PINK),
                ("[6]", "WINDOW", "Fist",
                 "All fingers closed, tight fist.\n"
                 "When ring fills: toggles window always-on-top.", _RED),
                ("[7]", "ALT+TAB", "Wolf",
                 "Middle and ring touch thumb,\n"
                 "index and pinky raised straight up.\n"
                 "When ring fills: switches windows.", _ORANGE),
                ("[8]", "HOLD CLICK", "Thumbs Up",
                 "Close all fingers into a fist, then raise only\n"
                 "your thumb. When ring fills: left button held.\n"
                 "Move your hand to drag. Change gesture to release.", _GOLD),
                ("[9]", "PAUSE / RESUME", "Open Palm",
                 "Show all five fingers open.\n"
                 "Hold for 1 second \u2014 gesture control pauses.\n"
                 "Repeat the same gesture to resume.\n"
                 "After activating Pause or Resume, return your\n"
                 "hand to a neutral position (e.g. close fist or\n"
                 "leave the camera) before performing the Open\n"
                 "Palm gesture again. Holding the gesture\n"
                 "continuously will not repeatedly toggle.\n"
                 "You can also use the Pause/Resume button.", _CYAN),
            ]

        for num, action, pose, desc, color in items:
            card = tk.Frame(inner, bg=_CARD, padx=12, pady=8)
            card.pack(fill="x", padx=pad, pady=2)
            top = tk.Frame(card, bg=_CARD)
            top.pack(fill="x")
            tk.Label(top, text=num, font=f_sm, fg=_DIM, bg=_CARD,
                     width=4, anchor="w").pack(side="left")
            tk.Label(top, text=action, font=f_lbl, fg=color, bg=_CARD,
                     width=12, anchor="w").pack(side="left")
            tk.Label(top, text=pose, font=f_sm, fg=_WHITE, bg=_CARD,
                     anchor="w").pack(side="left")
            tk.Label(card, text=desc, font=f_desc, fg="#8888aa",
                     bg=_CARD, justify="left", anchor="w",
                     wraplength=440).pack(fill="x", pady=(4, 0))
            tk.Frame(card, height=1, bg=_BORDER).pack(fill="x", pady=(6, 0))

        tk.Frame(inner, height=20, bg=_BG).pack()

        close_lbl = "Kapat" if is_tr else "Close"
        tk.Button(win, text=close_lbl, font=("Consolas", 10, "bold"),
                  fg=_BG, bg=_CYAN, activebackground="#0891b2",
                  relief="flat", bd=0, padx=20, pady=6,
                  cursor="hand2", command=win.destroy).pack(pady=8)

    # ══════════════════════════════════════════════════════════════════════════
    #  Button Callbacks
    # ══════════════════════════════════════════════════════════════════════════

    def _on_cal_click(self):
        if self.on_calibrate:
            self.on_calibrate()

    def _on_hand_click(self):
        if self.on_toggle_hand:
            self.on_toggle_hand()

    def _on_pause_click(self):
        if self.on_toggle_pause:
            self.on_toggle_pause()

    def _on_quit_click(self):
        self._running = False
        if self.on_quit:
            self.on_quit()
        try:
            self._root.quit()
        except Exception:
            pass

    def _on_dwell_slider(self, val):
        v = float(val)
        if self._lbl_dwell_val:
            self._lbl_dwell_val.configure(text=f"{v:.1f}s")
        if self.on_dwell_change:
            self.on_dwell_change(v)

    # ══════════════════════════════════════════════════════════════════════════
    #  Window Management
    # ══════════════════════════════════════════════════════════════════════════

    def _restore_layout(self):
        """Dock all floating panels back to the main window."""
        for sec in self._sections.values():
            if sec.is_floating:
                sec.dock()

    # ══════════════════════════════════════════════════════════════════════════
    #  Utilities
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _lighten(hex_color: str) -> str:
        try:
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return (f"#{min(255, r + 30):02x}"
                    f"{min(255, g + 30):02x}"
                    f"{min(255, b + 30):02x}")
        except Exception:
            return hex_color
