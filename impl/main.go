// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// Options deliberately permits flags before or after the schedule basename.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
type Options struct {
	schedule, mutation, check, evidence string
	all, mutations                      bool
	seeds                               int
}

// parseOptions rejects contradictory modes rather than silently ignoring them.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func parseOptions(args []string) (Options, error) {
	o := Options{seeds: 3}
	for i := 0; i < len(args); i++ {
		a := args[i]
		switch a {
		case "--all":
			o.all = true
		case "--mutations":
			o.mutations = true
		case "--seeds", "--mutation", "--check", "--evidence":
			if i+1 >= len(args) {
				return o, fmt.Errorf("missing value for %s", a)
			}
			i++
			v := args[i]
			switch a {
			case "--seeds":
				n, err := strconv.Atoi(v)
				if err != nil || n < 1 || n > 1000 {
					return o, fmt.Errorf("seeds must be 1..1000")
				}
				o.seeds = n
			case "--mutation":
				o.mutation = v
			case "--check":
				o.check = v
			case "--evidence":
				o.evidence = v
			}
		default:
			if strings.HasPrefix(a, "-") || o.schedule != "" {
				return o, fmt.Errorf("unknown argument %s", a)
			}
			o.schedule = a
		}
	}
	modes := 0
	if o.all {
		modes++
	}
	if o.mutations {
		modes++
	}
	if o.schedule != "" {
		modes++
	}
	if modes != 1 {
		return o, fmt.Errorf("use <schedule>, --all, or --mutations")
	}
	if o.mutation != "" && (o.schedule == "" || expectedClause(o.mutation) == "") {
		return o, fmt.Errorf("--mutation requires one schedule and P1..P12")
	}
	if o.check != "" && (o.schedule == "" || o.mutation != "") {
		return o, fmt.Errorf("--check requires one schedule and no mutation")
	}
	if o.evidence != "" && o.check == "" {
		return o, fmt.Errorf("--evidence requires --check")
	}
	return o, nil
}

// expectedClause implements the precommitted mutation scoring table.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func expectedClause(pair string) string {
	switch pair {
	case "P1", "P2", "P3":
		return "C1.1"
	case "P4", "P5", "P6":
		return "C1.2"
	case "P7", "P8", "P9":
		return "C1.3"
	case "P10", "P11", "P12":
		return "C1.4"
	}
	return ""
}

// runOne writes a fresh trace and scores only its decoded observable evidence.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
func runOne(s Schedule, seed int64, mutation string) (Verdict, string) {
	var nonce [8]byte
	if _, err := rand.Read(nonce[:]); err != nil {
		return Verdict{Reason: err.Error()}, ""
	}
	mode := "baseline"
	if mutation != "" {
		mode = mutation
	}
	run := fmt.Sprintf("%s-v2-%s-seed-%d-%s", s.Name, mode, seed, hex.EncodeToString(nonce[:]))
	if err := os.MkdirAll("observe", 0755); err != nil {
		return Verdict{Reason: err.Error()}, ""
	}
	path := filepath.Join("observe", run+".jsonl")
	emitter, err := newEmitter(path, run)
	if err != nil {
		return Verdict{Reason: err.Error()}, path
	}
	engine, err := newEngine(s, emitter, seed, mutation)
	if err != nil {
		_ = emitter.close()
		return Verdict{Reason: err.Error()}, path
	}
	evidence := engine.drive()
	engine.close()
	if err := emitter.close(); err != nil {
		return Verdict{Reason: err.Error()}, path
	}
	bytes, err := json.MarshalIndent(evidence, "", "  ")
	if err != nil {
		return Verdict{Reason: err.Error()}, path
	}
	if err = os.WriteFile(strings.TrimSuffix(path, ".jsonl")+".meta.json", append(bytes, '\n'), 0644); err != nil {
		return Verdict{Reason: err.Error()}, path
	}
	return checkTrace(path, s, evidence), path
}

// printResult always begins with the shared result vocabulary.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func printResult(v Verdict, schedule string, seed int, mutation, path string) {
	status := "PASS"
	if v.Clause != "" {
		status = "FAIL " + v.Clause
	} else if v.Reason != "" {
		status = "UNEXPLAINED " + v.Reason
	}
	fmt.Printf("%s schedule=%s seed=%d", status, schedule, seed)
	if mutation != "" {
		fmt.Printf(" mutation=%s expected=FAIL_%s", mutation, expectedClause(mutation))
	}
	if schedule == "false-suspicion-v1" {
		fmt.Print(" observed=true")
	}
	if path != "" {
		fmt.Printf(" trace=%s", path)
	}
	if v.Clause != "" {
		fmt.Printf(" detail=%q", v.Reason)
	}
	fmt.Println()
}

// execute runs every requested seed, even if an earlier seed fails.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func execute(args []string) int {
	o, err := parseOptions(args)
	if err != nil {
		fmt.Println("UNEXPLAINED", err)
		return 2
	}
	if o.check != "" {
		for _, path := range []string{o.check, o.evidence} {
			if path == "" {
				continue
			}
			if err := ownEvidencePath(path); err != nil {
				fmt.Println("UNEXPLAINED", err)
				return 2
			}
		}
		s, err := loadSchedule(o.schedule)
		if err != nil {
			fmt.Println("UNEXPLAINED", err)
			return 2
		}
		meta := o.evidence
		if meta == "" {
			meta = strings.TrimSuffix(o.check, ".jsonl") + ".meta.json"
		}
		if err := ownEvidencePath(meta); err != nil {
			fmt.Println("UNEXPLAINED", err)
			return 2
		}
		data, err := os.ReadFile(meta)
		if err != nil {
			fmt.Println("UNEXPLAINED", err)
			return 2
		}
		var evidence RunEvidence
		if err = json.Unmarshal(data, &evidence); err != nil {
			fmt.Println("UNEXPLAINED", err)
			return 2
		}
		v := checkTrace(o.check, s, evidence)
		printResult(v, s.Name, 0, "", o.check)
		if v.Clause != "" || v.Reason != "" {
			return 1
		}
		return 0
	}
	var schedules []string
	if o.all || o.mutations {
		for i := 1; i <= 12; i++ {
			schedules = append(schedules, fmt.Sprintf("P%d", i))
		}
		if o.all {
			schedules = append(schedules, "false-suspicion-v1")
		}
	} else {
		schedules = []string{o.schedule}
	}
	exit := 0
	killed := 0
	for _, name := range schedules {
		s, err := loadSchedule(name)
		if err != nil {
			fmt.Printf("UNEXPLAINED %s schedule=%s\n", err, name)
			exit = 1
			continue
		}
		mutation := o.mutation
		if o.mutations {
			mutation = name
		}
		allKilled := true
		for seed := 1; seed <= o.seeds; seed++ {
			v, path := runOne(s, int64(seed), mutation)
			printResult(v, name, seed, mutation, path)
			if mutation != "" {
				if v.Clause != expectedClause(mutation) {
					exit = 1
					allKilled = false
				}
			} else if v.Clause != "" || v.Reason != "" {
				exit = 1
			}
		}
		if mutation != "" && allKilled {
			killed++
		}
	}
	if o.mutations {
		fmt.Printf("Mutation kills: %d/12 across %d seed(s)\n", killed, o.seeds)
	}
	return exit
}

// main returns a nonzero status for any unexpected or unexplained result.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func main() { os.Exit(execute(os.Args[1:])) }

// ownEvidencePath confines offline reads, including symlinks, to this artifact.
// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
func ownEvidencePath(path string) error {
	root, err := filepath.Abs(".")
	if err != nil {
		return err
	}
	resolved, err := filepath.EvalSymlinks(path)
	if err != nil {
		return err
	}
	absolute, err := filepath.Abs(resolved)
	if err != nil {
		return err
	}
	rel, err := filepath.Rel(root, absolute)
	if err != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(os.PathSeparator)) {
		return fmt.Errorf("evidence outside impl/ is forbidden")
	}
	return nil
}
