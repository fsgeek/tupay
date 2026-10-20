// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"
)

// Trigger is a monotone predicate over previously emitted events.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
type Trigger struct {
	Start   bool
	Filters map[string]string
}

// UnmarshalYAML rejects unknown or non-observable trigger fields.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func (t *Trigger) UnmarshalYAML(n *yaml.Node) error {
	if n.Kind == yaml.ScalarNode {
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
// derives: C1.1, C1.2, C1.3, C1.4
func observable(s string) bool {
	switch s {
	case "Request", "Grant", "WriteAttempt", "WriteAccept", "WriteReject", "WriteAck":
		return true
	}
	return false
}

// Action is the complete, closed action language; there is no arbitrary sleep.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
type Action struct {
	Request   string     `yaml:"request,omitempty"`
	Write     string     `yaml:"write,omitempty"`
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
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
type Step struct {
	At Trigger `yaml:"at"`
	Do Action  `yaml:"do"`
}

// Schedule is the shared YAML interface interpreted independently here.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
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

// loadSchedule reads only this author's own directory, never shared artifacts.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func loadSchedule(name string) (Schedule, error) {
	var s Schedule
	path := name
	if !strings.HasSuffix(path, ".yaml") {
		path = filepath.Join("testbed", "schedules", path+".yaml")
	}
	root, err := filepath.Abs(".")
	if err != nil {
		return s, err
	}
	abs, err := filepath.EvalSymlinks(path)
	if err != nil {
		return s, err
	}
	abs, err = filepath.Abs(abs)
	if err != nil {
		return s, err
	}
	rel, err := filepath.Rel(root, abs)
	if err != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(os.PathSeparator)) {
		return s, fmt.Errorf("schedule outside impl/ is forbidden")
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
			if id == "" || id == "env" || id == "rest" || id == "grantor" || id == "holder" || ids[id] != "" {
				return s, fmt.Errorf("invalid process %q", id)
			}
			ids[id] = group.role
		}
	}
	known := map[string]bool{"C1.1": true, "C1.2": true, "C1.3": true, "C1.4": true, "F1.1": true, "F1.2": true, "F1.3": true}
	if len(s.Derives) == 0 {
		return s, fmt.Errorf("missing derivations")
	}
	for _, id := range s.Derives {
		if !known[id] {
			return s, fmt.Errorf("unknown derivation %s", id)
		}
	}
	for _, step := range s.Steps {
		if !step.At.Start && len(step.At.Filters) == 0 {
			return s, fmt.Errorf("missing trigger")
		}
		if err := validateAction(step.Do, ids); err != nil {
			return s, err
		}
	}
	if !s.End.Start && len(s.End.Filters) == 0 {
		return s, fmt.Errorf("missing end trigger")
	}
	return s, nil
}

// validateAction rejects out-of-model faults and malformed workload actions.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func validateAction(a Action, ids map[string]string) error {
	count := 0
	for _, v := range []bool{a.Request != "", a.Write != "", a.Crash != "", a.Restart != "", a.Partition != nil, a.Heal, a.Pause != "", a.Resume != ""} {
		if v {
			count++
		}
	}
	if count != 1 {
		return fmt.Errorf("action must contain exactly one operation")
	}
	if a.Request != "" || a.Write != "" {
		id := a.Request
		if a.Write != "" {
			id = a.Write
		}
		if ids[id] != "client" || a.Cell != "" || a.Request != "" && (a.Token != "" || a.Value != "") || a.Token != "" && a.Token != "stale" {
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
		if ids[id] == "" || a.Cell != "F1.1" {
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
					if ids[id] == "" && id != "grantor" && id != "holder" && id != "rest" {
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
	if a.Cell != "F1.3" || ids[id] != "client" {
		return fmt.Errorf("invalid pause/resume")
	}
	return nil
}

// triggerRef returns the first historical event satisfying all filters.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func triggerRef(t Trigger, events []Event) (Ref, bool) {
	if t.Start {
		return Ref{}, true
	}
	for _, e := range events {
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
