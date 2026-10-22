// derives: C1.1, C1.3, C1.4, C2.2, F1.1, F1.2, F2.1, F2.2, L1, L2, L3, E1, E3, T3
package main

import (
	"encoding/json"
	"fmt"
	raft "go.etcd.io/raft/v3"
	pb "go.etcd.io/raft/v3/raftpb"
	"math/rand"
	"path/filepath"
	"testing"
	"time"
)

// derives: C1.1, C1.4, F2.1, F2.2, L1, L2
func TestX2SharedCompiler(t *testing.T) {
	for i := 1; i <= 30; i++ {
		if _, err := loadSchedule(fmt.Sprintf("P%d", i)); err != nil {
			t.Errorf("P%d: %v", i, err)
		}
	}
	ids := processRoles(fixtureSchedule())
	for _, a := range []Action{
		{Cell: "F2.1", Cut: [][]string{{"rest", "n1"}}},
		{Cell: "F2.2", Drop: [][]string{{"n1"}}},
		{Cell: "F2.1", Drop: [][]string{{"n1", "n2"}}},
		{Cell: "F2.2", Cut: [][]string{{"n1", "n2"}}},
		{Cell: "F2.2", Drop: [][]string{{"missing", "n1"}}},
	} {
		if validateAction(a, ids) == nil {
			t.Errorf("invalid action admitted: %+v", a)
		}
	}
	s := fixtureSchedule()
	s.Steps = []Step{{At: Trigger{Start: true}, Do: Action{Cell: "F2.1", Cut: [][]string{{"grantor", "n2"}}}}}
	if validateSequence(s, ids) == nil {
		t.Fatal("early link selector admitted")
	}
}

// derives: C1.1, C1.4, F1.1, F2.1, F2.2
func TestX2RaftDirectionsAndSendTime(t *testing.T) {
	n := newRaftNetwork()
	n.register("n1")
	n.register("n2")
	ticket, err := n.route("n1", "n2", pb.Message{})
	if err != nil {
		t.Fatal(err)
	}
	n.setDown(map[link]bool{{"n1", "n2"}: true})
	if n.response(ticket) != nil {
		t.Fatal("request direction incorrectly gates reverse reply")
	}
	if _, err = n.route("n1", "n2", pb.Message{}); err == nil {
		t.Fatal("down send admitted")
	}
	if _, err = n.route("n2", "n1", pb.Message{}); err != nil {
		t.Fatal("up reverse send lost")
	}
	n.setDown(map[link]bool{{"n2", "n1"}: true})
	if n.response(ticket) == nil {
		t.Fatal("reply sent on down reverse link")
	}
	n.setDown(nil)
	if n.response(ticket) != nil {
		t.Fatal("cut history incorrectly gates a new reply send")
	}
	n.remove("n2")
	n.register("n2")
	if n.response(ticket) == nil {
		t.Fatal("reply crossed incarnation")
	}
}

// derives: C1.3, C2.2, F2.1, F2.2, L1, L2, A1, T2
func TestX2AccumulationFrozenLinksAndSchema(t *testing.T) {
	out, err := newEmitter(filepath.Join(t.TempDir(), "links.jsonl"), "links")
	if err != nil {
		t.Fatal(err)
	}
	defer out.close()
	e := &Engine{schedule: fixtureSchedule(), storage: "s", grantor: "n1", holder: "c1", out: out, network: newRaftNetwork()}
	f, err := e.freezeAction(Action{Cell: "F2.1", Cut: [][]string{{"grantor", "n2"}, {"n1", "grantor"}, {"grantor", "n2"}}})
	if err != nil {
		t.Fatal(err)
	}
	e.grantor = "n3"
	if err = e.act(f.Actions[0], Ref{}); err != nil {
		t.Fatal(err)
	}
	if !e.down[link{"n1", "n2"}] || !e.down[link{"n2", "n1"}] || len(e.down) != 2 {
		t.Fatalf("not symmetric/resolved/deduplicated: %v", e.down)
	}
	if err = e.act(Action{Cell: "F2.2", Drop: [][]string{{"s", "c1"}}}, Ref{}); err != nil {
		t.Fatal(err)
	}
	if !e.down[link{"n1", "n2"}] || !e.down[link{"s", "c1"}] || e.down[link{"c1", "s"}] {
		t.Fatal("drop overwrote cut or affected reverse")
	}
	if err = e.act(Action{Cell: "F1.2", Partition: [][]string{{"n1"}, {"n2", "n3", "c1", "c2", "s"}}}, Ref{}); err != nil {
		t.Fatal(err)
	}
	if !e.down[link{"s", "c1"}] {
		t.Fatal("partition replaced previous drop")
	}
	if err = e.act(Action{Cell: "F2.2", Heal: true}, Ref{}); err != nil {
		t.Fatal(err)
	}
	if len(e.down) != 0 {
		t.Fatal("heal incomplete")
	}
	for i, v := range out.events {
		b, _ := json.Marshal(v)
		var fields map[string]json.RawMessage
		json.Unmarshal(b, &fields)
		if i == 0 && len(v.Links) != 2 {
			t.Fatal("cut links not directed")
		}
		if v.Heal && string(fields["links"]) != "[]" {
			t.Fatalf("heal omitted empty links: %s", b)
		}
	}
}

// derives: C1.3, C2.2, F1.1, F2.1, F2.2
func TestX2ApplicationSendFate(t *testing.T) {
	out, err := newEmitter(filepath.Join(t.TempDir(), "wire.jsonl"), "wire")
	if err != nil {
		t.Fatal(err)
	}
	defer out.close()
	e, err := newEngine(fixtureSchedule(), out, 1, "")
	if err != nil {
		t.Fatal(err)
	}
	defer e.close()
	c := e.clients["c1"]
	c.grants = []HeldGrant{{token: 7, ref: Ref{"n1", 1}}}
	if err = e.write("c1", "before-cut", ""); err != nil {
		t.Fatal(err)
	}
	if err = e.act(Action{Cell: "F2.1", Cut: [][]string{{"c1", "s"}}}, Ref{}); err != nil {
		t.Fatal(err)
	}
	e.deliver(time.Now().Add(time.Second))
	if e.storageValue != "before-cut" {
		t.Fatal("pre-cut sent write discarded at arrival")
	}
	// Reply is still local pending work; its actual send happens on the down link.
	e.deliver(time.Now().Add(2 * time.Second))
	for _, v := range out.events {
		if v.Event == "WriteAck" {
			t.Fatal("reply sent on down link")
		}
	}
	if err = e.write("c1", "lost", ""); err != nil {
		t.Fatal(err)
	}
	if err = e.act(Action{Cell: "F1.2", Heal: true}, Ref{}); err != nil {
		t.Fatal(err)
	}
	e.deliver(time.Now().Add(3 * time.Second))
	if e.storageValue != "before-cut" {
		t.Fatal("lost write resurrected")
	}
	// A sent reply survives a subsequent cut.
	if err = e.write("c1", "reply-before-cut", ""); err != nil {
		t.Fatal(err)
	}
	e.deliver(time.Now().Add(4 * time.Second))
	e.deliver(time.Now().Add(5 * time.Second))
	if err = e.act(Action{Cell: "F2.2", Drop: [][]string{{"s", "c1"}}}, Ref{}); err != nil {
		t.Fatal(err)
	}
	e.deliver(time.Now().Add(6 * time.Second))
	found := false
	for _, v := range out.events {
		if v.Event == "WriteAck" {
			found = true
		}
	}
	if !found {
		t.Fatal("pre-cut sent reply lost at arrival")
	}
}

// derives: C1.4, F2.1, F2.2, L3
func TestX2C14LiteralClique(t *testing.T) {
	// Every node reaches storage/client but no two lease nodes reach each other.
	for _, simplex := range []bool{false, true} {
		links := [][]string{}
		for i := 1; i <= 3; i++ {
			for j := i + 1; j <= 3; j++ {
				links = append(links, []string{fmt.Sprintf("n%d", i), fmt.Sprintf("n%d", j)})
				if !simplex {
					links = append(links, []string{fmt.Sprintf("n%d", j), fmt.Sprintf("n%d", i)})
				}
			}
		}
		events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.2", Links: links}, {Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1}}}}
		evidence := RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1}, Ref{"env", 1}, 3000}}}
		g, err := readTrace(writeFixture(t, events))
		if err != nil {
			t.Fatal(err)
		}
		if v := g.checkC14(fixtureSchedule(), evidence); v.Clause != "" || v.Reason == "" {
			t.Fatalf("non-clique certified: %+v", v)
		}
	}
	// The isolated current grantor is irrelevant: followers form a full clique.
	events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.1", Links: [][]string{{"n1", "n2"}, {"n2", "n1"}, {"n1", "n3"}, {"n3", "n1"}}}, {Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1}}}}
	g, err := readTrace(writeFixture(t, events))
	if err != nil {
		t.Fatal(err)
	}
	if v := g.checkC14(fixtureSchedule(), RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1}, Ref{"env", 1}, 3000}}}); v.Clause != "C1.4" {
		t.Fatalf("clique excluding grantor ignored: %+v", v)
	}
}

// derives: C1.4, F2.1, F2.2, E1, E3, T3
func TestX2E3BoundCannotPass(t *testing.T) {
	s := fixtureSchedule()
	s.Name = "bound"
	s.Bound.Events = 1
	s.End = Trigger{Quiescent: true}
	s.Steps = []Step{{At: Trigger{Start: true}, Do: Action{Request: "c1"}}, {At: Trigger{Start: true}, Do: Action{Cell: "F2.2", Heal: true}}}
	out, err := newEmitter(filepath.Join(t.TempDir(), "bound.jsonl"), s.Name)
	if err != nil {
		t.Fatal(err)
	}
	defer out.close()
	e, err := newEngine(s, out, 1, "")
	if err != nil {
		t.Fatal(err)
	}
	defer e.close()
	ev := e.drive()
	if ev.Completed || ev.Reason != "event bound reached" {
		t.Fatalf("bound completion: %+v", ev)
	}
}

// Local reply work is volatile, unlike messages already sent into the network.
// derives: C1.3, C2.2, F1.1, F2.1, F2.2
func TestX2StorageCrashLosesOnlyUnsentReplies(t *testing.T) {
	out, err := newEmitter(filepath.Join(t.TempDir(), "crash-replies.jsonl"), "crash-replies")
	if err != nil {
		t.Fatal(err)
	}
	defer out.close()
	e, err := newEngine(fixtureSchedule(), out, 1, "")
	if err != nil {
		t.Fatal(err)
	}
	defer e.close()
	e.wire = []WireMessage{
		{kind: "ack", client: "c1", generation: 1, pendingSend: true},
		{kind: "read-ack", client: "c1", generation: 1, pendingSend: true},
		{kind: "ack", client: "c1", generation: 1, decision: Ref{"s", 1}},
	}
	if err = e.act(Action{Cell: "F1.1", Crash: "s"}, Ref{}); err != nil {
		t.Fatal(err)
	}
	if err = e.act(Action{Cell: "F1.1", Restart: "s"}, Ref{}); err != nil {
		t.Fatal(err)
	}
	if len(e.wire) != 1 || e.wire[0].pendingSend {
		t.Fatalf("unsent reply survived crash: %+v", e.wire)
	}
	e.deliver(time.Now().Add(time.Second))
	if out.events[len(out.events)-1].Event != "WriteAck" {
		t.Fatal("already-sent reply discarded by sender restart")
	}
}

// These checks exercise live eligibility separately from the offline trace checker.
// derives: C1.4, F2.1, F2.2, L3
func TestX2RuntimeCliqueAndLostGrantStanding(t *testing.T) {
	out, err := newEmitter(filepath.Join(t.TempDir(), "request.jsonl"), "request")
	if err != nil {
		t.Fatal(err)
	}
	defer out.close()
	e := &Engine{rng: rand.New(rand.NewSource(1)), schedule: fixtureSchedule(), storage: "s", storageUp: true, clients: map[string]*Client{"c2": {id: "c2", up: true, generation: 1}}, nodes: map[string]*LeaseNode{}, down: map[link]bool{}, out: out}
	for _, id := range e.schedule.Processes.Lease {
		e.nodes[id] = &LeaseNode{peer: &raft.RawNode{}, generation: 1}
	}
	r := &RequestState{client: "c2", generation: 1, ref: Ref{"c2", 1}}
	if !e.eligible(r) {
		t.Fatal("full clique not eligible")
	}
	e.down = map[link]bool{{"n1", "n2"}: true, {"n1", "n3"}: true, {"n2", "n3"}: true}
	if e.eligible(r) {
		t.Fatal("runtime counted a mutually disconnected majority")
	}
	e.down = map[link]bool{{"n1", "n2"}: true, {"n1", "n3"}: true}
	if !e.eligible(r) {
		t.Fatal("runtime ignored followers' clique")
	}
	e.down = map[link]bool{{"n1", "c2"}: true}
	e.finishAllocation(completedAllocation{request: r, node: "n1", generation: 1, allocation: Allocation{7, 2}})
	if r.done || len(e.clients["c2"].grants) > 0 || len(out.events) != 1 || out.events[0].Event != "Grant" {
		t.Fatal("issuance/receipt were conflated")
	}
	// Break relaying just for the lost direct send; then restore the normal path.
	// derives: C1.4, F2.2, R2
	e.mutation = "R2"
	e.deliverLease(time.Now().Add(time.Second))
	if r.done {
		t.Fatal("lost reply ended requester standing")
	}
	e.mutation = ""
	e.down = nil
	e.finishAllocation(completedAllocation{request: r, node: "n2", generation: 1, allocation: Allocation{8, 2}})
	if r.done {
		t.Fatal("new issuance completed before receipt")
	}
	e.deliverLease(time.Now().Add(2 * time.Second))
	e.deliverLease(time.Now().Add(3 * time.Second))
	if !r.done || len(e.clients["c2"].grants) != 1 || e.clients["c2"].grants[0].token != 8 {
		t.Fatal("fresh reply did not answer standing request")
	}

}
