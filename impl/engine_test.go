// derives: C1.4, F1.1
package main

import (
	"path/filepath"
	"testing"
)

// TestC14_F11_StartupVotersBeforeFaults probes the setup boundary before start faults.
// derives: C1.4, F1.1
func TestC14_F11_StartupVotersBeforeFaults(t *testing.T) {
	s := fixtureSchedule()
	s.Name = "bootstrap-regression"
	out, err := newEmitter(filepath.Join(t.TempDir(), "bootstrap.jsonl"), s.Name)
	if err != nil {
		t.Fatal(err)
	}
	defer out.close()
	e, err := newEngine(s, out, 1, "")
	if err != nil {
		t.Fatal(err)
	}
	defer e.close()
	for _, id := range s.Processes.Lease {
		_, configuration, err := e.nodes[id].durable.InitialState()
		if err != nil {
			t.Fatal(err)
		}
		voters := map[string]bool{}
		for _, number := range configuration.Voters {
			voters[e.network.names[number]] = true
		}
		if len(voters) != 3 {
			t.Errorf("%s exposes start before fixed cluster is ready: voters=%v", id, voters)
			continue
		}
		for _, want := range s.Processes.Lease {
			if !voters[want] {
				t.Errorf("%s missing voter %s before start", id, want)
			}
		}
	}
}
