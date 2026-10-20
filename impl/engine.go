// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
package main

import (
	"fmt"
	"math/rand"
	"sort"
	"time"

	"github.com/hashicorp/raft"
)

// grantLifetime is execution time only; observe lifetimes are milliseconds.
// derives: C1.1, C1.4, F1.3
const grantLifetime = 40 * time.Millisecond

// progressHorizon is the preregistered finite liveness opportunity.
// derives: C1.4, F1.1, F1.2, F1.3
const progressHorizon = 3 * time.Second

// HeldGrant retains provenance even when an old holder resumes after expiry.
// derives: C1.1, C1.2, F1.1, F1.3
type HeldGrant struct {
	token, term uint64
	ref         Ref
	expires     time.Time
}

// Client retains no grant or inbox across simulated crash/restart.
// derives: C1.2, C1.3, C1.4, F1.1, F1.3
type Client struct {
	id         string
	up, paused bool
	generation uint64
	grants     []HeldGrant
	pauseTime  time.Time
}

// RequestState tracks a particular observable request, not merely a client ID.
// derives: C1.1, C1.4, F1.1, F1.2, F1.3
type RequestState struct {
	client        string
	ref           Ref
	generation    uint64
	done          bool
	eligibleSince time.Time
}

// WireMessage is a sampled transport delivery or a paused client's inbox item.
// derives: C1.2, C1.3, F1.1, F1.2, F1.3
type WireMessage struct {
	kind, client      string
	generation        uint64
	attempt, decision Ref
	grant             HeldGrant
	value, outcome    string
	due               time.Time
}

// completedAllocation never communicates on an unbuffered runner channel.
// derives: C1.1, C1.4, F1.1, F1.2
type completedAllocation struct {
	request    *RequestState
	node       string
	generation uint64
	allocation Allocation
	err        error
}

// ProgressWitness records a finite progress horizon separately from the schema.
// derives: C1.4, F1.1, F1.2, F1.3
type ProgressWitness struct {
	Request      Ref   `json:"request"`
	StableFault  Ref   `json:"stable_fault"`
	BudgetMillis int64 `json:"budget_ms"`
}

// RunEvidence contains operational horizon certificates, never event ordering.
// derives: C1.4, F1.1, F1.2, F1.3, E1, E2
type RunEvidence struct {
	Derives     []string          `json:"derives"`
	Operational string            `json:"operational_error,omitempty"`
	Witnesses   []ProgressWitness `json:"progress_horizons"`
	Completed   bool              `json:"schedule_completed"`
	Reason      string            `json:"reason,omitempty"`
}

// Engine serializes workload actions while Raft runs its existing goroutines.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, A1, T1, T2, T3, E1
type Engine struct {
	schedule                                        Schedule
	out                                             *Emitter
	rng                                             *rand.Rand
	nodes                                           map[string]*LeaseNode
	network                                         *RaftNetwork
	clients                                         map[string]*Client
	sides                                           map[string]int
	rest                                            []string
	storage                                         string
	storageUp                                       bool
	ledger                                          uint64
	storageValue                                    string
	requests                                        []*RequestState
	wire                                            []WireMessage
	results                                         chan completedAllocation
	inflight                                        bool
	lastGrant                                       Ref
	grantor, holder                                 string
	nextGrant                                       time.Time
	mutation                                        string
	crashSeen, partitionSeen, pauseSeen, resumeSeen bool
}

// newEngine bootstraps exactly one fixed three-voter configuration.
// derives: C1.1, C1.4, F1.1, F1.2
func newEngine(s Schedule, out *Emitter, seed int64, mutation string) (*Engine, error) {
	e := &Engine{schedule: s, out: out, rng: rand.New(rand.NewSource(seed)), nodes: map[string]*LeaseNode{}, network: newRaftNetwork(), clients: map[string]*Client{}, sides: map[string]int{}, storage: s.Processes.Storage[0], storageUp: true, results: make(chan completedAllocation, 1), mutation: mutation}
	for _, id := range s.Processes.Clients {
		e.clients[id] = &Client{id: id, up: true, generation: 1}
	}
	for _, id := range s.Processes.Lease {
		n := newLeaseNode(id, e.network)
		e.nodes[id] = n
		if err := n.start(e.rpcTimeout()); err != nil {
			e.close()
			return nil, err
		}
	}
	e.connect()
	conf := raft.Configuration{}
	for _, id := range s.Processes.Lease {
		conf.Servers = append(conf.Servers, raft.Server{ID: raft.ServerID(id), Address: raft.ServerAddress(id), Suffrage: raft.Voter})
	}
	if err := e.nodes[s.Processes.Lease[0]].peer.BootstrapCluster(conf).Error(); err != nil {
		e.close()
		return nil, err
	}
	if err := e.awaitBootstrap(); err != nil {
		e.close()
		return nil, err
	}
	return e, nil
}

// awaitBootstrap establishes the fixed grantor before start-triggered faults.
// derives: C1.1, C1.4, F1.1, F1.2
func (e *Engine) awaitBootstrap() error {
	deadline := time.NewTimer(progressHorizon)
	defer deadline.Stop()
	ticker := time.NewTicker(time.Millisecond)
	defer ticker.Stop()
	for {
		ready := true
		for _, id := range e.schedule.Processes.Lease {
			configuration := e.nodes[id].peer.GetConfiguration()
			if err := configuration.Error(); err != nil {
				return fmt.Errorf("bootstrap configuration %s: %w", id, err)
			}
			servers := configuration.Configuration().Servers
			if len(servers) != len(e.schedule.Processes.Lease) {
				ready = false
				continue
			}
			for _, want := range e.schedule.Processes.Lease {
				found := false
				for _, server := range servers {
					if string(server.ID) == want && string(server.Address) == want && server.Suffrage == raft.Voter {
						found = true
					}
				}
				if !found {
					ready = false
				}
			}
		}
		if err := e.network.issue(); err != nil {
			return err
		}
		if ready {
			return nil
		}
		select {
		case <-deadline.C:
			return fmt.Errorf("initial fixed grantor configuration did not replicate")
		case <-ticker.C:
		}
	}
}

// rpcTimeout samples the Raft RPC timeout (not an observation timestamp).
// derives: C1.4, F1.2
func (e *Engine) rpcTimeout() time.Duration {
	return time.Duration(25+e.rng.Intn(15)) * time.Millisecond
}

// jitter samples within-side workload delivery order.
// derives: C1.2, C1.3, F1.2
func (e *Engine) jitter() time.Duration { return time.Duration(1+e.rng.Intn(5)) * time.Millisecond }

// close shuts down nodes even if execution failed partway through setup.
// derives: F1.1, C1.1
func (e *Engine) close() {
	for _, id := range e.schedule.Processes.Lease {
		if n := e.nodes[id]; n != nil {
			_ = n.stop()
		}
	}
}

// alive distinguishes durable state from a running process.
// derives: F1.1, C1.4
func (e *Engine) alive(id string) bool {
	if n := e.nodes[id]; n != nil {
		return n.peer != nil
	}
	if c := e.clients[id]; c != nil {
		return c.up
	}
	return id == e.storage && e.storageUp
}

// connected gates ALL application traffic, including replies, across the cut.
// derives: F1.1, F1.2, C1.3, C1.4
func (e *Engine) connected(a, b string) bool {
	return e.alive(a) && e.alive(b) && e.sides[a] == e.sides[b]
}

// connect applies the same complete cut to the Raft transport router.
// derives: F1.1, F1.2, C1.1, C1.4
func (e *Engine) connect() { e.network.partition(e.sides) }

// eligible is the contract's majority/storage/requester connectivity predicate.
// derives: C1.4, F1.1, F1.2, F1.3
func (e *Engine) eligible(r *RequestState) bool {
	c := e.clients[r.client]
	if !c.up || c.paused || c.generation != r.generation || !e.connected(r.client, e.storage) {
		return false
	}
	count := 0
	for _, id := range e.schedule.Processes.Lease {
		if e.connected(r.client, id) && e.connected(e.storage, id) {
			count++
		}
	}
	return count >= 2
}

// request emits once; retries reuse that request's identity.
// derives: C1.1, C1.4, F1.1, F1.2, F1.3
func (e *Engine) request(id string) error {
	c := e.clients[id]
	if !c.up || c.paused {
		return fmt.Errorf("request from unavailable client %s", id)
	}
	r := e.out.emit(Event{Proc: id, Event: "Request", Client: id, Key: "k"})
	e.requests = append(e.requests, &RequestState{client: id, ref: r, generation: c.generation})
	return nil
}

// suppressGrant is the deliberate liveness enforcement break, one pair per run.
// derives: C1.4, F1.1, F1.2, F1.3
func (e *Engine) suppressGrant() bool {
	// mutation: P10 suppress grant service after a minority crash.
	if e.mutation == "P10" && e.crashSeen {
		return true
	}
	// mutation: P11 suppress grant service after a partition, including after heal.
	if e.mutation == "P11" && e.partitionSeen {
		return true
	}
	// mutation: P12 retain a paused holder forever and suppress later grants.
	return e.mutation == "P12" && e.pauseSeen
}

// pump advances sampled messages and retries requests without blocking faults.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func (e *Engine) pump() {
	now := time.Now()
	select {
	case result := <-e.results:
		e.inflight = false
		e.finishAllocation(result)
	default:
	}
	e.deliver(now)
	for _, r := range e.requests {
		if r.done {
			continue
		}
		if e.eligible(r) {
			if r.eligibleSince.IsZero() {
				r.eligibleSince = now
			}
		} else {
			r.eligibleSince = time.Time{}
		}
	}
	if e.inflight || now.Before(e.nextGrant) || e.suppressGrant() {
		return
	}
	for _, r := range e.requests {
		c := e.clients[r.client]
		if r.done || !c.up || c.paused || r.generation != c.generation {
			continue
		}
		for _, id := range e.schedule.Processes.Lease {
			n := e.nodes[id]
			if n.peer == nil || n.peer.State() != raft.Leader || !e.connected(r.client, id) {
				continue
			}
			// Majority authority remains Raft's responsibility; the runner never allocates a token itself.
			future := n.peer.Apply([]byte("allocate"), 100*time.Millisecond)
			e.inflight = true
			go func(req *RequestState, node string, generation uint64, f raft.ApplyFuture) {
				v := completedAllocation{request: req, node: node, generation: generation, err: f.Error()}
				if v.err == nil {
					allocation, ok := f.Response().(Allocation)
					if !ok {
						v.err = fmt.Errorf("unexpected FSM reply %T", f.Response())
					} else {
						v.allocation = allocation
					}
				}
				e.results <- v
			}(r, id, n.generation, future)
			return
		}
	}
}

// finishAllocation issues a grant only if its committed reply reaches the client.
// derives: C1.1, C1.4, F1.1, F1.2, F1.3
func (e *Engine) finishAllocation(v completedAllocation) {
	r := v.request
	c := e.clients[r.client]
	n := e.nodes[v.node]
	if v.err != nil || r.done || c.generation != r.generation || c.paused || n.generation != v.generation || !e.connected(v.node, r.client) {
		return
	}
	token := v.allocation.Token
	// mutation: P1 lose the allocation watermark after grantor crash/restart.
	if e.mutation == "P1" && e.crashSeen {
		token = 1
	}
	// mutation: P2 reuse the initial token after the grantor is partitioned.
	if e.mutation == "P2" && e.partitionSeen {
		token = 1
	}
	// mutation: P3 reuse a token while the preceding holder is paused.
	if e.mutation == "P3" && e.pauseSeen && e.lastGrant.Seq != 0 {
		for _, event := range e.out.events {
			if (Ref{event.Proc, event.Seq}) == e.lastGrant {
				token = event.Token
				break
			}
		}
	}
	ref := e.out.emit(Event{Proc: v.node, Event: "Grant", Client: r.client, Key: "k", Token: token, Lifetime: grantLifetime.Milliseconds(), Term: v.allocation.Term}, r.ref, e.lastGrant)
	now := time.Now()
	c.grants = append(c.grants, HeldGrant{token: token, term: v.allocation.Term, ref: ref, expires: now.Add(grantLifetime)})
	e.lastGrant = ref
	e.grantor = v.node
	e.holder = r.client
	e.nextGrant = now.Add(grantLifetime)
	r.done = true
}

// write selects the client's actual grant and queues delivery to storage.
// derives: C1.2, C1.3, F1.1, F1.2, F1.3, T3
func (e *Engine) write(id, value, selection string) error {
	c := e.clients[id]
	if !c.up || c.paused || len(c.grants) == 0 {
		return fmt.Errorf("write without available grant: %s", id)
	}
	g := c.grants[len(c.grants)-1]
	if selection == "stale" {
		found := false
		for i := len(c.grants) - 1; i >= 0; i-- {
			candidate := c.grants[i]
			if candidate.token < e.highestGranted() {
				g = candidate
				found = true
				break
			}
		}
		if !found {
			return fmt.Errorf("T3: no numerically superseded token")
		}
	}
	ref := e.out.emit(Event{Proc: id, Event: "WriteAttempt", Client: id, Key: "k", Token: g.token, Term: g.term, Value: value}, g.ref)
	// A write sent across a cut is lost even if the partition heals immediately.
	if !e.connected(id, e.storage) {
		e.ghostAck(WireMessage{client: id, generation: c.generation, attempt: ref, grant: g})
		return nil
	}

	m := WireMessage{kind: "write", client: id, generation: c.generation, attempt: ref, grant: g, value: value, due: time.Now().Add(e.jitter())}
	e.wire = append(e.wire, m)
	if e.rng.Intn(3) == 0 {
		duplicate := m
		duplicate.due = duplicate.due.Add(e.jitter())
		e.wire = append(e.wire, duplicate)
	}
	return nil
}

// ghostAck breaks the client success path only for writes that never reached storage.
// derives: C1.3, F1.1, F1.2
func (e *Engine) ghostAck(m WireMessage) {
	c := e.clients[m.client]
	if !c.up || c.paused || c.generation != m.generation {
		return
	}
	// mutation: P8 manufacture success for an undelivered write across a partition.
	if e.mutation == "P8" && e.partitionSeen {
		e.out.emit(Event{Proc: m.client, Event: "WriteAck", Client: m.client, Key: "k", Token: m.grant.token, Outcome: "accepted"}, m.attempt)
	}
}

// storageDecision compares against the retained ledger atomically.
// derives: C1.2, C1.3, F1.1, F1.2, F1.3, T1, E2
func (e *Engine) storageDecision(m WireMessage) {
	// mutation: P7 after storage restart, bypass acceptance and fabricate its success reply.
	// derives: C1.3, F1.1, T1, E2
	if e.mutation == "P7" && e.crashSeen {
		m.kind = "ack"
		m.decision = m.attempt
		m.outcome = "accepted"
		m.due = time.Now().Add(e.jitter())
		e.wire = append(e.wire, m)
		return
	}
	before := e.ledger
	accept := m.grant.token >= before
	// mutation: P5 bypass the fencing comparison in the partition path.
	if e.mutation == "P5" && e.partitionSeen {
		accept = true
	}
	// mutation: P6 bypass the fencing comparison after a paused client resumes.
	if e.mutation == "P6" && e.resumeSeen {
		accept = true
	}
	name, outcome := "WriteReject", "rejected"
	if accept {
		name = "WriteAccept"
		outcome = "accepted"
		e.ledger = m.grant.token
		e.storageValue = m.value
	}
	ref := e.out.emit(Event{Proc: e.storage, Event: name, Key: "k", Token: m.grant.token, Term: m.grant.term, HighestBefore: &before}, m.attempt)
	m.kind = "ack"
	m.decision = ref
	m.outcome = outcome
	m.due = time.Now().Add(8*time.Millisecond + e.jitter())
	e.wire = append(e.wire, m)
}

// deliver samples due-message order; a cut drops messages rather than delaying them.
// derives: C1.2, C1.3, F1.1, F1.2, F1.3
func (e *Engine) deliver(now time.Time) {
	messages := e.wire
	e.wire = nil
	e.rng.Shuffle(len(messages), func(i, j int) { messages[i], messages[j] = messages[j], messages[i] })
	for _, m := range messages {
		if now.Before(m.due) {
			e.wire = append(e.wire, m)
			continue
		}
		c := e.clients[m.client]
		if m.kind == "write" {
			if !e.connected(m.client, e.storage) {
				e.ghostAck(m)
				continue
			}
			e.storageDecision(m)
			continue
		}
		if !e.connected(e.storage, m.client) || c.generation != m.generation {
			continue
		}
		if c.paused {
			e.wire = append(e.wire, m)
			continue
		}
		outcome := m.outcome
		// mutation: P9 turn an actual stale rejection after resume into a success reply.
		if e.mutation == "P9" && e.resumeSeen && outcome == "rejected" {
			outcome = "accepted"
		}
		e.out.emit(Event{Proc: m.client, Event: "WriteAck", Client: m.client, Key: "k", Token: m.grant.token, Outcome: outcome}, m.decision)
	}
}

// expandPartition resolves aliases at the trigger, not when the YAML is parsed.
// derives: F1.2, C1.1, C1.2, C1.4, A1
func (e *Engine) expandPartition(input [][]string) ([][]string, error) {
	output := [][]string{{}, {}}
	used := map[string]bool{}
	rest := -1
	for side, members := range input {
		for _, id := range members {
			switch id {
			case "grantor":
				id = e.grantor
			case "holder":
				id = e.holder
			case "rest":
				if rest >= 0 {
					return nil, fmt.Errorf("duplicate rest alias")
				}
				rest = side
				continue
			}
			if id == "" || used[id] {
				return nil, fmt.Errorf("unresolved or duplicate partition member %s", id)
			}
			used[id] = true
			output[side] = append(output[side], id)
		}
	}
	all := append(append(append([]string{}, e.schedule.Processes.Lease...), e.schedule.Processes.Clients...), e.storage)
	for _, id := range all {
		if !used[id] {
			if rest < 0 {
				return nil, fmt.Errorf("partition omits %s", id)
			}
			output[rest] = append(output[rest], id)
		}
	}
	if len(output[0]) == 0 || len(output[1]) == 0 {
		return nil, fmt.Errorf("empty partition side")
	}
	for i := range output {
		sort.Strings(output[i])
	}
	return output, nil
}

// act applies only a validated workload action or one admitted failure cell.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func (e *Engine) act(a Action, trigger Ref) error {
	if a.Request != "" {
		return e.request(a.Request)
	}
	if a.Write != "" {
		return e.write(a.Write, a.Value, a.Token)
	}
	v := Event{Proc: "env", Event: "Fault", Cell: a.Cell, Crash: a.Crash, Restart: a.Restart, Heal: a.Heal, Pause: a.Pause, Resume: a.Resume}
	if a.Partition != nil {
		resolved, err := e.expandPartition(a.Partition)
		if err != nil {
			return err
		}
		v.Partition = resolved
	}
	if a.Crash != "" && !e.alive(a.Crash) {
		return fmt.Errorf("crash of stopped process %s", a.Crash)
	}
	if a.Restart != "" && e.alive(a.Restart) {
		return fmt.Errorf("restart of running process %s", a.Restart)
	}
	if a.Pause != "" {
		c := e.clients[a.Pause]
		if !c.up || c.paused || len(c.grants) == 0 || !time.Now().Before(c.grants[len(c.grants)-1].expires) {
			return fmt.Errorf("pause requires an unexpired holder")
		}
	}
	if a.Resume != "" {
		c := e.clients[a.Resume]
		if !c.up || !c.paused || time.Since(c.pauseTime) <= grantLifetime {
			return fmt.Errorf("resume must follow pause longer than lifetime")
		}
	}
	e.out.emit(v, trigger)
	for _, r := range e.requests {
		r.eligibleSince = time.Time{}
	}
	// derives: F1.1 — crash discards volatile state, retaining only the named stores.
	if id := a.Crash; id != "" {
		e.crashSeen = true
		if n := e.nodes[id]; n != nil {
			if err := n.stop(); err != nil {
				return err
			}
		} else if c := e.clients[id]; c != nil {
			c.up = false
			c.paused = false
			c.grants = nil
			c.generation++
		} else {
			e.storageUp = false
		}
		e.connect()
	}
	// derives: F1.1 — restarted clients have no grant; Raft nodes replay durable logs.
	if id := a.Restart; id != "" {
		if n := e.nodes[id]; n != nil {
			if err := n.start(e.rpcTimeout()); err != nil {
				return err
			}
		} else if c := e.clients[id]; c != nil {
			c.up = true
			c.paused = false
			c.grants = nil
		} else {
			e.storageUp = true
			// mutation: P4 erase the durable storage ledger on the restart path.
			if e.mutation == "P4" {
				e.ledger = 0
			}
		}
		e.connect()
	}
	// derives: F1.2 — complete bipartition, dropped application and Raft messages.
	if v.Partition != nil {
		e.partitionSeen = true
		e.sides = map[string]int{}
		for side, ids := range v.Partition {
			for _, id := range ids {
				e.sides[id] = side
			}
		}
		e.dropCrossing()
		e.connect()
	}
	if a.Heal {
		e.sides = map[string]int{}
		e.connect()
	}
	// derives: F1.3 — client execution and reply receipt stop while grant time continues.
	if a.Pause != "" {
		e.pauseSeen = true
		c := e.clients[a.Pause]
		c.paused = true
		c.pauseTime = time.Now()
		// A later Grant is the schedule's witness of a complete holder pause.
		if horizon := c.pauseTime.Add(grantLifetime + time.Millisecond); horizon.After(e.nextGrant) {
			e.nextGrant = horizon
		}
	}
	if a.Resume != "" {
		e.resumeSeen = true
		e.clients[a.Resume].paused = false
	}
	return nil
}

// dropCrossing prevents a queued message from reappearing after heal.
// derives: F1.2, C1.3
func (e *Engine) dropCrossing() {
	messages := e.wire
	e.wire = nil
	for _, m := range messages {
		if e.sides[m.client] == e.sides[e.storage] {
			e.wire = append(e.wire, m)
		}
	}
}

// witnesses certifies only uninterrupted, eligible progress opportunities.
// derives: C1.4, F1.1, F1.2, F1.3
func (e *Engine) witnesses() []ProgressWitness {
	var result []ProgressWitness
	now := time.Now()
	for _, r := range e.requests {
		if !r.done && !r.eligibleSince.IsZero() && e.eligible(r) && now.Sub(r.eligibleSince) >= progressHorizon {
			result = append(result, ProgressWitness{r.ref, e.out.fault, progressHorizon.Milliseconds()})
		}
	}
	return result
}
