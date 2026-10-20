// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
package main

import (
	"path/filepath"
	"testing"
	"time"
)

// TestV2T1_FreshTrigger excludes matching events emitted before arming.
// derives: C1.1, F1.1, T1
func TestV2T1_FreshTrigger(t *testing.T) {
	trigger := Trigger{Filters: map[string]string{"event": "Grant", "client": "c1"}}
	events := []Event{{Proc: "n1", Seq: 1, Event: "Grant", Client: "c1"}}
	if _, ok := triggerRef(trigger, events, 1); ok {
		t.Fatal("historical event matched after arming")
	}
	events = append(events, Event{Proc: "n2", Seq: 1, Event: "Grant", Client: "c1"})
	if ref, ok := triggerRef(trigger, events, 1); !ok || ref != (Ref{"n2", 1}) {
		t.Fatalf("fresh event not matched: %v %v", ref, ok)
	}
}

// TestV2A1_FrozenSelectors checks binding before subsequent grants or action delay.
// derives: C1.1, F1.1, F1.2, T2, A1
func TestV2A1_FrozenSelectors(t *testing.T) {
	e := &Engine{schedule: fixtureSchedule(), storage: "s", grantor: "n1", holder: "c1"}
	f, err := e.freezeAction(Action{Cell: "F1.1", Crash: "grantor"})
	if err != nil {
		t.Fatal(err)
	}
	e.grantor = "n2"
	e.holder = "c2"
	if f.Actions[0].Crash != "n1" {
		t.Fatal("selector rebound after firing")
	}
	partition, err := e.freezeAction(Action{Cell: "F1.2", Partition: [][]string{{"grantor", "holder"}, {"rest"}}})
	if err != nil {
		t.Fatal(err)
	}
	if !partition.HasRest || len(partition.Rest) != 4 {
		t.Fatalf("rest complement: %+v", partition)
	}
	e.rest = []string{"c1", "c2"}
	group, err := e.freezeAction(Action{Cell: "F1.3", Pause: "rest"})
	if err != nil || len(group.Actions) != 2 {
		t.Fatalf("standalone rest context: %+v %v", group, err)
	}
	if group.Actions[0].Pause != "c1" || group.Actions[1].Pause != "c2" {
		t.Fatal("group selector omitted target")
	}
}

// TestV2A2_InvalidSchedules rejects definite illegal transitions before execution.
// derives: C1.4, F1.1, F1.3, A1, A2
func TestV2A2_InvalidSchedules(t *testing.T) {
	cases := [][]Action{
		{{Cell: "F1.1", Crash: "grantor"}},
		{{Cell: "F1.1", Restart: "n1"}},
		{{Cell: "F1.1", Crash: "n1"}, {Cell: "F1.1", Crash: "n1"}},
		{{Cell: "F1.3", Pause: "c1"}, {Cell: "F1.3", Pause: "c1"}},
		{{Cell: "F1.3", Resume: "c1"}},
		{{Cell: "F1.3", Pause: "n1"}},
		{{Cell: "F1.1", Crash: "rest"}},
	}
	for index, actions := range cases {
		s := fixtureSchedule()
		for _, a := range actions {
			s.Steps = append(s.Steps, Step{At: Trigger{Start: true}, Do: a})
		}
		err := validateSequence(s, processRoles(s))
		for _, a := range actions {
			if other := validateAction(a, processRoles(s)); other != nil {
				err = other
			}
		}
		if err == nil {
			t.Errorf("invalid schedule %d accepted", index)
		}
	}
}

// TestV2T3_ExpiredIsNotSuperseded protects the numeric definition of stale.
// derives: C1.1, C1.2, F1.3, T3
func TestV2T3_ExpiredIsNotSuperseded(t *testing.T) {
	c := &Client{id: "c1", up: true, generation: 1, grants: []HeldGrant{{token: 7, expires: time.Now().Add(-time.Hour)}}}
	e := &Engine{clients: map[string]*Client{"c1": c}, out: &Emitter{events: []Event{{Event: "Grant", Token: 7}}}}
	f := FrozenAction{Actions: []Action{{Write: "c1", Token: "stale"}}}
	if e.workloadReady(f) {
		t.Fatal("expiry alone counted as supersession")
	}
	e.out.events = append(e.out.events, Event{Event: "Grant", Token: 8})
	if !e.workloadReady(f) {
		t.Fatal("strictly superseded token unavailable")
	}
	c.paused = true
	if e.workloadReady(f) {
		t.Fatal("paused workload did not wait")
	}
}

// TestV2E1_ActiveWorkOnly distinguishes paused inboxes from active pending work.
// derives: C1.3, C1.4, F1.1, F1.3, E1
func TestV2E1_ActiveWorkOnly(t *testing.T) {
	c := &Client{id: "c1", up: true, generation: 1}
	e := &Engine{clients: map[string]*Client{"c1": c}, requests: []*RequestState{{client: "c1", generation: 1}}}
	if e.quiescent() {
		t.Fatal("pending active request ignored")
	}
	c.paused = true
	if !e.quiescent() {
		t.Fatal("paused requester counted")
	}
	e.requests = nil
	e.wire = []WireMessage{{kind: "ack", client: "c1", generation: 1}}
	if !e.quiescent() {
		t.Fatal("paused inbox counted")
	}
	c.paused = false
	if e.quiescent() {
		t.Fatal("active inbox ignored")
	}
	c.generation++
	if !e.quiescent() {
		t.Fatal("old incarnation counted")
	}
}

// TestV2T1T3_SynchronousEffects exercises fresh arming and both workload waits.
// derives: C1.1, C1.2, C1.3, C1.4, T1, T2, T3, E1
func TestV2T1T3_SynchronousEffects(t *testing.T) {
	for _, second := range []Action{{Write: "c1", Value: "waiting-for-token"}, {Request: "c1"}} {
		s := fixtureSchedule()
		s.Name = "v2-synchronous"
		s.Bound.Events = 200
		s.End = Trigger{Quiescent: true}
		s.Steps = []Step{{At: Trigger{Start: true}, Do: Action{Request: "c1"}}, {At: Trigger{Filters: map[string]string{"event": "Request", "client": "c1"}}, Do: second}}
		path := filepath.Join(t.TempDir(), "events.jsonl")
		out, err := newEmitter(path, s.Name)
		if err != nil {
			t.Fatal(err)
		}
		e, err := newEngine(s, out, 1, "")
		if err != nil {
			out.close()
			t.Fatal(err)
		}
		evidence := e.drive()
		e.close()
		if err := out.close(); err != nil {
			t.Fatal(err)
		}
		v := checkTrace(path, s, evidence)
		if v != (Verdict{}) {
			t.Fatalf("synchronous action lost or T3 did not wait: %+v", v)
		}
		grants := 0
		for _, event := range out.events {
			if event.Event == "Grant" {
				grants++
			}
		}
		expected := 1
		if second.Request != "" {
			expected = 2
		}
		if grants != expected {
			t.Fatalf("grants=%d, want %d", grants, expected)
		}
	}
}

// TestV2E2_SafetyBeforeUnreachableEnd does not turn a witnessed violation into timeout.
// derives: C1.3, F1.2, E1, E2
func TestV2E2_SafetyBeforeUnreachableEnd(t *testing.T) {
	events := checkerFixture()
	events = append(events, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Causes: []Ref{{"n1", 1}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"c1", 4}}})
	evidence := RunEvidence{Reason: "end unreachable", Operational: "later resource problem"}
	v := checkTrace(writeFixture(t, events), fixtureSchedule(), evidence)
	if v.Clause != "C1.3" {
		t.Fatalf("safety failure hidden by incomplete end: %+v", v)
	}
}

// TestV2SharedSchedules_OnlyRoot compiles all shared inputs and rejects private paths.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T3, A1, A2, E1
func TestV2SharedSchedules_OnlyRoot(t *testing.T) {
	for _, name := range []string{"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12", "false-suspicion-v1"} {
		s, err := loadSchedule(name)
		if err != nil {
			t.Errorf("shared %s: %v", name, err)
		} else if !s.End.Quiescent {
			t.Errorf("shared %s missing quiescent", name)
		}
	}
	if _, err := loadSchedule("testbed/schedules/P1.yaml"); err == nil {
		t.Fatal("private path accepted")
	}
}

// TestV2T1E1_EndSeesActionEffect checks an end armed at the final action boundary.
// derives: C1.1, C1.4, T1, E1
func TestV2T1E1_EndSeesActionEffect(t *testing.T) {
	s := fixtureSchedule()
	s.Name = "v2-end-action"
	s.Bound.Events = 200
	s.Steps = []Step{{At: Trigger{Start: true}, Do: Action{Request: "c1"}}}
	s.End = Trigger{Filters: map[string]string{"event": "Request", "client": "c1"}}
	out, err := newEmitter(filepath.Join(t.TempDir(), "end.jsonl"), s.Name)
	if err != nil {
		t.Fatal(err)
	}
	e, err := newEngine(s, out, 2, "")
	if err != nil {
		out.close()
		t.Fatal(err)
	}
	evidence := e.drive()
	e.close()
	if err := out.close(); err != nil {
		t.Fatal(err)
	}
	if !evidence.Completed {
		t.Fatalf("end missed synchronous final-action event: %+v", evidence)
	}
}

// TestV2A1_AllHolderTargets checks selector placement on every role-valid operation.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.3, A1, A2, T3
func TestV2A1_AllHolderTargets(t *testing.T) {
	e := &Engine{schedule: fixtureSchedule(), holder: "c2", grantor: "n2", storage: "s"}
	actions := []Action{{Request: "holder"}, {Write: "holder"}, {Cell: "F1.1", Crash: "holder"}, {Cell: "F1.1", Restart: "holder"}, {Cell: "F1.3", Pause: "holder"}, {Cell: "F1.3", Resume: "holder"}}
	for _, a := range actions {
		f, err := e.freezeAction(a)
		if err != nil {
			t.Fatalf("alias rejected for %+v: %v", a, err)
		}
		if len(f.Actions) != 1 || actionTarget(f.Actions[0]) != "c2" {
			t.Fatalf("holder binding: %+v", f)
		}
	}
}
