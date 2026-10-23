# Brief: review the X3 inputs for defects (read-only)

You are reviewing five draft input files for a change experiment, before anyone builds from them: `contract/v3.md`, `failure-model/v3.md`, the "v5 addendum" at the end of `observe/schema.md`, the "v5 addendum" at the end of `testbed/schedule-format.md`, and `tests/pairs-v4.md` (pairs P31 to P54 are new). Earlier sections of the schema and format files are fixed history; review them only as they bear on v5. Two independent authors will later build, from these files alone, a TLA+ model and a Go implementation of a lease service with fencing tokens whose lease-node membership changes at run time. They will not be able to ask questions.

Find defects: places where two careful authors could read the inputs differently and both be faithful; clauses no artifact can satisfy under the failure model (impossible obligations); clauses any artifact satisfies trivially (vacuous ones, e.g. by refusing everything); terms used but not defined; observable events whose fields cannot be produced by a process that only knows its own state; things that contradict each other; and anything a careful systems reviewer would object to. For each defect: where it is, why it is a defect, a concrete scenario showing it if you can, and a suggested repair. Rank by how much it would change what authors build.

Then say, separately, which single schedule (a sequence of faults and requests) you would expect to break most artifacts built from these inputs, in one paragraph. Do not write the schedule in any format.

Do not modify any file. Do not look for or use anything outside this directory; there is nothing else here to find. Write your answer to stdout.
