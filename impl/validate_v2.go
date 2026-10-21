// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, A1, A2, T3
package main

import "fmt"

// selectorRole checks alias roles without guessing their eventual incarnation.
// derives: C1.1, C1.4, F1.1, F1.3, A1, A2
func selectorRole(id string, ids map[string]string) string {
	switch id {
	case "grantor", "non-grantor":
		return "lease"
	case "holder":
		return "client"
	case "rest":
		return "selector"
	}
	return ids[id]
}

// processRoles is shared by static and incremental compilation of concrete actions.
// derives: C1.1, C1.4, F1.1, F1.3, A1, A2
func processRoles(s Schedule) map[string]string {
	ids := map[string]string{}
	for _, id := range s.Processes.Lease {
		ids[id] = "lease"
	}
	for _, id := range s.Processes.Clients {
		ids[id] = "client"
	}
	for _, id := range s.Processes.Storage {
		ids[id] = "storage"
	}
	return ids
}

// actionTarget identifies the one process-selector position outside partitions.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.3, A1, A2, T3
func actionTarget(a Action) string {
	for _, id := range []string{a.Request, a.Write, a.Crash, a.Restart, a.Pause, a.Resume} {
		if id != "" {
			return id
		}
	}
	return ""
}

// replaceTarget substitutes a frozen concrete process without changing operation.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.3, A1
func replaceTarget(a Action, id string) Action {
	switch {
	case a.Request != "":
		a.Request = id
	case a.Write != "":
		a.Write = id
	case a.Crash != "":
		a.Crash = id
	case a.Restart != "":
		a.Restart = id
	case a.Pause != "":
		a.Pause = id
	case a.Resume != "":
		a.Resume = id
	}
	return a
}

// validateSequence rejects statically impossible aliases and definite A2 errors.
// Alias-dependent transitions are compiled again against their frozen runtime IDs.
// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, T1, T3
func validateSequence(s Schedule, ids map[string]string) error {
	// 0 running, 1 crashed, 2 paused, 3 depends on a dynamic selector.
	state := map[string]int{}
	grantPossible := false
	restContext := false
	nonCrashPossible := false
	for index, step := range s.Steps {
		if step.At.Filters["event"] == "Grant" {
			grantPossible = true
		}
		targets := []string{actionTarget(step.Do)}
		if step.Do.Partition != nil {
			targets = nil
			for _, side := range step.Do.Partition {
				targets = append(targets, side...)
			}
		}
		for _, id := range targets {
			if (id == "holder" || id == "grantor" || id == "non-grantor") && !grantPossible {
				return fmt.Errorf("step %d: alias %s before any possible Grant", index+1, id)
			}
			if id == "non-grantor" && step.Do.Restart != "" && !nonCrashPossible {
				return fmt.Errorf("step %d: restart non-grantor without a preceding selector crash", index+1)
			}
			if id == "rest" && step.Do.Partition == nil && !restContext {
				return fmt.Errorf("step %d: rest has no partition context", index+1)
			}
		}
		if step.Do.Partition != nil {
			for _, side := range step.Do.Partition {
				for _, id := range side {
					if id == "rest" {
						restContext = true
					}
				}
			}
		}
		a := step.Do
		id := actionTarget(a)
		if id == "grantor" || id == "holder" || id == "rest" || id == "non-grantor" {
			role := selectorRole(id, ids)
			for process, processRole := range ids {
				if role == "selector" || role == processRole {
					state[process] = 3
				}
			}
		} else if id != "" {
			current := state[id]
			if current != 3 {
				if a.Crash != "" && current == 1 || a.Restart != "" && current != 1 || a.Pause != "" && current != 0 || a.Resume != "" && current != 2 {
					return fmt.Errorf("step %d: invalid A2 transition for %s", index+1, id)
				}
			}
			switch {
			case a.Crash != "":
				state[id] = 1
			case a.Restart != "":
				state[id] = 0
			case a.Pause != "":
				state[id] = 2
			case a.Resume != "":
				state[id] = 0
			}
		}
		if a.Crash == "non-grantor" {
			nonCrashPossible = true
		}
		if a.Request != "" {
			grantPossible = true
		}
	}
	return nil
}
