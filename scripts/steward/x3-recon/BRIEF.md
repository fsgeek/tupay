# Brief: choose one out-of-model failure

This directory holds a working implementation built from the service contract `contract/v3.md` and the failure
model `failure-model/v3.md`, with its shared schedules in `testbed/schedules/` and the schedule format beside them.

Someone else will add a **hook** to a copy of this implementation and run one schedule with it. A hook changes the
implementation's state or message delivery in service code; it never touches the code that records traces, so the
records report the hooked state truthfully. Your task is to choose the schedule and the hook.

1. Choose **one schedule** from these 59: P1 to P33, P40 to P54, P58 to P63, false-suspicion-v1, H7, H8, H9, H10.
2. Choose **one hook class**, exactly one of:
   - **ledger rollback**: storage's highest accepted token is set below a token it has already accepted, without a restart;
   - **lost durable record at a lease node**: an ordinary restart of a lease node that keeps all but one record it wrote durably;
   - **duplicated grant reply delivered after a newer grant**: a client receives an old grant reply again after a newer token was granted;
   - **storage restart from an older state**: storage restarts with the ledger and value it had at an earlier point.
3. Give its **parameters** precisely enough to implement without asking: which process, at which point of the
   schedule (step or event), and which value, record or reply.
4. Write `CHOICE.md` with: the schedule, the hook class, the parameters, and the failure you expect it to cause
   (which clause of `contract/v3.md`, if any, and which decision).

Create `CHOICE.md` and change nothing else. There is no git repository here; do not create one. You may read and
run anything here. When you are done, say so and stop.
