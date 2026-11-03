"""
2D Kalman Filtresi - cursor titremesini matematiksel olarak giderir.

State vektoru: [x, y, vx, vy]
Gozlem:        [x, y]

Performans notu:
  np.linalg.inv() yerine np.linalg.solve() kullanilir.
  solve() numerik olarak daha stabil ve genellikle daha hizlidir.
"""
import numpy as np


class KalmanFilter2D:
    def __init__(self,
                 process_noise: float = 0.004,
                 measurement_noise: float = 0.08):
        dt = 1.0 / 30.0

        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0,  dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1],
        ], dtype=np.float64)

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ], dtype=np.float64)

        self.Q = np.eye(4, dtype=np.float64) * process_noise
        self.R = np.eye(2, dtype=np.float64) * measurement_noise

        self.x = np.zeros(4, dtype=np.float64)
        self.P = np.eye(4, dtype=np.float64) * 500.0
        self._init = False

    def update(self, mx: float, my: float) -> tuple[float, float]:
        if not self._init:
            self.x[:] = [mx, my, 0.0, 0.0]
            self._init = True
            return mx, my

        # Tahmin adimi
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

        # Guncelleme adimi
        z = np.array([mx, my], dtype=np.float64)
        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        # np.linalg.solve(S, H @ P.T) = inv(S) @ H @ P.T
        # Daha stabil ve inv()'dan daha hizli
        K = np.linalg.solve(S, self.H @ self.P).T
        self.x = self.x + K @ y
        self.P = (np.eye(4, dtype=np.float64) - K @ self.H) @ self.P

        return float(self.x[0]), float(self.x[1])

    def reset(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x[:] = [x, y, 0.0, 0.0]
        self.P = np.eye(4, dtype=np.float64) * 500.0
        self._init = bool(x or y)
