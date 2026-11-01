# Brief: plant one defect

This directory holds a working artifact (`impl/` or `model/`) built from the service contract `contract/v3.md`
and the failure model `failure-model/v3.md`, with the schedule format `testbed/schedule-format.md` and the
other inputs beside them. Your task is to introduce **exactly one defect** and supply a schedule that witnesses it.

1. The defect makes the artifact **violate one named clause** of `contract/v3.md`.
2. The defect is in **lease-node, client or storage** behaviour only: not in the testbed, the schedule compiler,
   the trace emitter or recording code, the checks, or the tests.
3. The violation is **reachable by a schedule the format can express**. Write that schedule as `WITNESS.yaml` at
   the top of this directory. Run against your planted artifact, it must produce a FAIL of the clause you name.
4. Write `PLANT.md`: the clause violated, every file and line you changed, what the defect does, and how
   `WITNESS.yaml` reaches it.
5. Change nothing else. There is no git repository here; do not create one.

You may build and run the artifact as much as you like to check your witness. Work only in this directory.
When you are done, say so and stop.
