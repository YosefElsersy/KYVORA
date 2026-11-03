"""
Dwell Controller — jesti N saniye tutunca aksiyon tetikler.

Scroll jesti için özel mod: dwell dolduktan sonra scroll aktif kalır,
jest devam ettiği sürece scroll çalışmaya devam eder (tek seferlik değil).
"""

import time

_NO_DWELL = frozenset({"none", "pointing"})


class DwellController:
    def __init__(self, dwell_sec: float = 1.5):
        self.dwell_sec  = dwell_sec
        self._gesture   = "none"
        self._start     = 0.0
        self._fired     = False

    def update(self, gesture: str, now: float | None = None) -> tuple[float, bool]:
        """
        (ilerleme 0.0-1.0, bu_frame_tetiklendi_mi) döndürür.
        - pointing/none için her zaman (0.0, False)
        - Scroll (four) için fired sadece ilk dolu anında True olur,
          ama progress 1.0'da kalmaya devam eder — sürekli scroll için
        """
        if now is None:
            now = time.perf_counter()

        # Jest değişti → sıfırla
        if gesture != self._gesture:
            self._gesture = gesture
            self._start   = now
            self._fired   = False

        if gesture in _NO_DWELL:
            return 0.0, False

        elapsed  = now - self._start
        progress = min(elapsed / self.dwell_sec, 1.0)

        if progress >= 1.0 and not self._fired:
            self._fired = True
            return 1.0, True  # İlk tetiklenme

        return progress, False

    def reset(self) -> None:
        self._gesture = "none"
        self._start   = 0.0
        self._fired   = False

    @property
    def is_ready(self) -> bool:
        """Dwell doldu mu? (progress >= 1.0)"""
        if self._gesture in _NO_DWELL:
            return False
        return time.perf_counter() - self._start >= self.dwell_sec
