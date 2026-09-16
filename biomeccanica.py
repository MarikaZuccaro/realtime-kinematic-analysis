# -*- coding: utf-8 -*-
# biomeccanica.py - Motore di calcolo trigonometrico e analisi della postura

import math
import mediapipe as mp

mp_pose = mp.solutions.pose
VISIBILITA_MIN = 0.55


def calcola_angolo(a, b, c):
    """Calcola l'angolo geometrico tra tre snodi (b e' il vertice)."""
    angolo_rad = math.atan2(c[1] - b[1], c[0] - b[0]) - \
                 math.atan2(a[1] - b[1], a[0] - b[0])
    angolo_gradi = abs(angolo_rad * 180.0 / math.pi)
    if angolo_gradi > 180.0:
        angolo_gradi = 360.0 - angolo_gradi
    return angolo_gradi


def landmark_visibile(landmarks, *ids):
    for lid in ids:
        if landmarks[lid.value].visibility < VISIBILITA_MIN:
            return False
    return True


def _side_landmarks(arto):
    """
    Ritorna i landmark corretti compensando l'effetto SPECCHIO (cv2.flip) del video.
    Poiché il video è specchiato, per MediaPipe il lato fisico destro dell'utente 
    appare come il lato sinistro dell'immagine (e viceversa).
    """
    if arto == "destro":
        # Se l'utente clicca "Destro", chiediamo a MediaPipe i punti "LEFT"
        return {
            "shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER,
            "hip":      mp_pose.PoseLandmark.LEFT_HIP,
            "knee":     mp_pose.PoseLandmark.LEFT_KNEE,
            "ankle":    mp_pose.PoseLandmark.LEFT_ANKLE,
            "foot":     mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
            "elbow":    mp_pose.PoseLandmark.LEFT_ELBOW,
            "wrist":    mp_pose.PoseLandmark.LEFT_WRIST,
        }
    else:
        # Se l'utente clicca "Sinistro", chiediamo a MediaPipe i punti "RIGHT"
        return {
            "shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER,
            "hip":      mp_pose.PoseLandmark.RIGHT_HIP,
            "knee":     mp_pose.PoseLandmark.RIGHT_KNEE,
            "ankle":    mp_pose.PoseLandmark.RIGHT_ANKLE,
            "foot":     mp_pose.PoseLandmark.RIGHT_FOOT_INDEX,
            "elbow":    mp_pose.PoseLandmark.RIGHT_ELBOW,
            "wrist":    mp_pose.PoseLandmark.RIGHT_WRIST,
        }


def analizza_postura(esercizio, landmarks, w, h, stato, arto="sinistro"):
    """
    Returns:
        avviso (str)
        rep_completata (bool)
        punti_da_disegnare (list of (angolo, pos, colore))
        dati_ui (dict)
    """
    avviso = ""
    rep_completata = False
    punti_da_disegnare = []
    dati_ui = {}

    lm = _side_landmarks(arto)

    def punto(lid):
        l = landmarks[lid.value]
        return [l.x * w, l.y * h]

    
    # 1. SQUAT
    
    if esercizio == "squat":
        ids = [lm["shoulder"], lm["hip"], lm["knee"], lm["ankle"], lm["foot"]]
        if not landmark_visibile(landmarks, *ids):
            return "Corpo non rilevato - posizionati di profilo", False, [], {}

        spalla    = punto(lm["shoulder"])
        anca      = punto(lm["hip"])
        ginocchio = punto(lm["knee"])
        caviglia  = punto(lm["ankle"])
        piede     = punto(lm["foot"])

        ang_anca      = calcola_angolo(spalla, anca, ginocchio)
        ang_ginocchio = calcola_angolo(anca, ginocchio, caviglia)
        ang_caviglia  = calcola_angolo(ginocchio, caviglia, piede)

        ok_anca = ok_gin = ok_cav = True
        col_anca = col_gin = col_cav = (0, 220, 90)

        if ang_caviglia > 115:
            col_cav = (0, 60, 255); ok_cav = False
            avviso = "Tallone sollevato!"
        elif ang_ginocchio < 65:
            col_gin = (0, 60, 255); ok_gin = False
            avviso = "Iper-flessione ginocchio!"
        elif ang_anca < 60:
            col_anca = (0, 60, 255); ok_anca = False
            avviso = "Schiena troppo flessa in avanti!"

        if ang_ginocchio < 100 and stato["fase"] == "su":
            stato["fase"] = "giu"
        elif ang_ginocchio > 160 and stato["fase"] == "giu":
            stato["fase"] = "su"
            rep_completata = True

        punti_da_disegnare = [
            (ang_anca,      anca,      col_anca),
            (ang_ginocchio, ginocchio, col_gin),
            (ang_caviglia,  caviglia,  col_cav),
        ]
        dati_ui = {
            "angolo_anca": ang_anca,      "ok_anca": ok_anca,
            "angolo_ginocchio": ang_ginocchio, "ok_ginocchio": ok_gin,
            "angolo_caviglia": ang_caviglia,   "ok_caviglia": ok_cav,
        }

    
    # 2. LUNGE
    
    elif esercizio == "lunge":
        ids = [lm["shoulder"], lm["hip"], lm["knee"], lm["ankle"], lm["foot"]]
        if not landmark_visibile(landmarks, *ids):
            return "Corpo non rilevato - posizionati di profilo", False, [], {}

        spalla    = punto(lm["shoulder"])
        anca      = punto(lm["hip"])
        ginocchio = punto(lm["knee"])
        caviglia  = punto(lm["ankle"])
        piede     = punto(lm["foot"])

        ang_anca      = calcola_angolo(spalla, anca, ginocchio)
        ang_ginocchio = calcola_angolo(anca, ginocchio, caviglia)
        ang_caviglia  = calcola_angolo(ginocchio, caviglia, piede)

        ok_anca = ok_gin = ok_cav = True
        col_anca = col_gin = col_cav = (0, 220, 90)

        if ang_caviglia < 75:
            col_cav = (0, 60, 255); ok_cav = False
            avviso = "Ginocchio oltre la punta del piede!"
        elif ang_anca < 130:
            col_anca = (0, 60, 255); ok_anca = False
            avviso = "Raddrizza il busto!"
        elif ang_ginocchio < 75:
            col_gin = (0, 60, 255); ok_gin = False
            avviso = "Discesa troppo profonda!"

        if ang_ginocchio < 105 and stato["fase"] == "su":
            stato["fase"] = "giu"
        elif ang_ginocchio > 150 and stato["fase"] == "giu":
            stato["fase"] = "su"
            rep_completata = True

        punti_da_disegnare = [
            (ang_anca,      anca,      col_anca),
            (ang_ginocchio, ginocchio, col_gin),
            (ang_caviglia,  caviglia,  col_cav),
        ]
        dati_ui = {
            "angolo_anca": ang_anca,      "ok_anca": ok_anca,
            "angolo_ginocchio": ang_ginocchio, "ok_ginocchio": ok_gin,
            "angolo_caviglia": ang_caviglia,   "ok_caviglia": ok_cav,
        }

    
    # 3. SHOULDER
    
    elif esercizio == "shoulder":
        ids = [lm["hip"], lm["shoulder"], lm["elbow"], lm["wrist"]]
        if not landmark_visibile(landmarks, *ids):
            return "Corpo non rilevato - posizionati frontalmente", False, [], {}

        anca   = punto(lm["hip"])
        spalla = punto(lm["shoulder"])
        gomito = punto(lm["elbow"])
        polso  = punto(lm["wrist"])

        ang_spalla = calcola_angolo(anca, spalla, gomito)
        ang_gomito = calcola_angolo(spalla, gomito, polso)

        ok_spalla = ok_gomito = True
        col_spalla = col_gomito = (0, 220, 90)

        if ang_spalla > 100:
            col_spalla = (0, 60, 255); ok_spalla = False
            avviso = "Braccio troppo alto!"
        elif ang_gomito < 130:
            col_gomito = (0, 60, 255); ok_gomito = False
            avviso = "Distendi maggiormente il braccio!"

        if ang_spalla > 85 and stato["fase"] == "giu":
            stato["fase"] = "su"
        elif ang_spalla < 45 and stato["fase"] == "su":
            stato["fase"] = "giu"
            rep_completata = True

        punti_da_disegnare = [
            (ang_spalla, spalla, col_spalla),
            (ang_gomito, gomito, col_gomito),
        ]
        dati_ui = {
            "angolo_spalla": ang_spalla, "ok_spalla": ok_spalla,
            "angolo_gomito": ang_gomito, "ok_gomito": ok_gomito,
        }

    
    # 4. EXTENSION
    
    elif esercizio == "extension":
        ids = [lm["shoulder"], lm["hip"], lm["knee"], lm["ankle"]]
        if not landmark_visibile(landmarks, *ids):
            return "Corpo non rilevato - posizionati di profilo", False, [], {}

        spalla    = punto(lm["shoulder"])
        anca      = punto(lm["hip"])
        ginocchio = punto(lm["knee"])
        caviglia  = punto(lm["ankle"])

        ang_anca      = calcola_angolo(spalla, anca, ginocchio)
        ang_ginocchio = calcola_angolo(anca, ginocchio, caviglia)

        ok_anca = ok_gin = True
        col_anca = col_gin = (0, 220, 90)

        if ang_anca > 120:
            col_anca = (0, 60, 255); ok_anca = False
            avviso = "Tieni la schiena aderente allo schienale!"
        elif ang_ginocchio < 70:
            col_gin = (0, 60, 255); ok_gin = False
            avviso = "Piede troppo indietro sotto la sedia."

        if ang_ginocchio > 160 and stato["fase"] == "giu":
            stato["fase"] = "su"
        elif ang_ginocchio < 115 and stato["fase"] == "su":
            stato["fase"] = "giu"
            rep_completata = True

        punti_da_disegnare = [
            (ang_ginocchio, ginocchio, col_gin),
            (ang_anca,      anca,      col_anca),
        ]
        dati_ui = {
            "angolo_ginocchio": ang_ginocchio, "ok_ginocchio": ok_gin,
            "angolo_anca": ang_anca,           "ok_anca": ok_anca,
        }

    return avviso, rep_completata, punti_da_disegnare, dati_ui