"""
Yardim ekrani - Jest rehberi.
Tkinter ile tum platformlarda calisir.
"""

import threading
import platform
import lang as _lang_mod

_OS = platform.system()


# Renk paleti
_BG      = "#0d0d1a"
_CARD    = "#1a1a2e"
_BORDER  = "#2a2a4a"
_WHITE   = "#e8e8f0"
_DIM     = "#6a6a8a"
_GREEN   = "#4ade80"
_AMBER   = "#fbbf24"
_BLUE    = "#60a5fa"
_PURPLE  = "#c084fc"
_PINK    = "#f472b6"
_RED     = "#f87171"
_ORANGE  = "#fb923c"

_LOCK = threading.Lock()
_win  = [None]


def show() -> None:
    """Yardim penceresini ac (singleton)."""
    with _LOCK:
        if _win[0] is not None:
            try:
                _win[0].lift()
                _win[0].focus_force()
                return
            except Exception:
                _win[0] = None
    threading.Thread(target=_build, daemon=True).start()


def _build() -> None:
    try:
        import tkinter as tk
        from tkinter import font as tkfont
    except ImportError:
        return

    L = _lang_mod.get()
    is_ar = L.is_rtl

    root = tk.Tk()
    with _LOCK:
        _win[0] = root

    root.title(f"KYVORA \u2014 {L.t('help_title')}")
    root.configure(bg=_BG)
    root.resizable(False, False)
    root.attributes("-topmost", True)

    try:
        root.attributes("-alpha", 0.97)
    except Exception:
        pass

    # Ekranin sagina konumlandir
    root.update_idletasks()
    scr_w = root.winfo_screenwidth()
    scr_h = root.winfo_screenheight()
    win_w, win_h = 480, 680
    x = scr_w - win_w - 20
    y = (scr_h - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    # Fontlar
    f_title  = ("Consolas", 13, "bold")
    f_sub    = ("Consolas", 10)
    f_label  = ("Consolas", 11, "bold")
    f_desc   = ("Consolas", 9)
    f_header = ("Consolas", 15, "bold")
    f_close  = ("Consolas", 10, "bold")

    # Jest verileri
    if is_ar:
        gestures = [
            ("[1]", L.t("help_1_action"), "☝",  L.t("help_1_pose"), L.t("hud_move"),
             _GREEN,  L.t("help_1_desc")),
            ("[2]", L.t("help_2_action"), "🤌", L.t("help_2_pose"), L.t("hud_lclick"),
             _AMBER,  L.t("help_2_desc")),
            ("[3]", L.t("help_3_action"), "✌",  L.t("help_3_pose"), L.t("hud_rclick"),
             _BLUE,   L.t("help_3_desc")),
            ("[4]", L.t("help_4_action"), "🖐",  L.t("help_4_pose"), L.t("hud_scroll"),
             _PURPLE, L.t("help_4_desc")),
            ("[5]", L.t("help_5_action"), "🖖",  L.t("help_5_pose"), L.t("hud_keyboard"),
             _PINK,   L.t("help_5_desc")),
            ("[6]", L.t("help_6_action"), "✊",  L.t("help_6_pose"), L.t("hud_cam"),
             _RED,    L.t("help_6_desc")),
            ("[7]", L.t("help_7_action"), "🐺",  L.t("help_7_pose"), L.t("hud_wolf"),
             _ORANGE, L.t("help_7_desc")),
        ]
        title_text = "كيفية الاستخدام؟"
        mode_tr    = "جميع الإيماءات تستخدم نظام الانتظار.\nتحريك إصبع السبابة فوري."
        key_hint   = "C = معايرة    H = تبديل اليد    Q = خروج"
        close_lbl  = "إغلاق"
        dwell_lbl  = "مدة الانتظار"
    else:
        gestures = [
            ("[1]", "CURSOR",    "☝",  "Index Finger",            "Move the cursor",
             _GREEN,  "Only index finger raised,\nothers folded down."),
            ("[2]", "L-CLICK",   "🤌", "Pinch",                   "Left click - wait dwell",
             _AMBER,  "Bring thumb tip and index\nfinger tip together."),
            ("[3]", "R-CLICK",   "✌",  "V Sign",                  "Right click - wait dwell",
             _BLUE,   "Index and middle up,\nring and pinky folded."),
            ("[4]", "SCROLL",    "🖐",  "4 Fingers",               "Scroll - wait dwell",
             _PURPLE, "Index, middle, ring, pinky up.\nThumb closed.\nAfter ready: move hand up/down."),
            ("[5]", "KEYBOARD",  "🖖",  "3 Fingers",               "Toggle keyboard",
             _PINK,   "Index, middle, ring up.\nPinky and thumb closed."),
            ("[6]", "CAMERA",    "✊",  "Fist",                    "Toggle camera position",
             _RED,    "All fingers folded closed.\nMake a tight fist."),
            ("[7]", "ALT+TAB",   "🕷",  "Spider",                  "Switch windows",
             _ORANGE, "Middle and ring touch thumb,\nindex and pinky raised straight."),
        ]
        title_text = "HOW TO CONTROL?"
        mode_tr    = "All gestures use the dwell system.\nPointing finger is instant."
        key_hint   = "C = Calibrate    H = Hand switch    Q = Quit"
        close_lbl  = "Close"
        dwell_lbl  = "DWELL TIME"

    # Canvas ile scrollable alan
    canvas = tk.Canvas(root, bg=_BG, highlightthickness=0,
                       width=win_w, height=win_h - 50)
    canvas.pack(fill="both", expand=True)

    sb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=sb.set)

    inner = tk.Frame(canvas, bg=_BG)
    canvas.create_window((0, 0), window=inner, anchor="nw", width=win_w)

    def _on_resize(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    inner.bind("<Configure>", _on_resize)

    def _scroll(e):
        canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _scroll)

    pad = 16

    # Baslik
    tk.Label(inner, text=title_text, font=f_header,
             fg=_GREEN, bg=_BG, pady=14).pack(fill="x", padx=pad)

    # Dwell aciklamasi
    info_frame = tk.Frame(inner, bg=_CARD, padx=12, pady=8)
    info_frame.pack(fill="x", padx=pad, pady=(0, 8))
    tk.Label(info_frame, text=dwell_lbl, font=f_label,
             fg=_AMBER, bg=_CARD).pack(anchor="w")
    tk.Label(info_frame, text=mode_tr, font=f_desc,
             fg=_DIM, bg=_CARD, justify="left").pack(anchor="w")

    # Jest kartlari
    for num, action, icon, pose, desc, color, how in gestures:
        card = tk.Frame(inner, bg=_CARD, padx=12, pady=10)
        card.pack(fill="x", padx=pad, pady=3)

        # Ust satir: numara + aksiyon + aciklama
        top = tk.Frame(card, bg=_CARD)
        top.pack(fill="x")
        tk.Label(top, text=num, font=f_label,
                 fg=_DIM, bg=_CARD, width=4, anchor="w").pack(side="left")
        tk.Label(top, text=action, font=f_label,
                 fg=color, bg=_CARD, width=10, anchor="w").pack(side="left")
        tk.Label(top, text=desc, font=f_sub,
                 fg=_DIM, bg=_CARD, anchor="w").pack(side="left")

        # Pose ismi
        pose_row = tk.Frame(card, bg=_CARD)
        pose_row.pack(fill="x", pady=(4, 0))
        tk.Label(pose_row, text=pose, font=("Consolas", 10, "bold"),
                 fg=_WHITE, bg=_CARD, width=14, anchor="w").pack(side="left")

        # Nasil yapilir
        tk.Label(card, text=how, font=f_desc,
                 fg="#9090b0", bg=_CARD, justify="left", anchor="w",
                 wraplength=420).pack(fill="x", pady=(2, 0))

        # Alt cizgi (ince)
        tk.Frame(card, height=1, bg=_BORDER).pack(fill="x", pady=(8, 0))

    # Kisayollar
    hint_frame = tk.Frame(inner, bg=_CARD, padx=12, pady=8)
    hint_frame.pack(fill="x", padx=pad, pady=(4, 16))
    tk.Label(hint_frame, text=key_hint, font=f_desc,
             fg=_DIM, bg=_CARD).pack(anchor="w")

    # Kapat butonu
    btn_frame = tk.Frame(root, bg=_BG, pady=8)
    btn_frame.pack(fill="x")
    close_btn = tk.Button(
        btn_frame, text=close_lbl, font=f_close,
        fg=_BG, bg=_GREEN, activebackground="#22c55e",
        activeforeground=_BG, relief="flat", bd=0,
        padx=24, pady=6, cursor="hand2",
        command=root.destroy
    )
    close_btn.pack()

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    def _on_destroy():
        with _LOCK:
            _win[0] = None

    root.bind("<Destroy>", lambda e: _on_destroy() if e.widget is root else None)

    root.mainloop()
    with _LOCK:
        _win[0] = None
