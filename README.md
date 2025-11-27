## Protein Folding Structures

Desktop application built with PySide6 + VTK that lets researchers and hobbyists
upload Protein Data Bank (`.pdb`) files, inspect the processed MERS list, and
visualize individual structures in 3D. Navigation, processing state, and UI
components live under `app/`, `processing/`, and `ui/` respectively.

### Features
- Guided workflow: welcome ➜ file upload ➜ MER summary ➜ detailed viewer.
- Background worker so large `.pdb` files do not freeze the UI.
- Sidebar history of previously processed files with quick re‑open.
- 3D viewer powered by VTK plus raw-PDB viewer for quick sanity checks.
- Safety dialogs explaining when disconnected “islands” are stripped.

### Requirements
- Python 3.11+.
- System packages provided in `requirements.txt`:
  - `numpy`, `vtk`, `PySide6`, `matplotlib` and their runtime deps.


### Run the App
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

When the window opens, use **Select File** to choose a `.pdb`, then **Process
File** to generate interaction stats and renderable data. Double-click entries in
the sidebar to revisit earlier runs. Use **View Raw PDB** for a plain-text view.


### Troubleshooting
- VTK needs a GPU driver with OpenGL 2.1+; update drivers if the viewer fails.
- If Qt complains about missing plugins, ensure the virtual environment is
  active when running or packaging.
- Reinstall requirements after deleting `.venv` to recover from dependency
  issues.

### Contributing
Open issues/PRs on GitHub. Please run `python main.py` locally to sanity-check
UI flows before submitting changes.

