"""
Cross-platform ses geri bildirimi.

Windows : winsound.Beep()
macOS   : afplay (sistem sesi)
Linux   : paplay → aplay → beep → terminal zili

BUG FIX: Popen() zombie process leak duzeltmesi.
  subprocess.Popen() ile baslatilan process'ler wait() edilmezse
  zombie process olarak hafizada kalir.
  Duzeltme: Popen() yerine subprocess.run() kullan.
  run() = Popen() + wait() + communicate() — leak yok.
"""
import platform
import threading
import subprocess

_OS = platform.system()
_ENABLED = True


def set_enabled(flag: bool) -> None:
    """Sesleri ac/kapat."""
    global _ENABLED
    _ENABLED = bool(flag)


def _bg(fn):
    """Ses fonksiyonunu arka planda calistir (ana loop'u bloklamaz)."""
    if not _ENABLED:
        return
    threading.Thread(target=fn, daemon=True).start()


# ── Public API ────────────────────────────────────────────────────────────────

def play_confirm() -> None:
    """Jest onaylandi."""
    _bg(_confirm)

def play_cancel() -> None:
    """Jest iptal / geri."""
    _bg(_cancel)

def play_start() -> None:
    """Program basladi."""
    _bg(_start)

def play_error() -> None:
    """Hata durumu."""
    _bg(_error)

def play_hold() -> None:
    """Basili tutma basladi."""
    _bg(_hold)

def play_release() -> None:
    """Basili tutma bitti."""
    _bg(_release)


# ── Platform implementasyonlari ───────────────────────────────────────────────

def _beep_win(freq: int, ms: int) -> None:
    try:
        import winsound
        winsound.Beep(max(37, min(32767, freq)), max(1, ms))
    except Exception:
        pass

def _beep_mac(sound: str = "Tink") -> None:
    path = f"/System/Library/Sounds/{sound}.aiff"
    try:
        # subprocess.run() = Popen + wait — zombie process yok
        subprocess.run(
            ["afplay", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
    except Exception:
        pass

def _beep_linux(freq: int = 880, ms: int = 100) -> None:
    cmds = [
        ["paplay", "/usr/share/sounds/freedesktop/stereo/button-pressed.oga"],
        ["aplay",  "/usr/share/sounds/alsa/Front_Center.wav"],
        ["beep",   "-f", str(freq), "-l", str(ms)],
    ]
    for cmd in cmds:
        try:
            # subprocess.run() — zombie leak yok
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
            )
            return
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    print("\a", end="", flush=True)   # terminal zili


# ── Ses fonksiyonlari ─────────────────────────────────────────────────────────

def _confirm():
    if _OS == "Windows":   _beep_win(880, 80)
    elif _OS == "Darwin":  _beep_mac("Tink")
    else:                  _beep_linux(880, 80)

def _cancel():
    if _OS == "Windows":   _beep_win(440, 60)
    elif _OS == "Darwin":  _beep_mac("Pop")
    else:                  _beep_linux(440, 60)

def _start():
    if _OS == "Windows":
        _beep_win(660, 80)
        threading.Event().wait(0.12)
        _beep_win(880, 120)
    elif _OS == "Darwin":  _beep_mac("Glass")
    else:
        _beep_linux(660, 80)
        threading.Event().wait(0.12)
        _beep_linux(880, 120)

def _error():
    if _OS == "Windows":   _beep_win(300, 200)
    elif _OS == "Darwin":  _beep_mac("Basso")
    else:                  _beep_linux(300, 200)

def _hold():
    """Basili tutma sesi - pinch'ten biraz farkli."""
    if _OS == "Windows":   _beep_win(660, 60)
    elif _OS == "Darwin":  _beep_mac("Pop")
    else:                  _beep_linux(660, 60)

def _release():
    """Birakma sesi."""
    if _OS == "Windows":   _beep_win(550, 60)
    elif _OS == "Darwin":  _beep_mac("Tink")
    else:                  _beep_linux(550, 60)
