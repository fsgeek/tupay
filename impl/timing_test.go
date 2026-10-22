// derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2, T2, T3, E1
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
	"time"
)

// Production scheduling must contain no real clock, asynchronous execution or entropy.
// derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2, T2, T3, E1
func TestTimingNoHostScheduler(t *testing.T) {
	files, err := os.ReadDir(".")
	if err != nil {
		t.Fatal(err)
	}
	forbidden := map[string]bool{"Now": true, "Since": true, "Until": true, "Sleep": true, "NewTimer": true, "NewTicker": true, "After": true, "AfterFunc": true, "Tick": true}
	for _, file := range files {
		name := file.Name()
		if !strings.HasSuffix(name, ".go") || strings.HasSuffix(name, "_test.go") {
			continue
		}
		tree, err := parser.ParseFile(token.NewFileSet(), name, nil, 0)
		if err != nil {
			t.Fatal(err)
		}
		for _, imp := range tree.Imports {
			if imp.Path.Value == "\"crypto/rand\"" {
				t.Errorf("%s: entropy import", name)
			}
		}
		ast.Inspect(tree, func(node ast.Node) bool {
			switch x := node.(type) {
			case *ast.GoStmt:
				t.Errorf("%s: async protocol execution", name)
			case *ast.SelectStmt:
				t.Errorf("%s: select race", name)
			case *ast.CallExpr:
				if sel, ok := x.Fun.(*ast.SelectorExpr); ok {
					if pkg, ok := sel.X.(*ast.Ident); ok && pkg.Name == "time" && forbidden[sel.Sel.Name] {
						t.Errorf("%s: real clock time.%s", name, sel.Sel.Name)
					}
				}
			}
			return true
		})
	}
}

// canonicalTimingRun compares observable choices, excluding only unique file labels.
// derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2
func canonicalTimingRun(t *testing.T, s Schedule, seed int64, mutation string) []byte {
	t.Helper()
	path := filepath.Join(t.TempDir(), "events.jsonl")
	out, err := newEmitter(path, s.Name)
	if err != nil {
		t.Fatal(err)
	}
	e, err := newEngine(s, out, seed, mutation)
	if err != nil {
		out.close()
		t.Fatal(err)
	}
	evidence := e.drive()
	e.close()
	if err = out.close(); err != nil {
		t.Fatal(err)
	}
	verdict := checkTrace(path, s, evidence)
	expected := expectedClause(mutation)
	if mutation == "" {
		if verdict != (Verdict{}) {
			t.Fatalf("baseline %s seed %d: %+v", s.Name, seed, verdict)
		}
	} else if verdict.Clause != expected {
		t.Fatalf("mutation %s seed %d: %+v", mutation, seed, verdict)
	}
	contents, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	records := []map[string]any{}
	for _, line := range bytes.Split(bytes.TrimSpace(contents), []byte("\n")) {
		var v map[string]any
		if err = json.Unmarshal(line, &v); err != nil {
			t.Fatal(err)
		}
		delete(v, "run")
		records = append(records, v)
	}
	canonical, err := json.Marshal(struct {
		Records  []map[string]any
		Evidence RunEvidence
		Verdict  Verdict
	}{records, evidence, verdict})
	if err != nil {
		t.Fatal(err)
	}
	return canonical
}

// Host thread count and renamed schedule labels cannot affect seeded semantics.
// derives: C1.1, C1.4, C2.2, F1.3, F2.1, F2.2, T2, T3
func TestTimingCanonicalReplay(t *testing.T) {
	old := runtime.GOMAXPROCS(1)
	defer runtime.GOMAXPROCS(old)
	for _, name := range []string{"P18", "P29", "P30"} {
		for seed := int64(1); seed <= 3; seed++ {
			for _, mutation := range []string{"", name} {
				t.Run(fmt.Sprintf("%s/%d/%s", name, seed, mutation), func(t *testing.T) {
					s, err := loadSchedule(name)
					if err != nil {
						t.Fatal(err)
					}
					runtime.GOMAXPROCS(1)
					first := canonicalTimingRun(t, s, seed, mutation)
					runtime.GOMAXPROCS(2)
					time.Sleep(time.Millisecond)
					s.Name = "renamed-" + s.Name
					second := canonicalTimingRun(t, s, seed, mutation)
					if !bytes.Equal(first, second) {
						t.Fatal("same seed changed canonical execution after host/name perturbation")
					}
				})
			}
		}
	}
}

// Host elapsed time cannot consume a grant lifetime or progress horizon.
// derives: C1.4, F1.3, F2.1, F2.2, E1
func TestTimingClockIsSchedulerOwned(t *testing.T) {
	e := &Engine{}
	before := e.now()
	time.Sleep(5 * time.Millisecond)
	if e.now() != before {
		t.Fatal("host elapsed time advanced scheduler")
	}
	e.logicalNow = e.now().Add(41 * time.Millisecond)
	if e.now().Sub(before) != 41*time.Millisecond {
		t.Fatal("logical advancement lost precision")
	}
}
