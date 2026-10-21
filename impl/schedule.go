// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"
)

// Trigger describes a freshly armed event predicate or terminal quiescence.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
type Trigger struct {
	Start     bool
	Quiescent bool
	Filters   map[string]string
}

// UnmarshalYAML rejects unknown or non-observable trigger fields.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
func (t *Trigger) UnmarshalYAML(n *yaml.Node) error {
	if n.Kind == yaml.ScalarNode {
		if n.Value == "quiescent" {
			t.Quiescent = true
			return nil
		}
		if n.Value != "start" {
			return fmt.Errorf("unknown trigger %q", n.Value)
		}
		t.Start = true
		return nil
	}
	if n.Kind != yaml.MappingNode {
		return fmt.Errorf("trigger must be start or a mapping")
	}
	t.Filters = map[string]string{}
	allowed := map[string]bool{"event": true, "client": true, "key": true, "token": true, "lifetime": true, "grantor_term": true, "value": true, "highest_before": true, "outcome": true, "proc": true}
	for i := 0; i < len(n.Content); i += 2 {
		k, v := n.Content[i].Value, n.Content[i+1]
		if !allowed[k] || v.Kind != yaml.ScalarNode {
			return fmt.Errorf("unsupported trigger field %q", k)
		}
		if _, ok := t.Filters[k]; ok {
			return fmt.Errorf("duplicate trigger field %s", k)
		}
		t.Filters[k] = v.Value
	}
	if !observable(t.Filters["event"]) {
		return fmt.Errorf("trigger must name an observable event")
	}
	return nil
}

// observable excludes injector events from contract triggers.
// derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2
func observable(s string) bool {
	switch s {
	case "Request", "Grant", "WriteAttempt", "WriteAccept", "WriteReject", "WriteAck", "ReadAttempt", "ReadAccept", "ReadReject", "ReadAck":
		return true
	}
	return false
}

// Action is the complete, closed action language; there is no arbitrary sleep.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
type Action struct {
	Request   string     `yaml:"request,omitempty"`
	Write     string     `yaml:"write,omitempty"`
	Read      string     `yaml:"read,omitempty"`
	Value     string     `yaml:"value,omitempty"`
	Token     string     `yaml:"token,omitempty"`
	Cell      string     `yaml:"cell,omitempty"`
	Crash     string     `yaml:"crash,omitempty"`
	Restart   string     `yaml:"restart,omitempty"`
	Partition [][]string `yaml:"partition,omitempty"`
	Heal      bool       `yaml:"heal,omitempty"`
	Pause     string     `yaml:"pause,omitempty"`
	Resume    string     `yaml:"resume,omitempty"`
}

// Step waits for its trigger and then applies exactly one action.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
type Step struct {
	At Trigger `yaml:"at"`
	Do Action  `yaml:"do"`
}

// Schedule is the shared YAML interface interpreted independently here.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
type Schedule struct {
	Name      string   `yaml:"schedule"`
	Derives   []string `yaml:"derives"`
	Processes struct {
		Lease   []string `yaml:"lease"`
		Clients []string `yaml:"clients"`
		Storage []string `yaml:"storage"`
	} `yaml:"processes"`
	Steps []Step  `yaml:"steps"`
	End   Trigger `yaml:"end"`
	Bound struct {
		Events int `yaml:"events"`
	} `yaml:"bound"`
}

// loadSchedule resolves only the repository-root shared schedule directory.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
func loadSchedule(name string) (Schedule, error) {
	var s Schedule
	base := strings.TrimSuffix(name, ".yaml")
	if base == "" || filepath.Base(base) != base || strings.ContainsAny(base, "/\\") {
		return s, fmt.Errorf("schedule must be a shared basename")
	}
	root, err := filepath.Abs(filepath.Join("..", "testbed", "schedules"))
	if err != nil {
		return s, err
	}
	canonicalRoot, err := filepath.EvalSymlinks(root)
	if err != nil {
		return s, err
	}
	abs, err := filepath.EvalSymlinks(filepath.Join(root, base+".yaml"))
	if err != nil {
		return s, err
	}
	if filepath.Dir(abs) != canonicalRoot {
		return s, fmt.Errorf("schedule escapes shared directory")
	}
	f, err := os.Open(abs)
	if err != nil {
		return s, err
	}
	defer f.Close()
	d := yaml.NewDecoder(f)
	d.KnownFields(true)
	if err = d.Decode(&s); err != nil {
		return s, err
	}
	var extra any
	if err = d.Decode(&extra); err != io.EOF {
		return s, fmt.Errorf("exactly one YAML document required")
	}
	if s.Name == "" || strings.ContainsAny(s.Name, "/\\") || s.Bound.Events < 1 || s.Bound.Events > 10000 || len(s.Steps) == 0 {
		return s, fmt.Errorf("invalid schedule name, bound or empty steps")
	}
	if len(s.Processes.Lease) != 3 || len(s.Processes.Clients) != 2 || len(s.Processes.Storage) != 1 {
		return s, fmt.Errorf("need 3 lease nodes, 2 clients, 1 storage")
	}
	ids := map[string]string{}
	for _, group := range []struct {
		ids  []string
		role string
	}{{s.Processes.Lease, "lease"}, {s.Processes.Clients, "client"}, {s.Processes.Storage, "storage"}} {
		for _, id := range group.ids {
			if id == "" || id == "env" || id == "rest" || id == "grantor" || id == "holder" || id == "non-grantor" || ids[id] != "" {
				return s, fmt.Errorf("invalid process %q", id)
			}
			ids[id] = group.role
		}
	}
	known := map[string]bool{"C1.1": true, "C1.2": true, "C1.3": true, "C1.4": true, "C2.1": true, "C2.2": true, "F1.1": true, "F1.2": true, "F1.3": true, "T1": true, "T2": true, "T3": true, "A1": true, "A2": true, "E1": true, "E2": true}
	if len(s.Derives) == 0 {
		return s, fmt.Errorf("missing derivations")
	}
	for _, id := range s.Derives {
		if !known[id] {
			return s, fmt.Errorf("unknown derivation %s", id)
		}
	}
	for _, step := range s.Steps {
		if step.At.Quiescent || !step.At.Start && len(step.At.Filters) == 0 {
			return s, fmt.Errorf("missing trigger")
		}
		if err := validateAction(step.Do, ids); err != nil {
			return s, err
		}
	}
	if s.End.Start || !s.End.Quiescent && len(s.End.Filters) == 0 {
		return s, fmt.Errorf("missing end trigger")
	}
	if s.Name != base {
		return s, fmt.Errorf("schedule name differs from shared basename")
	}
	if err := validateSequence(s, ids); err != nil {
		return s, err
	}
	return s, nil
}

// validateAction rejects out-of-model faults and malformed workload actions.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
func validateAction(a Action, ids map[string]string) error {
	count := 0
	for _, v := range []bool{a.Request != "", a.Write != "", a.Read != "", a.Crash != "", a.Restart != "", a.Partition != nil, a.Heal, a.Pause != "", a.Resume != ""} {
		if v {
			count++
		}
	}
	if count != 1 {
		return fmt.Errorf("action must contain exactly one operation")
	}
	if a.Request != "" || a.Write != "" || a.Read != "" {
		id := a.Request
		if a.Write != "" {
			id = a.Write
		}
		if a.Read != "" {
			id = a.Read
		}
		if selectorRole(id, ids) != "client" && selectorRole(id, ids) != "selector" || a.Cell != "" || a.Request != "" && (a.Token != "" || a.Value != "") || a.Token != "" && a.Token != "stale" || a.Read != "" && a.Value != "" {
			return fmt.Errorf("invalid workload action")
		}
		return nil
	}
	if a.Token != "" || a.Value != "" {
		return fmt.Errorf("workload fields on fault")
	}
	if a.Crash != "" || a.Restart != "" {
		id := a.Crash
		if id == "" {
			id = a.Restart
		}
		if selectorRole(id, ids) == "" || a.Cell != "F1.1" {
			return fmt.Errorf("invalid crash/restart")
		}
		return nil
	}
	if a.Partition != nil || a.Heal {
		if a.Cell != "F1.2" {
			return fmt.Errorf("partition/heal requires F1.2")
		}
		if a.Partition != nil {
			if len(a.Partition) != 2 || len(a.Partition[0]) == 0 || len(a.Partition[1]) == 0 {
				return fmt.Errorf("need two nonempty partition sides")
			}
			for _, side := range a.Partition {
				for _, id := range side {
					if ids[id] == "" && id != "grantor" && id != "holder" && id != "rest" && id != "non-grantor" {
						return fmt.Errorf("unknown partition member %s", id)
					}
				}
			}
		}
		return nil
	}
	id := a.Pause
	if id == "" {
		id = a.Resume
	}
	if a.Cell != "F1.3" || selectorRole(id, ids) != "client" && selectorRole(id, ids) != "selector" {
		return fmt.Errorf("invalid pause/resume")
	}
	return nil
}

// triggerRef matches only events emitted after the trigger was armed.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
func triggerRef(t Trigger, events []Event, armed int) (Ref, bool) {
	if t.Start {
		return Ref{}, true
	}
	for _, e := range events[armed:] {
		fields := map[string]string{"event": e.Event, "client": e.Client, "key": e.Key, "token": fmt.Sprint(e.Token), "lifetime": fmt.Sprint(e.Lifetime), "grantor_term": fmt.Sprint(e.Term), "value": e.Value, "outcome": e.Outcome, "proc": e.Proc}
		if e.HighestBefore != nil {
			fields["highest_before"] = fmt.Sprint(*e.HighestBefore)
		}
		ok := true
		for k, v := range t.Filters {
			if fields[k] != v {
				ok = false
				break
			}
		}
		if ok {
			return Ref{e.Proc, e.Seq}, true
		}
	}
	return Ref{}, false
}
