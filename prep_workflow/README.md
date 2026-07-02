# prep-workflow — in-container data-preparation workflow engine

A small orchestration engine that runs a **multi-step, per-subject data-preparation
workflow inside a single container**. To MedPerf it looks like an ordinary
`DockerImage` data preparator with the usual `prepare` / `sanity_check` /
`statistics` tasks — so no MedPerf CLI or server changes are needed. Inside, the
engine runs many steps per subject, in parallel, with branching and human review.

## Why in-container?

Spawning a container per step per subject re-pays interpreter/CUDA/model-load
startup thousands of times (e.g. 500 subjects × 10 steps) and can't pipeline a
human-in-the-loop step (subject A being annotated while subject B keeps computing).
Running the orchestration inside one warm container fixes both.

## What an author writes

Only four things (everything else is provided):

```
project/
├── steps/         # Step subclasses (any number of files / classes)
├── conditions/    # Condition subclasses used for branching
├── workflow.yaml  # the step graph (which step follows which, and when)
└── requirements.txt
```

### Steps

```python
from prep_workflow import Step

class Convert(Step):
    per_subject = True            # runs once per subject (default). False = barrier.
    def run(self, ctx):
        # ctx.subject, ctx.paths.*, ctx.params, ctx.report, ctx.logger
        ...                        # raise to signal failure
```

### Conditions (for branching)

```python
from prep_workflow import Condition

class AnnotationDone(Condition):
    def evaluate(self, ctx) -> bool:
        ...
```

### workflow.yaml

```yaml
max_workers: 4
steps:
  - id: discover                  # first step must be a barrier that lists subjects
    step: DiscoverSubjects        # a built-in; or write your own barrier step
    per_subject: false
    next: convert
  - id: convert
    step: Convert
    per_subject: true
    limit: 4                      # max concurrent subjects in this step
    next: review
  - id: review
    step: PrepareForReview
    per_subject: true
    next:                         # branch on conditions
      if:
        - condition: AnnotationDone
          target: finalize
      else: review                # loop: wait `wait`s and re-check (step not re-run)
      wait: 60
  - id: finalize
    step: Finalize
    per_subject: false            # barrier: runs once after all subjects arrive
    next: null                    # terminal
```

`next` is a step id, `null` (terminal), or a branch (`if` / `else` / `wait`). A
branch target pointing at an earlier step forms a retry cycle. `on_error: ignore`
skips a failed subject instead of stopping the run.

Built-ins: `DiscoverSubjects` (one subject per input sub-dir; `config: {single: true}`
for a single-token dataset) and `ManualApproval` (`type: manual_approval` — a barrier
that waits for a confirmation marker file).

## Progress reporting

The engine continuously writes a per-subject `report.yaml` in the exact shape
MedPerf already ships, so `medperf dataset prepare` streams live progress with no
extra work.

## Build & run

```bash
./template/build.sh my-org/my-data-prep:0.0.1     # builds the image
# then register the container_config.yaml with MedPerf as a normal data preparator
```

## Develop / test the engine

```bash
pip install -e .[test]
pytest
```
