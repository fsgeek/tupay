#!/usr/bin/env python3
"""Build X3's judge packets, one per item, by a fixed rule. usage: packets.py <out-dir>
derives: experiments/X3-prereg.md measures 1(d), 1(e), 2 ("Gemini judge, packet inlined"); steward practice "Running
and judging" (no steward hypothesis; under about 120k characters; excerpting by a rule stated in the packet).
Items: every schedule on which an arm's two sides report differently (computed from runs/*/schedules.txt), and arm R's
implementation provenance reports (1(d)). Inputs are taken at the registration commit; artifacts from the steward's
scoring clones at the commits in runs/<side>/commit.txt; run outputs from the steward's runs."""
import json, subprocess, sys, pathlib, re, tarfile, io
T = pathlib.Path('/home/tony/projects/tupay'); S = pathlib.Path.home() / 'projects/tupay-x3-score'; REG = '38f6875'
out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
def at_reg(p): return subprocess.run(['git', '-C', str(T), 'show', f'{REG}:{p}'], capture_output=True, text=True, check=True).stdout
def lines(p, a, b=None): L = pathlib.Path(p).read_text().splitlines(True); return ''.join(L[a - 1:b])
def runlines(side, sid): return ''.join(l for l in open(T / f'experiments/X3/runs/{side}/schedules.txt') if l.startswith(f'schedule={sid} '))
def from_tar(side, suffix):
    with tarfile.open(T / f'experiments/X3/runs/{side}/observe.tar.xz') as t:
        m = next(m for m in t.getmembers() if m.name.endswith(suffix)); return t.extractfile(m).read().decode()
def tlc_excerpt(p):   # rule: the lines starting "Error:" and TLC's statistics lines; the behaviour is given elsewhere as a trace
    return ''.join(l for l in pathlib.Path(p).read_text().splitlines(True) if l.startswith('Error:') or 'states generated' in l or l.startswith(('Finished', 'Exception', 'java.', '\tat ', 'Caused by')))
def sched(sid):
    p = T / 'experiments/X3/holdout' / f'{sid}.yaml'
    return p.read_text() if p.exists() else at_reg(f'testbed/schedules/{sid}.yaml')
README = {'A': [('model/README.md, its X3 section (lines 11 to 356) without its tables of mutations and results (lines 133 to 336; each item gives the run\'s own verdict lines)', lambda: lines(S / 'armA-model/model/README.md', 11, 132) + '[lines 133 to 336, "Mutations (X3)" and "Results (X3)", omitted by rule]\n' + lines(S / 'armA-model/model/README.md', 337, 356)),
                ('impl/README.md, its X3 sections (line 1150 to the end)', lambda: lines(S / 'armA-impl/impl/README.md', 1150))],
          'R': [('model-regen/README.md, whole', lambda: (S / 'armR-model/model-regen/README.md').read_text()),
                ('impl-regen/README.md, whole', lambda: (S / 'armR-impl/impl-regen/README.md').read_text())]}
INPUTS = [('inputs/contract-v3.md', 'contract/v3.md'), ('inputs/failure-model-v3.md', 'failure-model/v3.md'),
          ('inputs/schedule-format.md', 'testbed/schedule-format.md'), ('inputs/observe-schema.md', 'observe/schema.md')]
HEAD = """# Judge task: tupay X3, {title}

You are the judge. You belong to a model family that wrote neither side. Work only from the text below; do not read files, run commands or search, and do not look for anything else.

Background: in each of two arms, a TLA+ model and an implementation were written independently, by different model families, from the same inputs (contract v3, failure model v3, the schedule format and the observe schema, all given below). Arm A adapted earlier artifacts; arm R wrote new ones. The steward ran each side on shared schedules and on hold-out schedules (H11 to H14) that no author saw. A side reports PASS, FAIL <clause>, or UNEXPLAINED <reason> for a schedule.

**Item.** {question}

Excerpts, by a fixed rule: an arm's READMEs as the sections named in their headings below; TLC output as its lines starting "Error:", its exception lines and its statistics lines (a counterexample's behaviour, where there is one, is given as a trace file). Everything else is whole.

Answer in JSON, one object: `verdict` "explained" or "unexplained"; `genuine_violation` "yes" if the run as reported shows a violation of a contract clause under the inputs as written, "no" if it does not (a premise does not hold, or a checker or runner misjudged), "not applicable" if no side claims a violation, or "undetermined"; `locus` "model", "implementation", "inputs" (the contract or failure model underdetermine the behaviour), "interface" (the schedule format or schema underdetermines it), "both", or "none"; `mechanism` in one or two sentences, or "none"; `evidence` citing specific records, states, lines or README entries; `reasoning`; `what_would_settle_it`. Be concrete and brief. Do not propose fixes. Do not assume either side is at fault; agreement between sides is not evidence of correctness, and disagreement is not evidence that either is wrong.

Every file follows, inline.
"""
def packet(name, title, question, arm, files):
    parts = [HEAD.format(title=title, question=question)]
    for fn, p in INPUTS: parts.append(f'\n===== FILE: {fn} =====\n' + at_reg(p))
    for fn, f in README[arm]: parts.append(f'\n===== FILE: arm {arm} {fn} =====\n' + f())
    for fn, text in files: parts.append(f'\n===== FILE: {fn} =====\n' + text)
    s = ''.join(parts); (out / f'{name}.md').write_text(s); print(name, len(s))
def two(arm, sid):
    return [(f'schedule {sid}.yaml', sched(sid)), (f'arm {arm} model: steward run, verdict lines for {sid}', runlines(f'arm{arm}-model', sid)),
            (f'arm {arm} implementation: steward run, verdict lines for {sid} (one line per repetition)', runlines(f'arm{arm}-impl', sid))]
for sid in ('H11', 'H14'):
    packet(f'A-{sid}', f'arm A, hold-out {sid}', f'Schedule {sid}. Arm A\'s model reports PASS; arm A\'s implementation reports UNEXPLAINED with the runner message shown (it did not run the schedule). The question is whether the schedule is valid under the inputs, whether the implementation\'s refusal is correct under them, and where the locus of the difference is.', 'A', two('A', sid))
packet('A-H13', 'arm A, hold-out H13', 'Schedule H13. Arm A\'s model reports PASS; arm A\'s implementation reports UNEXPLAINED "workload unavailable under T3" on all thirty runs. The question is what happened, whether either side\'s verdict is correct under the inputs, and where the locus is.', 'A',
       two('A', 'H13') + [('arm A implementation trace, H13 seed 1 repetition 1', from_tar('armA-impl', 'H13-x3-v1-baseline-seed-1-rep-0001.jsonl')),
                          ('arm A model trace for H13 (the run\'s exported witness)', from_tar('armA-model', '/H13.jsonl'))])
packet('R-H13', 'arm R, hold-out H13', 'Schedule H13. Arm R\'s implementation reports PASS; arm R\'s model reports UNEXPLAINED model-error (its TLC run ended in an error, shown). The question is what the error is, whether either side\'s verdict says anything about H13 under the inputs, and where the locus is.', 'R',
       two('R', 'H13') + [('arm R model: result.json for H13', (S / 'armR-model/model-regen/results/schedules/H13/result.json').read_text()),
                          ('arm R model: TLC output for H13 (excerpt)', tlc_excerpt(S / 'armR-model/model-regen/results/schedules/H13/safety.tlc.txt')),
                          ('arm R implementation trace, H13 seed 1 repetition 1', from_tar('armR-impl', '/H13-seed1-rep1.jsonl'))])
packet('R-P63', 'arm R, shared schedule P63', 'Schedule P63. Arm R\'s implementation reports PASS on all thirty runs; arm R\'s model reports FAIL C3.4 (a terminal state with an unmet obligation; its counterexample is shown). The question is whether the counterexample is a genuine violation of C3.4 under the inputs (read C3.4\'s premises with format Rule L3 as extended in v5), by what mechanism, and where the locus of the difference is.', 'R',
       two('R', 'P63') + [('arm R model: result.json for P63', (S / 'armR-model/model-regen/results/schedules/P63/result.json').read_text()),
                          ('arm R model: TLC output for P63 (excerpt)', tlc_excerpt(S / 'armR-model/model-regen/results/schedules/P63/safety.tlc.txt')),
                          ('arm R model: counterexample.jsonl for P63 (the TLC trace in observe-schema form)', (S / 'armR-model/model-regen/results/schedules/P63/counterexample.jsonl').read_text()),
                          ('arm R implementation trace, P63 seed 1 repetition 1', from_tar('armR-impl', '/' + next(l.strip().split('/')[-1] for l in open(T / 'experiments/X3/runs/armR-impl/traces.txt') if '/P63-seed1-rep1-' in l or '/P63-seed1-rep1.' in l)))])
prov = (T / 'experiments/X3/runs/armR-impl/provenance.txt').read_text().splitlines()
bad = [l for l in prov if l.startswith('FAIL') or (l and not l.startswith(('OK', 'PASS')))]
def first(sid): return next(l.split()[1].rstrip(':') for l in prov if l.startswith('FAIL') and f'/{sid}-' in l)
pf = [('observe/provenance_check.py (the steward\'s check)', at_reg('observe/provenance_check.py')),
      ('provenance_check.py output on arm R\'s implementation traces: each distinct message (trace names and repetition-specific numbers removed) with the number of traces it occurs in, by rule', ''.join(f'{n} x {m}\n' for m, n in sorted(__import__('collections').Counter(re.sub(r'seq=\d+', 'seq=N', l.strip()) for l in bad if not l.startswith('FAIL')).items())) + ''.join(f'{n} x {m}\n' for m, n in sorted(__import__('collections').Counter(re.sub(r'.*/(P\d+)-[^:]*:', r'\1:', l) for l in bad if l.startswith('FAIL')).items())))]
for sid in ('P7', 'P16'):
    t = first(sid); pf += [(f'schedule {sid}.yaml', sched(sid)), (f'arm R implementation trace {t}', from_tar('armR-impl', '/' + t.split('/')[-1]))]
packet('R-provenance', 'arm R implementation, provenance on P7 and P16', 'Arm R\'s implementation PASSes P7 and P16, but the steward\'s provenance check reports untraceable decisions in every one of their thirty runs (and on no other schedule), with the messages shown. The question is whether these are decisions whose recorded provenance is genuinely missing or wrong under the observe schema, or an artefact of the check, and where the locus is. Report `genuine_violation` as to the observe schema\'s provenance requirements.', 'R', pf)
