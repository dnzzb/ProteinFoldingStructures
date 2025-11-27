from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from PySide6.QtWidgets import QMainWindow, QWidget

from ui.file_upload_page import ProcessedFile, FileUploadPage
from ui.mer_list_page import MerListPage
from ui.protein_viewer_page import ProteinViewerPage
from ui.welcome_page import WelcomePage


@dataclass
class AppState:
    """Container for UI state shared across screens."""

    processed_files: List[ProcessedFile] = field(default_factory=list)
    current_best_mer: Optional[str] = None
    current_download_data: Optional[Dict[str, object]] = None
    current_interactions: Optional[Sequence] = None
    current_total_weight_sums: Optional[Dict[str, float]] = None
    current_all_distance_sums: Optional[Dict[str, Dict[str, float]]] = None


class NavigationController:
    """
    Encapsulates navigation and shared state so QMainWindow stays lean.
    """

    def __init__(self, window: QMainWindow):
        self.window = window
        self.state = AppState()
        self.go_to_welcome()

    # ------------------------------------------------------------------ #
    # Helper
    # ------------------------------------------------------------------ #
    def _set_widget(self, widget_factory: Callable[[], QWidget]) -> None:
        self.window.setCentralWidget(widget_factory())

    # ------------------------------------------------------------------ #
    # Navigation targets
    # ------------------------------------------------------------------ #
    def go_to_welcome(self) -> None:
        self._set_widget(lambda: WelcomePage(on_get_started=self.go_to_file_upload))

    def go_to_file_upload(self) -> None:
        def widget() -> QWidget:
            return FileUploadPage(
                on_back=self.go_to_welcome,
                on_mer_list=self.go_to_mer_list,
                on_view_raw=self.go_to_raw_viewer,
                processed_files=self.state.processed_files,
            )

        self._set_widget(widget)

    def go_to_mer_list(
        self,
        best_source_mer,
        download_data,
        processed_files,
        interactions,
        total_weight_sums,
        all_distance_sums,
    ) -> None:
        self.state.processed_files = processed_files
        self.state.current_best_mer = best_source_mer
        self.state.current_download_data = download_data
        self.state.current_interactions = interactions
        self.state.current_total_weight_sums = total_weight_sums
        self.state.current_all_distance_sums = all_distance_sums

        def widget() -> QWidget:
            return MerListPage(
                best_source_mer=best_source_mer,
                download_data=download_data,
                processed_files=self.state.processed_files,
                interactions=interactions,
                total_weight_sums=total_weight_sums,
                on_back=self.go_to_file_upload,
                on_view_mer=self.go_to_protein_viewer,
            )

        self._set_widget(widget)

    def go_to_protein_viewer(self, mer_name, pdb_content, interactions, _unused) -> None:
        if not self.state.current_all_distance_sums:
            distance_map_for_selected_mer = {}
        else:
            distance_map_for_selected_mer = self.state.current_all_distance_sums.get(mer_name, {})

        pdb_filename = self._resolve_pdb_filename(mer_name)

        def on_back():
            self.go_to_mer_list(
                self.state.current_best_mer,
                self.state.current_download_data,
                self.state.processed_files,
                self.state.current_interactions,
                self.state.current_total_weight_sums,
                self.state.current_all_distance_sums,
            )

        def widget() -> QWidget:
            return ProteinViewerPage(
                mer_name=mer_name,
                pdb_content=pdb_content,
                interactions=interactions,
                total_weight_sums=distance_map_for_selected_mer,
                on_back=on_back,
                pdb_file_name=pdb_filename,
            )

        self._set_widget(widget)

    def go_to_raw_viewer(self, pdb_content, file_path) -> None:
        pdb_filename = os.path.basename(file_path)

        def widget() -> QWidget:
            return ProteinViewerPage(
                mer_name="Raw PDB",
                pdb_content=pdb_content,
                interactions=[],
                total_weight_sums={},
                on_back=self.go_to_file_upload,
                pdb_file_name=pdb_filename,
                raw_mode=True,
            )

        self._set_widget(widget)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _resolve_pdb_filename(self, mer_name: str) -> str:
        pdb_file_path = None
        for pf in self.state.processed_files:
            if (
                mer_name in getattr(pf, "all_distance_sums", {})
                or pf.best_source_mer == self.state.current_best_mer
            ):
                pdb_file_path = pf.file_path
                break

        return os.path.basename(pdb_file_path) if pdb_file_path else "UnknownFile"

