# RANO — ported to the in-container workflow engine

The full RANO brain-tumor preparation pipeline (from the `airflow` branch)
expressed with the in-container orchestrator instead of Airflow.

- `project/stages/`, `project/sanity_check.py`, `project/metrics.py` — the reused
  scientific stage code (copied verbatim from the branch). `stages/constants.py`
  and the heavy libraries/models are provided by the base image
  `mlcommons/rano-data-prep-mlcube:1.0.10`.
- `project/steps/rano_steps.py` — thin `Step` wrappers that construct and run each
  stage per subject (replacing the branch's `direct_stages.py` Typer commands).
- `project/conditions/conditions.py` — `AnnotationDone` / `BrainMaskChanged`,
  ported to the `Condition` interface (branching now lives in `workflow.yaml`, not
  inside the stages).
- `project/workflow.yaml` — the control graph: per-subject fan-out → manual-review
  branch (with a rollback cycle) → barrier → manual-approval gate → consolidation.

The workflow shape (graph + step/condition discovery) is validated by
`tests/test_examples.py`. The scientific stages are **not** executed here — they
need the base image, the nnU-Net models, and real DICOM data. Build and run with:

```bash
docker build -f examples/rano/Dockerfile -t mlcommons/rano-data-prep-workflow:0.1.0 .
# register examples/rano/container_config.yaml with MedPerf as a data preparator
```

## Mapping from the Airflow workflow

| Airflow step (`command`)        | Ported step (`workflow.yaml` id / class) |
|---------------------------------|------------------------------------------|
| `initial_setup`                 | `setup` / `Setup`                        |
| `make_csv`                      | `make_csv` / `MakeCsv`                    |
| `convert_nifti`                 | `convert_nifti` / `ConvertNifti`         |
| `extract_brain`                 | `brain_extraction` / `BrainExtraction`   |
| `extract_tumor`                 | `tumor_extraction` / `TumorExtraction`   |
| `prepare_for_manual_review`     | `manual_review` / `PrepareForReview`     |
| `rollback_to_brain_extract`     | `rollback` / `Rollback`                  |
| `segmentation_comparison`       | `segmentation_comparison` / `SegmentationComparison` |
| `calculate_changed_voxels`      | `calculate_changed_voxels` / `CalculateChangedVoxels` (barrier) |
| `final_confirmation`            | `final_confirmation` (type: manual_approval) |
| `move_labeled_files`            | `move_labeled_files` / `MoveLabeledFiles` (barrier) |
| `consolidation_stage`           | `consolidate` / `Consolidate` (barrier, terminal) |
| `sanity_check` / `metrics`      | validation flow (`SanityCheck` → `Statistics`) |
