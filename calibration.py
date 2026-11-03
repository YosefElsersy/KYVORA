"""
Kalibrasyon sihirbazi - dil destekli.

Kose titreme duzeltmesi:
  Eski: hold suresi dolunca o anki tek frame koordinatini al → el titrediyse yanlis nokta
  Yeni: hold suresi boyunca her frame ornekle → medyan al → cok daha stabil
"""
import time, cv2
import numpy as np
import lang as _lang_mod

_BG    = (18,  18,  30)
_GREEN = (60,  220, 100)
_AMBER = (60,  180, 255)
_WHITE = (220, 220, 220)
_DIM   = (80,  80,  80)
_RED   = (60,  60,  220)


class CalibrationWizard:
    HOLD_SEC = 2.5   # Her kosede bekleme suresi (arttirildi - daha stabil)
    PALM_SEC = 3.0   # Avuc olcumu suresi

    def __init__(self, config):
        self.cfg    = config
        self.active = False
        self._step  = 0
        self._palm_samples: list[float] = []
        self._corner_idx  = 0
        self._corner_pts:  list[tuple[int,int]] = []
        self._hold_start  = 0.0
        self._palm_start  = 0.0
        # FIX: Her kose icin birikim ornekleri (medyan icin)
        self._corner_samples_x: list[int] = []
        self._corner_samples_y: list[int] = []

    def start(self) -> None:
        L = _lang_mod.get()
        self.active = True
        self._step  = 0
        self._palm_samples.clear()
        self._corner_idx = 0
        self._corner_pts.clear()
        self._hold_start = 0.0
        self._palm_start = time.perf_counter()
        self._corner_samples_x.clear()
        self._corner_samples_y.clear()
        print(L.t("cal_started"))

    def stop(self) -> None:
        L = _lang_mod.get()
        self.active = False
        print(L.t("cal_cancelled"))

    def update(self, frame, landmarks) -> bool:
        if not self.active:
            return False
        now  = time.perf_counter()
        h, w = frame.shape[:2]
        if self._step == 0:
            return self._palm(frame, landmarks, now, h, w)
        elif self._step == 1:
            return self._corners(frame, landmarks, now, h, w)
        return False

    # ── Adim 1: Avuc olcumu ───────────────────────────────────────────────────

    def _palm(self, frame, lm, now, h, w) -> bool:
        L = _lang_mod.get()
        n = len(self._palm_samples)
        self._overlay(frame, w, h,
            L.t("cal_step1_title"),
            L.t("cal_step1_inst"),
            f"{L.t('cal_measure')}: {n}/30")

        if lm:
            from hand_tracker import HandTracker as HT
            import math
            palm = math.hypot(
                lm[HT.MIDDLE_MCP][0] - lm[HT.WRIST][0],
                lm[HT.MIDDLE_MCP][1] - lm[HT.WRIST][1]
            )
            self._palm_samples.append(palm)
            for pt in lm:
                cv2.circle(frame, pt, 3, _GREEN, -1)

        elapsed = now - self._palm_start
        ratio   = min(elapsed / self.PALM_SEC, 1.0)
        bx, by, bw, bh = w // 4, h - 60, w // 2, 12
        cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (40,40,60), -1)
        cv2.rectangle(frame, (bx, by), (bx+int(bw*ratio), by+bh), _GREEN, -1)

        if elapsed >= self.PALM_SEC and n >= 10:
            avg = float(np.median(self._palm_samples))
            thr = max(0.22, min(0.36, 0.28 * (80 / max(avg, 1))))
            self.cfg.set("pinch_threshold", round(thr, 3))
            self._step       = 1
            self._corner_idx = 0
            self._hold_start = now
            self._corner_samples_x.clear()
            self._corner_samples_y.clear()
        return False

    # ── Adim 2: 4 kose tespiti ────────────────────────────────────────────────

    def _corners(self, frame, lm, now, h, w) -> bool:
        if self._corner_idx >= 4:
            return self._finish(frame, w, h)

        L = _lang_mod.get()
        labels  = [L.t("cal_corner_ul"), L.t("cal_corner_ur"),
                   L.t("cal_corner_lr"), L.t("cal_corner_ll")]
        targets = [(0.15, 0.15), (0.85, 0.15), (0.85, 0.85), (0.15, 0.85)]

        label = labels[self._corner_idx]
        tx    = int(targets[self._corner_idx][0] * w)
        ty    = int(targets[self._corner_idx][1] * h)

        self._overlay(frame, w, h,
            L.t("cal_step2_title", n=self._corner_idx+1),
            L.t("cal_step2_inst", label=label))

        # Hedef daire
        cv2.circle(frame, (tx, ty), 36, (50, 50, 80), -1)   # arka dolgu
        cv2.circle(frame, (tx, ty), 36, _RED, 2)
        cv2.circle(frame, (tx, ty), 5,  _RED, -1)
        cv2.putText(frame, label, (tx - 35, ty - 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, _AMBER, 1, cv2.LINE_AA)

        # Ornek sayisi goster
        n_samples = len(self._corner_samples_x)
        if n_samples > 0:
            cv2.putText(frame, f"{n_samples}",
                        (tx - 6, ty + 44),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, _DIM, 1, cv2.LINE_AA)

        if lm:
            from hand_tracker import HandTracker as HT
            fx, fy = lm[HT.INDEX_TIP]

            # Parmak ucunu goster
            cv2.circle(frame, (fx, fy), 10, _GREEN, -1)
            cv2.circle(frame, (fx, fy), 16, _GREEN, 2)

            dist = ((fx - tx)**2 + (fy - ty)**2) ** 0.5

            if dist < 50:   # Hedef yakininda
                held  = now - self._hold_start
                ratio = min(held / self.HOLD_SEC, 1.0)

                # Dolan halka
                cv2.ellipse(frame, (tx, ty), (36, 36),
                            -90, 0, int(ratio * 360), _GREEN, 3)

                # FIX: Hold suresi boyunca her frame ornekle
                self._corner_samples_x.append(fx)
                self._corner_samples_y.append(fy)

                # Geri sayim
                remaining = max(0.0, self.HOLD_SEC - held)
                cv2.putText(frame, f"{remaining:.1f}",
                            (tx - 10, ty + 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.50, _GREEN, 1, cv2.LINE_AA)

                if ratio >= 1.0:
                    # FIX: Tek frame degil, tum orneklerin medyani al
                    stable_x = int(np.median(self._corner_samples_x))
                    stable_y = int(np.median(self._corner_samples_y))
                    self._corner_pts.append((stable_x, stable_y))

                    print(f"  Kose {self._corner_idx+1}: ({stable_x}, {stable_y}) "
                          f"[{len(self._corner_samples_x)} ornek]")

                    self._corner_idx += 1
                    self._hold_start  = now
                    # Bir sonraki kose icin ornek listesini sifirla
                    self._corner_samples_x.clear()
                    self._corner_samples_y.clear()

            else:
                # Uzakta → timer ve ornekleri sifirla
                self._hold_start = now
                self._corner_samples_x.clear()
                self._corner_samples_y.clear()

        return False

    # ── Bitis ─────────────────────────────────────────────────────────────────

    def _finish(self, frame, w, h) -> bool:
        L  = _lang_mod.get()
        xs = [p[0] for p in self._corner_pts]
        ys = [p[1] for p in self._corner_pts]

        # 10px marj ekle, ekran sinirlarina clip yap
        x_min = max(0, min(xs) - 10)
        x_max = min(w, max(xs) + 10)
        y_min = max(0, min(ys) - 10)
        y_max = min(h, max(ys) + 10)

        self.cfg.update({
            "calibrated": True,
            "cal_x_min":  x_min,
            "cal_x_max":  x_max,
            "cal_y_min":  y_min,
            "cal_y_max":  y_max,
        })
        self.active = False
        print(L.t("cal_done"))
        print(f"  Alan: x[{x_min}-{x_max}]  y[{y_min}-{y_max}]")

        self._overlay(frame, w, h,
            L.t("cal_done_title"),
            L.t("cal_done_inst"),
            L.t("cal_done_sub"))
        return True

    # ── Overlay yardimcisi ────────────────────────────────────────────────────

    def _overlay(self, frame, w, h, title, instruction, sub="") -> None:
        L = _lang_mod.get()
        # Arka plan
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Baslik
        cv2.rectangle(frame, (0, 0), (w, 68), _BG, -1)
        cv2.putText(frame, title, (12, 44),
                    cv2.FONT_HERSHEY_DUPLEX, 0.88, _AMBER, 2, cv2.LINE_AA)

        # Talimat
        cv2.putText(frame, instruction, (12, h // 2 - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.60, _WHITE, 1, cv2.LINE_AA)
        if sub:
            cv2.putText(frame, sub, (12, h // 2 + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, _DIM, 1, cv2.LINE_AA)

        # Iptal ipucu
        cv2.putText(frame, L.t("cal_cancel_hint"), (w - 120, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, _DIM, 1, cv2.LINE_AA)
