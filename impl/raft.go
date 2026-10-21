// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"sync"
	"time"

	"github.com/hashicorp/raft"
)

// Allocation uses the committed Raft entry's globally ordered index and term.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
type Allocation struct{ Token, Term uint64 }

// TokenFSM is reconstructed from retained logs or a snapshot on restart.
// derives: C1.1, F1.1
type TokenFSM struct {
	mu   sync.Mutex
	last Allocation
}

// Apply allocates only after Raft has committed this command.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (f *TokenFSM) Apply(l *raft.Log) interface{} {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.last = Allocation{l.Index, l.Term}
	return f.last
}

// Snapshot captures an immutable state copy.
// derives: C1.1, F1.1
func (f *TokenFSM) Snapshot() (raft.FSMSnapshot, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	return tokenSnapshot{f.last}, nil
}

// Restore replaces all volatile FSM state with the durable snapshot.
// derives: C1.1, F1.1
func (f *TokenFSM) Restore(r io.ReadCloser) error {
	defer r.Close()
	f.mu.Lock()
	defer f.mu.Unlock()
	return json.NewDecoder(r).Decode(&f.last)
}

// tokenSnapshot contains only durable state.
// derives: C1.1, F1.1
type tokenSnapshot struct{ last Allocation }

// Persist writes the snapshot before closing the sink.
// derives: C1.1, F1.1
func (s tokenSnapshot) Persist(w raft.SnapshotSink) error {
	if err := json.NewEncoder(w).Encode(s.last); err != nil {
		_ = w.Cancel()
		return err
	}
	return w.Close()
}

// Release has no resources because snapshots are immutable values.
// derives: C1.1, F1.1
func (s tokenSnapshot) Release() {}

// LeaseNode separates retained stores from the replaceable Raft process.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
type LeaseNode struct {
	id         string
	durable    *raft.InmemStore
	snapshots  *raft.InmemSnapshotStore
	transport  *RaftTransport
	network    *RaftNetwork
	peer       *raft.Raft
	generation uint64
}

// newLeaseNode creates stable stores once, before initial bootstrap.
// derives: C1.1, F1.1
func newLeaseNode(id string, network *RaftNetwork) *LeaseNode {
	return &LeaseNode{id: id, network: network, durable: raft.NewInmemStore(), snapshots: raft.NewInmemSnapshotStore()}
}

// start creates a fresh volatile FSM and transport, preserving only stores.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (n *LeaseNode) start(timeout time.Duration) error {
	conf := raft.DefaultConfig()
	conf.LocalID = raft.ServerID(n.id)
	conf.HeartbeatTimeout = 80 * time.Millisecond
	conf.ElectionTimeout = 80 * time.Millisecond
	conf.LeaderLeaseTimeout = 40 * time.Millisecond
	conf.CommitTimeout = 5 * time.Millisecond
	conf.SnapshotInterval = 20 * time.Second
	conf.SnapshotThreshold = 1024
	conf.LogOutput = io.Discard
	n.transport = newRaftTransport(n.id, n.network, timeout)
	r, err := raft.NewRaft(conf, &TokenFSM{}, n.durable, n.durable, n.snapshots, n.transport)
	if err != nil {
		n.network.remove(n.id)
		n.transport = nil
		return fmt.Errorf("start %s: %w", n.id, err)
	}
	n.peer = r
	n.generation++
	return nil
}

// stop discards process-local state after a durable-store-preserving crash.
// derives: F1.1, C1.1
func (n *LeaseNode) stop() error {
	if n.peer == nil {
		return nil
	}
	n.network.remove(n.id)
	err := n.peer.Shutdown().Error()
	n.peer = nil
	n.transport = nil
	return err
}
