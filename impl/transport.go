// derives: C1.1, C1.4, F1.1, F1.2
package main

import (
	"fmt"
	"io"
	"sync"
	"time"

	"github.com/hashicorp/raft"
)

// link identifies a direction; complete partitions disable both directions.
// derives: F1.2, C1.1, C1.4
type link struct{ from, to string }

// rpcTicket prevents replies from crossing a crash or a cut followed by heal.
// derives: F1.1, F1.2, C1.1
type rpcTicket struct {
	path                              link
	fromGeneration, toGeneration, cut uint64
}

// RaftNetwork routes the library's RPCs; it contains no election/allocation logic.
// derives: C1.1, C1.4, F1.1, F1.2
type RaftNetwork struct {
	mu         sync.Mutex
	boxes      map[string]chan raft.RPC
	generation map[string]uint64
	sides      map[string]int
	cuts       map[link]uint64
	problem    error
}

// newRaftNetwork starts a single connected network, with no live endpoints yet.
// derives: F1.1, F1.2, C1.4
func newRaftNetwork() *RaftNetwork {
	return &RaftNetwork{boxes: map[string]chan raft.RPC{}, generation: map[string]uint64{}, sides: map[string]int{}, cuts: map[link]uint64{}}
}

// register creates a new incarnation; no prior inbox is carried into it.
// derives: F1.1, C1.1
func (n *RaftNetwork) register(id string) chan raft.RPC {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.generation[id]++
	box := make(chan raft.RPC, 1024)
	n.boxes[id] = box
	return box
}

// remove discards a crashed process's inbox without closing channels Raft may use.
// derives: F1.1, C1.1
func (n *RaftNetwork) remove(id string) {
	n.mu.Lock()
	defer n.mu.Unlock()
	delete(n.boxes, id)
	n.generation[id]++
}

// partition atomically changes both directions of every affected Raft link.
// derives: F1.2, C1.1, C1.4
func (n *RaftNetwork) partition(sides map[string]int) {
	n.mu.Lock()
	defer n.mu.Unlock()
	for a := range n.generation {
		for b := range n.generation {
			if n.sides[a] == n.sides[b] && sides[a] != sides[b] {
				n.cuts[link{a, b}]++
			}
		}
	}
	n.sides = map[string]int{}
	for id, side := range sides {
		n.sides[id] = side
	}
}

// route performs the send-time connectivity check and inbox delivery atomically.
// derives: F1.1, F1.2, C1.1, C1.4
func (n *RaftNetwork) route(from, to string, rpc raft.RPC) (rpcTicket, error) {
	n.mu.Lock()
	defer n.mu.Unlock()
	path := link{from, to}
	ticket := rpcTicket{path, n.generation[from], n.generation[to], n.cuts[path]}
	if n.boxes[from] == nil || n.boxes[to] == nil || n.sides[from] != n.sides[to] {
		return ticket, fmt.Errorf("RPC dropped on disconnected link %s -> %s", from, to)
	}
	select {
	case n.boxes[to] <- rpc:
		return ticket, nil
	default:
		n.problem = fmt.Errorf("RPC inbox exhausted for %s", to)
		return ticket, n.problem
	}
}

// issue distinguishes an operational resource limit from an admitted fault.
// derives: F1.2, C1.1, C1.4
func (n *RaftNetwork) issue() error {
	n.mu.Lock()
	defer n.mu.Unlock()
	return n.problem
}

// response checks the whole RPC's incarnation/cut history, even after healing.
// derives: F1.1, F1.2, C1.1
func (n *RaftNetwork) response(t rpcTicket) error {
	n.mu.Lock()
	defer n.mu.Unlock()
	if n.boxes[t.path.from] == nil || n.boxes[t.path.to] == nil || n.generation[t.path.from] != t.fromGeneration || n.generation[t.path.to] != t.toGeneration || n.sides[t.path.from] != n.sides[t.path.to] || n.cuts[t.path] != t.cut {
		return fmt.Errorf("RPC reply lost across cut or process replacement")
	}
	return nil
}

// RaftTransport implements the existing library's transport, never its protocol.
// derives: C1.1, C1.4, F1.1, F1.2
type RaftTransport struct {
	id      string
	network *RaftNetwork
	inbox   chan raft.RPC
	timeout time.Duration
}

// newRaftTransport registers an empty inbox for a new lease-node incarnation.
// derives: F1.1, F1.2, C1.4
func newRaftTransport(id string, n *RaftNetwork, timeout time.Duration) *RaftTransport {
	return &RaftTransport{id: id, network: n, inbox: n.register(id), timeout: timeout}
}

// rpc sends one existing Raft RPC and gates the response independently.
// derives: C1.1, C1.4, F1.1, F1.2
func (t *RaftTransport) rpc(target raft.ServerAddress, command interface{}, reader io.Reader) (raft.RPCResponse, error) {
	replies := make(chan raft.RPCResponse, 1)
	ticket, err := t.network.route(t.id, string(target), raft.RPC{Command: command, Reader: reader, RespChan: replies})
	if err != nil {
		return raft.RPCResponse{}, err
	}
	timer := time.NewTimer(t.timeout)
	defer timer.Stop()
	select {
	case reply := <-replies:
		if err := t.network.response(ticket); err != nil {
			return raft.RPCResponse{}, err
		}
		return reply, reply.Error
	case <-timer.C:
		return raft.RPCResponse{}, fmt.Errorf("Raft RPC timeout")
	}
}

// Consumer is an inbox: messages already delivered before a cut may be processed.
// derives: C1.1, F1.1, F1.2
func (t *RaftTransport) Consumer() <-chan raft.RPC { return t.inbox }

// LocalAddr is stable across replacement; network tickets distinguish incarnations.
// derives: C1.1, F1.1
func (t *RaftTransport) LocalAddr() raft.ServerAddress { return raft.ServerAddress(t.id) }

// AppendEntriesPipeline uses the library's supported non-pipelined fallback.
// derives: C1.1, F1.2
func (t *RaftTransport) AppendEntriesPipeline(raft.ServerID, raft.ServerAddress) (raft.AppendPipeline, error) {
	return nil, raft.ErrPipelineReplicationNotSupported
}

// AppendEntries transports the existing replication RPC.
// derives: C1.1, C1.4, F1.1, F1.2
func (t *RaftTransport) AppendEntries(_ raft.ServerID, target raft.ServerAddress, args *raft.AppendEntriesRequest, resp *raft.AppendEntriesResponse) error {
	r, err := t.rpc(target, args, nil)
	if err == nil {
		v, ok := r.Response.(*raft.AppendEntriesResponse)
		if !ok {
			return fmt.Errorf("bad append reply")
		}
		*resp = *v
	}
	return err
}

// RequestVote transports the existing election RPC.
// derives: C1.1, C1.4, F1.1, F1.2
func (t *RaftTransport) RequestVote(_ raft.ServerID, target raft.ServerAddress, args *raft.RequestVoteRequest, resp *raft.RequestVoteResponse) error {
	r, err := t.rpc(target, args, nil)
	if err == nil {
		v, ok := r.Response.(*raft.RequestVoteResponse)
		if !ok {
			return fmt.Errorf("bad vote reply")
		}
		*resp = *v
	}
	return err
}

// RequestPreVote supports the library's optional pre-vote interface.
// derives: C1.1, C1.4, F1.1, F1.2
func (t *RaftTransport) RequestPreVote(_ raft.ServerID, target raft.ServerAddress, args *raft.RequestPreVoteRequest, resp *raft.RequestPreVoteResponse) error {
	r, err := t.rpc(target, args, nil)
	if err == nil {
		v, ok := r.Response.(*raft.RequestPreVoteResponse)
		if !ok {
			return fmt.Errorf("bad pre-vote reply")
		}
		*resp = *v
	}
	return err
}

// InstallSnapshot transports durable state using the library's snapshot RPC.
// derives: C1.1, F1.1, F1.2
func (t *RaftTransport) InstallSnapshot(_ raft.ServerID, target raft.ServerAddress, args *raft.InstallSnapshotRequest, resp *raft.InstallSnapshotResponse, data io.Reader) error {
	r, err := t.rpc(target, args, data)
	if err == nil {
		v, ok := r.Response.(*raft.InstallSnapshotResponse)
		if !ok {
			return fmt.Errorf("bad snapshot reply")
		}
		*resp = *v
	}
	return err
}

// TimeoutNow transports leadership transfer using the library's existing RPC.
// derives: C1.1, C1.4, F1.2
func (t *RaftTransport) TimeoutNow(_ raft.ServerID, target raft.ServerAddress, args *raft.TimeoutNowRequest, resp *raft.TimeoutNowResponse) error {
	r, err := t.rpc(target, args, nil)
	if err == nil {
		v, ok := r.Response.(*raft.TimeoutNowResponse)
		if !ok {
			return fmt.Errorf("bad transfer reply")
		}
		*resp = *v
	}
	return err
}

// EncodePeer preserves the library's address representation.
// derives: C1.1, F1.2
func (t *RaftTransport) EncodePeer(_ raft.ServerID, addr raft.ServerAddress) []byte {
	return []byte(addr)
}

// DecodePeer reverses address encoding without changing protocol identities.
// derives: C1.1, F1.2
func (t *RaftTransport) DecodePeer(data []byte) raft.ServerAddress { return raft.ServerAddress(data) }

// SetHeartbeatHandler leaves heartbeats on the same gated inbox as all RPCs.
// derives: C1.1, F1.2
func (t *RaftTransport) SetHeartbeatHandler(func(raft.RPC)) {}

// Compile-time interface checks keep the adapter on the existing Raft protocol.
// derives: C1.1, C1.4, F1.1, F1.2
var _ raft.Transport = (*RaftTransport)(nil)

// derives: C1.1, C1.4, F1.1, F1.2
var _ raft.WithPreVote = (*RaftTransport)(nil)
