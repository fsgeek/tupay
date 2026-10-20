// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

// checkerFixture is hand-authored evidence, independent of the running service.
// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3
func checkerFixture() []Event {
	zero := uint64(0)
	return []Event{
		{Proc: "c1", Seq: 1, Event: "Request", Client: "c1", Key: "k"},
		{Proc: "n1", Seq: 1, Event: "Grant", Client: "c1", Key: "k", Token: 7, Term: 2, Lifetime: 40, Causes: []Ref{{"c1", 1}}},
		{Proc: "c1", Seq: 2, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "v", Causes: []Ref{{"n1", 1}}},
		{Proc: "s", Seq: 1, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &zero, Causes: []Ref{{"c1", 2}}},
		{Proc: "c1", Seq: 3, Event: "WriteAck", Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"s", 1}}},
	}
}

// writeFixture deliberately reverses JSONL line order to rule out clock/line ordering.
// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3
func writeFixture(t *testing.T, events []Event) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "trace.jsonl")
	f, err := os.Create(path)
	if err != nil {
		t.Fatal(err)
	}
	encoder := json.NewEncoder(f)
	for i := len(events) - 1; i >= 0; i-- {
		e := events[i]
		e.Run = "fixture"
		e.Side = "impl"
		if e.Causes == nil {
			e.Causes = []Ref{}
		}
		if err := encoder.Encode(e); err != nil {
			t.Fatal(err)
		}
	}
	if err := f.Close(); err != nil {
		t.Fatal(err)
	}
	return path
}

// fixtureSchedule describes identities only; it is not a second service implementation.
// derives: C1.1, C1.2, C1.3, C1.4
func fixtureSchedule() Schedule {
	var s Schedule
	s.Processes.Lease = []string{"n1", "n2", "n3"}
	s.Processes.Clients = []string{"c1", "c2"}
	s.Processes.Storage = []string{"s"}
	return s
}

// TestC11C12C13_CausalOrder accepts valid evidence independent of line serialization.
// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3
func TestC11C12C13_CausalOrder(t *testing.T) {
	v := checkTrace(writeFixture(t, checkerFixture()), fixtureSchedule(), RunEvidence{Completed: true})
	if v != (Verdict{}) {
		t.Fatalf("valid reversed trace: %+v", v)
	}
}

// TestC11_F11_ReusedToken is an independent counterexample to monotonic grants.
// derives: C1.1, F1.1
func TestC11_F11_ReusedToken(t *testing.T) {
	events := checkerFixture()
	events = append(events, Event{Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k"}, Event{Proc: "n2", Seq: 1, Event: "Grant", Client: "c2", Key: "k", Token: 7, Term: 3, Lifetime: 40, Causes: []Ref{{"c2", 1}, {"n1", 1}}})
	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
	if v.Clause != "C1.1" {
		t.Fatalf("wanted C1.1, got %+v", v)
	}
}

// TestC12_F11_LedgerLoss rejects a forged post-restart highest_before.
// derives: C1.2, F1.1
func TestC12_F11_LedgerLoss(t *testing.T) {
	events := checkerFixture()
	zero := uint64(0)
	events = append(events, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &zero, Causes: []Ref{{"c1", 2}}})
	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
	if v.Clause != "C1.2" {
		t.Fatalf("wanted C1.2, got %+v", v)
	}
}

// TestC12_F12_EqualTokenAllowed guards against an invalid greater-than mutation.
// derives: C1.2, F1.2
func TestC12_F12_EqualTokenAllowed(t *testing.T) {
	events := checkerFixture()
	seven := uint64(7)
	events = append(events, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Causes: []Ref{{"c1", 2}}})
	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
	if v != (Verdict{}) {
		t.Fatalf("equal token must be accepted: %+v", v)
	}
}

// TestC13_F12_UnacceptedAttempt distinguishes a ghost success from a lost real ack.
// derives: C1.3, F1.2
func TestC13_F12_UnacceptedAttempt(t *testing.T) {
	events := checkerFixture()
	events = append(events, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "different-attempt", Causes: []Ref{{"n1", 1}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"c1", 4}}})
	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
	if v.Clause != "C1.3" {
		t.Fatalf("wanted C1.3, got %+v", v)
	}
}

// TestC13_F13_MissingLinkUnexplained avoids calling a provenance gap a safety failure.
// derives: C1.3, F1.3
func TestC13_F13_MissingLinkUnexplained(t *testing.T) {
	events := checkerFixture()
	events[4].Causes = []Ref{{"c1", 2}}
	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
	if v.Clause != "" || v.Reason == "" {
		t.Fatalf("wanted UNEXPLAINED, got %+v", v)
	}
}

// TestC14_F11_ProgressHorizon distinguishes a finite liveness witness from a timeout.
// derives: C1.4, F1.1
func TestC14_F11_ProgressHorizon(t *testing.T) {
	events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F1.1", Crash: "n1"}, {Proc: "c1", Seq: 1, Event: "Request", Client: "c1", Key: "k", Causes: []Ref{{"env", 1}}}}
	path := writeFixture(t, events)
	v := checkTrace(path, fixtureSchedule(), RunEvidence{Reason: "timeout"})
	if v.Clause != "" || v.Reason == "" {
		t.Fatalf("timeout alone is not C1.4: %+v", v)
	}
	evidence := RunEvidence{Witnesses: []ProgressWitness{{Request: Ref{"c1", 1}, StableFault: Ref{"env", 1}, BudgetMillis: 3000}}}
	v = checkTrace(path, fixtureSchedule(), evidence)
	if v.Clause != "C1.4" {
		t.Fatalf("wanted C1.4 with eligible horizon: %+v", v)
	}
}

// TestCompiler_F12_F13_RejectUnknown rejects out-of-model faults before execution.
// derives: F1.2, F1.3, C1.4
func TestCompiler_F12_F13_RejectUnknown(t *testing.T) {
	ids := map[string]string{"c1": "client", "n1": "lease", "s": "storage"}
	for _, a := range []Action{{Cell: "X2", Partition: [][]string{{"c1"}, {"rest"}}}, {Cell: "F1.3", Pause: "n1"}, {Cell: "F1.1", Crash: "missing"}, {Request: "c1", Write: "c1"}} {
		if err := validateAction(a, ids); err == nil {
			t.Fatalf("accepted invalid action %+v", a)
		}
	}
}
