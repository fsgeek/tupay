// derives: C1.1, C1.4, F1.1, F1.2, T1, A1, A2, E1
package main

import (
	"path/filepath"
	"testing"

	"github.com/hashicorp/raft"
)

// nonGrantorFixture uses non-lexical numeric order and controlled process availability.
// derives: C1.4, F1.1, A1
func nonGrantorFixture() *Engine {
	s := fixtureSchedule()
	s.Processes.Lease = []string{"n10", "n3", "n2"}
	e := &Engine{schedule: s, storage: "s", grantor: "n10", nodes: map[string]*LeaseNode{}}
	for _, id := range s.Processes.Lease {
		e.nodes[id] = &LeaseNode{id: id, peer: &raft.Raft{}}
	}
	return e
}

// TestV21A1_LowestUpNode checks number order, grantor exclusion and unavailable nodes.
// derives: C1.1, C1.4, F1.1, A1, A2
func TestV21A1_LowestUpNode(t *testing.T) {
	e := nonGrantorFixture()
	e.grantor = "n3"
	selected, err := e.nonGrantor()
	if err != nil || selected != "n2" {
		t.Fatalf("numeric selection=%s: %v", selected, err)
	}
	e.nodes["n2"].peer = nil
	selected, err = e.nonGrantor()
	if err != nil || selected != "n10" {
		t.Fatalf("down node included: %s %v", selected, err)
	}
	e.nodes["n10"].peer = nil
	if _, err = e.nonGrantor(); err == nil {
		t.Fatal("selected unavailable follower")
	}
	e = nonGrantorFixture()
	e.grantor = ""
	if _, err = e.nonGrantor(); err == nil {
		t.Fatal("selector resolved before observable Grant")
	}
	e = nonGrantorFixture()
	e.schedule.Processes.Lease = []string{"n10", "peer"}
	e.nodes["peer"] = &LeaseNode{id: "peer", peer: &raft.Raft{}}
	if _, err = e.nonGrantor(); err == nil {
		t.Fatal("unnumbered candidate silently ordered")
	}
}

// TestV21A1_FrozenCrashAndRememberedRestart checks normative v2.2 A1 restart binding.
// derives: C1.4, F1.1, A1, A2
func TestV21A1_FrozenCrashAndRememberedRestart(t *testing.T) {
	e := nonGrantorFixture()
	f, err := e.freezeAction(Action{Cell: "F1.1", Crash: "non-grantor"})
	if err != nil {
		t.Fatal(err)
	}
	if f.Actions[0].Crash != "n2" || f.NonGrantorCrash != "n2" {
		t.Fatalf("crash selection=%+v", f)
	}
	if e.lastNonGrantor != "" {
		t.Fatal("mere resolution changed crash history")
	}
	e.grantor = "n2"
	if f.Actions[0].Crash != "n2" {
		t.Fatal("target changed after firing")
	}
	e.lastNonGrantor = "n3"
	e.nodes["n3"].peer = nil
	restart, err := e.freezeAction(Action{Cell: "F1.1", Restart: "non-grantor"})
	if err != nil || restart.Actions[0].Restart != "n3" {
		t.Fatalf("restart reselected an up candidate: %+v %v", restart, err)
	}
	e.lastNonGrantor = ""
	if _, err = e.freezeAction(Action{Cell: "F1.1", Restart: "non-grantor"}); err == nil {
		t.Fatal("restart without selector crash accepted")
	}
}

// TestV21A1_PartitionAndRoles checks every process-selector position's role discipline.
// derives: C1.4, F1.1, F1.2, F1.3, A1, A2
func TestV21A1_PartitionAndRoles(t *testing.T) {
	e := nonGrantorFixture()
	f, err := e.freezeAction(Action{Cell: "F1.2", Partition: [][]string{{"non-grantor"}, {"rest"}}})
	if err != nil {
		t.Fatal(err)
	}
	if len(f.Actions[0].Partition[0]) != 1 || f.Actions[0].Partition[0][0] != "n2" {
		t.Fatalf("partition selector=%+v", f)
	}
	for _, a := range []Action{{Request: "non-grantor"}, {Write: "non-grantor"}, {Cell: "F1.3", Pause: "non-grantor"}, {Cell: "F1.3", Resume: "non-grantor"}} {
		if err := validateAction(a, processRoles(e.schedule)); err == nil {
			t.Fatalf("lease selector accepted for client-only operation: %+v", a)
		}
	}
	s := fixtureSchedule()
	s.Steps = []Step{{At: Trigger{Start: true}, Do: Action{Cell: "F1.1", Crash: "non-grantor"}}}
	if err := validateSequence(s, processRoles(s)); err == nil {
		t.Fatal("unbound non-grantor accepted statically")
	}
	s.Steps = []Step{{At: Trigger{Filters: map[string]string{"event": "Grant", "client": "c1"}}, Do: Action{Cell: "F1.1", Restart: "non-grantor"}}}
	if err := validateSequence(s, processRoles(s)); err == nil {
		t.Fatal("restart without selector crash accepted statically")
	}
}

// TestV21P10A1_Lifecycle observes the shared schedule's crash/restart selection and liveness.
// derives: C1.4, F1.1, T1, A1, A2, E1
func TestV21P10A1_Lifecycle(t *testing.T) {
	s, err := loadSchedule("P10")
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(t.TempDir(), "p10.jsonl")
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
		t.Fatalf("shared P10: %+v", v)
	}
	grantor, crashed := "", ""
	faults, grants := 0, 0
	for _, event := range out.events {
		if event.Event == "Grant" {
			grantor = event.Proc
			grants++
		}
		if event.Event != "Fault" {
			continue
		}
		faults++
		switch faults {
		case 1:
			want := "n1"
			if grantor == want {
				want = "n2"
			}
			if event.Crash != want {
				t.Fatalf("non-grantor=%s, want %s excluding %s", event.Crash, want, grantor)
			}
			crashed = event.Crash
		case 2:
			if event.Restart != crashed {
				t.Fatalf("restart=%s, original crash=%s", event.Restart, crashed)
			}
		case 3:
			if event.Crash != grantor {
				t.Fatalf("grantor crash=%s, last grantor=%s", event.Crash, grantor)
			}
		}
	}
	if faults != 3 || grants != 3 {
		t.Fatalf("faults=%d grants=%d", faults, grants)
	}
	if e.lastNonGrantor != crashed {
		t.Fatalf("applied crash not remembered: %s != %s", e.lastNonGrantor, crashed)
	}
}
