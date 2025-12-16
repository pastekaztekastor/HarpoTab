"""
Système de suivi de progression pour le pipeline HarpoTab
"""
import threading
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ProgressStatus(Enum):
    """États possibles d'une étape"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProgressStep:
    """Représente une étape du pipeline"""
    id: str
    name: str
    status: ProgressStatus
    progress: int  # 0-100
    message: str = ""
    substeps: list = None

    def __post_init__(self):
        if self.substeps is None:
            self.substeps = []


class ProgressTracker:
    """Gestionnaire de progression du pipeline"""

    # Définition des étapes du pipeline
    PIPELINE_STEPS = [
        {
            'id': 'ocr',
            'name': 'OCR Musical',
            'substeps': [
                {'id': 'ocr_init', 'name': 'Initialisation Audiveris'},
                {'id': 'ocr_process', 'name': 'Analyse de la partition'},
                {'id': 'ocr_parse', 'name': 'Parsing MusicXML'}
            ]
        },
        {
            'id': 'melody',
            'name': 'Extraction Mélodie',
            'substeps': [
                {'id': 'melody_select', 'name': 'Sélection partie principale'},
                {'id': 'melody_extract', 'name': 'Extraction des notes'}
            ]
        },
        {
            'id': 'analysis',
            'name': 'Analyse Musicale',
            'substeps': [
                {'id': 'analysis_key', 'name': 'Détection tonalité'},
                {'id': 'analysis_range', 'name': 'Calcul tessiture'}
            ]
        },
        {
            'id': 'mapping_load',
            'name': 'Chargement Mapping',
            'substeps': []
        },
        {
            'id': 'transpose',
            'name': 'Transposition',
            'substeps': [
                {'id': 'transpose_check', 'name': 'Vérification jouabilité'},
                {'id': 'transpose_apply', 'name': 'Application transposition'}
            ]
        },
        {
            'id': 'tablature',
            'name': 'Génération Tablature',
            'substeps': [
                {'id': 'tablature_map', 'name': 'Mapping notes → trous'},
                {'id': 'tablature_optimize', 'name': 'Optimisation positions'}
            ]
        },
        {
            'id': 'pdf',
            'name': 'Génération PDF',
            'substeps': [
                {'id': 'pdf_format', 'name': 'Formatage Lilypond'},
                {'id': 'pdf_compile', 'name': 'Compilation PDF'}
            ]
        }
    ]

    def __init__(self, session_id: str):
        """
        Initialise le tracker de progression

        Args:
            session_id: Identifiant unique de la session
        """
        self.session_id = session_id
        self.steps = {}
        self.current_step = None
        self.callbacks = []
        self.lock = threading.Lock()
        self.start_time = time.time()

        # Initialiser toutes les étapes
        self._initialize_steps()

    def _initialize_steps(self):
        """Initialise toutes les étapes avec le statut PENDING"""
        for step_def in self.PIPELINE_STEPS:
            step = ProgressStep(
                id=step_def['id'],
                name=step_def['name'],
                status=ProgressStatus.PENDING,
                progress=0,
                substeps=[]
            )

            # Initialiser les sous-étapes
            for substep_def in step_def.get('substeps', []):
                substep = ProgressStep(
                    id=substep_def['id'],
                    name=substep_def['name'],
                    status=ProgressStatus.PENDING,
                    progress=0
                )
                step.substeps.append(substep)

            self.steps[step.id] = step

    def start_step(self, step_id: str, message: str = ""):
        """Démarre une étape principale"""
        with self.lock:
            if step_id in self.steps:
                self.steps[step_id].status = ProgressStatus.IN_PROGRESS
                self.steps[step_id].message = message
                self.current_step = step_id
                self._notify_change()

    def complete_step(self, step_id: str, message: str = ""):
        """Complète une étape principale"""
        with self.lock:
            if step_id in self.steps:
                self.steps[step_id].status = ProgressStatus.COMPLETED
                self.steps[step_id].progress = 100
                self.steps[step_id].message = message
                self._notify_change()

    def error_step(self, step_id: str, message: str):
        """Marque une étape en erreur"""
        with self.lock:
            if step_id in self.steps:
                self.steps[step_id].status = ProgressStatus.ERROR
                self.steps[step_id].message = message
                self._notify_change()

    def start_substep(self, step_id: str, substep_id: str, message: str = ""):
        """Démarre une sous-étape"""
        with self.lock:
            if step_id in self.steps:
                for substep in self.steps[step_id].substeps:
                    if substep.id == substep_id:
                        substep.status = ProgressStatus.IN_PROGRESS
                        substep.message = message
                        self._notify_change()
                        break

    def complete_substep(self, step_id: str, substep_id: str, message: str = ""):
        """Complète une sous-étape"""
        with self.lock:
            if step_id in self.steps:
                for substep in self.steps[step_id].substeps:
                    if substep.id == substep_id:
                        substep.status = ProgressStatus.COMPLETED
                        substep.progress = 100
                        substep.message = message
                        self._update_step_progress(step_id)
                        self._notify_change()
                        break

    def _update_step_progress(self, step_id: str):
        """Met à jour le progrès global d'une étape basé sur ses sous-étapes"""
        if step_id in self.steps:
            step = self.steps[step_id]
            if step.substeps:
                completed = sum(1 for s in step.substeps if s.status == ProgressStatus.COMPLETED)
                step.progress = int((completed / len(step.substeps)) * 100)
            else:
                step.progress = 100 if step.status == ProgressStatus.COMPLETED else 50

    def _calculate_overall_progress(self) -> int:
        """Calcule le progrès global (version interne sans lock)"""
        if not self.steps:
            return 0

        total_steps = len(self.steps)
        completed_steps = sum(1 for s in self.steps.values() if s.status == ProgressStatus.COMPLETED)

        return int((completed_steps / total_steps) * 100)

    def get_overall_progress(self) -> int:
        """Calcule le progrès global du pipeline"""
        with self.lock:
            return self._calculate_overall_progress()

    def _build_status(self) -> Dict[str, Any]:
        """Construit le statut (version interne sans lock - le lock doit déjà être acquis)"""
        return {
            'session_id': self.session_id,
            'overall_progress': self._calculate_overall_progress(),
            'elapsed_time': int(time.time() - self.start_time),
            'current_step': self.current_step,
            'steps': [
                {
                    'id': step.id,
                    'name': step.name,
                    'status': step.status.value,
                    'progress': step.progress,
                    'message': step.message,
                    'substeps': [
                        {
                            'id': substep.id,
                            'name': substep.name,
                            'status': substep.status.value,
                            'progress': substep.progress,
                            'message': substep.message
                        }
                        for substep in step.substeps
                    ]
                }
                for step in self.steps.values()
            ]
        }

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut complet de la progression"""
        with self.lock:
            return self._build_status()

    def add_callback(self, callback: Callable):
        """Ajoute un callback appelé à chaque changement"""
        self.callbacks.append(callback)

    def _notify_change(self):
        """Notifie tous les callbacks d'un changement (le lock doit déjà être acquis)"""
        status = self._build_status()  # Utiliser la version interne
        for callback in self.callbacks:
            try:
                callback(status)
            except Exception as e:
                print(f"Erreur callback: {e}")


# Stockage global des trackers (session_id → tracker)
_trackers: Dict[str, ProgressTracker] = {}
_trackers_lock = threading.Lock()


def get_tracker(session_id: str) -> Optional[ProgressTracker]:
    """Récupère un tracker par son ID"""
    with _trackers_lock:
        return _trackers.get(session_id)


def create_tracker(session_id: str) -> ProgressTracker:
    """Crée un nouveau tracker"""
    with _trackers_lock:
        tracker = ProgressTracker(session_id)
        _trackers[session_id] = tracker
        return tracker


def remove_tracker(session_id: str):
    """Supprime un tracker"""
    with _trackers_lock:
        if session_id in _trackers:
            del _trackers[session_id]
