"""
MouseController - Kalman filtreli cursor kontrolu.
pyautogui.FAILSAFE = True korunur (sol ust kose = dur).

Basili tutma ozelligi eklendi:
  mouse_down() / mouse_up() / is_held
"""

import pyautogui
from kalman import KalmanFilter2D

pyautogui.PAUSE = 0   # Her hareket sonrasi bekleme yok


class MouseController:
    def __init__(self,
                 cam_w: int, cam_h: int,
                 margin: int = 60,
                 process_noise: float = 0.004,
                 measurement_noise: float = 0.08):

        if cam_w <= 0 or cam_h <= 0:
            raise ValueError(f"Invalid camera size: {cam_w}x{cam_h}")

        max_m = min(cam_w, cam_h) // 2 - 1
        self.margin = max(0, min(margin, max_m))
        self.cam_w  = cam_w
        self.cam_h  = cam_h

        self.scr_w, self.scr_h = pyautogui.size()

        self._kf = KalmanFilter2D(process_noise, measurement_noise)
        self._kf.reset(self.scr_w / 2, self.scr_h / 2)

        m = self.margin
        self.cal_x_min = float(m)
        self.cal_x_max = float(cam_w - m)
        self.cal_y_min = float(m)
        self.cal_y_max = float(cam_h - m)
        self._recalc()

        self._held = False   # Sol tus basili tutuluyor mu?

    def _recalc(self) -> None:
        self._aw = max(1.0, self.cal_x_max - self.cal_x_min)
        self._ah = max(1.0, self.cal_y_max - self.cal_y_min)

    def set_calibration(self, x_min, x_max, y_min, y_max) -> None:
        self.cal_x_min = float(x_min)
        self.cal_x_max = float(x_max)
        self.cal_y_min = float(y_min)
        self.cal_y_max = float(y_max)
        self._recalc()

    @property
    def is_held(self) -> bool:
        """Sol tus su an basili mi?"""
        return self._held

    def move(self, cam_x: int, cam_y: int) -> None:
        cx = max(self.cal_x_min, min(self.cal_x_max, float(cam_x)))
        cy = max(self.cal_y_min, min(self.cal_y_max, float(cam_y)))

        tx = ((cx - self.cal_x_min) / self._aw) * self.scr_w
        ty = ((cy - self.cal_y_min) / self._ah) * self.scr_h

        fx, fy = self._kf.update(tx, ty)
        sx = int(max(0, min(self.scr_w - 1, fx)))
        sy = int(max(0, min(self.scr_h - 1, fy)))
        pyautogui.moveTo(sx, sy)

    def left_click(self) -> None:
        """Tek tik. Eger tus basili tutuluyorsa once birak."""
        if self._held:
            self.mouse_up()
        pyautogui.click()

    def right_click(self) -> None:
        pyautogui.rightClick()

    def double_click(self) -> None:
        pyautogui.doubleClick()

    def scroll(self, d: int) -> None:
        pyautogui.scroll(d)

    def mouse_down(self) -> None:
        """Sol tusu basili tut (surukle baslatir)."""
        if not self._held:
            pyautogui.mouseDown(button="left")
            self._held = True

    def mouse_up(self) -> None:
        """Basili tutulan sol tusu birak."""
        if self._held:
            pyautogui.mouseUp(button="left")
            self._held = False

    def release_all(self) -> None:
        """Guvenlik: program kapanirken tum tuslari birak."""
        self.mouse_up()
