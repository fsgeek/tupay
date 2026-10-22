// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
package main

import (
	"fmt"
	pb "go.etcd.io/raft/v3/raftpb"
	"time"
)

// link names one directed connection; its reverse has independent fate.
// derives: C1.1, C1.4, F1.2, F2.1, F2.2
type link struct{ from, to string }

// rpcTicket records endpoint incarnations at an admitted send.
// derives: C1.1, C1.4, F1.1, F2.1, F2.2
type rpcTicket struct {
	path                         link
	fromGeneration, toGeneration uint64
}

// RaftPacket is an already-sent library message with a logical delivery deadline.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
type RaftPacket struct {
	message pb.Message
	ticket  rpcTicket
	due     time.Time
}

// RaftNetwork is synchronous; only the event loop mutates routing and wire state.
// The fixture inboxes test admission independently of protocol processing.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
type RaftNetwork struct {
	owner      *Engine
	ids        map[string]uint64
	names      map[uint64]string
	boxes      map[string][]pb.Message
	generation map[string]uint64
	down       map[link]bool
	wire       []RaftPacket
	problem    error
}

// derives: C1.4, F1.1, F1.2, F2.1, F2.2
func newRaftNetwork() *RaftNetwork {
	return &RaftNetwork{ids: map[string]uint64{}, names: map[uint64]string{}, boxes: map[string][]pb.Message{}, generation: map[string]uint64{}, down: map[link]bool{}}
}

// derives: C1.1, F1.1
func (n *RaftNetwork) register(id string) []pb.Message {
	n.generation[id]++
	n.boxes[id] = []pb.Message{}
	return n.boxes[id]
}

// derives: C1.1, F1.1
func (n *RaftNetwork) remove(id string) { delete(n.boxes, id); n.generation[id]++ }

// derives: C1.1, C1.4, F1.2, F2.1, F2.2, L2
func (n *RaftNetwork) setDown(down map[link]bool) {
	n.down = map[link]bool{}
	for p, v := range down {
		if v {
			n.down[p] = true
		}
	}
}

// partition is the legacy fixture adapter; all failures accumulate until heal.
// derives: C1.1, C1.4, F1.2, F2.1, F2.2, L2
func (n *RaftNetwork) partition(sides map[string]int) {
	if sides == nil {
		n.down = map[link]bool{}
		return
	}
	for a := range n.generation {
		for b := range n.generation {
			if sides[a] != sides[b] {
				n.down[link{a, b}] = true
			}
		}
	}
}

// admit fixes fate at send and never rechecks a down link at delivery.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (n *RaftNetwork) admit(from, to string) (rpcTicket, error) {
	p := link{from, to}
	ticket := rpcTicket{p, n.generation[from], n.generation[to]}
	_, a := n.boxes[from]
	_, b := n.boxes[to]
	if !a || !b || n.down[p] {
		return ticket, fmt.Errorf("Raft send lost: %s -> %s", from, to)
	}
	return ticket, nil
}

// route exposes admission/inbox delivery for protocol-independent injector fixtures.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
func (n *RaftNetwork) route(from, to string, m pb.Message) (rpcTicket, error) {
	ticket, err := n.admit(from, to)
	if err == nil {
		n.boxes[to] = append(n.boxes[to], m)
	}
	return ticket, err
}

// response is a distinct reverse send, used by the directional injector fixtures.
// derives: C1.1, C1.4, F1.1, F2.1, F2.2
func (n *RaftNetwork) response(t rpcTicket) error {
	if n.generation[t.path.from] != t.fromGeneration || n.generation[t.path.to] != t.toGeneration {
		return fmt.Errorf("process replaced")
	}
	_, err := n.admit(t.path.to, t.path.from)
	return err
}

// derives: C1.1, C1.4, F1.1, F2.1, F2.2
func (n *RaftNetwork) issue() error { return n.problem }
