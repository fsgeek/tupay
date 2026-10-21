# Brief: both authors, adaptation to schedule format v2.1

Same access list as your v2 brief (`docs/briefs/adapt-v2-model.md` or `adapt-v2-impl.md`); the other side's directory is absent from your checkout on purpose. Read `testbed/schedule-format.md` (now v2.1; changelog at the end) and `testbed/schedules/P10.yaml` (rewritten).

Two changes. T1 now says that a predecessor step's own synchronous events count as after the next trigger was armed; both of you already read v2 this way, so expect no behaviour change, but tag the rule. A new selector `non-grantor` (rule A1): a lease node other than `grantor` that is up when the trigger fires; the model explores every such node, the impl picks the lowest-numbered. `restart: non-grantor` names the node that was crashed by the most recent `crash: non-grantor`.

Order: commit predictions for all thirteen schedules and the mutations first; adapt; run everything; README interpretations additively; commit the adapted version. Report commit hash, results, wall-clock time.
