// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C2.1, C2.2
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

// Ref identifies an event without a cross-process clock.
// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3, C2.1, C2.2
type Ref struct {
	Proc string `json:"proc"`
	Seq  uint64 `json:"seq"`
}

// Event is the shared observable record. Fault fields are copied from the action.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C2.1, C2.2
type Event struct {
	Proc          string     `json:"proc"`
	Seq           uint64     `json:"seq"`
	Event         string     `json:"event"`
	Client        string     `json:"client,omitempty"`
	Key           string     `json:"key,omitempty"`
	Token         uint64     `json:"token,omitempty"`
	Lifetime      int64      `json:"lifetime,omitempty"`
	Term          uint64     `json:"grantor_term,omitempty"`
	Value         string     `json:"value,omitempty"`
	ValuePresent  bool       `json:"-"`
	HighestBefore *uint64    `json:"highest_before,omitempty"`
	Outcome       string     `json:"outcome,omitempty"`
	Causes        []Ref      `json:"causes"`
	Run           string     `json:"run"`
	Side          string     `json:"side"`
	Cell          string     `json:"cell,omitempty"`
	Crash         string     `json:"crash,omitempty"`
	Restart       string     `json:"restart,omitempty"`
	Partition     [][]string `json:"partition,omitempty"`
	Heal          bool       `json:"heal,omitempty"`
	Pause         string     `json:"pause,omitempty"`
	Resume        string     `json:"resume,omitempty"`
}

// Emitter persists events synchronously; only the runner's event loop calls it.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C2.1, C2.2
type Emitter struct {
	file   *os.File
	run    string
	seq    map[string]uint64
	events []Event
	fault  Ref
	err    error
}

// newEmitter creates one trace per run, without truncating another run's trace.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C2.1, C2.2
func newEmitter(path, run string) (*Emitter, error) {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0644)
	if err != nil {
		return nil, err
	}
	return &Emitter{file: f, run: run, seq: map[string]uint64{}}, nil
}

// emit adds local program order and the latest environmental cause.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C2.1, C2.2
func (e *Emitter) emit(v Event, causes ...Ref) Ref {
	e.seq[v.Proc]++
	v.Seq = e.seq[v.Proc]
	v.Run = e.run
	v.Side = "impl"
	v.Causes = make([]Ref, 0, len(causes)+2)
	add := func(r Ref) {
		if r.Seq == 0 {
			return
		}
		for _, x := range v.Causes {
			if x == r {
				return
			}
		}
		v.Causes = append(v.Causes, r)
	}
	if v.Seq > 1 {
		add(Ref{v.Proc, v.Seq - 1})
	}
	add(e.fault)
	for _, r := range causes {
		add(r)
	}
	if err := json.NewEncoder(e.file).Encode(v); err != nil && e.err == nil {
		e.err = err
	}
	e.events = append(e.events, v)
	r := Ref{v.Proc, v.Seq}
	if v.Event == "Fault" {
		e.fault = r
	}
	return r
}

// close makes emitter failures operational errors rather than checker results.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C2.1, C2.2
func (e *Emitter) close() error {
	err := e.file.Close()
	if e.err != nil {
		return fmt.Errorf("observe: %w", e.err)
	}
	return err
}

// MarshalJSON emits even an empty value exactly when a read serves a value.
// derives: C2.2
func (e Event) MarshalJSON() ([]byte, error) {
	type plain Event
	var value *string
	if e.Event == "ReadAccept" || e.Event == "ReadAck" && e.Outcome == "served" || e.Event == "WriteAttempt" && e.Value != "" {
		value = &e.Value
	}
	return json.Marshal(struct {
		plain
		Value *string `json:"value,omitempty"`
	}{plain(e), value})
}

// UnmarshalJSON retains value presence so empty and absent are distinguishable.
// derives: C2.2
func (e *Event) UnmarshalJSON(data []byte) error {
	type plain Event
	var v plain
	if err := json.Unmarshal(data, &v); err != nil {
		return err
	}
	var fields map[string]json.RawMessage
	if err := json.Unmarshal(data, &fields); err != nil {
		return err
	}
	*e = Event(v)
	raw, ok := fields["value"]
	e.ValuePresent = ok && string(raw) != "null"
	return nil
}
