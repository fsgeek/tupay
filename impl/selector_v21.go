// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, A1, A2
package main

import (
	"fmt"
	"strconv"
)

// leaseNumber interprets the trailing decimal identifier for lowest-numbered selection.
// derives: C1.4, F1.1, A1
func leaseNumber(id string) (uint64, error) {
	start := len(id)
	for start > 0 && id[start-1] >= '0' && id[start-1] <= '9' {
		start--
	}
	if start == len(id) {
		return 0, fmt.Errorf("A1: lease node %q has no numeric suffix", id)
	}
	number, err := strconv.ParseUint(id[start:], 10, 64)
	if err != nil {
		return 0, fmt.Errorf("A1: invalid lease node number %q: %w", id, err)
	}
	return number, nil
}

// nonGrantor resolves A1 at trigger firing, using the observable grantor and live nodes.
// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, A1, A2
func (e *Engine) nonGrantor() (string, error) {
	if e.grantor == "" {
		return "", fmt.Errorf("A1: non-grantor before any observable Grant")
	}
	best := ""
	var bestNumber uint64
	for _, id := range e.schedule.Processes.Lease {
		if id == e.grantor || !e.alive(id) {
			continue
		}
		number, err := leaseNumber(id)
		if err != nil {
			return "", err
		}
		if best == "" || number < bestNumber || number == bestNumber && id < best {
			best = id
			bestNumber = number
		}
	}
	if best == "" {
		return "", fmt.Errorf("A1: no up non-grantor lease node")
	}
	return best, nil
}
