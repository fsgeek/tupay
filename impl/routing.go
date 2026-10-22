// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3, E1, T3
package main

import "time"

// RouteHop certifies one admitted directed send, using a fault reference, not a clock.
// derives: C1.4, F1.1, F1.2, F2.1, F2.2
type RouteHop struct {
	From           string `json:"from"`
	To             string `json:"to"`
	FromGeneration uint64 `json:"from_generation"`
	ToGeneration   uint64 `json:"to_generation"`
	Fault          Ref    `json:"fault"`
}

// GrantDelivery is trusted receipt instrumentation, separate from observable issuance.
// derives: C1.1, C1.4, F1.1, F1.3, F2.1, F2.2
type GrantDelivery struct {
	Request          Ref        `json:"request"`
	Grant            Ref        `json:"grant"`
	ClientGeneration uint64     `json:"client_generation"`
	RequestHops      []RouteHop `json:"request_hops"`
	ReplyHops        []RouteHop `json:"reply_hops"`
	ReceivedAfter    Ref        `json:"received_after"`
}

// LeasePacket carries request identity or immutable grant authority through lease nodes.
// grant-send is local volatile work; request/grant are already-sent network packets.
// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
type LeasePacket struct {
	kind, from, to    string
	targetGeneration  uint64
	request           *RequestState
	grant             HeldGrant
	hops, requestHops []RouteHop
	due               time.Time
}

// processGeneration distinguishes volatile endpoint incarnations on the lease wire.
// derives: C1.4, F1.1
func (e *Engine) processGeneration(id string) uint64 {
	if n := e.nodes[id]; n != nil {
		return n.generation
	}
	if c := e.clients[id]; c != nil {
		return c.generation
	}
	return 0
}

// sendLease fixes fate independently per outgoing direction; no route oracle is used.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (e *Engine) sendLease(m LeasePacket, from, to string) {
	if from == to || !e.canSend(from, to) {
		return
	}
	m.from, m.to = from, to
	m.targetGeneration = e.processGeneration(to)
	hop := RouteHop{from, to, e.processGeneration(from), m.targetGeneration, e.out.fault}
	m.hops = append(append([]RouteHop{}, m.hops...), hop)
	m.due = e.now().Add(e.jitter())
	e.leaseWire = append(e.leaseWire, m)
}

// retryRequest multicasts the same standing Request to every configured lease node.
// derives: C1.4, F1.1, F1.3, F2.1, F2.2, L3
func (e *Engine) retryRequest(r *RequestState, now time.Time) {
	c := e.clients[r.client]
	if r.done || !c.up || c.paused || c.generation != r.generation || now.Before(r.retryAt) {
		return
	}
	r.retryAt = now.Add(20 * time.Millisecond)
	for _, id := range e.schedule.Processes.Lease {
		e.sendLease(LeasePacket{kind: "request", request: r}, r.client, id)
	}
}

// visitedLease bounds forwarding to simple paths, independent of schedule names.
// derives: C1.4, F2.1, F2.2
func visitedLease(hops []RouteHop, id string) bool {
	for _, hop := range hops {
		if hop.From == id || hop.To == id {
			return true
		}
	}
	return false
}

// spreadGrant preserves the original Grant reference; followers cannot allocate.
// R2 deliberately breaks only the reply relaying mechanism.
// derives: C1.1, C1.4, F1.1, F2.1, F2.2, L3
func (e *Engine) spreadGrant(m LeasePacket, id string) {
	m.kind = "grant"
	e.sendLease(m, id, m.request.client)
	if e.mutation == "R2" {
		return
	}
	for _, next := range e.schedule.Processes.Lease {
		if next != id && !visitedLease(m.hops, next) {
			e.sendLease(m, id, next)
		}
	}
}

// deliverLease only checks receiver incarnation after send; cuts cannot retract packets.
// Received requests enable allocation locally. R1 disables follower forwarding.
// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3, E1, T3
func (e *Engine) deliverLease(now time.Time) {
	messages := e.leaseWire
	e.leaseWire = nil
	e.rng.Shuffle(len(messages), func(i, j int) { messages[i], messages[j] = messages[j], messages[i] })
	for _, m := range messages {
		if now.Before(m.due) {
			e.leaseWire = append(e.leaseWire, m)
			continue
		}
		r := m.request
		c := e.clients[r.client]
		if r.done || c.generation != r.generation || !e.alive(m.to) || e.processGeneration(m.to) != m.targetGeneration {
			continue
		}
		if m.kind == "grant-send" {
			e.spreadGrant(m, m.to)
			continue
		}
		if m.kind == "request" {
			if r.ingress == nil {
				r.ingress = map[string]uint64{}
				r.paths = map[string][]RouteHop{}
			}
			r.ingress[m.to] = m.targetGeneration
			r.paths[m.to] = append([]RouteHop{}, m.hops...)
			if e.mutation != "R1" {
				for _, id := range e.schedule.Processes.Lease {
					if !visitedLease(m.hops, id) {
						e.sendLease(m, m.to, id)
					}
				}
			}
			continue
		}
		if m.to != r.client {
			e.spreadGrant(m, m.to)
			continue
		}
		if c.paused {
			e.leaseWire = append(e.leaseWire, m)
			continue
		}
		c.grants = append(c.grants, m.grant)
		r.done = true
		r.eligibleSince = time.Time{}
		e.deliveries = append(e.deliveries, GrantDelivery{r.ref, m.grant.ref, c.generation, m.requestHops, m.hops, e.out.fault})
	}
}
