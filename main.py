"""
KYVORA — Gesture Control System

Thread architecture:
  Main thread  : tkinter UI  (UIManager.run() — blocks here)
  Camera thread: capture + hand tracking + gesture processing + mouse control

DirectShow fix (Windows):
  cv2.waitKey(1) is called every frame for message pump.
  A hidden 1×1 window handles this without visible OpenCV windows.
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
import time
import signal
import platform
import threading
import cv2
import pyautogui

from config import Config
cfg = Config()

import lang as _lang_mod
L = _lang_mod.ask_and_init(cfg)

from hand_tracker import HandTracker
from gesture      import (get_gesture, get_cursor_point,
                           get_scroll_ref, get_palm_center,
                           reset_pinch, set_pinch_threshold)
from mouse_ctrl   import MouseController
from vkeyboard    import VirtualKeyboard
from dwell        import DwellController
from calibration  import CalibrationWizard
from ui_manager   import UIManager
from tray         import SystemTray
import sound

# Config-based behaviors
set_pinch_threshold(cfg.get("pinch_threshold", 0.26))
sound.set_enabled(cfg.get("sound_enabled", True))

_OS       = platform.system()
_WIN_PUMP = "_kv_pump_"
_LOW_PERF = bool(cfg.get("low_perf", False))

_COLOR = {
    "pointing":  (100, 255, 100),
    "pinch":     (255, 220, 100),
    "thumbs_up": (255, 215,   0),
    "v_sign":    (100, 200, 255),
    "four":      (180, 120, 255),
    "three":     (255, 100, 200),
    "fist":      ( 80,  80, 255),
    "wolf":      (255, 180,  60),
    "open_palm": (  0, 220, 220),
    "none":      (120, 120, 120),
}


# ── Gesture stabilization ────────────────────────────────────────────────────

class GestureLock:
    """
    Stabilizes raw gesture stream.
    Confirmed after CONFIRM_N consecutive identical frames.
    Held for HOLD_N frames despite brief interruptions.
    """
    CONFIRM_N = 4
    HOLD_N    = 10

    def __init__(self):
        self.stable = "none"
        self._cand  = "none"
        self._cc    = 0
        self._hc    = 0

    def update(self, raw: str) -> str:
        if raw == self._cand:
            self._cc += 1
        else:
            self._cand = raw
            self._cc   = 1
        if self._cc >= self.CONFIRM_N:
            if raw != self.stable:
                self.stable = raw
                self._hc    = 0
        elif self.stable != "none" and self.stable != raw:
            self._hc += 1
            if self._hc >= self.HOLD_N:
                self.stable = "none"
                self._hc    = 0
        else:
            self._hc = 0
        return self.stable

    def reset(self) -> None:
        self.stable = "none"
        self._cand  = "none"
        self._cc    = 0
        self._hc    = 0
        reset_pinch()

    @property
    def lock_progress(self) -> float:
        return min(self._cc / self.CONFIRM_N, 1.0)


# ── Frame overlay (drawn directly on the camera frame) ───────────────────────

def _draw_frame_overlay(frame, stable: str, glock: GestureLock,
                        progress: float, landmarks,
                        scroll_active: bool, hold_active: bool,
                        paused: bool = False) -> None:
    """
    Draw overlays that belong ON the camera image:
    - Lock confirmation bar (thin bar at top)
    - Dwell ring on fingertip
    - Pointing cursor dot
    - Holding indicator text
    - PAUSED overlay
    """
    h, w = frame.shape[:2]
    col  = _COLOR.get(stable, (200, 200, 200))

    # Lock progress bar (thin 3px bar at top of frame)
    lp = glock.lock_progress
    cv2.rectangle(frame, (0, 0), (w, 3), (25, 25, 45), -1)
    cv2.rectangle(frame, (0, 0), (int(w * lp), 3), col, -1)

    # PAUSED overlay — semi-transparent banner
    if paused:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h // 2 - 30), (w, h // 2 + 30),
                      (10, 10, 30), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        pause_txt = "PAUSED"
        ts, _ = cv2.getTextSize(pause_txt, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
        tx = (w - ts[0]) // 2
        cv2.putText(frame, pause_txt, (tx, h // 2 + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 220, 220), 3,
                    cv2.LINE_AA)
        # Show resume hint
        hint = "Open Palm to Resume"
        hs, _ = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        hx = (w - hs[0]) // 2
        cv2.putText(frame, hint, (hx, h // 2 + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 180, 180), 1,
                    cv2.LINE_AA)
        return  # Don't draw other overlays when paused

    # Dwell ring — on fingertip
    if stable not in ("none", "pointing") and landmarks and progress > 0:
        cx, cy = get_cursor_point(landmarks)
        ring_r = 30
        cv2.circle(frame, (cx, cy), ring_r, (35, 35, 55), 3)
        angle = int(progress * 360)
        if angle > 0:
            ring_col = (60, 220, 60) if progress >= 1.0 else col
            cv2.ellipse(frame, (cx, cy), (ring_r, ring_r),
                        -90, 0, angle, ring_col, 3, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), 5, col, -1)
        if progress < 1.0:
            sn = cfg.get("dwell_sec", 1.5)
            cv2.putText(frame, f"{sn*(1-progress):.1f}s",
                        (cx - 16, cy + 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50, col, 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, L.t("hud_ready"), (cx - 22, cy + 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.56, (60, 220, 60), 2,
                        cv2.LINE_AA)

    elif stable == "pointing" and landmarks:
        cx, cy = get_cursor_point(landmarks)
        cv2.circle(frame, (cx, cy), 9, col, -1)
        cv2.circle(frame, (cx, cy), 16, col, 1)

    # Thumbs-up hold indicator (center of frame)
    if hold_active:
        hold_txt = L.t("hud_holding_indicator")
        tw, _ = cv2.getTextSize(hold_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 2)
        cx_txt = (w - tw[0]) // 2
        cv2.rectangle(frame, (cx_txt - 8, h // 2 - 26),
                       (cx_txt + tw[0] + 8, h // 2 + 8),
                       (40, 40, 0), -1)
        cv2.putText(frame, hold_txt, (cx_txt, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 215, 0), 2,
                    cv2.LINE_AA)


# ── Camera Thread ─────────────────────────────────────────────────────────────

def camera_loop(cap, tracker, mouse, keyboard, dwell, glock,
                calib, state, ui, stop_event):
    _scroll_dz  = 8
    _scroll_spd = cfg.get("scroll_speed", 2)
    _max_drops  = cfg.get("max_drops", 30)

    dropped       = 0
    fps_t         = time.perf_counter()
    fps_val       = 0.0
    fc            = 0
    results       = None
    landmarks     = None
    prev_stable   = "none"
    scroll_ref    = None
    scroll_active = False
    hold_active   = False

    # ── Pause/Resume state machine ───────────────────────────────────────────
    _PAUSE_COOLDOWN   = 2.0    # seconds after toggle before next toggle allowed
    _PAUSE_DWELL      = 1.0    # seconds open palm must be held to trigger
    _paused           = False
    _pause_dwell_t    = 0.0    # when open_palm dwell started
    _pause_dwelling   = False  # currently accumulating open_palm dwell
    _pause_last_toggle= 0.0    # timestamp of last toggle (cooldown)
    _pause_need_neutral = False  # must leave open_palm before next toggle

    # ── Hidden pump window (DirectShow message pump on Windows) ──────────────
    if _OS == "Windows":
        cv2.namedWindow(_WIN_PUMP, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(_WIN_PUMP, 1, 1)
        try:
            import ctypes
            user32 = ctypes.WinDLL("user32")
            hwnd   = user32.FindWindowA(None, _WIN_PUMP.encode())
            if hwnd:
                user32.SetWindowPos(hwnd, 0, -10, -10, 1, 1, 0x0040)
        except Exception:
            pass

    while not stop_event.is_set():

        # ── DirectShow message pump ──────────────────────────────────────────
        cv2.waitKey(1)

        ret, frame = cap.read()
        if not ret:
            dropped += 1
            if dropped >= _max_drops:
                print(L.t("cam_lost"))
                stop_event.set()
                ui.request_quit()
                break
            time.sleep(0.02)
            continue
        dropped = 0
        frame = cv2.flip(frame, 1)

        # Read state
        with state["lock"]:
            need_cal   = state["do_calib"]
            left_hand  = state["left_hand"]
            cam_top    = state["cam_top"]
            calibrated = state["calibrated"]
            kb_on      = state["kb_visible"]

        # ── Calibration ──────────────────────────────────────────────────────
        if need_cal and not calib.active:
            calib.start()
            glock.reset()
            with state["lock"]:
                state["do_calib"] = False

        if calib.active:
            try:
                results   = tracker.process(frame)
                landmarks = tracker.get_landmarks(results, frame.shape)
            except Exception:
                results = landmarks = None
            done = calib.update(frame, landmarks)
            if done:
                mouse.set_calibration(
                    cfg.get("cal_x_min"), cfg.get("cal_x_max"),
                    cfg.get("cal_y_min"), cfg.get("cal_y_max"),
                )
                set_pinch_threshold(cfg.get("pinch_threshold", 0.26))
                with state["lock"]:
                    state["calibrated"] = True
                sound.play_confirm()
            # Send calibration frame to embedded preview
            ui.update_frame(frame)
            fc += 1
            continue

        # ── Normal gesture detection ─────────────────────────────────────────
        try:
            results   = tracker.process(frame)
            landmarks = tracker.get_landmarks(results, frame.shape)
        except Exception as e:
            print(f"[!] {L.t('warn_frame')}: {e}")
            results = landmarks = None

        raw    = get_gesture(landmarks, left_hand)
        stable = glock.update(raw)

        now = time.perf_counter()
        progress, fired = dwell.update(stable, now)

        # ── Pause/Resume via open_palm gesture ────────────────────────────────
        # Check if paused was toggled externally via GUI button
        with state["lock"]:
            if state.get("_pause_toggled", False):
                _paused = state["paused"]
                state["_pause_toggled"] = False
                _pause_last_toggle = now
                _pause_need_neutral = True
                _pause_dwelling = False
                if _paused:
                    # Entering pause: release held inputs
                    if hold_active:
                        mouse.mouse_up()
                        hold_active = False
                    mouse.release_all()
                    scroll_ref = None
                    scroll_active = False

        if stable == "open_palm":
            # Cooldown check
            if now - _pause_last_toggle >= _PAUSE_COOLDOWN and not _pause_need_neutral:
                if not _pause_dwelling:
                    _pause_dwelling = True
                    _pause_dwell_t = now
                elif now - _pause_dwell_t >= _PAUSE_DWELL:
                    # Toggle!
                    _paused = not _paused
                    _pause_last_toggle = now
                    _pause_need_neutral = True
                    _pause_dwelling = False
                    with state["lock"]:
                        state["paused"] = _paused
                    if _paused:
                        # Release all held inputs
                        if hold_active:
                            mouse.mouse_up()
                            hold_active = False
                        mouse.release_all()
                        scroll_ref = None
                        scroll_active = False
                        sound.play_confirm()
                        ui.show_notify("paused")
                        print(f"[+] {L.t('action_paused')}")
                    else:
                        glock.reset()
                        sound.play_confirm()
                        ui.show_notify("resumed")
                        print(f"[+] {L.t('action_resumed')}")
            else:
                _pause_dwelling = False
        else:
            _pause_dwelling = False
            # Left open_palm → neutral achieved
            if _pause_need_neutral:
                _pause_need_neutral = False

        # ── Gesture change cleanup & actions (only when ACTIVE) ─────────────────
        if not _paused:

            if stable != prev_stable:
                # Release hold when leaving thumbs_up
                if prev_stable == "thumbs_up" and hold_active:
                    mouse.mouse_up()
                    hold_active = False
                    sound.play_release()
                    ui.show_notify("thumbs_up_release")
                    print(f"[+] {L.t('action_hold_end')}")
                # Reset scroll state
                if stable != "four":
                    scroll_ref    = None
                    scroll_active = False
                prev_stable = stable

            # ── Actions ──────────────────────────────────────────────────────

            # [1] Cursor movement — no dwell, instant
            if stable == "pointing" and landmarks:
                try:
                    mouse.move(*get_cursor_point(landmarks))
                except pyautogui.FailSafeException:
                    print(f"\n{L.t('failsafe')}")
                    stop_event.set(); ui.request_quit(); break

            # [4] Scroll — continuous after dwell completes
            elif stable == "four" and landmarks:
                if progress >= 1.0:
                    scroll_active = True
                    wy = get_scroll_ref(landmarks)[1]
                    if scroll_ref is None:
                        scroll_ref = wy
                        if fired:
                            sound.play_confirm()
                    else:
                        delta = scroll_ref - wy
                        if abs(delta) > _scroll_dz:
                            try:
                                mouse.scroll(
                                    (1 if delta > 0 else -1) * _scroll_spd)
                            except pyautogui.FailSafeException:
                                print(f"\n{L.t('failsafe')}")
                                stop_event.set(); ui.request_quit(); break
                            scroll_ref += delta * 0.3

            elif scroll_active:
                scroll_active = False
                scroll_ref    = None

            # [8] Thumbs Up — hold left click + drag
            elif stable == "thumbs_up" and landmarks:
                if fired and not hold_active:
                    mouse.mouse_down()
                    hold_active = True
                    sound.play_hold()
                    ui.show_notify("thumbs_up_hold")
                    print(f"[+] {L.t('action_hold_start')}")
                elif hold_active:
                    px, py = get_palm_center(landmarks)
                    try:
                        mouse.move(px, py)
                    except pyautogui.FailSafeException:
                        print(f"\n{L.t('failsafe')}")
                        mouse.mouse_up()
                        hold_active = False
                        stop_event.set(); ui.request_quit(); break

            # Single-fire gestures — only on fired=True
            elif fired:
                if stable == "pinch":
                    try:
                        mouse.left_click()
                    except pyautogui.FailSafeException:
                        print(f"\n{L.t('failsafe')}")
                        stop_event.set(); ui.request_quit(); break
                    sound.play_confirm()
                    ui.show_notify("pinch")
                    print(f"[+] {L.t('action_lclick')}")

                elif stable == "v_sign":
                    try:
                        mouse.right_click()
                    except pyautogui.FailSafeException:
                        print(f"\n{L.t('failsafe')}")
                        stop_event.set(); ui.request_quit(); break
                    sound.play_confirm()
                    ui.show_notify("v_sign")
                    print(f"[+] {L.t('action_rclick')}")

                elif stable == "three":
                    keyboard.toggle()
                    sound.play_confirm()
                    ui.show_notify("three")
                    with state["lock"]:
                        state["kb_visible"] = keyboard.visible
                    print(f"[+] {L.t('action_keyboard')}")

                elif stable == "wolf":
                    pyautogui.hotkey("alt", "tab")
                    sound.play_confirm()
                    ui.show_notify("wolf")
                    print(f"[+] {L.t('action_alttab')}")

                elif stable == "fist":
                    with state["lock"]:
                        state["cam_top"] = not state["cam_top"]
                        ct = state["cam_top"]
                    sound.play_confirm()
                    ui.show_notify("fist")
                    lbl = L.t("action_cam_top") if ct else L.t("action_cam_back")
                    print(f"[+] {lbl}")

        else:
            # PAUSED — still track prev_stable for display only
            prev_stable = stable

        # ── Update gesture state in UI ────────────────────────────────────────
        ui.update_gesture(
            stable, progress,
            scroll_active=scroll_active,
            hold_active=hold_active,
        )

        # ── FPS + state update ────────────────────────────────────────────────
        fc += 1
        if fc % 15 == 0:
            e = now - fps_t
            if e > 0:
                fps_val = 15.0 / e
                with state["lock"]:
                    state["fps"] = fps_val
                    state["hand_detected"] = landmarks is not None
            fps_t = now
            with state["lock"]:
                s = {k: v for k, v in state.items()
                     if k not in ("lock", "do_calib", "_pause_toggled")}
            ui.update_state(s)

        # ── Draw overlays on frame and send to embedded preview ───────────────
        if results is not None:
            tracker.draw(frame, results)
        _draw_frame_overlay(frame, stable, glock, progress,
                            landmarks, scroll_active, hold_active,
                            paused=_paused)
        ui.update_frame(frame)

    # Thread cleanup
    mouse.release_all()
    cv2.destroyAllWindows()
    print("[Camera] Thread stopped.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 54)
    print(f"  KYVORA  —  {L.t('startup_title')}")
    print("=" * 54)
    print(f"  {L.t('startup_os')}: {_OS}   Python: {sys.version.split()[0]}")
    print(f"  {L.t('startup_dwell')}: {cfg.get('dwell_sec')}s   "
          f"{L.t('startup_hand')}: {cfg.get('dominant_hand')}")
    cal_str = (L.t("startup_cal_ok") if cfg.get("calibrated")
               else L.t("startup_cal_no"))
    print(f"  {L.t('startup_cal')}: {cal_str}")
    print("=" * 54)
    print(f"  {L.t('startup_failsafe')}\n")

    print(L.t("cam_opening"))
    cap = cv2.VideoCapture(
        cfg.get("cam_index", 0),
        cv2.CAP_DSHOW if _OS == "Windows" else cv2.CAP_ANY,
    )
    if not cap.isOpened():
        print(L.t("cam_error"))
        sys.exit(1)

    fw = 320 if _LOW_PERF else cfg.get("frame_w", 640)
    fh = 240 if _LOW_PERF else cfg.get("frame_h", 480)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  fw)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, fh)
    cap.set(cv2.CAP_PROP_FPS,          30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)
    print(L.t("cam_ready") + "\n")

    margin = cfg.get("margin", 60)

    tracker  = HandTracker(low_perf=_LOW_PERF)
    mouse    = MouseController(
        fw, fh,
        margin            = margin,
        process_noise     = cfg.get("kalman_process_noise",     0.004),
        measurement_noise = cfg.get("kalman_measurement_noise", 0.08),
    )
    keyboard = VirtualKeyboard()
    dwell    = DwellController(dwell_sec=cfg.get("dwell_sec", 1.5))
    glock    = GestureLock()
    calib    = CalibrationWizard(cfg)

    if cfg.get("calibrated"):
        mouse.set_calibration(
            cfg.get("cal_x_min"), cfg.get("cal_x_max"),
            cfg.get("cal_y_min"), cfg.get("cal_y_max"),
        )

    state = {
        "lock":       threading.Lock(),
        "left_hand":  cfg.get("dominant_hand") == "left",
        "calibrated": cfg.get("calibrated", False),
        "fps":        0.0,
        "kb_visible": False,
        "cam_top":    False,
        "dwell_sec":  cfg.get("dwell_sec", 1.5),
        "do_calib":   False,
        "paused":     False,
        "_pause_toggled": False,
        "hand_detected": False,
    }

    stop_event = threading.Event()
    ui         = UIManager(cfg=cfg)

    def _do_calibrate() -> None:
        with state["lock"]:
            state["do_calib"] = True

    def _do_toggle_hand() -> None:
        with state["lock"]:
            state["left_hand"] = not state["left_hand"]
            lh = state["left_hand"]
        cfg.set("dominant_hand", "left" if lh else "right")
        glock.reset()
        print(f"[+] {L.t('hand_changed')}: "
              f"{L.t('hand_left') if lh else L.t('hand_right')}")

    def _do_quit() -> None:
        stop_event.set()
        ui.stop()

    def _do_toggle_pause() -> None:
        with state["lock"]:
            state["paused"] = not state["paused"]
            state["_pause_toggled"] = True
            p = state["paused"]
        if p:
            mouse.release_all()
            sound.play_confirm()
            ui.show_notify("paused")
            print(f"[+] {L.t('action_paused')}")
        else:
            glock.reset()
            sound.play_confirm()
            ui.show_notify("resumed")
            print(f"[+] {L.t('action_resumed')}")

    def _do_dwell_change(val: float) -> None:
        val = max(0.3, min(3.0, val))
        dwell.dwell_sec = val
        with state["lock"]:
            state["dwell_sec"] = val
        cfg.set("dwell_sec", val)

    ui.on_calibrate    = _do_calibrate
    ui.on_toggle_hand  = _do_toggle_hand
    ui.on_quit         = _do_quit
    ui.on_toggle_pause = _do_toggle_pause
    ui.on_dwell_change = _do_dwell_change

    def _sig(s, _):
        print(f"\n{L.t('shutting_down')}")
        _do_quit()
    signal.signal(signal.SIGINT, _sig)

    tray = SystemTray(
        on_toggle_cam = lambda: None,
        on_calibrate  = _do_calibrate,
        on_quit       = _do_quit,
    )
    tray.start()

    cam_thread = threading.Thread(
        target = camera_loop,
        args   = (cap, tracker, mouse, keyboard, dwell,
                  glock, calib, state, ui, stop_event),
        daemon = True,
        name   = "KYVORA-Camera",
    )
    cam_thread.start()

    sound.play_start()
    print(L.t("started_cam"))

    try:
        ui.run()
    except pyautogui.FailSafeException:
        print(f"\n{L.t('failsafe')}")
    except Exception as e:
        print(f"\n[{L.t('error')}] {e}")
        import traceback
        traceback.print_exc()
    finally:
        stop_event.set()
        cam_thread.join(timeout=5)
        if cam_thread.is_alive():
            print("[Warning] Camera thread still alive after timeout")
        tray.stop()
        keyboard.hide()
        mouse.release_all()     # Release any held buttons
        tracker.close()         # MediaPipe cleanup
        cap.release()
        cv2.destroyAllWindows()
        print(L.t("closed"))


if __name__ == "__main__":
    main()
