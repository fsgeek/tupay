// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"
)

// Verdict distinguishes observed clause failure from missing evidence.
// derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2
type Verdict struct {
	Clause string
	Reason string
}

// traceGraph is rebuilt from the JSONL, never from implementation state.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
type traceGraph struct {
	events  map[Ref]Event
	local   map[string][]Event
	ordered []Event
}

// readTrace validates local sequence continuity and reconstructs causal order.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
func readTrace(path string) (*traceGraph, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	g := &traceGraph{events: map[Ref]Event{}, local: map[string][]Event{}}
	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 4096), 1<<20)
	run := ""
	for scanner.Scan() {
		var v Event
		decoderErr := json.Unmarshal(scanner.Bytes(), &v)
		if decoderErr != nil {
			return nil, decoderErr
		}
		if v.Proc == "" || v.Seq == 0 || v.Side != "impl" || v.Run == "" || !observable(v.Event) && v.Event != "Fault" {
			return nil, fmt.Errorf("malformed observable record")
		}
		if run == "" {
			run = v.Run
		}
		if v.Run != run {
			return nil, fmt.Errorf("mixed runs")
		}
		r := Ref{v.Proc, v.Seq}
		if _, ok := g.events[r]; ok {
			return nil, fmt.Errorf("duplicate event reference %v", r)
		}
		g.events[r] = v
		g.local[v.Proc] = append(g.local[v.Proc], v)
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	if len(g.events) == 0 {
		return nil, fmt.Errorf("empty trace")
	}
	for proc, events := range g.local {
		sort.Slice(events, func(i, j int) bool { return events[i].Seq < events[j].Seq })
		for i, e := range events {
			if e.Seq != uint64(i+1) {
				return nil, fmt.Errorf("missing local sequence on %s", proc)
			}
		}
		g.local[proc] = events
	}
	// Topological sorting uses references and process order, never input line order.
	degree := map[Ref]int{}
	children := map[Ref][]Ref{}
	for r, v := range g.events {
		edges := map[Ref]bool{}
		if r.Seq > 1 {
			edges[Ref{r.Proc, r.Seq - 1}] = true
		}
		for _, cause := range v.Causes {
			edges[cause] = true
		}
		for cause := range edges {
			if _, ok := g.events[cause]; !ok {
				return nil, fmt.Errorf("missing cause %v", cause)
			}
			degree[r]++
			children[cause] = append(children[cause], r)
		}
	}
	var ready []Ref
	for r := range g.events {
		if degree[r] == 0 {
			ready = append(ready, r)
		}
	}
	less := func(i, j int) bool {
		if ready[i].Proc == ready[j].Proc {
			return ready[i].Seq < ready[j].Seq
		}
		return ready[i].Proc < ready[j].Proc
	}
	for len(ready) > 0 {
		sort.Slice(ready, less)
		r := ready[0]
		ready = ready[1:]
		g.ordered = append(g.ordered, g.events[r])
		for _, next := range children[r] {
			degree[next]--
			if degree[next] == 0 {
				ready = append(ready, next)
			}
		}
	}
	if len(g.ordered) != len(g.events) {
		return nil, fmt.Errorf("causal cycle")
	}
	return g, nil
}

// precedes traverses explicit causes plus implicit per-process program order.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
func (g *traceGraph) precedes(a, b Ref) bool {
	if a == b {
		return false
	}
	stack := []Ref{b}
	seen := map[Ref]bool{}
	for len(stack) > 0 {
		r := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if seen[r] {
			continue
		}
		seen[r] = true
		v, ok := g.events[r]
		if !ok {
			continue
		}
		edges := append([]Ref{}, v.Causes...)
		if r.Seq > 1 {
			edges = append(edges, Ref{r.Proc, r.Seq - 1})
		}
		for _, p := range edges {
			if p == a {
				return true
			}
			stack = append(stack, p)
		}
	}
	return false
}

// directEvent finds an explicit causal parent of a particular event type.
// derives: C1.1, C1.2, C1.3, C2.1, C2.2
func (g *traceGraph) directEvent(e Event, names ...string) (Event, bool) {
	for _, r := range e.Causes {
		v := g.events[r]
		for _, name := range names {
			if v.Event == name {
				return v, true
			}
		}
	}
	return Event{}, false
}

// checkC11 compares all ordered grants and demands a total observable grant order.
// derives: C1.1, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
func (g *traceGraph) checkC11() Verdict {
	var grants []Event
	for _, v := range g.ordered {
		if v.Event == "Grant" {
			if v.Key != "k" || v.Token == 0 || v.Term == 0 || v.Lifetime <= 0 {
				return Verdict{Reason: "malformed grant"}
			}
			r, ok := g.directEvent(v, "Request")
			if !ok || r.Client != v.Client || r.Key != v.Key {
				return Verdict{Reason: "grant lacks matching Request"}
			}
			grants = append(grants, v)
		}
	}
	for i, a := range grants {
		for _, b := range grants[i+1:] {
			ar, br := Ref{a.Proc, a.Seq}, Ref{b.Proc, b.Seq}
			if !g.precedes(ar, br) {
				return Verdict{Reason: "grants lack total causal order"}
			}
			if b.Token <= a.Token {
				return Verdict{Clause: "C1.1", Reason: fmt.Sprintf("grant %v token %d follows token %d", br, b.Token, a.Token)}
			}
		}
	}
	return Verdict{}
}

// checkProvenance checks the authority path for EVERY acceptance and rejection.
// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
func (g *traceGraph) checkProvenance() Verdict {
	for _, e := range g.ordered {
		if e.Event != "WriteAccept" && e.Event != "WriteReject" && e.Event != "ReadAccept" && e.Event != "ReadReject" {
			continue
		}
		attemptName := "WriteAttempt"
		if e.Event == "ReadAccept" || e.Event == "ReadReject" {
			attemptName = "ReadAttempt"
		}
		a, ok := g.directEvent(e, attemptName)
		if !ok || a.Key != e.Key || a.Token != e.Token || a.Term != e.Term || e.HighestBefore == nil {
			return Verdict{Reason: "storage decision lacks matching attempt/ledger"}
		}
		grant, ok := g.directEvent(a, "Grant")
		if !ok || grant.Client != a.Client || grant.Token != a.Token || grant.Term != a.Term || grant.Key != a.Key {
			return Verdict{Reason: "attempt lacks matching grant and grantor term"}
		}
	}
	return Verdict{}
}

// checkC12 reconstructs the durable maximum using storage's own sequence only.
// derives: C1.2, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
func (g *traceGraph) checkC12(storage string) Verdict {
	var highest uint64
	for _, e := range g.local[storage] {
		if e.Event != "WriteAccept" && e.Event != "WriteReject" {
			continue
		}
		if e.HighestBefore == nil {
			return Verdict{Reason: "storage decision missing highest_before"}
		}
		if *e.HighestBefore != highest {
			return Verdict{Clause: "C1.2", Reason: fmt.Sprintf("storage seq %d ledger %d, reconstructed %d", e.Seq, *e.HighestBefore, highest)}
		}
		if e.Event == "WriteAccept" {
			if e.Token < highest {
				return Verdict{Clause: "C1.2", Reason: fmt.Sprintf("storage accepted stale token %d below %d", e.Token, highest)}
			}
			highest = e.Token
		}
	}
	return Verdict{}
}

// checkC13 correlates each success to THIS attempt's acceptance, including late acks.
// derives: C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
func (g *traceGraph) checkC13() Verdict {
	unknown := Verdict{}
acks:
	for _, ack := range g.ordered {
		if ack.Event != "WriteAck" {
			continue
		}
		if ack.Outcome != "accepted" && ack.Outcome != "rejected" {
			return Verdict{Reason: "unknown ack outcome"}
		}
		if ack.Outcome != "accepted" {
			continue
		}
		decision, ok := g.directEvent(ack, "WriteAccept")
		if !ok {
			// Missing causal evidence alone cannot establish a contract violation.
			// Recover the precise attempt from either the ack or its rejection.
			attempt, found := g.directEvent(ack, "WriteAttempt")
			if !found {
				if rejection, rejected := g.directEvent(ack, "WriteReject"); rejected {
					attempt, found = g.directEvent(rejection, "WriteAttempt")
				}
			}
			if !found {
				unknown = Verdict{Reason: "success ack lacks attempt correlation"}
				continue
			}
			for _, candidate := range g.ordered {
				if candidate.Event != "WriteAccept" {
					continue
				}
				parent, exists := g.directEvent(candidate, "WriteAttempt")
				if exists && (Ref{parent.Proc, parent.Seq}) == (Ref{attempt.Proc, attempt.Seq}) {
					unknown = Verdict{Reason: "success ack omits an existing acceptance reference"}
					continue acks
				}
			}
			return Verdict{Clause: "C1.3", Reason: fmt.Sprintf("success ack %s:%d refers to an attempt never accepted", ack.Proc, ack.Seq)}
		}
		if decision.Key != ack.Key || decision.Token != ack.Token {
			return Verdict{Clause: "C1.3", Reason: "success ack mismatches acceptance key/token"}
		}
		attempt, ok := g.directEvent(decision, "WriteAttempt")
		if !ok || attempt.Client != ack.Client || attempt.Proc != ack.Proc || attempt.Key != ack.Key || attempt.Token != ack.Token {
			return Verdict{Clause: "C1.3", Reason: "success ack mismatches the accepted attempt"}
		}
	}
	return unknown
}

// checkC14 independently reconstructs the final environment from Fault records.
// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, C2.1, C2.2
func (g *traceGraph) checkC14(s Schedule, evidence RunEvidence) Verdict {
	if len(evidence.Witnesses) == 0 {
		return Verdict{}
	}
	up := map[string]bool{}
	paused := map[string]bool{}
	down := map[link]bool{}
	var lastFault Ref
	for _, id := range append(append(append([]string{}, s.Processes.Lease...), s.Processes.Clients...), s.Processes.Storage...) {
		up[id] = true
	}
	for _, e := range g.local["env"] {
		if e.Event != "Fault" {
			continue
		}
		lastFault = Ref{e.Proc, e.Seq}
		if e.Crash != "" {
			up[e.Crash] = false
			paused[e.Crash] = false
		}
		if e.Restart != "" {
			up[e.Restart] = true
		}
		// Independently reconstruct the directed environment from observable faults.
		// derives: C1.4, F1.2, F2.1, F2.2, L2, L3
		if e.Partition != nil {
			for _, a := range e.Partition[0] {
				for _, b := range e.Partition[1] {
					down[link{a, b}] = true
					down[link{b, a}] = true
				}
			}
		}
		for _, pair := range e.Links {
			if len(pair) != 2 || !upName(s, pair[0]) || !upName(s, pair[1]) || pair[0] == pair[1] {
				return Verdict{Reason: "malformed directed Fault links"}
			}
			down[link{pair[0], pair[1]}] = true
		}
		if e.Heal {
			down = map[link]bool{}
		}
		if e.Pause != "" {
			paused[e.Pause] = true
		}
		if e.Resume != "" {
			paused[e.Resume] = false
		}
	}
	connected := func(a, b string) bool { return up[a] && up[b] && !down[link{a, b}] && !down[link{b, a}] }
	for _, w := range evidence.Witnesses {
		request, ok := g.events[w.Request]
		if !ok || request.Event != "Request" || w.StableFault != lastFault || w.BudgetMillis < 3000 {
			return Verdict{Reason: "invalid progress horizon certificate"}
		}
		client, storage := request.Client, s.Processes.Storage[0]
		if !up[client] || paused[client] || !up[storage] || !connected(client, storage) {
			return Verdict{Reason: "progress certificate has unavailable requester/storage"}
		}
		clique := false
		for i, a := range s.Processes.Lease {
			for _, b := range s.Processes.Lease[i+1:] {
				if connected(a, b) && connected(a, client) && connected(b, client) && connected(a, storage) && connected(b, storage) {
					clique = true
				}
			}
		}
		if !clique {
			return Verdict{Reason: "progress certificate lacks connected majority"}
		}
		granted := false
		for _, e := range g.ordered {
			if e.Event == "Grant" {
				r, ok := g.directEvent(e, "Request")
				if ok && (Ref{r.Proc, r.Seq}) == w.Request {
					granted = true
					break
				}
			}
		}
		if !granted {
			return Verdict{Clause: "C1.4", Reason: fmt.Sprintf("eligible request %v unfulfilled through finite horizon", w.Request)}
		}
	}
	return Verdict{}
}

// checkTrace reports clause failures before operational incompleteness.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, E2, C2.1, C2.2
func checkTrace(path string, s Schedule, evidence RunEvidence) Verdict {
	g, err := readTrace(path)
	if err != nil {
		return Verdict{Reason: err.Error()}
	}
	checks := []Verdict{g.checkC11(), g.checkC12(s.Processes.Storage[0]), g.checkC13(), g.checkC14(s, evidence), g.checkC21(s.Processes.Storage[0]), g.checkC22(s.Processes.Storage[0]), g.checkProvenance(), g.checkAckAnswers()}
	for _, v := range checks {
		if v.Clause != "" {
			return v
		}
	}
	if evidence.Operational != "" {
		return Verdict{Reason: evidence.Operational}
	}
	for _, v := range checks {
		if v.Reason != "" {
			return v
		}
	}
	if !evidence.Completed {
		return Verdict{Reason: evidence.Reason}
	}
	return Verdict{}
}

// upName validates a reconstructed fault endpoint against the shared identities.
// derives: C1.4, F2.1, F2.2, L1, L3
func upName(s Schedule, id string) bool { return processRoles(s)[id] != "" }
