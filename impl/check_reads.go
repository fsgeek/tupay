// derives: C2.1, C2.2, F1.1, F1.2, F1.3
package main

import "fmt"

// checkC21 reconstructs the write-only fence in storage order, including restarts.
// Reads must report that ledger but never advance it, even with a larger token.
// derives: C2.1, C1.2, F1.1, F1.2, F1.3
func (g *traceGraph) checkC21(storage string) Verdict {
	var highest uint64
	for _, e := range g.local[storage] {
		if e.Event == "WriteAccept" && e.Token > highest {
			highest = e.Token
		}
		if e.Event != "ReadAccept" && e.Event != "ReadReject" {
			continue
		}
		if e.HighestBefore == nil {
			return Verdict{Reason: "read decision missing highest_before"}
		}
		if *e.HighestBefore != highest {
			return Verdict{Clause: "C2.1", Reason: fmt.Sprintf("read storage seq %d ledger %d, write-only maximum %d", e.Seq, *e.HighestBefore, highest)}
		}
		if e.Event == "ReadAccept" && e.Token < highest {
			return Verdict{Clause: "C2.1", Reason: fmt.Sprintf("storage served stale read token %d below %d", e.Token, highest)}
		}
	}
	return Verdict{}
}

// checkC22 reconstructs value snapshots and requires exact attempt/serve/ack linkage.
// Missing evidence is distinguished from a witnessed wrong value or unserved read.
// derives: C2.2, C1.2, C1.3, F1.1, F1.2, F1.3, E2
func (g *traceGraph) checkC22(storage string) Verdict {
	unknown := Verdict{}
	value := ""
	known := true
	for _, e := range g.local[storage] {
		switch e.Event {
		case "WriteAccept":
			attempt, ok := g.directEvent(e, "WriteAttempt")
			if !ok {
				known = false
				unknown = Verdict{Reason: "cannot reconstruct stored value without write attempt"}
			} else {
				value = attempt.Value
				known = true
			}
		case "ReadAccept":
			if !e.ValuePresent {
				unknown = Verdict{Reason: "served read lacks explicit value"}
				continue
			}
			if known && e.Value != value {
				return Verdict{Clause: "C2.2", Reason: fmt.Sprintf("read storage seq %d served %q, stored %q", e.Seq, e.Value, value)}
			}
		case "ReadReject":
			if e.ValuePresent {
				unknown = Verdict{Reason: "rejected read decision carries value"}
			}
		}
	}
acks:
	for _, ack := range g.ordered {
		if ack.Event != "ReadAck" {
			continue
		}
		if ack.Outcome != "served" && ack.Outcome != "rejected" {
			unknown = Verdict{Reason: "unknown read ack outcome"}
			continue
		}
		if ack.Outcome == "rejected" {
			if ack.ValuePresent {
				unknown = Verdict{Reason: "rejected read ack carries value"}
			}
			continue
		}
		if !ack.ValuePresent {
			unknown = Verdict{Reason: "served read ack lacks explicit value"}
			continue
		}
		serve, ok := g.directEvent(ack, "ReadAccept")
		if !ok {
			attempt, found := g.directEvent(ack, "ReadAttempt")
			if !found {
				if rejection, rejected := g.directEvent(ack, "ReadReject"); rejected {
					attempt, found = g.directEvent(rejection, "ReadAttempt")
				}
			}
			if !found {
				unknown = Verdict{Reason: "served ack lacks attempt correlation"}
				continue
			}
			for _, candidate := range g.ordered {
				if candidate.Event != "ReadAccept" {
					continue
				}
				parent, exists := g.directEvent(candidate, "ReadAttempt")
				if exists && (Ref{parent.Proc, parent.Seq}) == (Ref{attempt.Proc, attempt.Seq}) {
					unknown = Verdict{Reason: "served ack omits an existing serve reference"}
					continue acks
				}
			}
			return Verdict{Clause: "C2.2", Reason: fmt.Sprintf("served ack %s:%d refers to an attempt never served", ack.Proc, ack.Seq)}
		}
		attempt, found := g.directEvent(serve, "ReadAttempt")
		if !found {
			unknown = Verdict{Reason: "served read lacks attempt provenance"}
			continue
		}
		if serve.Proc != storage || serve.Key != ack.Key || serve.Token != ack.Token || attempt.Client != ack.Client || attempt.Proc != ack.Proc || attempt.Key != ack.Key || attempt.Token != ack.Token {
			return Verdict{Clause: "C2.2", Reason: "served ack mismatches the served attempt"}
		}
		if !serve.ValuePresent {
			unknown = Verdict{Reason: "serve lacks explicit value for ack comparison"}
			continue
		}
		if ack.Value != serve.Value {
			return Verdict{Clause: "C2.2", Reason: fmt.Sprintf("read ack value %q differs from served snapshot %q", ack.Value, serve.Value)}
		}
	}
	return unknown
}
