"""
KYVORA - Language Module (AR / EN)
Arabic (RTL) and English (LTR) localization.
"""

import sys

# Ensure UTF-8 console output for Arabic text on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import Config

_S: dict[str, dict[str, str]] = {
    # ── Language / Startup ────────────────────────────────────────────────────
    "lang_prompt":      {"ar": "اختر اللغة / Select language  [AR/EN]: ",
                         "en": "اختر اللغة / Select language  [AR/EN]: "},
    "lang_invalid":     {"ar": "اختيار غير صالح - يتم استخدام العربية.",
                         "en": "Invalid choice - using English."},

    "cam_mode_question":{"ar": "\nهل تريد إظهار الكاميرا على الشاشة؟\n"
                               "  [Y] نعم - نافذة الكاميرا مرئية\n"
                               "  [N] لا  - الكاميرا تعمل في الخلفية\n"
                               "اختيارك [Y/N]: ",
                         "en": "\nShow camera on screen?\n"
                               "  [Y] Yes - camera window visible\n"
                               "  [N] No  - camera runs in background\n"
                               "Your choice [Y/N]: "},

    # ── System startup ────────────────────────────────────────────────────────
    "startup_title":    {"ar": "نظام التحكم بالإيماءات",
                         "en": "Gesture Control System"},
    "startup_os":       {"ar": "النظام",            "en": "System"},
    "startup_dwell":    {"ar": "مدة الانتظار",       "en": "Dwell time"},
    "startup_hand":     {"ar": "اليد المفضلة",       "en": "Dominant hand"},
    "startup_cal":      {"ar": "المعايرة",           "en": "Calibration"},
    "startup_cal_ok":   {"ar": "تمت",               "en": "Done"},
    "startup_cal_no":   {"ar": "لم تتم بعد",         "en": "Not done yet"},
    "startup_failsafe": {"ar": "أمان: حرّك الماوس إلى الزاوية العلوية اليسرى -> يتوقف البرنامج",
                         "en": "SAFETY: Move mouse to TOP-LEFT corner -> program stops"},

    # ── Camera ────────────────────────────────────────────────────────────────
    "cam_opening":      {"ar": "جاري فتح الكاميرا، يرجى الانتظار...",
                         "en": "Opening camera, please wait..."},
    "cam_ready":        {"ar": "الكاميرا جاهزة.",    "en": "Camera ready."},
    "cam_error":        {"ar": "[خطأ] تعذر فتح الكاميرا. تحقق من فهرس الكاميرا.",
                         "en": "[ERROR] Could not open camera. Check camera index."},
    "cam_lost":         {"ar": "[خطأ] انقطع اتصال الكاميرا.",
                         "en": "[ERROR] Camera connection lost."},

    # ── Start / Shutdown ─────────────────────────────────────────────────────
    "started_cam":      {"ar": "تم التشغيل — استخدم لوحة التحكم للخروج.",
                         "en": "Started — Use control panel to quit."},
    "started_headless": {"ar": "تم التشغيل (خلفي) — استخدم لوحة التحكم للخروج.",
                         "en": "Started (background) — Use control panel to quit."},
    "shutting_down":    {"ar": "جاري الإغلاق...",    "en": "Shutting down..."},
    "closed":           {"ar": "تم إغلاق البرنامج.", "en": "Program closed."},
    "failsafe":         {"ar": "تم تفعيل الأمان — البرنامج متوقف.",
                         "en": "Safety triggered — program stopped."},
    "error":            {"ar": "خطأ غير متوقع",     "en": "Unexpected error"},
    "warn_frame":       {"ar": "خطأ في معالجة الإطار","en": "Frame processing error"},

    # ── Hand switching ────────────────────────────────────────────────────────
    "hand_changed":     {"ar": "تم تبديل اليد",     "en": "Hand switched"},
    "hand_left":        {"ar": "اليد اليسرى",       "en": "Left hand"},
    "hand_right":       {"ar": "اليد اليمنى",       "en": "Right hand"},

    # ── Actions (terminal) ───────────────────────────────────────────────────
    "action_lclick":    {"ar": "نقر أيسر",          "en": "Left click"},
    "action_rclick":    {"ar": "نقر أيمن",          "en": "Right click"},
    "action_keyboard":  {"ar": "تبديل لوحة المفاتيح","en": "Keyboard toggle"},
    "action_cam_top":   {"ar": "الكاميرا: في المقدمة","en": "Camera: In front"},
    "action_cam_back":  {"ar": "الكاميرا: في الخلفية","en": "Camera: Moved back"},
    "action_alttab":    {"ar": "تم تنفيذ Alt+Tab",  "en": "Alt+Tab performed"},
    "action_hold_start":{"ar": "الزر الأيسر مضغوط باستمرار","en": "Left button HELD DOWN"},
    "action_hold_end":  {"ar": "تم تحرير الزر الأيسر", "en": "Left button RELEASED"},
    "action_paused":    {"ar": "تم إيقاف التحكم بالإيماءات مؤقتاً", "en": "Gesture control PAUSED"},
    "action_resumed":   {"ar": "تم استئناف التحكم بالإيماءات", "en": "Gesture control RESUMED"},

    # ── HUD - Gesture labels ─────────────────────────────────────────────────
    "hud_none":         {"ar": "لم يتم اكتشاف يد",  "en": "NO HAND DETECTED"},
    "hud_unknown":      {"ar": "إيماءة غير معروفة",  "en": "UNKNOWN GESTURE"},
    "hud_move":         {"ar": "[1] تحريك المؤشر",   "en": "[1] CURSOR MOVE"},
    "hud_lclick":       {"ar": "[2] نقر أيسر",      "en": "[2] LEFT CLICK"},
    "hud_rclick":       {"ar": "[3] نقر أيمن",      "en": "[3] RIGHT CLICK"},
    "hud_scroll":       {"ar": "[4] التمرير",        "en": "[4] SCROLL"},
    "hud_keyboard":     {"ar": "[5] لوحة المفاتيح",  "en": "[5] KEYBOARD"},
    "hud_cam":          {"ar": "[6] الكاميرا",       "en": "[6] CAMERA"},
    "hud_wolf":         {"ar": "[7] تبديل النافذة",  "en": "[7] SWITCH WINDOW"},
    "hud_hold":         {"ar": "[8] الضغط المستمر",  "en": "[8] HOLD CLICK"},
    "hud_hold_active":  {"ar": "[8] جاري الضغط...",  "en": "[8] HOLDING..."},
    "hud_open_palm":    {"ar": "[9] إيقاف/استئناف",  "en": "[9] PAUSE/RESUME"},
    "hud_paused":       {"ar": "متوقف مؤقتاً",      "en": "PAUSED"},
    "hud_active":       {"ar": "نشط",               "en": "ACTIVE"},
    "hud_holding_indicator": {"ar": "الزر الأيسر مضغوط","en": "LEFT BTN HELD"},
    "hud_tip_thumbsup": {"ar": "إبهام لأعلى — انتظر حتى تمتلئ الحلقة للضغط المستمر",
                         "en": "Thumbs up — hold until ring fills to press & hold left click"},
    "hud_tip_holding":  {"ar": "الزر الأيسر مضغوط — غيّر الإيماءة للتحرير",
                         "en": "Left button held — change gesture to release"},

    # ── HUD - Status and tip messages ─────────────────────────────────────────
    "hud_tip_none":     {"ar": "أظهر يدك أمام الكاميرا",
                         "en": "Show your hand to the camera"},
    "hud_tip_pointing": {"ar": "حرّك إصبعك للتحكم بالمؤشر",
                         "en": "Move your finger to control cursor"},
    "hud_tip_pinch":    {"ar": "قرّب الإبهام والسبابة معاً",
                         "en": "Bring thumb + index together"},
    "hud_tip_vsign":    {"ar": "اعمل علامة V وانتظر",
                         "en": "Hold V sign to right-click"},
    "hud_tip_scroll":   {"ar": "4 أصابع — حرّك اليد للأعلى/الأسفل",
                         "en": "4 fingers — move hand up/down"},
    "hud_tip_three":    {"ar": "ارفع 3 أصابع وانتظر",
                         "en": "Hold 3 fingers to toggle keyboard"},
    "hud_tip_fist":     {"ar": "اقبض يدك وانتظر",
                         "en": "Hold fist to toggle camera"},
    "hud_tip_wolf":     {"ar": "اعمل وضعية الذئب وانتظر",
                         "en": "Hold wolf pose to switch window"},
    "hud_tip_open_palm":{"ar": "افتح الكف للإيقاف المؤقت أو الاستئناف",
                         "en": "Open palm to pause or resume gesture control"},
    "hud_tip_paused":   {"ar": "التحكم بالإيماءات متوقف — افتح الكف أو اضغط الزر للاستئناف",
                         "en": "Gesture control paused — open palm or press button to resume"},
    "hud_tip_dwell":    {"ar": "حافظ على الإيماءة...",
                         "en": "Hold the gesture..."},
    "hud_tip_ready":    {"ar": "تم التعرف على الإيماءة!",
                         "en": "Gesture recognized!"},
    "hud_scroll_active":{"ar": "التمرير نشط — حرّك اليد للأعلى/الأسفل",
                         "en": "SCROLLING — move hand up/down"},
    "hud_ready":        {"ar": "تم!",               "en": "DONE!"},
    "hud_hold_sec":     {"ar": "ث",                 "en": "s"},
    "hud_how_to":       {"ar": "كيفية الاستخدام؟",   "en": "How To Use?"},
    "hud_kb_on":        {"ar": "لوحة:مفعّل",        "en": "KB:ON"},
    "hud_kb_off":       {"ar": "لوحة:معطّل",        "en": "KB:OFF"},
    "hud_cam_front":    {"ar": "كاميرا:أمام",       "en": "CAM:FRONT"},
    "hud_cam_top":      {"ar": "كاميرا:أمام",       "en": "CAM:FRONT"},
    "hud_cam_back":     {"ar": "كاميرا:خلف",        "en": "CAM:BACK"},
    "hud_cal_ok":       {"ar": "معايرة:تمت",        "en": "CAL:OK"},
    "hud_cal_no":       {"ar": "معايرة:مفقودة",     "en": "CAL:MISSING"},

    # ── Calibration ──────────────────────────────────────────────────────────
    "cal_started":      {"ar": "بدأت المعايرة.",
                         "en": "Calibration started."},
    "cal_cancelled":    {"ar": "تم إلغاء المعايرة.",
                         "en": "Calibration cancelled."},
    "cal_done":         {"ar": "اكتملت المعايرة! تم حفظ الإعدادات.",
                         "en": "Calibration complete! Settings saved."},
    "cal_step1_title":  {"ar": "الخطوة 1/2 - قياس اليد",
                         "en": "STEP 1/2 - HAND MEASUREMENT"},
    "cal_step1_inst":   {"ar": "افتح كفك وأبقِه في المنتصف.",
                         "en": "Open your palm and hold it in the center."},
    "cal_step2_title":  {"ar": "الخطوة 2/2 - الزاوية {n}/4",
                         "en": "STEP 2/2 - CORNER {n}/4"},
    "cal_step2_inst":   {"ar": "وجّه إصبع السبابة إلى زاوية {label} وانتظر.",
                         "en": "Point index finger to the {label} corner and hold."},
    "cal_done_title":   {"ar": "اكتملت المعايرة",
                         "en": "CALIBRATION COMPLETE"},
    "cal_done_inst":    {"ar": "تم حفظ جميع الإعدادات بنجاح.",
                         "en": "All settings saved successfully."},
    "cal_done_sub":     {"ar": "جاري استئناف الوضع الطبيعي...",
                         "en": "Resuming normal mode..."},
    "cal_cancel_hint":  {"ar": "ESC = إلغاء المعايرة",
                         "en": "ESC = Cancel calibration"},
    "cal_corner_ul":    {"ar": "أعلى اليسار",       "en": "TOP LEFT"},
    "cal_corner_ur":    {"ar": "أعلى اليمين",       "en": "TOP RIGHT"},
    "cal_corner_lr":    {"ar": "أسفل اليمين",       "en": "BOTTOM RIGHT"},
    "cal_corner_ll":    {"ar": "أسفل اليسار",       "en": "BOTTOM LEFT"},
    "cal_measure":      {"ar": "جاري القياس",       "en": "Measuring"},

    # ── System tray ──────────────────────────────────────────────────────────
    "tray_started":     {"ar": "شريط النظام جاهز.",
                         "en": "System tray ready."},
    "tray_no_lib":      {"ar": "لم يتم العثور على pystray — شريط النظام معطّل.\n"
                               "للتثبيت: pip install pystray Pillow",
                         "en": "pystray not found — tray disabled.\n"
                               "Install with: pip install pystray Pillow"},
    "tray_toggle_cam":  {"ar": "إظهار / إخفاء الكاميرا",
                         "en": "Show / Hide Camera"},
    "tray_calibrate":   {"ar": "تشغيل المعايرة",    "en": "Run Calibration"},
    "tray_quit":        {"ar": "إغلاق البرنامج",    "en": "Quit Program"},

    # ── Notifications ────────────────────────────────────────────────────────
    "notify_lclick":    {"ar": "نقر أيسر",          "en": "LEFT CLICK"},
    "notify_rclick":    {"ar": "نقر أيمن",          "en": "RIGHT CLICK"},
    "notify_scroll":    {"ar": "تمرير",             "en": "SCROLL"},
    "notify_keyboard":  {"ar": "لوحة المفاتيح",     "en": "KEYBOARD"},
    "notify_cam":       {"ar": "الكاميرا",          "en": "CAMERA"},
    "notify_wolf":      {"ar": "ALT+TAB",           "en": "ALT+TAB"},
    "notify_hold":      {"ar": "ضغط مستمر",         "en": "HOLDING"},
    "notify_release":   {"ar": "تم التحرير",        "en": "RELEASED"},
    "notify_paused":    {"ar": "متوقف مؤقتاً",      "en": "PAUSED"},
    "notify_resumed":   {"ar": "تم الاستئناف",      "en": "RESUMED"},

    # ── On-screen keyboard ───────────────────────────────────────────────────
    "kb_opened":        {"ar": "تم فتح لوحة المفاتيح على الشاشة.",
                         "en": "On-screen keyboard opened."},
    "kb_closed":        {"ar": "تم إغلاق لوحة المفاتيح على الشاشة.",
                         "en": "On-screen keyboard closed."},
    "kb_not_found":     {"ar": "لم يتم العثور على تطبيق لوحة المفاتيح:",
                         "en": "Keyboard application not found:"},
    "kb_timeout":       {"ar": "انتهت مهلة فتح لوحة المفاتيح.",
                         "en": "Keyboard open timed out."},
    "kb_error_open":    {"ar": "خطأ في فتح لوحة المفاتيح:",
                         "en": "Error opening keyboard:"},
    "kb_error_close":   {"ar": "خطأ في إغلاق لوحة المفاتيح:",
                         "en": "Error closing keyboard:"},
    "kb_linux_none":    {"ar": "لم يتم العثور على لوحة مفاتيح على الشاشة في Linux.",
                         "en": "No on-screen keyboard found on Linux."},
    "kb_linux_install": {"ar": "للتثبيت: sudo apt install onboard",
                         "en": "Install with: sudo apt install onboard"},
    "kb_using":         {"ar": "يتم استخدام:",       "en": "Using:"},

    # ── Control panel button labels ──────────────────────────────────────────
    "panel_calibrate":  {"ar": "تشغيل المعايرة",    "en": "Run Calibration"},
    "panel_hand":       {"ar": "تبديل اليد",        "en": "Switch Hand"},
    "panel_how_to":     {"ar": "كيفية الاستخدام؟",   "en": "How To Use?"},
    "panel_quit":       {"ar": "إغلاق البرنامج",    "en": "Quit Program"},
    "panel_pause":      {"ar": "إيقاف مؤقت",        "en": "Pause"},
    "panel_resume":     {"ar": "استئناف",            "en": "Resume"},
    "panel_hand_lbl":   {"ar": "اليد:",             "en": "Hand:"},
    "panel_cal_lbl":    {"ar": "المعايرة:",          "en": "Calibration:"},
    "panel_fps_lbl":    {"ar": "FPS:",              "en": "FPS:"},
    "panel_kb_lbl":     {"ar": "لوحة المفاتيح:",     "en": "Keyboard:"},
    "panel_cam_lbl":    {"ar": "الكاميرا:",          "en": "Camera:"},
    "panel_dwell_lbl":  {"ar": "الانتظار:",          "en": "Dwell:"},
    "panel_status_lbl": {"ar": "الحالة:",            "en": "Status:"},
    "panel_hand_det_lbl":{"ar": "اكتشاف اليد:",     "en": "Hand Det.:"},

    # ── Modular panel labels ─────────────────────────────────────────────────
    "panel_detach":     {"ar": "فصل",               "en": "Detach"},
    "panel_dock":       {"ar": "إرساء",             "en": "Dock"},
    "panel_restore":    {"ar": "استعادة التخطيط",    "en": "Restore Layout"},
    "panel_cam_title":  {"ar": "معاينة الكاميرا",    "en": "Camera Preview"},
    "panel_status_title":{"ar": "حالة النظام",      "en": "System Status"},
    "panel_gesture_title":{"ar": "مراقب الإيماءات", "en": "Gesture Monitor"},
    "panel_actions_title":{"ar": "سجل الأنشطة",    "en": "Activity"},
    "panel_notif_title":{"ar": "الإشعارات",         "en": "Notifications"},
    "panel_controls_title":{"ar": "أدوات التحكم",   "en": "Controls"},
    "panel_dwell_delay":{"ar": "تأخير تنشيط الإيماءة","en": "Gesture Activation Delay"},
    "panel_dwell_time": {"ar": "مدة الانتظار (Dwell Time)","en": "Dwell Time"},
    "panel_always_top": {"ar": "دائماً في المقدمة",  "en": "Always on Top"},
    "panel_detached_msg":{"ar": "تم فصل اللوحة",    "en": "Panel detached"},

    # ── Notification system ──────────────────────────────────────────────────
    "notify_dwell_changed":{"ar": "تم تحديث مدة الانتظار","en": "Dwell time updated"},
    "notify_app_started":{"ar": "تم تشغيل التطبيق", "en": "Application started"},
    "notify_cam_ok":    {"ar": "تم توصيل الكاميرا",  "en": "Camera connected"},
    "notify_hand_found":{"ar": "تم اكتشاف اليد",    "en": "Hand detected"},
    "notify_hand_lost": {"ar": "فُقدت اليد",        "en": "Hand lost"},
    "hud_hand_yes":     {"ar": "مكتشفة",            "en": "DETECTED"},
    "hud_hand_no":      {"ar": "غير موجودة",        "en": "NONE"},

    # ── Help dialog ──────────────────────────────────────────────────────────
    "help_title":       {"ar": "كيفية الاستخدام؟",   "en": "HOW TO USE?"},
    "help_close":       {"ar": "إغلاق",             "en": "Close"},
    "help_dwell_title": {"ar": "نظام الانتظار (DWELL)",       "en": "DWELL SYSTEM"},
    "help_dwell_desc":  {"ar": "جميع الإيماءات عدا التأشير تستخدم نظام الانتظار.\n"
                               "قم بالإيماءة وانتظر حتى تمتلئ الحلقة — عندها يتم تنفيذ الأمر.\n"
                               "يمكنك ضبط مدة الانتظار من شريط التمرير في لوحة التحكم.",
                         "en": "All gestures except pointing use the dwell system.\n"
                               "Hold the gesture until the ring fills — action fires then.\n"
                               "Adjust the dwell time with the slider in the Controls panel."},

    # Help items [1]-[9] — Arabic
    "help_1_action":    {"ar": "المؤشر",             "en": "CURSOR"},
    "help_1_pose":      {"ar": "إصبع السبابة",       "en": "Index Finger"},
    "help_1_desc":      {"ar": "ارفع إصبع السبابة فقط، وأغلق بقية الأصابع.\n"
                               "يحرّك الماوس مباشرة — بدون انتظار.",
                         "en": "Only index finger raised, others closed.\n"
                               "Moves mouse directly — no dwell needed."},

    "help_2_action":    {"ar": "نقر أيسر",           "en": "L-CLICK"},
    "help_2_pose":      {"ar": "القرص (Pinch)",      "en": "Pinch"},
    "help_2_desc":      {"ar": "قرّب طرف الإبهام من طرف السبابة.\n"
                               "عند امتلاء الحلقة: نقرة يسرى.",
                         "en": "Bring thumb tip and index fingertip together.\n"
                               "When ring fills: left click."},

    "help_3_action":    {"ar": "نقر أيمن",           "en": "R-CLICK"},
    "help_3_pose":      {"ar": "علامة V",            "en": "V Sign"},
    "help_3_desc":      {"ar": "ارفع السبابة والوسطى، وأغلق البنصر والخنصر.\n"
                               "عند امتلاء الحلقة: نقرة يمنى.",
                         "en": "Index and middle up, ring and pinky closed.\n"
                               "When ring fills: right click."},

    "help_4_action":    {"ar": "التمرير",            "en": "SCROLL"},
    "help_4_pose":      {"ar": "4 أصابع",           "en": "4 Fingers"},
    "help_4_desc":      {"ar": "ارفع السبابة والوسطى والبنصر والخنصر — الإبهام مغلق.\n"
                               "عند الجاهزية: حرّك اليد للأعلى/الأسفل للتمرير.",
                         "en": "Index, middle, ring, pinky up — thumb closed.\n"
                               "When ready: move hand up/down to scroll."},

    "help_5_action":    {"ar": "لوحة المفاتيح",      "en": "KEYBOARD"},
    "help_5_pose":      {"ar": "3 أصابع",           "en": "3 Fingers"},
    "help_5_desc":      {"ar": "ارفع السبابة والوسطى والبنصر — الخنصر والإبهام مغلقان.\n"
                               "عند امتلاء الحلقة: تبديل لوحة المفاتيح على الشاشة.",
                         "en": "Index, middle, ring up — pinky and thumb closed.\n"
                               "When ring fills: toggles on-screen keyboard."},

    "help_6_action":    {"ar": "النافذة",            "en": "WINDOW"},
    "help_6_pose":      {"ar": "قبضة اليد",         "en": "Fist"},
    "help_6_desc":      {"ar": "أغلق جميع الأصابع بقبضة محكمة.\n"
                               "عند امتلاء الحلقة: تبديل النافذة بين المقدمة والخلفية.",
                         "en": "All fingers closed, tight fist.\n"
                               "When ring fills: toggles window always-on-top."},

    "help_7_action":    {"ar": "ALT+TAB",            "en": "ALT+TAB"},
    "help_7_pose":      {"ar": "الذئب",              "en": "Wolf"},
    "help_7_desc":      {"ar": "الوسطى والبنصر يلمسان الإبهام،\n"
                               "السبابة والخنصر مرفوعان.\n"
                               "عند امتلاء الحلقة: تبديل النوافذ.",
                         "en": "Middle and ring touch thumb,\n"
                               "index and pinky raised straight up.\n"
                               "When ring fills: switches windows."},

    "help_8_action":    {"ar": "الضغط المستمر",      "en": "HOLD CLICK"},
    "help_8_pose":      {"ar": "إبهام لأعلى",       "en": "Thumbs Up"},
    "help_8_desc":      {"ar": "اقبض يدك ثم ارفع الإبهام فقط.\n"
                               "عند امتلاء الحلقة: يبقى الزر الأيسر مضغوطاً.\n"
                               "حرّك يدك للسحب. غيّر الإيماءة للتحرير.",
                         "en": "Close all fingers into a fist, then raise only\n"
                               "your thumb. When ring fills: left button held.\n"
                               "Move your hand to drag. Change gesture to release."},

    "help_9_action":    {"ar": "إيقاف / استئناف",    "en": "PAUSE / RESUME"},
    "help_9_pose":      {"ar": "كف مفتوح",          "en": "Open Palm"},
    "help_9_desc":      {"ar": "افتح جميع الأصابع الخمسة.\n"
                               "انتظر ثانية واحدة — يتوقف التحكم بالإيماءات مؤقتاً.\n"
                               "كرر نفس الإيماءة للاستئناف.\n"
                               "بعد الإيقاف أو الاستئناف، أعد يدك إلى وضع\n"
                               "محايد (مثلاً اقبض يدك أو ابعدها عن الكاميرا)\n"
                               "قبل تكرار إيماءة الكف المفتوح.\n"
                               "الإبقاء على الإيماءة لن يكرر التبديل.\n"
                               "يمكنك أيضاً استخدام زر إيقاف/استئناف.",
                         "en": "Show all five fingers open.\n"
                               "Hold for 1 second — gesture control pauses.\n"
                               "Repeat the same gesture to resume.\n"
                               "After activating Pause or Resume, return your\n"
                               "hand to a neutral position (e.g. close fist or\n"
                               "leave the camera) before performing the Open\n"
                               "Palm gesture again. Holding the gesture\n"
                               "continuously will not repeatedly toggle.\n"
                               "You can also use the Pause/Resume button."},
    # ── Language selection & switching ───────────────────────────────────────
    "notify_lang_changed":{"ar": "تم تغيير اللغة إلى العربية", "en": "Language changed to English"},
    "panel_language":   {"ar": "اللغة",             "en": "Language"},
    "lang_en":          {"ar": "English",           "en": "English"},
    "lang_ar":          {"ar": "العربية",           "en": "العربية"},
}


class Lang:
    def __init__(self, code: str = "en"):
        self.set_code(code)

    def set_code(self, code: str) -> None:
        code = code.lower().strip()
        if code not in ("ar", "en"):
            code = "en"
        self.code = code

    def t(self, key: str, **kwargs) -> str:
        entry = _S.get(key)
        if not entry:
            return key
        text = entry.get(self.code, entry.get("en", key))
        return text.format(**kwargs) if kwargs else text

    @property
    def is_rtl(self) -> bool:
        """Return True if the current language is right-to-left."""
        return self.code == "ar"


_lang: Lang | None = None


def get() -> Lang:
    global _lang
    if _lang is None:
        _lang = Lang("en")
    return _lang


def init(cfg: Config) -> Lang:
    """Initialize language without prompting; defaults to English on fresh run."""
    global _lang
    saved = cfg.get("language", "")
    # Migrate old Turkish config ("tr") or invalid setting to English
    if saved == "tr" or saved not in ("ar", "en"):
        saved = "en"
        cfg.set("language", "en")
    if _lang is None:
        _lang = Lang(saved)
    else:
        _lang.set_code(saved)
    return _lang


def ask_and_init(cfg: Config) -> Lang:
    """Alias for init(); launches directly in default language without prompting."""
    return init(cfg)


def set_lang(code: str, cfg: Config | None = None) -> Lang:
    """Switch language at runtime and optionally persist to configuration."""
    global _lang
    if _lang is None:
        _lang = Lang(code)
    else:
        _lang.set_code(code)
    if cfg:
        cfg.set("language", _lang.code)
    return _lang


def ask_cam_mode(lang_obj: "Lang") -> bool:
    """Ask every run, NOT saved to config."""
    print(lang_obj.t("cam_mode_question"), end="", flush=True)
    try:
        ans = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        ans = ""
    return ans in ("y", "yes", "n3m", "نعم")
