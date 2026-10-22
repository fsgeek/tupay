// derives: C1.1, C1.3, C1.4, C2.2, F1.1, F1.2, F2.1, F2.2, L1, L2, L3
package main

import (
	"fmt"
	"time"
)

// expandLinks freezes each selector and removes self-pairs and duplicates.
// An empty resolved list is valid: every input pair may have been a self-pair.
// derives: F2.1, F2.2, L1, A1, T2
func (e *Engine) expandLinks(input [][]string) ([][]string, error) {
	result := [][]string{}
	seen := map[link]bool{}
	for _, pair := range input {
		if len(pair) != 2 {
			return nil, fmt.Errorf("link requires two ends")
		}
		ends := [2]string{}
		for i, id := range pair {
			switch id {
			case "grantor":
				id = e.grantor
			case "holder":
				id = e.holder
			case "non-grantor":
				var err error
				id, err = e.nonGrantor()
				if err != nil {
					return nil, err
				}
			case "rest":
				return nil, fmt.Errorf("rest is forbidden in a link")
			}
			if id == "" || processRoles(e.schedule)[id] == "" {
				return nil, fmt.Errorf("unresolved/unknown link endpoint %s", id)
			}
			ends[i] = id
		}
		path := link{ends[0], ends[1]}
		if ends[0] == ends[1] || seen[path] {
			continue
		}
		seen[path] = true
		result = append(result, []string{ends[0], ends[1]})
	}
	return result, nil
}

// faultLinks names directed down links; complete partitions use the same matrix.
// derives: F1.2, F2.1, F2.2, L1, L2
func faultLinks(partition, cut, drop [][]string) [][]string {
	result := [][]string{}
	seen := map[link]bool{}
	add := func(a, b string) {
		p := link{a, b}
		if a != b && !seen[p] {
			seen[p] = true
			result = append(result, []string{a, b})
		}
	}
	if partition != nil {
		for _, a := range partition[0] {
			for _, b := range partition[1] {
				add(a, b)
				add(b, a)
			}
		}
	}
	for _, p := range cut {
		add(p[0], p[1])
		add(p[1], p[0])
	}
	for _, p := range drop {
		add(p[0], p[1])
	}
	return result
}

// canSend admits one direction at the actual send, independently of its reverse.
// derives: C1.1, C1.3, C1.4, C2.2, F1.1, F1.2, F2.1, F2.2
func (e *Engine) canSend(from, to string) bool {
	return e.alive(from) && e.alive(to) && !e.down[link{from, to}]
}

// queueReply holds local work before send, then samples network delivery latency.
// A fault before send may lose the reply; one after send cannot change its fate.
// derives: C1.3, C2.2, F1.1, F1.2, F2.1, F2.2
func (e *Engine) queueReply(m WireMessage) {
	m.pendingSend = true
	m.due = e.now().Add(8 * time.Millisecond)
	e.wire = append(e.wire, m)
}
