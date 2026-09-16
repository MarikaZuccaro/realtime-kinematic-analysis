# -*- coding: utf-8 -*-
# config.py - Configurazione centralizzata dei protocolli riabilitativi

ESERCIZI = {
    "squat": {
        "nome": "Squat Riabilitativo",
        "vista": "PROFILO",
        "istruzioni": "Posizionati interamente di profilo con il lato da riabilitare verso la telecamera. Talloni saldi a terra, scendi flettendo ginocchia e anche in modo controllato.",
        "fase_iniziale": "su",
        "icon": "🦵",
        "rep_target": 15,
        "mono_arto": True,
    },
    "lunge": {
        "nome": "Affondo Post-Operatorio",
        "vista": "PROFILO",
        "istruzioni": "Posizionati di profilo con il lato da riabilitare verso la telecamera. Fai un passo avanti e scendi verticalmente. Il ginocchio anteriore NON deve superare la punta del piede.",
        "fase_iniziale": "su",
        "icon": "🚶",
        "rep_target": 12,
        "mono_arto": True,
    },
    "shoulder": {
        "nome": "Abduzione Spalla",
        "vista": "FRONTALE",
        "istruzioni": "Posizionati frontalmente rispetto alla telecamera con il braccio da riabilitare ben visibile. Solleva lateralmente il braccio teso fino a renderlo parallelo al suolo (90°), poi abbassa lentamente.",
        "fase_iniziale": "giu",
        "icon": "💪",
        "rep_target": 15,
        "mono_arto": True,
    },
    "extension": {
        "nome": "Estensione Ginocchio",
        "vista": "PROFILO",
        "istruzioni": "Siediti di profilo con il lato da riabilitare verso la telecamera. Blocca la schiena allo schienale. Estendi completamente il ginocchio in avanti e ritorna lentamente.",
        "fase_iniziale": "giu",
        "icon": "🪑",
        "rep_target": 20,
        "mono_arto": True,
    }
}