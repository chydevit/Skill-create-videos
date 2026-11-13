"""Characters: Milo, Luna, Bobo and the farm animals, plus procedural animation.

Every character is built from the same code in every scene so it always looks
identical. Animation is computed per frame as numpy arrays (see bl_util.Anim).
"""
import math

import numpy as np

import bl_util as U
from bl_util import mat, sphere, cyl, empty, obj, window, smooth

PI = math.pi

SKIN_MILO = "#F5C6A0"
SKIN_LUNA = "#EDB892"
EYE_WHITE = "#FFFFFF"
MOUTH = "#8E1B2C"
TONGUE = "#F06292"

KID_CFG = {
    "milo": dict(skin=SKIN_MILO, hair="#7A4524", shirt="#FF7043",
                 pants="#1E88E5", shoes="#43A047", pupil="#4E342E",
                 girl=False, cheek="#FF8A80"),
    "luna": dict(skin=SKIN_LUNA, hair="#2E1A14", shirt="#AB47BC",
                 pants="#AB47BC", shoes="#EC407A", pupil="#3E2723",
                 girl=True, cheek="#FF80AB", bow="#FFD54F"),
}


def eye(name, parent, loc, side, r, pupil_col, rot_z, lashes=False):
    e = empty(name, loc, parent, rot=(0, 0, rot_z))
    sphere(name + "_w", (0, 0, 0), (r, r * 0.55, r * 1.15), mat(EYE_WHITE, 0.25), e)
    sphere(name + "_p", (0, -r * 0.42, -r * 0.05), (r * 0.64, r * 0.36, r * 0.75),
           mat(pupil_col, 0.2), e)
    sphere(name + "_h", (r * 0.22, -r * 0.72, r * 0.3), r * 0.2,
           U.flat("#FFFFFF"), e, seg=12)
    if lashes:
        for k, (dx, a) in enumerate(((0.55, 0.5), (0.85, 0.9))):
            cyl(name + "_l%d" % k, (side * r * dx, -r * 0.2, r * 0.95), 0.008, 0.045,
                mat("#1B1B1B"), e, rot=(0, side * a, 0), seg=8)
    return e


# ====================================================================== KID
class Kid:
    def __init__(self, name, home=(0, 0), rz=0.0):
        c = KID_CFG[name]
        self.name = name
        self.kind = "kid"
        self.home = home
        self.base_rz = rz
        skin = mat(c["skin"], 0.5)
        shirt = mat(c["shirt"], 0.7)
        pants = mat(c["pants"], 0.7)
        shoes = mat(c["shoes"], 0.35, coat=0.3)
        hair = mat(c["hair"], 0.45)
        white = mat("#FAFAFA", 0.6)
        n = name
        self.root = empty(n + "_root", (home[0], home[1], 0), rot=(0, 0, rz))
        self.hop = empty(n + "_hop", (0, 0, 0), self.root)
        pel = self.pelvis = empty(n + "_pelvis", (0, 0, 0.5), self.hop)
        # legs
        self.hips = {}
        for s in (-1, 1):
            h = empty(n + "_hip%d" % s, (s * 0.085, 0, 0), pel)
            self.hips[s] = h
            cyl(n + "_leg%d" % s, (0, 0, -0.42), 0.052, 0.42, skin, h)
            cyl(n + "_sock%d" % s, (0, 0, -0.43), 0.056, 0.09, white, h)
            sphere(n + "_shoe%d" % s, (0, -0.035, -0.445), (0.075, 0.115, 0.058), shoes, h)
            if not c["girl"]:
                cyl(n + "_short%d" % s, (0, 0, -0.17), (0.075, 0.075), 0.18, pants, h,
                    r2=0.085)
        if c["girl"]:
            cyl(n + "_dress", (0, 0, -0.2), 0.3, 0.46, shirt, pel, r2=0.47, seg=32)
            cyl(n + "_hem", (0, 0, -0.205), 0.305, 0.03, white, pel, seg=32)
        else:
            sphere(n + "_shorts", (0, 0, 0.0), (0.19, 0.15, 0.13), pants, pel)
        sp = self.spine = empty(n + "_spine", (0, 0, 0.04), pel)
        sphere(n + "_torso", (0, 0, 0.19), (0.19, 0.155, 0.24), shirt, sp)
        if not c["girl"]:
            # a yellow star on Milo's shirt
            obj(n + "_logo", U.mesh_star(5, 1, 0.45, 0.4), (0, -0.152, 0.2),
                0.055, (0.12, 0, 0), mat("#FFEB3B", 0.4), sp)
        else:
            for s_ in (-1, 1):
                sphere(n + "_button%d" % s_, (0, -0.15, 0.13 + 0.09 * s_), 0.022,
                       mat(c["bow"], 0.4), sp)
        # arms
        self.sh = {}
        for s in (-1, 1):
            a = empty(n + "_sh%d" % s, (s * 0.19, 0, 0.35), sp)
            self.sh[s] = a
            sphere(n + "_sleeve%d" % s, (0, 0, -0.04), (0.075, 0.075, 0.09), shirt, a)
            cyl(n + "_arm%d" % s, (0, 0, -0.36), 0.043, 0.33, skin, a)
            sphere(n + "_hand%d" % s, (0, 0, -0.39), 0.06, skin, a)
        # head
        nk = self.neck = empty(n + "_neck", (0, 0, 0.42), sp)
        cyl(n + "_neckc", (0, 0, -0.02), 0.055, 0.12, skin, nk)
        hd = self.head = empty(n + "_head", (0, 0, 0.3), nk)
        sphere(n + "_skull", (0, 0, 0), (0.3, 0.285, 0.29), skin, hd, seg=48)
        for s in (-1, 1):
            sphere(n + "_ear%d" % s, (s * 0.295, 0.01, -0.01), (0.035, 0.05, 0.065), skin, hd)
            sphere(n + "_cheek%d" % s, (s * 0.165, -0.235, -0.075), (0.055, 0.02, 0.034),
                   mat(c["cheek"], 0.6), hd)
        sphere(n + "_nose", (0, -0.29, -0.03), (0.032, 0.03, 0.028), skin, hd)
        self.eyes = {}
        self.brows = {}
        for s in (-1, 1):
            self.eyes[s] = eye(n + "_eye%d" % s, hd, (s * 0.1, -0.248, 0.04), s, 0.068,
                               c["pupil"], s * 0.33, lashes=c["girl"])
            b = empty(n + "_brow%d" % s, (s * 0.1, -0.262, 0.145), hd, rot=(0, 0, s * 0.3))
            cyl(n + "_browc%d" % s, (-0.045, 0, 0), 0.013, 0.09, mat(c["hair"], 0.6), b,
                rot=(0, PI / 2, 0), seg=10)
            self.brows[s] = b
        mo = self.mouth = empty(n + "_mouth", (0, -0.272, -0.1), hd)
        self.smile = obj(n + "_smile", U.mesh_torus(0.055, 0.012, 20, 8, PI, PI),
                         (0, 0, 0), 1, (0, 0, 0), mat(MOUTH, 0.4), mo)
        self.mopen = empty(n + "_mopen", (0, 0.004, -0.03), mo)
        sphere(n + "_mo", (0, 0, 0), (0.05, 0.022, 0.042), mat(MOUTH, 0.4), self.mopen)
        sphere(n + "_tongue", (0, -0.008, -0.022), (0.03, 0.012, 0.014),
               mat(TONGUE, 0.4), self.mopen)
        self.mopen.scale = (1, 1, 0.05)
        # hair
        sphere(n + "_hair", (0, 0.035, 0.075), (0.318, 0.315, 0.295), hair, hd, seg=48)
        if not c["girl"]:
            for k, (x, y, z, rx, ry) in enumerate(((0.02, -0.19, 0.24, -0.9, 0.2),
                                                   (0.12, -0.14, 0.25, -0.8, 0.6),
                                                   (-0.1, -0.16, 0.25, -0.8, -0.5),
                                                   (0.0, 0.0, 0.34, -0.3, 0.1))):
                sphere(n + "_tuft%d" % k, (x, y, z), (0.07, 0.05, 0.11), hair, hd,
                       rot=(rx, ry, 0))
        else:
            sphere(n + "_backhair", (0, 0.1, -0.12), (0.3, 0.2, 0.3), hair, hd)
            for s in (-1, 1):
                pt = empty(n + "_tail%d" % s, (s * 0.3, 0.06, 0.02), hd)
                sphere(n + "_pig%d" % s, (s * 0.05, 0.02, -0.14), (0.085, 0.085, 0.15),
                       hair, pt)
                bow = mat(c["bow"], 0.4, coat=0.2)
                sphere(n + "_bowa%d" % s, (s * 0.03, -0.06, 0.1), (0.05, 0.035, 0.085),
                       bow, pt, rot=(0, 1.0, 0))
                sphere(n + "_bowb%d" % s, (s * 0.03, -0.06, 0.1), (0.05, 0.035, 0.085),
                       bow, pt, rot=(0, -1.0, 0))
                sphere(n + "_bowc%d" % s, (s * 0.03, -0.095, 0.1), 0.032, bow, pt)

    # ------------------------------------------------------------ animation
    def init_pose(self, A):
        nf = A.nf
        P = {}
        z = np.zeros(nf)
        for k in ["hop_z", "spine_rx", "spine_ry", "spine_rz", "neck_rx", "neck_ry",
                  "neck_rz", "brow_z", "smile_ry", "walkw", "hipP", "hipN"]:
            P[k] = z.copy()
        P["root_x"] = np.full(nf, float(self.home[0]))
        P["root_y"] = np.full(nf, float(self.home[1]))
        P["root_rz"] = np.full(nf, float(self.base_rz))
        P["squash"] = np.ones(nf)
        for s in (-1, 1):
            P["sh%d_rx" % s] = z.copy()
            P["sh%d_ry" % s] = np.full(nf, -s * 0.13)
            P["sh%d_rz" % s] = z.copy()
            P["brow%d" % s] = z.copy()
        P["eye_sz"] = np.ones(nf)
        P["eye_s"] = np.ones(nf)
        P["mouth"] = np.full(nf, 0.05)
        P["mouth_sx"] = np.ones(nf)
        P["smile_s"] = np.ones(nf)
        self.P = P
        return P

    def write(self, A):
        P = self.P
        A.set(self.root, "location", 0, P["root_x"])
        A.set(self.root, "location", 1, P["root_y"])
        A.set(self.root, "rotation_euler", 2, P["root_rz"])
        A.set(self.hop, "location", 2, P["hop_z"])
        A.set(self.hop, "scale", 2, P["squash"])
        A.set(self.hop, "scale", 0, 1 / np.sqrt(P["squash"]))
        A.set(self.hop, "scale", 1, 1 / np.sqrt(P["squash"]))
        for i, ax in enumerate("xyz"):
            A.set(self.spine, "rotation_euler", i, P["spine_r" + ax])
            A.set(self.neck, "rotation_euler", i, P["neck_r" + ax])
        for s in (-1, 1):
            for i, ax in enumerate("xyz"):
                A.set(self.sh[s], "rotation_euler", i, P["sh%d_r%s" % (s, ax)])
            A.set(self.hips[s], "rotation_euler", 0, P["hipP" if s > 0 else "hipN"])
            e = self.eyes[s]
            A.set(e, "scale", 0, P["eye_s"])
            A.set(e, "scale", 1, P["eye_s"])
            A.set(e, "scale", 2, P["eye_s"] * P["eye_sz"])
            A.set(self.brows[s], "rotation_euler", 1, P["brow%d" % s])
            A.set(self.brows[s], "location", 2, 0.145 + P["brow_z"])
        A.set(self.mopen, "scale", 2, P["mouth"])
        A.set(self.mopen, "scale", 0, P["mouth_sx"])
        A.set(self.smile, "rotation_euler", 1, P["smile_ry"])
        for i in range(3):
            A.set(self.smile, "scale", i, P["smile_s"])


# ===================================================================== BOBO
class Bobo:
    def __init__(self, home=(0, 0, 1.3)):
        self.name = "bobo"
        self.kind = "bird"
        self.home = home
        n = "bobo"
        blue = mat("#29B6F6", 0.45)
        dark = mat("#0288D1", 0.5)
        belly = mat("#E1F5FE", 0.6)
        orange = mat("#FF9800", 0.35, coat=0.3)
        self.root = empty(n + "_root", home)
        self.root.scale = (1.25, 1.25, 1.25)
        self.body = empty(n + "_body", (0, 0, 0), self.root)
        b = self.body
        sphere(n + "_ball", (0, 0, 0), (0.17, 0.16, 0.18), blue, b, seg=40)
        sphere(n + "_belly", (0, -0.115, -0.05), (0.12, 0.07, 0.11), belly, b)
        for s in (-1, 1):
            sphere(n + "_cheek%d" % s, (s * 0.1, -0.13, -0.01), (0.03, 0.012, 0.02),
                   mat("#FF80AB", 0.6), b)
        self.eyes = {}
        for s in (-1, 1):
            self.eyes[s] = eye(n + "_eye%d" % s, b, (s * 0.062, -0.13, 0.055), s, 0.05,
                               "#1A237E", s * 0.4)
        self.beak = empty(n + "_beak", (0, -0.16, 0.0), b)
        cyl(n + "_beaku", (0, 0.0, 0.008), (0.045, 0.024), 0.085, orange, self.beak,
            r2=0.0, rot=(PI / 2, 0, 0), seg=16)
        self.jaw = empty(n + "_jaw", (0, 0.0, -0.004), self.beak)
        cyl(n + "_beakl", (0, 0.0, -0.01), (0.036, 0.015), 0.065, orange, self.jaw,
            r2=0.0, rot=(PI / 2, 0, 0), seg=16)
        self.wings = {}
        for s in (-1, 1):
            w = empty(n + "_wing%d" % s, (s * 0.15, 0.02, 0.01), b)
            sphere(n + "_wingm%d" % s, (s * 0.07, 0, 0), (0.1, 0.045, 0.065), dark, w)
            self.wings[s] = w
        for k, a in enumerate((-0.35, 0, 0.35)):
            sphere(n + "_tuft%d" % k, (a * 0.08, 0.0, 0.19), (0.018, 0.018, 0.06), dark, b,
                   rot=(0, a, 0))
            sphere(n + "_tail%d" % k, (a * 0.1, 0.17, -0.07), (0.03, 0.08, 0.018), dark, b,
                   rot=(-0.5, 0, a))
        for s in (-1, 1):
            sphere(n + "_foot%d" % s, (s * 0.055, -0.03, -0.18), (0.03, 0.045, 0.015),
                   orange, b)

    def init_pose(self, A):
        nf = A.nf
        z = np.zeros(nf)
        P = {k: z.copy() for k in ["bob", "rx", "ry", "spin", "jaw", "flap_amp",
                                   "flap_off"]}
        P["x"] = np.full(nf, float(self.home[0]))
        P["y"] = np.full(nf, float(self.home[1]))
        P["z"] = np.full(nf, float(self.home[2]))
        P["rz"] = z.copy()
        P["perch"] = z.copy()
        P["eye_sz"] = np.ones(nf)
        P["eye_s"] = np.ones(nf)
        P["flap_freq"] = np.full(nf, 3.0)
        P["flap_amp"] = np.full(nf, 0.35)
        P["hover"] = np.ones(nf)
        P["squash"] = np.ones(nf)
        self.P = P
        return P

    def write(self, A):
        P = self.P
        t = A.t
        # hover bob
        bob = P["bob"] + 0.035 * np.sin(2 * PI * 0.9 * t) * P["hover"] * (1 - P["perch"])
        A.set(self.root, "location", 0, P["x"])
        A.set(self.root, "location", 1, P["y"])
        A.set(self.root, "location", 2, P["z"] + bob)
        A.set(self.root, "rotation_euler", 2, P["rz"] + P["spin"])
        A.set(self.body, "rotation_euler", 0, P["rx"])
        A.set(self.body, "rotation_euler", 1, P["ry"])
        A.set(self.body, "scale", 2, P["squash"])
        A.set(self.body, "scale", 0, 1 / np.sqrt(P["squash"]))
        A.set(self.body, "scale", 1, 1 / np.sqrt(P["squash"]))
        phase = 2 * PI * np.cumsum(P["flap_freq"]) / U.FPS
        amp = P["flap_amp"] * (1 - P["perch"])
        flap = 0.15 + amp * np.sin(phase) + P["flap_off"]
        rest = -0.75
        for s in (-1, 1):
            a = rest * P["perch"] + flap * (1 - P["perch"])
            A.set(self.wings[s], "rotation_euler", 1, -s * a)
            e = self.eyes[s]
            A.set(e, "scale", 0, P["eye_s"])
            A.set(e, "scale", 1, P["eye_s"])
            A.set(e, "scale", 2, P["eye_s"] * P["eye_sz"])
        A.set(self.jaw, "rotation_euler", 0, P["jaw"])


# ================================================================== ANIMALS
class Animal:
    """Simple cute farm animals. kind: cat, dog, duck, cow, rabbit."""

    def __init__(self, kind, loc, rz=0.0, scale=1.0):
        self.name = kind
        self.kind = kind
        n = kind
        loc = tuple(loc) + (0.0,) * (3 - len(loc))
        self.root = empty(n + "_root", loc, rot=(0, 0, rz))
        self.root.scale = (scale,) * 3
        self.hop = empty(n + "_hop", (0, 0, 0), self.root)
        self.tail = None
        self.ears = []
        eyecol = "#212121"
        if kind in ("cat", "dog", "cow"):
            if kind == "cat":
                fur, fur2 = "#FFA040", "#FFF3E0"
                bl, bw, bh, leg, hr = 0.28, 0.17, 0.16, 0.2, 0.19
            elif kind == "dog":
                fur, fur2 = "#C58B5A", "#FFF3E0"
                bl, bw, bh, leg, hr = 0.33, 0.2, 0.18, 0.24, 0.21
            else:
                fur, fur2 = "#FAFAFA", "#F8BBD0"
                bl, bw, bh, leg, hr = 0.55, 0.36, 0.33, 0.42, 0.3
            m1 = mat(fur, 0.7)
            m2 = mat(fur2, 0.7)
            body_z = leg + bh * 0.85
            self.body = empty(n + "_body", (0, 0, body_z), self.hop)
            sphere(n + "_torso", (0, 0, 0), (bw, bl, bh), m1, self.body)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    cyl(n + "_leg%d%d" % (sx, sy), (sx * bw * 0.55, sy * bl * 0.55, -body_z),
                        bw * 0.28, body_z, m1 if kind != "cow" else mat("#FAFAFA", 0.7), self.body)
                    sphere(n + "_paw%d%d" % (sx, sy), (sx * bw * 0.55, sy * bl * 0.55 - 0.01,
                                                       -body_z + 0.02),
                           (bw * 0.3, bw * 0.36, bw * 0.18),
                           m2 if kind != "cow" else mat("#5D4037", 0.5), self.body)
            if kind == "cow":
                spot = mat("#212121", 0.7)
                for k, (x, y, z, r) in enumerate(((0.3, 0.1, 0.12, 0.13), (-0.28, -0.15, 0.1, 0.12),
                                                  (0.1, 0.3, 0.26, 0.11), (-0.2, 0.28, -0.05, 0.1))):
                    sphere(n + "_spot%d" % k, (x, y, z), (r * 0.5 if abs(x) > 0.2 else r,
                                                          r, r * 0.8), spot, self.body)
            # head
            self.headp = empty(n + "_headp", (0, -bl * 0.85, bh * 0.75), self.body)
            h = self.head = empty(n + "_head", (0, -hr * 0.3, hr * 0.6), self.headp)
            sphere(n + "_skull", (0, 0, 0), (hr, hr * 0.92, hr * 0.95), m1, h)
            sn = (0.55, 0.35, 0.42) if kind != "cow" else (0.65, 0.4, 0.45)
            sphere(n + "_snout", (0, -hr * 0.75, -hr * 0.3),
                   (hr * sn[0], hr * sn[1], hr * sn[2]), m2, h)
            nose_c = "#F48FB1" if kind != "dog" else "#212121"
            if kind == "cow":
                for s in (-1, 1):
                    sphere(n + "_nostril%d" % s, (s * hr * 0.2, -hr * 1.12, -hr * 0.25),
                           hr * 0.06, mat("#AD1457", 0.5), h)
            else:
                sphere(n + "_nose", (0, -hr * 1.08, -hr * 0.18), (hr * 0.14, hr * 0.1, hr * 0.1),
                       mat(nose_c, 0.3, coat=0.5), h)
            self.jaw = empty(n + "_jaw", (0, -hr * 0.85, -hr * 0.5), h)
            sphere(n + "_mouth", (0, 0, 0), (hr * 0.22, hr * 0.1, hr * 0.14),
                   mat(MOUTH, 0.4), self.jaw)
            self.jaw.scale = (1, 1, 0.1)
            for s in (-1, 1):
                eye(n + "_eye%d" % s, h, (s * hr * 0.38, -hr * 0.78, hr * 0.2), s,
                    hr * 0.2, eyecol, s * 0.35)
            if kind == "cat":
                for s in (-1, 1):
                    e = empty(n + "_ear%d" % s, (s * hr * 0.55, 0, hr * 0.7), h,
                              rot=(0, s * 0.35, 0))
                    cyl(n + "_earc%d" % s, (0, 0, 0), (hr * 0.3, hr * 0.14), hr * 0.55, m1, e,
                        r2=0.0, seg=12)
                    cyl(n + "_eari%d" % s, (0, -hr * 0.07, 0.01), (hr * 0.18, hr * 0.06),
                        hr * 0.4, mat("#F8BBD0", 0.6), e, r2=0.0, seg=12)
                    self.ears.append(e)
                    for k in range(3):
                        cyl(n + "_wh%d%d" % (s, k), (s * hr * 0.3, -hr * 1.0, -hr * 0.3 + k * 0.02),
                            0.004, hr * 0.8, mat("#5D4037"), h,
                            rot=(0, s * (PI / 2 - 0.1 + k * 0.1), 0), seg=6)
                self.tail = empty(n + "_tailp", (0, bl * 0.9, bh * 0.2), self.body,
                                  rot=(-0.5, 0, 0))
                cyl(n + "_tail", (0, 0, 0), 0.035, 0.32, m1, self.tail, seg=12)
                sphere(n + "_tailtip", (0, 0, 0.32), 0.04, m1, self.tail)
            elif kind == "dog":
                for s in (-1, 1):
                    e = empty(n + "_ear%d" % s, (s * hr * 0.75, 0, hr * 0.45), h,
                              rot=(0, -s * 0.3, 0))
                    sphere(n + "_earc%d" % s, (s * 0.02, 0, -hr * 0.45),
                           (hr * 0.2, hr * 0.12, hr * 0.5), mat("#8D6E63", 0.7), e)
                    self.ears.append(e)
                sphere(n + "_patch", (hr * 0.4, -hr * 0.55, hr * 0.3), (hr * 0.3, hr * 0.2, hr * 0.28),
                       mat("#8D6E63", 0.7), h)
                self.tail = empty(n + "_tailp", (0, bl * 0.9, bh * 0.35), self.body,
                                  rot=(-0.6, 0, 0))
                cyl(n + "_tail", (0, 0, 0), 0.035, 0.22, m1, self.tail, r2=0.5, seg=12)
                sphere(n + "_collar", (0, -bl * 0.75, bh * 0.75), (bw * 0.6, bw * 0.45, 0.03),
                       mat("#E53935", 0.4), self.body)
            else:  # cow
                for s in (-1, 1):
                    e = empty(n + "_ear%d" % s, (s * hr * 0.95, 0.02, hr * 0.3), h,
                              rot=(0, -s * 0.5, 0))
                    sphere(n + "_earc%d" % s, (s * hr * 0.2, 0, 0), (hr * 0.3, hr * 0.1, hr * 0.14),
                           m1, e)
                    self.ears.append(e)
                    cyl(n + "_horn%d" % s, (s * hr * 0.45, 0.02, hr * 0.75), hr * 0.08, hr * 0.3,
                        mat("#FFF8E1", 0.4), h, r2=0.4, rot=(0, s * 0.5, 0))
                sphere(n + "_bell", (0, -bl * 0.8, bh * 0.2), 0.06, mat("#FFC107", 0.2, metal=0.8),
                       self.body)
                self.tail = empty(n + "_tailp", (0, bl * 0.95, bh * 0.4), self.body,
                                  rot=(0.3, 0, 0))
                cyl(n + "_tail", (0, 0, -0.35), 0.02, 0.35, m1, self.tail, seg=8)
                sphere(n + "_tailtip", (0, 0, -0.37), (0.04, 0.04, 0.06), mat("#212121", 0.7), self.tail)
        elif kind == "duck":
            yel = mat("#FFE45C", 0.6)
            orange = mat("#FF9800", 0.35, coat=0.3)
            self.body = empty(n + "_body", (0, 0, 0.2), self.hop)
            sphere(n + "_torso", (0, 0.03, 0), (0.18, 0.23, 0.16), yel, self.body)
            sphere(n + "_tailf", (0, 0.24, 0.07), (0.07, 0.07, 0.05), yel, self.body,
                   rot=(-0.6, 0, 0))
            for s in (-1, 1):
                sphere(n + "_wing%d" % s, (s * 0.16, 0.05, 0.03), (0.04, 0.14, 0.09), yel,
                       self.body, rot=(0.2, 0, 0))
                sphere(n + "_foot%d" % s, (s * 0.07, -0.05, -0.19), (0.05, 0.07, 0.015), orange,
                       self.body)
            self.headp = empty(n + "_headp", (0, -0.14, 0.13), self.body)
            h = self.head = empty(n + "_head", (0, 0, 0.1), self.headp)
            sphere(n + "_skull", (0, 0, 0), 0.13, yel, h)
            sphere(n + "_bill", (0, -0.13, -0.02), (0.075, 0.07, 0.025), orange, h)
            self.jaw = empty(n + "_jaw", (0, -0.12, -0.04), h)
            sphere(n + "_billl", (0, -0.005, 0), (0.06, 0.06, 0.018), orange, self.jaw)
            self.jaw_is_rot = True
            for s in (-1, 1):
                eye(n + "_eye%d" % s, h, (s * 0.055, -0.1, 0.035), s, 0.03, eyecol, s * 0.45)
        elif kind == "rabbit":
            fur = mat("#F5F5F5", 0.7)
            pink = mat("#F8BBD0", 0.6)
            self.body = empty(n + "_body", (0, 0, 0.2), self.hop)
            sphere(n + "_torso", (0, 0.03, 0), (0.17, 0.2, 0.2), fur, self.body)
            sphere(n + "_puff", (0, 0.23, -0.05), 0.07, mat("#FFFFFF", 0.9),
                   self.body)
            for s in (-1, 1):
                sphere(n + "_foot%d" % s, (s * 0.09, -0.06, -0.18), (0.055, 0.11, 0.035), fur,
                       self.body)
                sphere(n + "_paw%d" % s, (s * 0.06, -0.17, -0.07), (0.035, 0.04, 0.05), fur,
                       self.body)
            self.headp = empty(n + "_headp", (0, -0.08, 0.2), self.body)
            h = self.head = empty(n + "_head", (0, 0, 0.1), self.headp)
            sphere(n + "_skull", (0, 0, 0), (0.15, 0.14, 0.14), fur, h)
            sphere(n + "_nose", (0, -0.14, -0.01), (0.025, 0.018, 0.018), mat("#F06292", 0.3), h)
            for s in (-1, 1):
                sphere(n + "_cheekp%d" % s, (s * 0.035, -0.125, -0.04), (0.035, 0.025, 0.03), fur, h)
                e = empty(n + "_ear%d" % s, (s * 0.06, 0.02, 0.11), h, rot=(0, s * 0.18, 0))
                sphere(n + "_earc%d" % s, (0, 0, 0.14), (0.04, 0.025, 0.15), fur, e)
                sphere(n + "_eari%d" % s, (0, -0.012, 0.14), (0.025, 0.015, 0.11), pink, e)
                self.ears.append(e)
                eye(n + "_eye%d" % s, h, (s * 0.06, -0.11, 0.03), s, 0.032, eyecol, s * 0.45)
            self.jaw = empty(n + "_jaw", (0, -0.125, -0.06), h)
            sphere(n + "_mouth", (0, 0, 0), (0.02, 0.01, 0.014), mat(MOUTH, 0.4), self.jaw)
            self.jaw.scale = (1, 1, 0.1)

    def init_pose(self, A):
        nf = A.nf
        z = np.zeros(nf)
        self.P = {"hop": z.copy(), "nod": z.copy(), "tilt": z.copy(), "mouth": np.full(nf, 0.1),
                  "wag": z.copy(), "squash": np.ones(nf), "turn": z.copy()}
        return self.P

    def write(self, A):
        P, t = self.P, A.t
        breathe = 1 + 0.015 * np.sin(2 * PI * 0.4 * t + len(self.kind))
        A.set(self.hop, "location", 2, P["hop"])
        A.set(self.hop, "scale", 2, P["squash"] * breathe)
        A.set(self.headp, "rotation_euler", 0, P["nod"] + 0.04 * np.sin(2 * PI * 0.3 * t))
        A.set(self.headp, "rotation_euler", 1, P["tilt"] + 0.06 * np.sin(2 * PI * 0.21 * t + 1))
        A.set(self.headp, "rotation_euler", 2, P["turn"])
        if getattr(self, "jaw_is_rot", False):
            A.set(self.jaw, "rotation_euler", 0, 0.6 * np.clip(P["mouth"] - 0.1, 0, 1))
        else:
            A.set(self.jaw, "scale", 2, P["mouth"])
        if self.tail is not None:
            base = self.tail.rotation_euler[1]
            A.set(self.tail, "rotation_euler", 1,
                  base + 0.15 * np.sin(2 * PI * 0.5 * t) + P["wag"] * np.sin(2 * PI * 5 * t))
        for k, e in enumerate(self.ears):
            if self.kind == "rabbit":
                base = e.rotation_euler[0]
                A.set(e, "rotation_euler", 0,
                      base + 0.08 * np.sin(2 * PI * 0.35 * t + k) - 0.3 * np.clip(P["hop"] * 3, 0, 1))


# =============================================================== BEHAVIOUR
def blink_curve(t, seed):
    rng = np.random.default_rng(seed)
    out = np.ones_like(t)
    tb = rng.uniform(0.5, 2.0)
    while tb < t[-1]:
        out *= 1 - 0.92 * np.exp(-((t - tb) / 0.055) ** 2)
        tb += rng.uniform(2.2, 4.8)
    return out


def blend(arr, target, w):
    arr[:] = arr * (1 - w) + target * w


def outer_side(ch, P, i):
    return -1 if P["root_x"][i] < 0 else 1


def kid_action(ch, A, act, t0, d, params, others):
    P, t = ch.P, A.t
    i0 = min(int(t0 * U.FPS), A.nf - 1)
    w = window(t, t0, t0 + d, 0.22)
    u = np.clip((t - t0) / d, 0, 1)
    s = outer_side(ch, P, i0)
    if act == "wave":
        blend(P["sh%d_ry" % s], -s * (2.55 + 0.28 * np.sin(2 * PI * 2.2 * (t - t0))), w)
        blend(P["sh%d_rx" % s], np.full_like(t, -0.25), w)
        P["spine_ry"] += -s * 0.05 * w
    elif act in ("jump", "jump3"):
        n = 1 if act == "jump" else 3
        uu = (u * n) % 1.0
        air = np.clip((uu - 0.18) / 0.64, 0, 1)
        h = np.sin(PI * air) * (air > 0) * (air < 1)
        mask = (t >= t0) & (t <= t0 + d)
        P["hop_z"] += np.where(mask, 0.3 * h, 0)
        sq = np.where(mask & (uu < 0.18), -0.12 * np.sin(PI * uu / 0.18), 0)
        sq += np.where(mask & (uu > 0.82), -0.1 * np.sin(PI * (uu - 0.82) / 0.18), 0)
        sq += np.where(mask, 0.06 * h, 0)
        P["squash"] += sq
        for sd in (-1, 1):
            blend(P["sh%d_ry" % sd], -sd * (0.4 + 1.9 * h), w)
        P["hipP"] += -0.3 * h
        P["hipN"] += -0.3 * h
    elif act == "clap":
        for sd in (-1, 1):
            blend(P["sh%d_rx" % sd], np.full_like(t, -1.25), w)
            blend(P["sh%d_ry" % sd], np.zeros_like(t), w)
            psi = 0.4 + 0.13 * np.cos(2 * PI * 2.4 * (t - t0))
            blend(P["sh%d_rz" % sd], -sd * psi, w)
    elif act == "point":
        blend(P["sh%d_rx" % s], np.full_like(t, -1.35), w)
        blend(P["sh%d_ry" % s], np.full_like(t, -s * 0.45), w)
    elif act == "point_up":
        blend(P["sh%d_rx" % s], np.full_like(t, -0.5), w)
        blend(P["sh%d_ry" % s], np.full_like(t, -s * 2.5), w)
        P["neck_rx"] += -0.25 * w
    elif act == "point_self":
        sd = -s
        blend(P["sh%d_rx" % sd], np.full_like(t, -1.0), w)
        blend(P["sh%d_ry" % sd], np.zeros_like(t), w)
        blend(P["sh%d_rz" % sd], np.full_like(t, -sd * 0.95), w)
    elif act == "nod":
        P["neck_rx"] += 0.16 * np.sin(2 * PI * 2.0 * (t - t0)) ** 2 * w
    elif act == "laugh":
        P["hop_z"] += 0.035 * np.abs(np.sin(2 * PI * 3.2 * (t - t0))) * w
        P["neck_rx"] += -0.18 * w
        P["eye_sz"] *= 1 - 0.6 * w
        P["smile_s"] += 0.3 * w
    elif act == "hug":
        other = [o for o in others if o.kind == "kid" and o is not ch]
        if other:
            dx = other[0].P["root_x"][i0] - P["root_x"][i0]
            sd = 1 if dx > 0 else -1
            P["spine_ry"] += sd * 0.16 * w
            blend(P["sh%d_ry" % sd], np.full_like(t, -sd * 1.5), w)
            blend(P["sh%d_rx" % sd], np.full_like(t, -0.6), w)
            P["smile_s"] += 0.25 * w
            P["eye_sz"] *= 1 - 0.4 * w
    elif act in ("run", "walk_in_place"):
        f, a, bounce = (2.8, 0.85, 0.07) if act == "run" else (1.45, 0.42, 0.025)
        ph = 2 * PI * f * (t - t0)
        P["hipP"] += a * np.sin(ph) * w
        P["hipN"] += -a * np.sin(ph) * w
        for sd in (-1, 1):
            blend(P["sh%d_rx" % sd], sd * a * 1.1 * np.sin(ph), w)
        P["hop_z"] += bounce * np.abs(np.sin(ph)) * w
        if act == "run":
            P["spine_rx"] += 0.12 * w
    elif act == "dance":
        f = 112 / 60
        ph = 2 * PI * f * (t - t0)
        P["hop_z"] += 0.07 * np.abs(np.sin(ph)) * w
        P["spine_ry"] += 0.18 * np.sin(ph / 2) * w
        P["root_rz"] += 0.35 * np.sin(ph / 4) * w
        for sd in (-1, 1):
            blend(P["sh%d_ry" % sd], -sd * (2.2 + 0.45 * np.sin(ph / 2 + (sd + 1) * PI / 2)), w)
            blend(P["sh%d_rx" % sd], np.full_like(t, -0.3), w)
        P["hipP"] += 0.25 * np.sin(ph / 2) * w
        P["hipN"] += -0.25 * np.sin(ph / 2) * w
        P["smile_s"] += 0.3 * w
    elif act in ("flap", "yawn", "dizzy"):
        pass


def bird_action(ch, A, act, t0, d, params):
    P, t = ch.P, A.t
    w = window(t, t0, t0 + d, 0.2)
    u = np.clip((t - t0) / d, 0, 1)
    if act in ("flap", "clap", "wave", "point", "point_up", "point_self"):
        P["flap_freq"] += 5.0 * w
        P["flap_amp"] += 0.45 * w
        P["bob"] += 0.06 * np.sin(PI * u) * w
    elif act in ("jump", "jump3"):
        n = 1 if act == "jump" else 3
        uu = (u * n) % 1.0
        P["bob"] += 0.22 * np.sin(PI * uu) * ((t >= t0) & (t <= t0 + d))
        P["flap_freq"] += 4.0 * w
        P["flap_amp"] += 0.4 * w
    elif act in ("dance",):
        f = 112 / 60
        ph = 2 * PI * f * (t - t0)
        P["spin"] += 2 * PI * smooth(u) * 2
        P["bob"] += 0.08 * np.abs(np.sin(ph)) * w
        P["ry"] += 0.25 * np.sin(ph / 2) * w
        P["flap_freq"] += 3 * w
    elif act in ("run", "walk_in_place"):
        P["flap_freq"] += (7.0 if act == "run" else 3.0) * w
        P["flap_amp"] += 0.4 * w
        P["rx"] += 0.25 * w
        P["ry"] += 0.15 * np.sin(2 * PI * 1.5 * (t - t0)) * w
    elif act == "laugh":
        P["bob"] += 0.03 * np.abs(np.sin(2 * PI * 3.2 * (t - t0))) * w
        P["eye_sz"] *= 1 - 0.6 * w
    elif act == "nod":
        P["rx"] += 0.2 * np.sin(2 * PI * 2 * (t - t0)) ** 2 * w
    elif act == "yawn":
        P["jaw"] += 0.55 * w
        P["eye_sz"] *= 1 - 0.85 * w
        P["flap_off"] += 0.9 * w
        P["flap_amp"] *= 1 - 0.8 * w
        P["rx"] += -0.2 * w
    elif act == "dizzy":
        P["spin"] += 2 * PI * 3 * smooth(u)
        P["ry"] += 0.3 * np.sin(2 * PI * 2.5 * (t - t0)) * w
        P["eye_sz"] *= 1 - 0.5 * w


MOODS_KID = {
    #            eye_s eye_sz brow_z brow smile_s smile_ry mouth neck_rx
    "happy":    (1.00, 0.78, 0.012, 0.0, 1.3, 0.0, 0.0, -0.05),
    "sad":      (0.95, 0.72, -0.004, 0.38, 0.85, PI, 0.0, 0.22),
    "excited":  (1.15, 1.05, 0.03, -0.1, 1.45, 0.0, 0.55, -0.1),
    "tired":    (1.00, 0.28, -0.01, 0.1, 0.6, 0.0, 0.0, 0.12),
    "surprised": (1.25, 1.12, 0.045, -0.15, 0.0, 0.0, 0.75, -0.08),
}


def kid_mood(ch, A, mood, t0, d):
    P, t = ch.P, A.t
    w = window(t, t0, t0 + d, 0.3)
    es, esz, bz, br, ss, sry, mo, nrx = MOODS_KID[mood]
    blend(P["eye_s"], np.full_like(t, es), w)
    blend(P["eye_sz"], np.full_like(t, esz), w)
    P["brow_z"] += bz * w
    for s in (-1, 1):
        P["brow%d" % s] += s * br * w
    blend(P["smile_s"], np.full_like(t, ss), w)
    blend(P["smile_ry"], np.full_like(t, sry), w)
    ch.mood_mouth = np.maximum(getattr(ch, "mood_mouth", np.zeros_like(t)), mo * w)
    if mood == "surprised":
        blend(P["mouth_sx"], np.full_like(t, 0.65), w)
    P["neck_rx"] += nrx * w
    if mood == "tired":
        P["neck_ry"] += 0.2 * w
        P["squash"] -= 0.03 * w
    if mood == "sad":
        for s in (-1, 1):
            P["sh%d_ry" % s] *= 1 - 0.8 * w
    if mood == "excited":
        P["hop_z"] += 0.03 * np.abs(np.sin(2 * PI * 2.5 * t)) * w


def bird_mood(ch, A, mood, t0, d):
    P, t = ch.P, A.t
    w = window(t, t0, t0 + d, 0.3)
    if mood == "tired":
        P["eye_sz"] *= 1 - 0.7 * w
        P["rx"] += 0.15 * w
        P["flap_amp"] *= 1 - 0.6 * w
    elif mood == "surprised":
        P["eye_s"] += 0.3 * w
        P["jaw"] += 0.3 * w
    elif mood == "happy":
        P["eye_sz"] *= 1 - 0.25 * w
    elif mood == "excited":
        P["eye_s"] += 0.15 * w
        P["bob"] += 0.04 * np.abs(np.sin(2 * PI * 2.5 * t)) * w
    elif mood == "sad":
        P["eye_sz"] *= 1 - 0.3 * w
        P["rx"] += 0.2 * w


def walk(ch, A, t0, d, target):
    """Walk from current position to target (x, y)."""
    P, t = ch.P, A.t
    i0 = min(int(t0 * U.FPS), A.nf - 1)
    x0, y0 = P["root_x"][i0], P["root_y"][i0]
    x1, y1 = target
    u = smooth((t - t0) / d)
    after = t >= t0
    P["root_x"][after] = (x0 + (x1 - x0) * u)[after]
    P["root_y"][after] = (y0 + (y1 - y0) * u)[after]
    heading = math.atan2(x1 - x0, -(y1 - y0))
    base = P["root_rz"][i0]
    w = window(t, t0 - 0.15, t0 + d + 0.25, 0.3)
    blend(P["root_rz"], np.full_like(t, heading), w)
    wk = window(t, t0, t0 + d, 0.2)
    ph = 2 * PI * 1.47 * (t - t0)
    P["hipP"] += 0.5 * np.sin(ph) * wk
    P["hipN"] += -0.5 * np.sin(ph) * wk
    for s in (-1, 1):
        P["sh%d_rx" % s] += s * 0.45 * np.sin(ph) * wk
    P["hop_z"] += 0.03 * np.abs(np.sin(ph)) * wk


def idle_kid(ch, A, seed):
    P, t = ch.P, A.t
    P["squash"] *= 1 + 0.012 * np.sin(2 * PI * 0.33 * t + seed)
    P["spine_ry"] += 0.025 * np.sin(2 * PI * 0.19 * t + seed)
    P["neck_ry"] += 0.04 * np.sin(2 * PI * 0.13 * t + seed * 2)
    for s in (-1, 1):
        P["sh%d_ry" % s] += -s * 0.03 * np.sin(2 * PI * 0.33 * t + seed)


def speech_drive(chars, A, speeches):
    """Mouths follow the voice envelope; listeners look at the speaker."""
    nf = A.nf
    by = {c.name: c for c in chars}
    for c in chars:
        c.env = np.zeros(nf)
    for sp in speeches:
        i0 = int(round(sp["t"] * U.FPS))
        for m, env in sp["env"].items():
            if m not in by:
                continue
            e = np.array(env)
            i1 = min(nf, i0 + len(e))
            if i1 > i0:
                by[m].env[i0:i1] = np.maximum(by[m].env[i0:i1], e[:i1 - i0])
    for c in chars:
        # smooth a little so mouths do not flicker
        k = np.array([0.25, 0.5, 0.25])
        c.env = np.convolve(c.env, k, mode="same")
    t = A.t
    for sp in speeches:
        members = [m for m in sp["members"] if m in by]
        if not members:
            continue
        w = window(t, sp["t"] - 0.2, sp["t"] + sp["dur"] + 0.3, 0.25)
        i0 = min(int(sp["t"] * U.FPS), nf - 1)
        spk = by[members[0]]
        sx = spk.P["root_x"][i0] if spk.kind == "kid" else spk.P.get("x", [0] * nf)[i0]
        for c in chars:
            if c.kind != "kid" or c.name in members:
                continue
            dx = sx - c.P["root_x"][i0]
            ang = np.clip(dx * 0.35, -0.45, 0.45) - (c.P["root_rz"][i0] - c.base_rz) * 0.5
            c.P["neck_rz"] += ang * w
            c.P["spine_rz"] += ang * 0.3 * w


def finish_kid(ch, A, seed):
    P, t = ch.P, A.t
    P["eye_sz"] *= blink_curve(t, seed)
    base = getattr(ch, "mood_mouth", np.zeros_like(t))
    P["mouth"] = np.maximum(np.maximum(0.05, base), 0.08 + 0.95 * ch.env)
    P["neck_rx"] += -0.05 * ch.env
    P["neck_ry"] += 0.05 * np.sin(2 * PI * 0.8 * t) * np.clip(ch.env * 3, 0, 1)
    P["smile_s"] = np.maximum(P["smile_s"], 0)


def finish_bird(ch, A, seed):
    P, t = ch.P, A.t
    P["eye_sz"] *= blink_curve(t, seed)
    P["jaw"] += 0.45 * ch.env
    P["flap_freq"] += 2.0 * np.clip(ch.env * 3, 0, 1)


def finish_animal(ch, A, speeches):
    P, t = ch.P, A.t
    for sp in speeches:
        env = sp["env"].get(ch.name)
        if env is None:
            continue
        i0 = int(round(sp["t"] * U.FPS))
        e = np.array(env)
        i1 = min(A.nf, i0 + len(e))
        P["mouth"][i0:i1] = np.maximum(P["mouth"][i0:i1], 0.15 + 0.95 * e[:i1 - i0])
        w = window(t, sp["t"], sp["t"] + sp["dur"], 0.15)
        P["nod"] += -0.15 * w
        P["hop"] += 0.03 * np.abs(np.sin(2 * PI * 3 * t)) * w
        P["wag"] += 0.5 * w


def animal_action(ch, A, act, t0):
    P, t = ch.P, A.t
    if act == "happy":
        w = window(t, t0, t0 + 1.8, 0.2)
        P["wag"] += 0.6 * w
        P["hop"] += 0.05 * np.abs(np.sin(2 * PI * 2.5 * (t - t0))) * w
        P["tilt"] += 0.15 * np.sin(2 * PI * 1.0 * (t - t0)) * w
    elif act == "hop":
        d = 1.6
        u = np.clip((t - t0) / d, 0, 1)
        uu = (u * 3) % 1.0
        mask = (t >= t0) & (t <= t0 + d)
        P["hop"] += np.where(mask, 0.22 * np.sin(PI * uu), 0)
        P["squash"] += np.where(mask, 0.08 * np.sin(PI * uu) - 0.05, 0)
