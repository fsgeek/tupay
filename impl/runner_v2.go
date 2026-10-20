// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
package main

import (
	"fmt"
	"time"
)

// FrozenAction captures selectors when a trigger fires, before delay or waiting.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T2, T3, A1, A2
type FrozenAction struct {
	Actions []Action
	Rest    []string
	HasRest bool
}

// freezeAction resolves aliases everywhere and checks concrete operation roles.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, A1, A2, T2, T3
func (e *Engine) freezeAction(a Action) (FrozenAction, error) {
	frozen := FrozenAction{}
	if a.Partition != nil {
		sides, err := e.expandPartition(a.Partition)
		if err != nil {
			return frozen, err
		}
		for side, members := range a.Partition {
			for _, id := range members {
				if id == "rest" {
					frozen.Rest = append([]string{}, sides[side]...)
					frozen.HasRest = true
				}
			}
		}
		a.Partition = sides
		frozen.Actions = []Action{a}
	} else {
		id := actionTarget(a)
		targets := []string{id}
		switch id {
		case "grantor":
			targets = []string{e.grantor}
		case "holder":
			targets = []string{e.holder}
		case "rest":
			targets = append([]string{}, e.rest...)
		}
		if len(targets) == 0 {
			return frozen, fmt.Errorf("rest has no partition context")
		}
		if id == "" {
			frozen.Actions = []Action{a}
		} else {
			for _, target := range targets {
				if target == "" {
					return frozen, fmt.Errorf("unresolved alias %s at trigger firing", id)
				}
				frozen.Actions = append(frozen.Actions, replaceTarget(a, target))
			}
		}
	}
	for _, concrete := range frozen.Actions {
		if err := validateAction(concrete, processRoles(e.schedule)); err != nil {
			return frozen, err
		}
	}
	return frozen, nil
}

// highestGranted implements the v2 numeric stale-token definition even in mutations.
// derives: C1.1, C1.2, F1.3, T3
func (e *Engine) highestGranted() uint64 {
	var max uint64
	for _, event := range e.out.events {
		if event.Event == "Grant" && event.Token > max {
			max = event.Token
		}
	}
	return max
}

// workloadReady waits for client availability, tokens and previous request replies.
// derives: C1.1, C1.2, C1.4, F1.1, F1.3, T3, A1
func (e *Engine) workloadReady(f FrozenAction) bool {
	for _, a := range f.Actions {
		id := a.Request
		if a.Write != "" {
			id = a.Write
		}
		if id == "" {
			continue
		}
		c := e.clients[id]
		if c == nil || !c.up || c.paused {
			return false
		}
		if a.Request != "" {
			for _, r := range e.requests {
				if r.client == id && r.generation == c.generation && !r.done {
					return false
				}
			}
			continue
		}
		if len(c.grants) == 0 {
			return false
		}
		if a.Token == "stale" {
			found := false
			for _, g := range c.grants {
				if g.token < e.highestGranted() {
					found = true
					break
				}
			}
			if !found {
				return false
			}
		}
	}
	return true
}

// quiescent counts active workload only, excluding stopped/paused incarnations.
// derives: C1.3, C1.4, F1.1, F1.3, E1
func (e *Engine) quiescent() bool {
	for _, r := range e.requests {
		c := e.clients[r.client]
		if !r.done && c.up && !c.paused && c.generation == r.generation {
			return false
		}
	}
	for _, m := range e.wire {
		c := e.clients[m.client]
		if c.up && !c.paused && c.generation == m.generation {
			return false
		}
	}
	return true
}

// validateTransition compiles state-dependent A2 checks before any side effect.
// derives: C1.1, C1.4, F1.1, F1.3, A1, A2
func (e *Engine) validateTransition(a Action) error {
	if a.Crash != "" && !e.alive(a.Crash) {
		return fmt.Errorf("A2: crash of stopped process %s", a.Crash)
	}
	if a.Restart != "" && e.alive(a.Restart) {
		return fmt.Errorf("A2: restart of running process %s", a.Restart)
	}
	if a.Pause != "" {
		c := e.clients[a.Pause]
		if c == nil || !c.up || c.paused {
			return fmt.Errorf("A2: pause requires running client")
		}
	}
	if a.Resume != "" {
		c := e.clients[a.Resume]
		if c == nil || !c.up || !c.paused {
			return fmt.Errorf("A2: resume requires paused client")
		}
	}
	return nil
}

// drive applies fresh arming, frozen selectors, sampled delay and bounded quiescence.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
func (e *Engine) drive() RunEvidence {
	result := RunEvidence{Derives: []string{"C1.1", "C1.2", "C1.3", "C1.4", "F1.1", "F1.2", "F1.3", "T1", "T2", "T3", "A1", "A2", "E1", "E2"}}
	wait := func(ready func() bool, reason string) bool {
		deadline := time.Now().Add(progressHorizon + 2*time.Second)
		for {
			if ready() {
				return true
			}
			if len(e.out.events) >= e.schedule.Bound.Events {
				result.Reason = "event bound reached"
				return false
			}
			e.pump()
			if err := e.network.issue(); err != nil {
				result.Reason = err.Error()
				result.Operational = err.Error()
				return false
			}
			if e.out.err != nil {
				result.Reason = e.out.err.Error()
				return false
			}
			if len(e.witnesses()) > 0 {
				result.Reason = "progress horizon exhausted"
				return false
			}
			if time.Now().After(deadline) {
				result.Reason = reason
				return false
			}
			time.Sleep(time.Millisecond)
		}
	}
	finish := func() RunEvidence { result.Witnesses = e.witnesses(); return result }
	armed := 0
	for _, step := range e.schedule.Steps {
		var trigger Ref
		if !wait(func() bool { var ok bool; trigger, ok = triggerRef(step.At, e.out.events, armed); return ok }, "trigger unreachable after arming") {
			return finish()
		}
		frozen, err := e.freezeAction(step.Do)
		if err != nil {
			result.Reason = err.Error()
			return finish()
		}
		delayUntil := time.Now().Add(time.Duration(e.rng.Intn(3)) * time.Millisecond)
		if !wait(func() bool { return !time.Now().Before(delayUntil) }, "action delay unreachable") {
			return finish()
		}
		if !wait(func() bool { return e.workloadReady(frozen) }, "workload unavailable under T3") {
			return finish()
		}
		for _, a := range frozen.Actions {
			if err := e.validateTransition(a); err != nil {
				result.Reason = err.Error()
				return finish()
			}
		}
		// Arm the successor at the action boundary, before synchronous observable effects.
		armed = len(e.out.events)
		for _, a := range frozen.Actions {
			if err := e.act(a, trigger); err != nil {
				result.Reason = err.Error()
				return finish()
			}
		}
		if frozen.HasRest {
			e.rest = append([]string{}, frozen.Rest...)
		}
	}
	if e.schedule.End.Quiescent {
		if !wait(e.quiescent, "end unreachable: active workload did not quiesce") {
			return finish()
		}
	} else {
		if !wait(func() bool { _, ok := triggerRef(e.schedule.End, e.out.events, armed); return ok }, "end unreachable: fresh event not witnessed") {
			return finish()
		}
	}
	result.Completed = true
	return finish()
}
