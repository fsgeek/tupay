// derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2, T2, T3, E1
package main

import "time"

// now returns only scheduler time; no host clock can enter the execution state.
// derives: C1.1, C1.4, C2.2, F1.3, F2.1, F2.2, T2, T3, E1
func (e *Engine) now() time.Time {
	if e.logicalNow.IsZero() {
		e.logicalNow = time.Unix(0, 0).UTC()
	}
	return e.logicalNow
}
