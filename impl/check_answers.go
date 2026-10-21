// derives: C1.3, C2.2, F1.1, F1.2, F1.3
package main

import "fmt"

// checkAckAnswers enforces observe schema v3 without inventing a contract clause.
// Redundant identity must match causal provenance even for same-token retries.
// derives: C1.3, C2.2, F1.1, F1.2, F1.3
func (g *traceGraph) checkAckAnswers() Verdict {
	for _, ack := range g.ordered {
		attemptName, acceptName, rejectName := "", "", ""
		switch ack.Event {
		case "WriteAck":
			attemptName, acceptName, rejectName = "WriteAttempt", "WriteAccept", "WriteReject"
		case "ReadAck":
			attemptName, acceptName, rejectName = "ReadAttempt", "ReadAccept", "ReadReject"
		default:
			continue
		}
		if ack.Answers == nil {
			return Verdict{Reason: "ack missing schema-v3 answers"}
		}
		attempt, ok := g.events[*ack.Answers]
		if !ok || attempt.Event != attemptName || attempt.Proc != ack.Proc || attempt.Client != ack.Client || attempt.Proc != ack.Client || attempt.Key != ack.Key || attempt.Token != ack.Token {
			return Verdict{Reason: fmt.Sprintf("ack %s:%d answers does not name its matching attempt", ack.Proc, ack.Seq)}
		}
		if !g.precedes(*ack.Answers, Ref{ack.Proc, ack.Seq}) {
			return Verdict{Reason: "ack answers is not reachable through causal provenance"}
		}
		if decision, found := g.directEvent(ack, acceptName, rejectName); found {
			actual, exists := g.directEvent(decision, attemptName)
			if !exists || (Ref{actual.Proc, actual.Seq}) != *ack.Answers {
				return Verdict{Reason: "ack answers disagrees with storage decision attempt"}
			}
		} else if actual, found := g.directEvent(ack, attemptName); found && (Ref{actual.Proc, actual.Seq}) != *ack.Answers {
			return Verdict{Reason: "ack answers disagrees with direct attempt cause"}
		}
	}
	return Verdict{}
}
