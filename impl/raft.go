// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
package main

import (
	"encoding/binary"
	"fmt"
	"io"
	"log"
	"time"

	raft "go.etcd.io/raft/v3"
	pb "go.etcd.io/raft/v3/raftpb"
)

// Allocation is the index/term of an actually committed Raft log entry.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
type Allocation struct{ Token, Term uint64 }

// LeaseNode retains storage/applied FSM state across logical process replacement.
// RawNode has no timer goroutine and receives only scheduler-controlled inputs.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
type LeaseNode struct {
	id         string
	number     uint64
	durable    *raft.MemoryStorage
	network    *RaftNetwork
	peer       *raft.RawNode
	generation uint64
	applied    uint64
	electionAt time.Time
}

// newLeaseNode creates one retained store and a fixed voter identity.
// derives: C1.1, C1.4, F1.1
func newLeaseNode(id string, network *RaftNetwork) *LeaseNode {
	number := network.ids[id]
	return &LeaseNode{id: id, number: number, network: network, durable: raft.NewMemoryStorage()}
}

// start initializes a fixed configuration or recovers the prior hard state/log.
// The bootstrap snapshot fixes membership only; it allocates no fencing token.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (n *LeaseNode) start() error {
	e := n.network.owner
	if n.applied == 0 {
		voters := make([]uint64, 0, len(e.schedule.Processes.Lease))
		for _, id := range e.schedule.Processes.Lease {
			voters = append(voters, n.network.ids[id])
		}
		snap := pb.Snapshot{Metadata: pb.SnapshotMetadata{Index: 1, Term: 1, ConfState: pb.ConfState{Voters: voters}}}
		if err := n.durable.ApplySnapshot(snap); err != nil {
			return err
		}
		if err := n.durable.SetHardState(pb.HardState{Term: 1, Commit: 1}); err != nil {
			return err
		}
		n.applied = 1
	}
	config := &raft.Config{ID: n.number, ElectionTick: 10, HeartbeatTick: 1, Storage: n.durable, Applied: n.applied, MaxSizePerMsg: 1 << 20, MaxInflightMsgs: 256, CheckQuorum: true, PreVote: true, Logger: &raft.DefaultLogger{Logger: log.New(io.Discard, "", 0)}}
	peer, err := raft.NewRawNode(config)
	if err != nil {
		return fmt.Errorf("start %s: %w", n.id, err)
	}
	n.peer = peer
	n.generation++
	n.network.register(n.id)
	n.resetElection()
	return nil
}

// resetElection supplies the only election deadline that can trigger a campaign.
// RawNode's randomized follower timeout is never used (followers tick quiesced).
// derives: C1.4, F1.1, F1.2, F2.1, F2.2
func (n *LeaseNode) resetElection() {
	e := n.network.owner
	n.electionAt = e.now().Add(time.Duration(100+e.rng.Intn(80)) * time.Millisecond)
}

// stop loses volatile state and inbox membership while retaining storage/FSM state.
// derives: C1.1, C1.4, F1.1
func (n *LeaseNode) stop() error {
	if n.peer != nil {
		n.network.remove(n.id)
		n.peer = nil
	}
	return nil
}

// raftCommand identifies a proposal, never the allocation's authoritative token.
// derives: C1.1, C1.4, F1.1
func raftCommand(id uint64) []byte {
	data := make([]byte, 8)
	binary.BigEndian.PutUint64(data, id)
	return data
}
