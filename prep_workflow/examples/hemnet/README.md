# HEMnet — ported to the in-container workflow engine

The HEMnet histopathology pipeline (from the `airflow` branch) expressed with the
in-container orchestrator. The reused HEMnet scripts (`project/science/*.py`) are
invoked as subprocesses from their working directory in the image; slides are
registered as subjects and flow per-subject through registration/masking/tiling,
with barrier steps for normalisation, consolidation and cleanup.

Note: the reference Airflow version passed `--partition` to scripts that actually
expect `-s/--subject-subdir`; this port uses the correct flag. Requires the
`andrewsu1/hemnet` base image and real `.svs` slides; not executed here.

```bash
docker build -f examples/hemnet/Dockerfile -t mlcommons/hemnet-prep-workflow:0.1.0 .
# register examples/hemnet/container_config.yaml with MedPerf
```
