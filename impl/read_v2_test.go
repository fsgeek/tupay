// derives: C2.1, C2.2, F1.1, F1.2, F1.3, T1, T3, A1, E2
package main

import (
	"encoding/json"
	"fmt"
	"gopkg.in/yaml.v3"
	"path/filepath"
	"testing"
	"time"
)

// readFixture extends hand-authored accepted-write evidence with one served read.
// Removing C2 checking or trusting reply values makes the counterexamples fail.
// derives: C2.1, C2.2, F1.1, F1.2, F1.3
func readFixture() []Event {
	es := checkerFixture()
	seven := uint64(7)
	return append(es,
		Event{Proc: "c1", Seq: 4, Event: "ReadAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Causes: []Ref{{"n1", 1}}},
		Event{Proc: "s", Seq: 2, Event: "ReadAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Value: "v", Causes: []Ref{{"c1", 4}}},
		Event{Proc: "c1", Seq: 5, Event: "ReadAck", Answers: &Ref{"c1", 4}, Client: "c1", Key: "k", Token: 7, Outcome: "served", Value: "v", Causes: []Ref{{"s", 2}}})
}

// TestX1ReadCheckers uses counterexamples independent of running storage state.
// derives: C2.1, C2.2, F1.1, F1.2, F1.3, E2
func TestX1ReadCheckers(t *testing.T) {
	cases := []struct {
		name, clause string
		change       func([]Event) []Event
	}{
		{"equal-token-valid", "", func(es []Event) []Event { return es }},
		{"stale-served", "C2.1", func(es []Event) []Event { es[6].Token = 6; return es }},
		{"forged-read-ledger", "C2.1", func(es []Event) []Event { zero := uint64(0); es[6].HighestBefore = &zero; return es }},
		{"wrong-storage-snapshot", "C2.2", func(es []Event) []Event { es[6].Value = "invented"; es[7].Value = "invented"; return es }},
		{"wrong-reply-value", "C2.2", func(es []Event) []Event { es[7].Value = "later-value"; return es }},
		{"wrong-reply-client", "C2.2", func(es []Event) []Event { es[7].Client = "c2"; return es }},
		{"unserved-attempt", "C2.2", func(es []Event) []Event { es = append(es[:6], es[7]); es[6].Causes = []Ref{{"c1", 4}}; return es }},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			es := tc.change(readFixture())
			v := checkTrace(writeFixture(t, es), fixtureSchedule(), RunEvidence{Completed: true})
			if v.Clause != tc.clause || tc.clause == "" && v.Reason != "" {
				t.Fatalf("want %q, got %+v", tc.clause, v)
			}
			if tc.clause != "" {
				v = checkTrace(writeFixture(t, es), fixtureSchedule(), RunEvidence{Reason: "end unreachable"})
				if v.Clause != tc.clause {
					t.Fatalf("E2: %+v", v)
				}
			}
		})
	}
}

// TestX1ReadValuePresence distinguishes the initial empty value from no value.
// derives: C2.2
func TestX1ReadValuePresence(t *testing.T) {
	for _, tc := range []struct {
		event, outcome string
		present        bool
	}{{"ReadAccept", "", true}, {"ReadAck", "served", true}, {"ReadReject", "", false}, {"ReadAck", "rejected", false}} {
		b, err := json.Marshal(Event{Event: tc.event, Outcome: tc.outcome})
		if err != nil {
			t.Fatal(err)
		}
		var fields map[string]json.RawMessage
		if err = json.Unmarshal(b, &fields); err != nil {
			t.Fatal(err)
		}
		_, has := fields["value"]
		if has != tc.present {
			t.Errorf("%s %s value present=%v, want %v", tc.event, tc.outcome, has, tc.present)
		}
	}
}

// TestX1SharedReadCompiler rejects stale closed-language handling of new schedules.
// derives: C2.1, C2.2, F1.1, F1.2, F1.3, T1, T3, A1
func TestX1SharedReadCompiler(t *testing.T) {
	for i := 13; i <= 18; i++ {
		if _, err := loadSchedule(fmt.Sprintf("P%d", i)); err != nil {
			t.Errorf("P%d: %v", i, err)
		}
	}
}

// TestX1ReadStoragePath catches reads changing the write ledger or fabricating values.
// derives: C2.1, C2.2, F1.1, F1.2, F1.3, T3
func TestX1ReadStoragePath(t *testing.T) {
	for _, token := range []uint64{6, 7, 9} {
		t.Run(fmt.Sprint(token), func(t *testing.T) {
			out, err := newEmitter(filepath.Join(t.TempDir(), "read.jsonl"), "read-path")
			if err != nil {
				t.Fatal(err)
			}
			defer out.close()
			e, err := newEngine(fixtureSchedule(), out, 1, "")
			if err != nil {
				t.Fatal(err)
			}
			defer e.close()
			e.ledger = 7
			e.storageValue = "stored"
			e.clients["c1"].grants = []HeldGrant{{token: token, term: 2, ref: Ref{"n1", 1}}}
			var a Action
			if err = yaml.Unmarshal([]byte("read: c1"), &a); err != nil {
				t.Fatal(err)
			}
			if err = e.act(a, Ref{}); err != nil {
				t.Fatal(err)
			}
			e.deliver(time.Now().Add(time.Second))
			e.deliver(time.Now().Add(2 * time.Second))
			e.deliver(time.Now().Add(3 * time.Second))
			if e.ledger != 7 {
				t.Fatalf("read advanced ledger to %d", e.ledger)
			}
			ack := Event{}
			for _, v := range out.events {
				if v.Event == "ReadAck" {
					ack = v
				}
			}
			want := "served"
			value := "stored"
			if token < 7 {
				want = "rejected"
				value = ""
			}
			if ack.Outcome != want || ack.Value != value {
				t.Fatalf("want %s %q, got %+v", want, value, ack)
			}
		})
	}
}
