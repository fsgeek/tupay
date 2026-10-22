// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
package main

import (
	"bytes"
	"encoding/binary"
	"fmt"
	raft "go.etcd.io/raft/v3"
	pb "go.etcd.io/raft/v3/raftpb"
	"sort"
	"time"
)

// proposalFlight correlates one committed-library command with a live request.
// derives: C1.1, C1.4, F1.1, F2.1, F2.2
type proposalFlight struct {
	id         uint64
	completion completedAllocation
	deadline   time.Time
}

// collectReady persists before sends and applies only committed Raft entries.
// Sorting message bytes removes upstream map iteration from scheduler inputs.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (e *Engine) collectReady(n *LeaseNode) {
	for n.peer != nil && n.peer.HasReady() {
		rd := n.peer.Ready()
		if !raft.IsEmptySnap(rd.Snapshot) {
			if err := n.durable.ApplySnapshot(rd.Snapshot); err != nil {
				e.network.problem = err
				return
			}
		}
		if err := n.durable.Append(rd.Entries); err != nil {
			e.network.problem = err
			return
		}
		if !raft.IsEmptyHardState(rd.HardState) {
			if err := n.durable.SetHardState(rd.HardState); err != nil {
				e.network.problem = err
				return
			}
		}
		sort.SliceStable(rd.Messages, func(i, j int) bool {
			a, _ := rd.Messages[i].Marshal()
			b, _ := rd.Messages[j].Marshal()
			return bytes.Compare(a, b) < 0
		})
		for _, m := range rd.Messages {
			from, to := e.network.names[m.From], e.network.names[m.To]
			ticket, err := e.network.admit(from, to)
			if err != nil {
				continue
			}
			e.network.wire = append(e.network.wire, RaftPacket{m, ticket, e.now().Add(e.jitter())})
		}
		for _, entry := range rd.CommittedEntries {
			if entry.Index <= n.applied {
				continue
			}
			n.applied = entry.Index
			if entry.Type != pb.EntryNormal {
				e.network.problem = fmt.Errorf("unexpected membership change")
				return
			}
			if len(entry.Data) == 0 {
				continue
			}
			if len(entry.Data) != 8 {
				e.network.problem = fmt.Errorf("bad allocation command")
				return
			}
			id := binary.BigEndian.Uint64(entry.Data)
			if e.inflight && e.flight != nil && e.flight.id == id && e.flight.completion.node == n.id && e.flight.completion.generation == n.generation {
				result := e.flight.completion
				result.allocation = Allocation{entry.Index, entry.Term}
				e.inflight = false
				e.flight = nil
				e.finishAllocation(result)
			}
		}
		n.peer.Advance(rd)
	}
}

// stepConsensus runs every library transition on the seeded logical event loop.
// Follower/candidate ticks cannot consult the library's random election timeout:
// quiesced ticks advance lease age; only our seeded Campaign deadlines can elect.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (e *Engine) stepConsensus() {
	now := e.now()
	if now.Sub(time.Unix(0, 0).UTC())%(10*time.Millisecond) == 0 {
		for _, id := range e.schedule.Processes.Lease {
			n := e.nodes[id]
			if n.peer == nil {
				continue
			}
			if n.peer.BasicStatus().RaftState == raft.StateLeader {
				n.peer.Tick()
			} else {
				n.peer.TickQuiesced()
			}
		}
	}
	for _, id := range e.schedule.Processes.Lease {
		n := e.nodes[id]
		if n.peer == nil {
			continue
		}
		if n.peer.BasicStatus().RaftState != raft.StateLeader && !now.Before(n.electionAt) {
			if err := n.peer.Campaign(); err != nil {
				e.network.problem = err
			}
			n.resetElection()
		}
		e.collectReady(n)
	}
	messages := e.network.wire
	e.network.wire = nil
	e.rng.Shuffle(len(messages), func(i, j int) { messages[i], messages[j] = messages[j], messages[i] })
	for _, packet := range messages {
		if now.Before(packet.due) {
			e.network.wire = append(e.network.wire, packet)
			continue
		}
		id := e.network.names[packet.message.To]
		n := e.nodes[id]
		if n == nil || n.peer == nil || e.network.generation[id] != packet.ticket.toGeneration {
			continue
		}
		if err := n.peer.Step(packet.message); err != nil {
			e.network.problem = err
			continue
		}
		st := n.peer.BasicStatus()
		if (packet.message.Type == pb.MsgApp || packet.message.Type == pb.MsgHeartbeat) && st.Lead == packet.message.From && st.Term == packet.message.Term {
			n.resetElection()
		}
		e.collectReady(n)
	}
	if e.inflight && e.flight != nil && !now.Before(e.flight.deadline) {
		e.inflight = false
		e.flight = nil
	}
}
