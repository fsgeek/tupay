// derives: C1.3, C2.2, F1.1, F1.2, F1.3, A1, A2
package main

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

// schemaRecords writes independent raw records so malformed answers are not repaired.
// Removing ack provenance validation must make its counterexample tests fail.
// derives: C1.3, C2.2, F1.1, F1.2, F1.3
func schemaRecords(t *testing.T, events []Event, change func([]map[string]any)) string {
	t.Helper()
	records := make([]map[string]any, len(events))
	for i, e := range events {
		e.Run = "schema-v3-fixture"
		e.Side = "impl"
		if e.Causes == nil {
			e.Causes = []Ref{}
		}
		b, err := json.Marshal(e)
		if err != nil {
			t.Fatal(err)
		}
		if err = json.Unmarshal(b, &records[i]); err != nil {
			t.Fatal(err)
		}
		if e.Event == "WriteAck" {
			records[i]["answers"] = Ref{"c1", 2}
		}
		if e.Event == "ReadAck" {
			records[i]["answers"] = Ref{"c1", 4}
		}
	}
	change(records)
	path := filepath.Join(t.TempDir(), "schema.jsonl")
	f, err := os.Create(path)
	if err != nil {
		t.Fatal(err)
	}
	enc := json.NewEncoder(f)
	for i := len(records) - 1; i >= 0; i-- {
		if err = enc.Encode(records[i]); err != nil {
			t.Fatal(err)
		}
	}
	if err = f.Close(); err != nil {
		t.Fatal(err)
	}
	return path
}

// TestObserveV3Answers rejects malformed correlation without inventing a contract failure.
// derives: C1.3, C2.2, F1.1, F1.2, F1.3
func TestObserveV3Answers(t *testing.T) {
	for _, kind := range []string{"write", "read"} {
		t.Run(kind, func(t *testing.T) {
			base := checkerFixture()
			if kind == "read" {
				base = readFixture()
			}
			for _, tc := range []struct {
				name   string
				bad    bool
				change func(map[string]any)
			}{
				{"valid", false, func(m map[string]any) {}},
				{"missing", true, func(m map[string]any) { delete(m, "answers") }},
				{"zero", true, func(m map[string]any) { m["answers"] = Ref{} }},
				{"absent", true, func(m map[string]any) { m["answers"] = Ref{"c1", 99} }},
				{"wrong-kind", true, func(m map[string]any) { m["answers"] = Ref{"n1", 1} }},
				{"wrong-operation", true, func(m map[string]any) {
					if kind == "read" {
						m["answers"] = Ref{"c1", 2}
					} else {
						m["answers"] = Ref{"c1", 1}
					}
				}},
			} {
				t.Run(tc.name, func(t *testing.T) {
					path := schemaRecords(t, base, func(ms []map[string]any) { tc.change(ms[len(ms)-1]) })
					v := checkTrace(path, fixtureSchedule(), RunEvidence{Completed: true})
					if tc.bad {
						if v.Clause != "" || v.Reason == "" {
							t.Fatalf("want unexplained provenance, got %+v", v)
						}
					} else if v != (Verdict{}) {
						t.Fatalf("valid answers: %+v", v)
					}
				})
			}
		})
	}
}

// TestObserveV3SameTokenRetry catches answers to an old attempt reachable through program order.
// derives: C1.3, F1.1, F1.2
func TestObserveV3SameTokenRetry(t *testing.T) {
	es := checkerFixture()
	seven := uint64(7)
	es = append(es, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "retry", Causes: []Ref{{"n1", 1}, {"c1", 3}}}, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Causes: []Ref{{"c1", 4}, {"s", 1}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"s", 2}, {"c1", 4}}})
	path := schemaRecords(t, es, func(ms []map[string]any) {})
	v := checkTrace(path, fixtureSchedule(), RunEvidence{Completed: true})
	if v.Clause != "" || v.Reason == "" {
		t.Fatalf("old same-token attempt should be unexplained: %+v", v)
	}
}

// TestObserveV3LiveAcks checks actual write/read/late-reply emission, not just fixtures.
// derives: C1.3, C2.2, F1.3
func TestObserveV3LiveAcks(t *testing.T) {
	s, err := loadSchedule("P18")
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(t.TempDir(), "live.jsonl")
	out, err := newEmitter(path, "schema-v3-live")
	if err != nil {
		t.Fatal(err)
	}
	e, err := newEngine(s, out, 1, "")
	if err != nil {
		out.close()
		t.Fatal(err)
	}
	evidence := e.drive()
	e.close()
	if err = out.close(); err != nil {
		t.Fatal(err)
	}
	if !evidence.Completed {
		t.Fatalf("schedule: %+v", evidence)
	}
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var records []map[string]any
	dec := json.NewDecoder(bytes.NewReader(data))
	for dec.More() {
		var m map[string]any
		if err = dec.Decode(&m); err != nil {
			t.Fatal(err)
		}
		records = append(records, m)
	}
	count := 0
	for _, m := range records {
		_, has := m["answers"]
		if m["event"] == "WriteAck" || m["event"] == "ReadAck" {
			count++
			if !has {
				t.Errorf("%s missing answers", m["event"])
			}
		} else if has {
			t.Errorf("non-ack %s has answers", m["event"])
		}
	}
	if count < 3 {
		t.Fatalf("missing write/read/late acknowledgements: %d", count)
	}
}
