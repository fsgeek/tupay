// derives: C1.1, C1.4, F1.1, F2.1, F2.2, L3, T3
package main

import (
	"fmt"
	"path/filepath"
	"testing"
)

// derives: C1.1, C1.4, F2.2
func TestFixRIssuanceBeforeReceipt(t *testing.T) {
	out, err := newEmitter(filepath.Join(t.TempDir(), "issued.jsonl"), "issued")
	if err != nil {
		t.Fatal(err)
	}
	defer out.close()
	e, err := newEngine(fixtureSchedule(), out, 1, "")
	if err != nil {
		t.Fatal(err)
	}
	defer e.close()
	if err = e.request("c2"); err != nil {
		t.Fatal(err)
	}
	r := e.requests[0]
	n := e.nodes["n1"]
	e.down[link{"n1", "c2"}] = true
	e.finishAllocation(completedAllocation{request: r, node: "n1", generation: n.generation, allocation: Allocation{7, 2}})
	if len(out.events) != 2 || out.events[1].Event != "Grant" {
		t.Fatal("issued-but-undelivered Grant omitted")
	}
	if r.done || len(e.clients["c2"].grants) != 0 {
		t.Fatal("issuance completed request without receipt")
	}
}

// A recorded reply with no receipt must not mask the already-satisfied premise.
// derives: C1.4, F2.2, L3
func TestFixRC14IssuedNotDelivered(t *testing.T) {
	es := []Event{
		{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.2", Links: [][]string{{"n1", "c2"}}},
		{Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1}}},
		{Proc: "n1", Seq: 1, Event: "Grant", Client: "c2", Key: "k", Token: 7, Term: 2, Lifetime: 40, Causes: []Ref{{"c2", 1}}},
	}
	evidence := RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1}, Ref{"env", 1}, 3000}}, Reason: "horizon exhausted"}
	v := checkTrace(writeFixture(t, es), fixtureSchedule(), evidence)
	if v.Clause != "C1.4" {
		t.Fatalf("undelivered issuance masked liveness: %+v", v)
	}
}

// Rename the shared topology in memory to exclude schedule-name routing branches.
// derives: C1.1, C1.4, F1.1, F2.1, F2.2, L3, T3
func TestFixRRenamedRoutingShapes(t *testing.T) {
	for _, name := range []string{"H8", "H9"} {
		t.Run(name, func(t *testing.T) {
			s, err := loadSchedule(name)
			if err != nil {
				t.Fatal(err)
			}
			s.Name = "renamed-" + name
			path := filepath.Join(t.TempDir(), "routing.jsonl")
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
			if err = out.close(); err != nil {
				t.Fatal(err)
			}
			if v := checkTrace(path, s, evidence); v != (Verdict{}) {
				t.Fatalf("routing shape failed: %+v", v)
			}
		})
	}
}

// Directional request and reply routes are independent; no schedule-name oracle.
// derives: C1.1, C1.4, F2.2, L3
func TestFixRDirectedRoutes(t *testing.T) {
	cases := [][][]string{
		{{"c2", "grantor"}},
		{{"grantor", "c2"}},
		{{"c2", "grantor"}, {"grantor", "c2"}, {"non-grantor", "grantor"}},
	}
	for index, pairs := range cases {
		t.Run(fmt.Sprint(index), func(t *testing.T) {
			s, err := loadSchedule("H9")
			if err != nil {
				t.Fatal(err)
			}
			s.Name = "directed-route-shape"
			s.Steps[1].Do = Action{Cell: "F2.2", Drop: pairs}
			path := filepath.Join(t.TempDir(), "directed.jsonl")
			out, err := newEmitter(path, s.Name)
			if err != nil {
				t.Fatal(err)
			}
			e, err := newEngine(s, out, int64(index+1), "")
			if err != nil {
				out.close()
				t.Fatal(err)
			}
			ev := e.drive()
			e.close()
			out.close()
			if v := checkTrace(path, s, ev); v != (Verdict{}) {
				t.Fatalf("directional routing failed: %+v", v)
			}
			if len(ev.Deliveries) != 2 {
				t.Fatalf("missing client receipts: %+v", ev.Deliveries)
			}
			// Make sure plausibility checks reject altered route evidence.
			d := ev.Deliveries[1]
			d.ReplyHops = append([]RouteHop{}, d.ReplyHops...)
			d.ReplyHops[0].ToGeneration++
			ev.Deliveries = append([]GrantDelivery{}, ev.Deliveries...)
			ev.Deliveries[1] = d
			v := checkTrace(path, s, ev)
			if v.Clause != "" || v.Reason == "" {
				t.Fatalf("bad route evidence not unexplained: %+v", v)
			}
		})
	}
}

// An unreachable requester must not monopolize the serialized allocation service.
// derives: C1.1, C1.4, F2.2, L3, T3
func TestFixRFairStandingRequests(t *testing.T) {
	s := fixtureSchedule()
	s.Name = "fair-standing-requests"
	s.Bound.Events = 200
	s.Steps = []Step{
		{At: Trigger{Start: true}, Do: Action{Request: "c1"}},
		{At: Trigger{Filters: map[string]string{"event": "Grant", "client": "c1"}}, Do: Action{Write: "c1", Value: "initial"}},
		{At: Trigger{Filters: map[string]string{"event": "WriteAck", "client": "c1"}}, Do: Action{Cell: "F2.2", Drop: [][]string{{"n1", "c1"}, {"n2", "c1"}, {"n3", "c1"}}}},
		{At: Trigger{Start: true}, Do: Action{Request: "c1"}},
		{At: Trigger{Start: true}, Do: Action{Request: "c2"}},
		{At: Trigger{Start: true}, Do: Action{Write: "c2", Value: "eligible"}},
	}
	s.End = Trigger{Filters: map[string]string{"event": "WriteAck", "client": "c2", "outcome": "accepted"}}
	path := filepath.Join(t.TempDir(), "fair.jsonl")
	out, err := newEmitter(path, s.Name)
	if err != nil {
		t.Fatal(err)
	}
	e, err := newEngine(s, out, 1, "")
	if err != nil {
		out.close()
		t.Fatal(err)
	}
	ev := e.drive()
	e.close()
	out.close()
	if v := checkTrace(path, s, ev); v != (Verdict{}) {
		t.Fatalf("eligible requester starved: %+v", v)
	}
}

// An expired old grant must not satisfy readiness for a pause after renewal issuance.
// derives: C1.1, C1.4, F1.3, F2.1, F2.2, T3
func TestFixRRenewalPauseWaitsForReceipt(t *testing.T) {
	s := fixtureSchedule()
	s.Name = "renewal-pause"
	s.Bound.Events = 200
	s.End = Trigger{Quiescent: true}
	s.Steps = []Step{
		{At: Trigger{Start: true}, Do: Action{Request: "c1"}},
		{At: Trigger{Filters: map[string]string{"event": "Grant", "client": "c1"}}, Do: Action{Request: "c1"}},
		{At: Trigger{Filters: map[string]string{"event": "Grant", "client": "c1"}}, Do: Action{Cell: "F1.3", Pause: "holder"}},
		{At: Trigger{Start: true}, Do: Action{Request: "c2"}},
		{At: Trigger{Filters: map[string]string{"event": "Grant", "client": "c2"}}, Do: Action{Cell: "F1.3", Resume: "c1"}},
	}
	path := filepath.Join(t.TempDir(), "renewal.jsonl")
	out, err := newEmitter(path, s.Name)
	if err != nil {
		t.Fatal(err)
	}
	e, err := newEngine(s, out, 1, "")
	if err != nil {
		out.close()
		t.Fatal(err)
	}
	ev := e.drive()
	e.close()
	out.close()
	if v := checkTrace(path, s, ev); v != (Verdict{}) {
		t.Fatalf("renewal pause failed: %+v", v)
	}
}
