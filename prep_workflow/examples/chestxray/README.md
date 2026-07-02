# ChestXRay tutorial — ported to the in-container workflow engine

A minimal, linear port of the ChestXRay tutorial preparator. The tutorial's
`prepare` / `sanity_check` / `statistics` functions are reused verbatim (under
`project/science/`) and wrapped as barrier `Step`s — ChestXRay prepares the whole
dataset in one pass, so there is no per-subject fan-out.

```bash
docker build -f examples/chestxray/Dockerfile -t mlcommons/chestxray-prep-workflow:0.1.0 .
# register examples/chestxray/container_config.yaml with MedPerf
```
