"""
KYVORA - Dil modulu (TR / EN)
ASCII only - Turkce ozel karakter kullanilmaz.
"""

from config import Config

_S: dict[str, dict[str, str]] = {
    # ── Dil / Baslangic ──────────────────────────────────────────────────────
    "lang_prompt":      {"tr": "Dil secin / Select language  [TR/EN]: ",
                         "en": "Dil secin / Select language  [TR/EN]: "},
    "lang_invalid":     {"tr": "Gecersiz secim - Turkce kullaniliyor.",
                         "en": "Invalid choice - using English."},

    "cam_mode_question":{"tr": "\nKamera gorunsun mu?\n"
                               "  [E] Evet  - kamera penceresi acik calisir\n"
                               "  [H] Hayir - kamera arka planda calisir\n"
                               "Seciminiz [E/H]: ",
                         "en": "\nShow camera on screen?\n"
                               "  [Y] Yes - camera window visible\n"
                               "  [N] No  - camera runs in background\n"
                               "Your choice [Y/N]: "},

    # ── Sistem baslangici ────────────────────────────────────────────────────
    "startup_title":    {"tr": "El Hareketiyle Kontrol Sistemi",
                         "en": "Gesture Control System"},
    "startup_os":       {"tr": "Sistem",           "en": "System"},
    "startup_dwell":    {"tr": "Bekleme suresi",   "en": "Dwell time"},
    "startup_hand":     {"tr": "Baskin el",        "en": "Dominant hand"},
    "startup_cal":      {"tr": "Kalibrasyon",      "en": "Calibration"},
    "startup_cal_ok":   {"tr": "Yapildi",          "en": "Done"},
    "startup_cal_no":   {"tr": "Henuz yapilmadi",  "en": "Not done yet"},
    "startup_failsafe": {"tr": "GUVENLIK: Fareyi SOL UST koseye gotur -> program durur",
                         "en": "SAFETY: Move mouse to TOP-LEFT corner -> program stops"},

    # ── Kamera ───────────────────────────────────────────────────────────────
    "cam_opening":      {"tr": "Kamera aciliyor, lutfen bekleyin...",
                         "en": "Opening camera, please wait..."},
    "cam_ready":        {"tr": "Kamera hazir.",    "en": "Camera ready."},
    "cam_error":        {"tr": "[HATA] Kamera acilamadi. Kamera indeksini kontrol edin.",
                         "en": "[ERROR] Could not open camera. Check camera index."},
    "cam_lost":         {"tr": "[HATA] Kamera baglantisi kesildi.",
                         "en": "[ERROR] Camera connection lost."},

    # ── Baslama / Kapanma ────────────────────────────────────────────────────
    "started_cam":      {"tr": "Baslatildi — Kontrol panelinden cikilebilir.",
                         "en": "Started — Use control panel to quit."},
    "started_headless": {"tr": "Baslatildi (arka plan) — Kontrol panelinden cikilebilir.",
                         "en": "Started (background) — Use control panel to quit."},
    "shutting_down":    {"tr": "Kapatiliyor...",   "en": "Shutting down..."},
    "closed":           {"tr": "Program kapatildi.","en": "Program closed."},
    "failsafe":         {"tr": "Guvenlik devreye girdi — program durduruldu.",
                         "en": "Safety triggered — program stopped."},
    "error":            {"tr": "Beklenmeyen hata", "en": "Unexpected error"},
    "warn_frame":       {"tr": "Kare isleme hatasi","en": "Frame processing error"},

    # ── El ve el degistirme ──────────────────────────────────────────────────
    "hand_changed":     {"tr": "El degistirildi",  "en": "Hand switched"},
    "hand_left":        {"tr": "Sol el",           "en": "Left hand"},
    "hand_right":       {"tr": "Sag el",           "en": "Right hand"},

    # ── Aksiyonlar (terminal) ────────────────────────────────────────────────
    "action_lclick":    {"tr": "Sol tik",          "en": "Left click"},
    "action_rclick":    {"tr": "Sag tik",          "en": "Right click"},
    "action_keyboard":  {"tr": "Klavye toggle",    "en": "Keyboard toggle"},
    "action_cam_top":   {"tr": "Kamera: On planda","en": "Camera: In front"},
    "action_cam_back":  {"tr": "Kamera: Arkaya alindi","en": "Camera: Moved back"},
    "action_alttab":    {"tr": "Alt+Tab yapildi",  "en": "Alt+Tab performed"},
    "action_hold_start":{"tr": "Sol tus BASILI TUTULUYOR","en": "Left button HELD DOWN"},
    "action_hold_end":  {"tr": "Sol tus BIRAKILDI", "en": "Left button RELEASED"},
    "action_paused":    {"tr": "Jest kontrolu DURAKLATILDI", "en": "Gesture control PAUSED"},
    "action_resumed":   {"tr": "Jest kontrolu DEVAM EDIYOR", "en": "Gesture control RESUMED"},

    # ── HUD - Jest etiketleri ────────────────────────────────────────────────
    "hud_none":         {"tr": "EL ALGILANAMADI",  "en": "NO HAND DETECTED"},
    "hud_unknown":      {"tr": "BILINMEYEN HAREKET","en": "UNKNOWN GESTURE"},
    "hud_move":         {"tr": "[1] IMLEC HAREKETI","en": "[1] CURSOR MOVE"},
    "hud_lclick":       {"tr": "[2] SOL TIK",      "en": "[2] LEFT CLICK"},
    "hud_rclick":       {"tr": "[3] SAG TIK",      "en": "[3] RIGHT CLICK"},
    "hud_scroll":       {"tr": "[4] KAYDIRMA",     "en": "[4] SCROLL"},
    "hud_keyboard":     {"tr": "[5] KLAVYE",       "en": "[5] KEYBOARD"},
    "hud_cam":          {"tr": "[6] KAMERA",       "en": "[6] CAMERA"},
    "hud_wolf":         {"tr": "[7] PENCERE DEGISTIR","en": "[7] SWITCH WINDOW"},
    "hud_hold":         {"tr": "[8] BASILI TUT",     "en": "[8] HOLD CLICK"},
    "hud_hold_active":  {"tr": "[8] BASILI TUTULUYOR","en": "[8] HOLDING..."},
    "hud_open_palm":    {"tr": "[9] DURAKLAT/DEVAM", "en": "[9] PAUSE/RESUME"},
    "hud_paused":       {"tr": "DURAKLATILDI",     "en": "PAUSED"},
    "hud_active":       {"tr": "AKTIF",            "en": "ACTIVE"},
    "hud_holding_indicator": {"tr": "SOL TUS BASILI","en": "LEFT BTN HELD"},
    "hud_tip_thumbsup": {"tr": "Begeni isareti — dwell dolunca sol tus basili kalir",
                         "en": "Thumbs up — hold until ring fills to press & hold left click"},
    "hud_tip_holding":  {"tr": "Sol tus basili — jest degistirince birakir",
                         "en": "Left button held — change gesture to release"},

    # ── HUD - Durum ve ipucu mesajlari ───────────────────────────────────────
    "hud_tip_none":     {"tr": "Elinizi kameraya gosterin",
                         "en": "Show your hand to the camera"},
    "hud_tip_pointing": {"tr": "Parmaginizi hareket ettirin",
                         "en": "Move your finger to control cursor"},
    "hud_tip_pinch":    {"tr": "Basparmak + isaret birlestirin",
                         "en": "Bring thumb + index together"},
    "hud_tip_vsign":    {"tr": "V isareti yapip bekleyin",
                         "en": "Hold V sign to right-click"},
    "hud_tip_scroll":   {"tr": "4 parmak — elini yukari/asagi hareket ettir",
                         "en": "4 fingers — move hand up/down"},
    "hud_tip_three":    {"tr": "3 parmak yapip bekleyin",
                         "en": "Hold 3 fingers to toggle keyboard"},
    "hud_tip_fist":     {"tr": "Yumruk yapip bekleyin",
                         "en": "Hold fist to toggle camera"},
    "hud_tip_wolf":     {"tr": "Kurt pozisyonu yapip bekleyin",
                         "en": "Hold wolf pose to switch window"},
    "hud_tip_open_palm":{"tr": "Avuc acarak duraklatabilir veya devam edebilirsiniz",
                         "en": "Open palm to pause or resume gesture control"},
    "hud_tip_paused":   {"tr": "Jest kontrolu duraklatildi — devam icin avuc acin veya butona basin",
                         "en": "Gesture control paused — open palm or press button to resume"},
    "hud_tip_dwell":    {"tr": "Hareketi koruyun...",
                         "en": "Hold the gesture..."},
    "hud_tip_ready":    {"tr": "Hareket tanimlandi!",
                         "en": "Gesture recognized!"},
        "hud_scroll_active": {"tr": "KAYDIRMA AKTIF — yukari/asagi hareket et",
                         "en": "SCROLLING — move hand up/down"},
    "hud_ready":        {"tr": "TAMAM!",           "en": "DONE!"},
    "hud_hold_sec":     {"tr": "sn",               "en": "s"},
    "hud_how_to":       {"tr": "Nasil Kullanilir?","en": "How To Use?"},
    "hud_kb_on":        {"tr": "KB:ACIK",          "en": "KB:ON"},
    "hud_kb_off":       {"tr": "KB:KAPALI",        "en": "KB:OFF"},
    "hud_cam_front":    {"tr": "CAM:ONDE",         "en": "CAM:FRONT"},
    "hud_cam_top":      {"tr": "CAM:ONDE",         "en": "CAM:FRONT"},
    "hud_cam_back":     {"tr": "CAM:ARKA",         "en": "CAM:BACK"},
    "hud_cal_ok":       {"tr": "KAL:OK",           "en": "CAL:OK"},
    "hud_cal_no":       {"tr": "KAL:EKSIK",        "en": "CAL:MISSING"},

    # ── Kalibrasyon ──────────────────────────────────────────────────────────
    "cal_started":      {"tr": "Kalibrasyon baslatildi.",
                         "en": "Calibration started."},
    "cal_cancelled":    {"tr": "Kalibrasyon iptal edildi.",
                         "en": "Calibration cancelled."},
    "cal_done":         {"tr": "Kalibrasyon tamamlandi! Ayarlar kaydedildi.",
                         "en": "Calibration complete! Settings saved."},
    "cal_step1_title":  {"tr": "ADIM 1/2 - EL OLCUMU",
                         "en": "STEP 1/2 - HAND MEASUREMENT"},
    "cal_step1_inst":   {"tr": "Avucunu kameraya ac ve ortada tut.",
                         "en": "Open your palm and hold it in the center."},
    "cal_step2_title":  {"tr": "ADIM 2/2 - KOSE {n}/4",
                         "en": "STEP 2/2 - CORNER {n}/4"},
    "cal_step2_inst":   {"tr": "Isaret parmaginı {label} koseye gotur ve bekle.",
                         "en": "Point index finger to the {label} corner and hold."},
    "cal_done_title":   {"tr": "KALIBRASYON TAMAMLANDI",
                         "en": "CALIBRATION COMPLETE"},
    "cal_done_inst":    {"tr": "Tum ayarlar basariyla kaydedildi.",
                         "en": "All settings saved successfully."},
    "cal_done_sub":     {"tr": "Program normal modda devam ediyor...",
                         "en": "Resuming normal mode..."},
    "cal_cancel_hint":  {"tr": "ESC = Kalibrasyon iptal",
                         "en": "ESC = Cancel calibration"},
    "cal_corner_ul":    {"tr": "SOL UST",          "en": "TOP LEFT"},
    "cal_corner_ur":    {"tr": "SAG UST",          "en": "TOP RIGHT"},
    "cal_corner_lr":    {"tr": "SAG ALT",          "en": "BOTTOM RIGHT"},
    "cal_corner_ll":    {"tr": "SOL ALT",          "en": "BOTTOM LEFT"},
    "cal_measure":      {"tr": "Olculuyor",        "en": "Measuring"},

    # ── Sistem tepsisi ───────────────────────────────────────────────────────
    "tray_started":     {"tr": "Sistem tepsisi hazir.",
                         "en": "System tray ready."},
    "tray_no_lib":      {"tr": "pystray bulunamadi — tepsi devre disi.\n"
                               "Kurmak icin: pip install pystray Pillow",
                         "en": "pystray not found — tray disabled.\n"
                               "Install with: pip install pystray Pillow"},
    "tray_toggle_cam":  {"tr": "Kamerayi Goster / Gizle",
                         "en": "Show / Hide Camera"},
    "tray_calibrate":   {"tr": "Kalibrasyon Yap",  "en": "Run Calibration"},
    "tray_quit":        {"tr": "Programi Kapat",   "en": "Quit Program"},

    # ── Bildirim ─────────────────────────────────────────────────────────────
    "notify_lclick":    {"tr": "SOL TIK",          "en": "LEFT CLICK"},
    "notify_rclick":    {"tr": "SAG TIK",          "en": "RIGHT CLICK"},
    "notify_scroll":    {"tr": "KAYDIRMA",         "en": "SCROLL"},
    "notify_keyboard":  {"tr": "KLAVYE",           "en": "KEYBOARD"},
    "notify_cam":       {"tr": "KAMERA",           "en": "CAMERA"},
    "notify_wolf":      {"tr": "ALT+TAB",          "en": "ALT+TAB"},
    "notify_hold":      {"tr": "BASILI TUTULUYOR", "en": "HOLDING"},
    "notify_release":   {"tr": "BIRAKILDI",        "en": "RELEASED"},
    "notify_paused":    {"tr": "DURAKLATILDI",     "en": "PAUSED"},
    "notify_resumed":   {"tr": "DEVAM EDIYOR",     "en": "RESUMED"},

    # ── Ekran klavyesi ───────────────────────────────────────────────────────
    "kb_opened":        {"tr": "Ekran klavyesi acildi.",
                         "en": "On-screen keyboard opened."},
    "kb_closed":        {"tr": "Ekran klavyesi kapatildi.",
                         "en": "On-screen keyboard closed."},
    "kb_not_found":     {"tr": "Klavye uygulamasi bulunamadi:",
                         "en": "Keyboard application not found:"},
    "kb_timeout":       {"tr": "Klavye acilirken zaman asimi.",
                         "en": "Keyboard open timed out."},
    "kb_error_open":    {"tr": "Klavye acma hatasi:",
                         "en": "Error opening keyboard:"},
    "kb_error_close":   {"tr": "Klavye kapama hatasi:",
                         "en": "Error closing keyboard:"},
    "kb_linux_none":    {"tr": "Linux icin ekran klavyesi bulunamadi.",
                         "en": "No on-screen keyboard found on Linux."},
    "kb_linux_install": {"tr": "Kurmak icin: sudo apt install onboard",
                         "en": "Install with: sudo apt install onboard"},
    "kb_using":         {"tr": "Kullaniliyor:",    "en": "Using:"},

    # ── Kontrol paneli buton etiketleri ──────────────────────────────────────
    "panel_calibrate":  {"tr": "Kalibrasyon Yap",  "en": "Run Calibration"},
    "panel_hand":       {"tr": "El Degistir",      "en": "Switch Hand"},
    "panel_how_to":     {"tr": "Nasil Kullanilir?","en": "How To Use?"},
    "panel_quit":       {"tr": "Programi Kapat",   "en": "Quit Program"},
    "panel_pause":      {"tr": "Duraklat",         "en": "Pause"},
    "panel_resume":     {"tr": "Devam Et",         "en": "Resume"},
    "panel_hand_lbl":   {"tr": "El:",              "en": "Hand:"},
    "panel_cal_lbl":    {"tr": "Kalibrasyon:",     "en": "Calibration:"},
    "panel_fps_lbl":    {"tr": "FPS:",             "en": "FPS:"},
    "panel_kb_lbl":     {"tr": "Klavye:",          "en": "Keyboard:"},
    "panel_cam_lbl":    {"tr": "Kamera:",          "en": "Camera:"},
    "panel_dwell_lbl":  {"tr": "Bekleme:",         "en": "Dwell:"},
    "panel_status_lbl": {"tr": "Durum:",           "en": "Status:"},
    "panel_hand_det_lbl":{"tr": "El Algilama:",    "en": "Hand Det.:"},

    # ── Modular panel etiketleri ─────────────────────────────────────────────
    "panel_detach":     {"tr": "Ayir",             "en": "Detach"},
    "panel_dock":       {"tr": "Yerlestir",        "en": "Dock"},
    "panel_restore":    {"tr": "Duzeni Sifirla",   "en": "Restore Layout"},
    "panel_cam_title":  {"tr": "Kamera Onizleme",  "en": "Camera Preview"},
    "panel_status_title":{"tr": "Sistem Durumu",   "en": "System Status"},
    "panel_gesture_title":{"tr": "Jest Izleme",    "en": "Gesture Monitor"},
    "panel_actions_title":{"tr": "Etkinlikler",    "en": "Activity"},
    "panel_notif_title":{"tr": "Bildirimler",      "en": "Notifications"},
    "panel_controls_title":{"tr": "Kontroller",    "en": "Controls"},
    "panel_dwell_delay":{"tr": "Jest Aktivasyon Gecikmesi","en": "Gesture Activation Delay"},
    "panel_dwell_time": {"tr": "Bekleme Suresi (Dwell Time)","en": "Dwell Time"},
    "panel_always_top": {"tr": "Her Zaman Ustte",  "en": "Always on Top"},
    "panel_detached_msg":{"tr": "Panel ayrildi",   "en": "Panel detached"},

    # ── Bildirim sistemi ─────────────────────────────────────────────────────
    "notify_dwell_changed":{"tr": "Bekleme suresi guncellendi","en": "Dwell time updated"},
    "notify_app_started":{"tr": "Uygulama baslatildi","en": "Application started"},
    "notify_cam_ok":    {"tr": "Kamera baglandi",  "en": "Camera connected"},
    "notify_hand_found":{"tr": "El algilandi",     "en": "Hand detected"},
    "notify_hand_lost": {"tr": "El algilanamadi",  "en": "Hand lost"},
    "hud_hand_yes":     {"tr": "ALGILANDI",        "en": "DETECTED"},
    "hud_hand_no":      {"tr": "YOK",              "en": "NONE"},
}


class Lang:
    def __init__(self, code: str = "tr"):
        self.code = code.lower().strip()
        if self.code not in ("tr", "en"):
            self.code = "tr"

    def t(self, key: str, **kwargs) -> str:
        entry = _S.get(key)
        if not entry:
            return key
        text = entry.get(self.code, entry.get("en", key))
        return text.format(**kwargs) if kwargs else text


_lang: Lang | None = None


def get() -> Lang:
    global _lang
    if _lang is None:
        _lang = Lang("tr")
    return _lang


def ask_and_init(cfg: Config) -> Lang:
    global _lang
    saved = cfg.get("language", "")
    if saved in ("tr", "en"):
        _lang = Lang(saved)
        return _lang
    print("\n" + "-" * 48)
    print("  KYVORA  -  Dil Secimi / Language")
    print("-" * 48)
    try:
        choice = input("  [TR/EN]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "tr"
    lang_obj = Lang(choice if choice in ("tr", "en") else "tr")
    if choice not in ("tr", "en"):
        print(lang_obj.t("lang_invalid"))
    cfg.set("language", lang_obj.code)
    _lang = lang_obj
    return _lang


def ask_cam_mode(lang_obj: "Lang") -> bool:
    """Her calistirmada sorar, config'e KAYDEDILMEZ."""
    print(lang_obj.t("cam_mode_question"), end="", flush=True)
    try:
        ans = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        ans = ""
    return ans in ("e", "evet", "y", "yes")
