// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3
package main

import "fmt"

// routeEnvironment reconstructs the state at a hop's send-fault reference.
// derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
type routeEnvironment struct {
	up         map[string]bool
	generation map[string]uint64
	down       map[link]bool
	paused     map[string]bool
}

// routingEnvironments reads only observable Fault records, not the live injector.
// derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
func (g *traceGraph) routingEnvironments(s Schedule) map[Ref]routeEnvironment {
	states := map[Ref]routeEnvironment{}
	current := routeEnvironment{map[string]bool{}, map[string]uint64{}, map[link]bool{}, map[string]bool{}}
	roles := processRoles(s)
	for id := range roles {
		current.up[id] = true
		current.generation[id] = 1
	}
	save := func(ref Ref) {
		copy := routeEnvironment{map[string]bool{}, map[string]uint64{}, map[link]bool{}, map[string]bool{}}
		for id, v := range current.up {
			copy.up[id] = v
		}
		for id, v := range current.generation {
			copy.generation[id] = v
		}
		for p, v := range current.down {
			copy.down[p] = v
		}
		for id, v := range current.paused {
			copy.paused[id] = v
		}
		states[ref] = copy
	}
	save(Ref{})
	for _, e := range g.local["env"] {
		if e.Event != "Fault" {
			continue
		}
		if e.Crash != "" {
			current.up[e.Crash] = false
			current.paused[e.Crash] = false
			if roles[e.Crash] == "client" {
				current.generation[e.Crash]++
			}
		}
		if e.Restart != "" {
			current.up[e.Restart] = true
			if roles[e.Restart] == "lease" {
				current.generation[e.Restart]++
			}
		}
		if e.Partition != nil && len(e.Partition) == 2 {
			for _, a := range e.Partition[0] {
				for _, b := range e.Partition[1] {
					current.down[link{a, b}] = true
					current.down[link{b, a}] = true
				}
			}
		}
		for _, pair := range e.Links {
			if len(pair) == 2 {
				current.down[link{pair[0], pair[1]}] = true
			}
		}
		if e.Heal {
			current.down = map[link]bool{}
		}
		if e.Pause != "" {
			current.paused[e.Pause] = true
		}
		if e.Resume != "" {
			current.paused[e.Resume] = false
		}
		save(Ref{e.Proc, e.Seq})
	}
	return states
}

// checkGrantDeliveries checks route plausibility and exact identities independently.
// Actual receipt and the duration horizon remain trusted sidecar instrumentation.
// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3
func (g *traceGraph) checkGrantDeliveries(s Schedule, evidence RunEvidence) Verdict {
	states := g.routingEnvironments(s)
	roles := processRoles(s)
	seen := map[Ref]bool{}
	for _, d := range evidence.Deliveries {
		req, ok := g.events[d.Request]
		grant, issued := g.events[d.Grant]
		actual, answers := g.directEvent(grant, "Request")
		if !ok || !issued || req.Event != "Request" || grant.Event != "Grant" || req.Client != grant.Client || !answers || (Ref{actual.Proc, actual.Seq}) != d.Request || seen[d.Request] {
			return Verdict{Reason: "invalid/duplicate grant delivery identity"}
		}
		seen[d.Request] = true
		received, ok := states[d.ReceivedAfter]
		if !ok || !received.up[req.Client] || received.paused[req.Client] || received.generation[req.Client] != d.ClientGeneration {
			return Verdict{Reason: "invalid grant receipt incarnation"}
		}
		paths := [][]RouteHop{d.RequestHops, d.ReplyHops}
		for kind, hops := range paths {
			if len(hops) == 0 {
				return Verdict{Reason: "missing grant delivery route"}
			}
			start, end := req.Client, grant.Proc
			if kind == 1 {
				start, end = grant.Proc, req.Client
			}
			if hops[0].From != start || hops[len(hops)-1].To != end {
				return Verdict{Reason: "grant delivery route has wrong endpoints"}
			}
			for i, h := range hops {
				state, ok := states[h.Fault]
				if !ok || h.From == h.To || !state.up[h.From] || !state.up[h.To] || state.down[link{h.From, h.To}] || state.generation[h.From] != h.FromGeneration || state.generation[h.To] != h.ToGeneration {
					return Verdict{Reason: fmt.Sprintf("grant delivery hop not admitted: %s -> %s", h.From, h.To)}
				}
				if i > 0 {
					prev := hops[i-1]
					if prev.To != h.From || prev.ToGeneration != h.FromGeneration || prev.Fault.Seq > h.Fault.Seq || roles[h.From] != "lease" {
						return Verdict{Reason: "discontinuous grant delivery route"}
					}
				}
				if h.Fault.Seq > d.ReceivedAfter.Seq {
					return Verdict{Reason: "grant delivery hop follows receipt"}
				}
			}
		}
		if d.ReplyHops[len(d.ReplyHops)-1].ToGeneration != d.ClientGeneration {
			return Verdict{Reason: "grant delivery names wrong client generation"}
		}
	}
	return Verdict{}
}

// requestObtained requires receipt evidence or an observable operation using a grant.
// An issuer's Grant alone says nothing about delivery to its client.
// derives: C1.4, F1.1, F2.1, F2.2, L3
func (g *traceGraph) requestObtained(request Ref, evidence RunEvidence) bool {
	for _, d := range evidence.Deliveries {
		if d.Request == request {
			return true
		}
	}
	for _, e := range g.ordered {
		if e.Event != "WriteAttempt" && e.Event != "ReadAttempt" {
			continue
		}
		grant, ok := g.directEvent(e, "Grant")
		if !ok {
			continue
		}
		req, ok := g.directEvent(grant, "Request")
		if ok && (Ref{req.Proc, req.Seq}) == request && e.Client == req.Client {
			return true
		}
	}
	return false
}
