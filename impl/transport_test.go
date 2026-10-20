// derives: C1.1, C1.4, F1.1, F1.2
package main

import (
	"testing"

	"github.com/hashicorp/raft"
)

// TestF12_SendAcrossCutLostAfterHeal checks the injector, not the token allocator.
// derives: F1.2, C1.1, C1.4
func TestF12_SendAcrossCutLostAfterHeal(t *testing.T) {
	n := newRaftNetwork()
	n.register("n1")
	n.register("n2")
	n.partition(map[string]int{"n1": 0, "n2": 1})
	if _, err := n.route("n1", "n2", raft.RPC{}); err == nil {
		t.Fatal("send crossed cut")
	}
	n.partition(nil)
	if len(n.boxes["n2"]) != 0 {
		t.Fatal("lost message resurrected after heal")
	}
}

// TestF12_ReplyCannotSurviveCutHeal checks a response already in flight at a cut.
// derives: F1.2, C1.1, C1.4
func TestF12_ReplyCannotSurviveCutHeal(t *testing.T) {
	n := newRaftNetwork()
	n.register("n1")
	n.register("n2")
	ticket, err := n.route("n1", "n2", raft.RPC{})
	if err != nil {
		t.Fatal(err)
	}
	n.partition(map[string]int{"n1": 0, "n2": 1})
	n.partition(nil)
	if err := n.response(ticket); err == nil {
		t.Fatal("pre-cut response survived cut and heal")
	}
}

// TestF12_ConnectedSideRetainsReplies rules out dropping unrelated majority traffic.
// derives: F1.2, C1.4
func TestF12_ConnectedSideRetainsReplies(t *testing.T) {
	n := newRaftNetwork()
	n.register("n1")
	n.register("n2")
	n.register("n3")
	ticket, err := n.route("n2", "n3", raft.RPC{})
	if err != nil {
		t.Fatal(err)
	}
	n.partition(map[string]int{"n1": 0, "n2": 1, "n3": 1})
	if err := n.response(ticket); err != nil {
		t.Fatalf("connected-side reply dropped: %v", err)
	}
}

// TestF11_OldReplyCannotReachNewIncarnation checks volatile inbox replacement.
// derives: F1.1, C1.1, C1.4
func TestF11_OldReplyCannotReachNewIncarnation(t *testing.T) {
	n := newRaftNetwork()
	n.register("n1")
	n.register("n2")
	ticket, err := n.route("n1", "n2", raft.RPC{})
	if err != nil {
		t.Fatal(err)
	}
	n.remove("n2")
	n.register("n2")
	if err := n.response(ticket); err == nil {
		t.Fatal("reply crossed process replacement")
	}
	if len(n.boxes["n2"]) != 0 {
		t.Fatal("new incarnation inherited old inbox")
	}
}
