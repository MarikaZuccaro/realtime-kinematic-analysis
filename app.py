# -*- coding: utf-8 -*-
# app.py - Server Web Edge AI per la gestione dello streaming video

import threading
import time
import cv2
import mediapipe as mp
import numpy as np
from flask import Flask, render_template, Response, request, jsonify

from config import ESERCIZI
from biomeccanica import analizza_postura

app = Flask(__name__)


# Stato globale thread-safe

_lock = threading.Lock()
stato = {
    "fase":        "su",
    "ripetizioni": 0,
    "avviso":      "",
    "dati_ui":     {},
    "errori_sessione": {}, # <- Registro degli errori
    "ultimo_avviso": ""    # <- Evita di contare lo stesso errore 100 volte al secondo
}
esercizio_corrente = "squat"
arto_corrente      = "sinistro"


def get_snapshot():
    with _lock:
        return {
            "ripetizioni":   stato["ripetizioni"],
            "avviso":        stato["avviso"],
            "fase":          stato["fase"],
            "esercizio":     esercizio_corrente,
            "arto":          arto_corrente,
            "rep_target":    ESERCIZI[esercizio_corrente]["rep_target"],
            "errori_sessione": stato["errori_sessione"], # <- Lo mandiamo al browser
            **stato["dati_ui"],
        }


# Singleton webcam

class CameraManager:
    def __init__(self):
        self._cap  = None
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            if self._cap is None or not self._cap.isOpened():
                self._cap = cv2.VideoCapture(0)
                self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return self._cap

camera = CameraManager()


# Generatore video — SOLO scheletro + gradi sulle articolazioni

def genera_video():
    global esercizio_corrente, arto_corrente, stato

    mp_drawing = mp.solutions.drawing_utils
    mp_pose    = mp.solutions.pose
    cap        = camera.get()

    with mp_pose.Pose(min_detection_confidence=0.5,
                      min_tracking_confidence=0.5) as pose:
        while True:
            success, frame = cap.read()
            if not success:
                time.sleep(0.05)
                cap = camera.get()
                continue

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            h, w, _ = image.shape

            with _lock:
                es   = esercizio_corrente
                arto = arto_corrente
                stato_locale = {"fase": stato["fase"]}

            if results.pose_landmarks:
                avviso, rep_completata, punti, dati_ui = analizza_postura(
                    es, results.pose_landmarks.landmark, w, h, stato_locale, arto
                )

                with _lock:
                    stato["fase"]    = stato_locale["fase"]
                    if rep_completata:
                        stato["ripetizioni"] += 1
                    stato["avviso"]  = avviso
                    stato["dati_ui"] = dati_ui

                    # LOGICA DI CONTEGGIO ERRORI CLINICI
                    if avviso and avviso != stato["ultimo_avviso"]:
                        if avviso not in stato["errori_sessione"]:
                            stato["errori_sessione"][avviso] = 0
                        stato["errori_sessione"][avviso] += 1
                    
                    stato["ultimo_avviso"] = avviso

                # Scheletro: verde = ok, rosso = errore
                col_sk = (0, 220, 90) if not avviso else (0, 60, 255)
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=col_sk, thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=col_sk, thickness=2),
                )

                # Solo gradi sulle articolazioni
                for angolo, pos, colore in punti:
                    px, py = int(pos[0]), int(pos[1])
                    
                    cv2.putText(image, f"{int(angolo)}", (px + 10, py),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 4, cv2.LINE_AA)
                    cv2.putText(image, f"{int(angolo)}", (px + 10, py),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, colore,   2, cv2.LINE_AA)
            else:
                with _lock:
                    stato["avviso"] = ""

            ret, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


# Routes

@app.route('/')
def index():
    return render_template('index.html', esercizi=ESERCIZI)

@app.route('/video_feed')
def video_feed():
    return Response(genera_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def data():
    return jsonify(get_snapshot())

@app.route('/cambia_esercizio', methods=['POST'])
def cambia_esercizio():
    global esercizio_corrente, stato
    payload = request.get_json()
    nuovo = payload.get("esercizio")
    if nuovo not in ESERCIZI:
        return jsonify({"status": "errore"}), 400
    with _lock:
        esercizio_corrente       = nuovo
        stato["ripetizioni"]     = 0
        stato["fase"]            = ESERCIZI[nuovo]["fase_iniziale"]
        stato["avviso"]          = ""
        stato["dati_ui"]         = {}
    return jsonify({
        "status":     "ok",
        "istruzioni": ESERCIZI[nuovo]["istruzioni"],
        "vista":      ESERCIZI[nuovo]["vista"],
        "nome":       ESERCIZI[nuovo]["nome"],
        "rep_target": ESERCIZI[nuovo]["rep_target"],
        "mono_arto":  ESERCIZI[nuovo]["mono_arto"],
    })

@app.route('/cambia_arto', methods=['POST'])
def cambia_arto():
    global arto_corrente, stato
    payload = request.get_json()
    nuovo_arto = payload.get("arto")
    if nuovo_arto not in ("sinistro", "destro"):
        return jsonify({"status": "errore"}), 400
    with _lock:
        arto_corrente        = nuovo_arto
        stato["ripetizioni"] = 0
        stato["fase"]        = ESERCIZI[esercizio_corrente]["fase_iniziale"]
        stato["dati_ui"]     = {}
    return jsonify({"status": "ok", "arto": nuovo_arto})

@app.route('/reset')
def reset():
    global stato
    with _lock:
        stato["ripetizioni"] = 0
        stato["fase"]        = ESERCIZI[esercizio_corrente]["fase_iniziale"]
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)