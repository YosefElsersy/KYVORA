"""
VirtualKeyboard — OS built-in on-screen keyboard launcher.
Windows: osk.exe | macOS: AppleScript | Linux: onboard/florence/xvkbd
"""
import subprocess, platform, threading
import lang as _lang_mod

_OS = platform.system()

class VirtualKeyboard:
    def __init__(self):
        self._visible = False
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @property
    def visible(self) -> bool: return self._visible

    def toggle(self):
        with self._lock:
            self._close() if self._visible else self._open()

    def show(self):
        with self._lock:
            if not self._visible: self._open()

    def hide(self):
        with self._lock:
            if self._visible: self._close()

    def _open(self):
        L = _lang_mod.get()
        try:
            if _OS == "Windows":
                import os; os.startfile("osk.exe"); self._proc = None
            elif _OS == "Darwin":
                subprocess.run(["osascript", "-e",
                    'tell application "System Events" to key code 32 '
                    'using {command down, option down}'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
                self._proc = None
            elif _OS == "Linux":
                self._proc = self._linux_open()
                if self._proc is None: return
            self._visible = True
            print(L.t("kb_opened"))
        except FileNotFoundError as e: print(f"{L.t('kb_not_found')} {e}")
        except subprocess.TimeoutExpired: print(L.t("kb_timeout"))
        except Exception as e: print(f"{L.t('kb_error_open')} {e}")

    def _close(self):
        L = _lang_mod.get()
        try:
            if _OS == "Windows":
                self._visible = False; return
            elif _OS == "Darwin":
                subprocess.run(["osascript", "-e",
                    'tell application "System Events" to key code 32 '
                    'using {command down, option down}'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            elif _OS == "Linux":
                if self._proc:
                    self._proc.terminate()
                    try: self._proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self._proc.kill(); self._proc.wait()
        except Exception as e: print(f"{L.t('kb_error_close')} {e}")
        finally:
            self._proc = None; self._visible = False
            print(L.t("kb_closed"))

    def _linux_open(self):
        L = _lang_mod.get()
        for cmd in (["onboard"],["florence"],["xvkbd"],["cellwriter"]):
            try:
                p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"{L.t('kb_using')} {cmd[0]}"); return p
            except FileNotFoundError: continue
        print(L.t("kb_linux_none")); print(L.t("kb_linux_install"))
        return None
