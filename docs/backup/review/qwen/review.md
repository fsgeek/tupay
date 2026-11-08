I found the following defects.

1. **Severity: blocking. Where: T8, B1.1, B1.10, B1.12.**  
   **What is wrong:** the contract requires verification/re-verification *at R* while also requiring snapshot contents at R to be encrypted and R never to hold the key.  
   **Why:** T8: “every file of the snapshot was read at R, and its hash matched the manifest”; B1.10: “Snapshot contents at R … are encrypted under the escrowed key. R never holds that key.”  
   **Fix:** define ciphertext manifests, or move verification to a key-holding host.

2. **Severity: blocking. Where: B1.11; EX1.2, EX1.3, EX1.4; AI1.2, AI1.3, AI1.4.**  
   **What is wrong:** B1.11 cannot be satisfied because several EX/AI items have no review date.  
   **Why:** B1.11: “Every EX and AI item carries a review date”; but EX1.2, EX1.3, EX1.4, AI1.2, AI1.3, AI1.4 have none.  
   **Fix:** add review dates or exempt those items.

3. **Severity: blocking. Where: §5, BF1.7 row; B1.12, B1.13, B1.15.**  
   **What is wrong:** plaza unavailability is only given a W effect for B1.7, although other clauses also require notices to reach the plaza; unlisted pairs are H, which cannot hold when the plaza is down.  
   **Why:** “Every pair not listed below is H”; B1.12: “a notice reaches the plaza within *D*.”  
   **Fix:** add W/S effects for every notice obligation under BF1.7.

4. **Severity: significant. Where: §5 BF1.2/B1.8 and BF1.11/B1.8; B1.7.**  
   **What is wrong:** effects rely on B1.7 reporting overdue restore checks, but B1.7 has no such trigger.  
   **Why:** BF1.2/B1.8: “Past *M*, B1.8 is violated and B1.7 reports it”; B1.7 only says: “If a run fails, or no acknowledged snapshot is younger than *H*…”  
   **Fix:** add a reporting trigger for B1.8 violations or correct the effects.

5. **Severity: significant. Where: T15; B1.8, B1.12.**  
   **What is wrong:** the status record is defined only as run outcomes *ok/failed*, but clauses require state marks that are not run outcomes.  
   **Why:** T15: “Each entry has a sequence number, a result (*ok* or *failed*)…”; B1.8: “marks it *not restore-checked*”; B1.12: “marked *damaged* in the status record.”  
   **Fix:** expand T15 or define a separate state record.

6. **Severity: minor. Where: intro, §3, §7.**  
   **What is wrong:** gap numbering/mapping is inconsistent.  
   **Why:** §3: “B1.12 to B1.15 are new in draft 2 (gaps 1 to 4, §7)”; §7 assigns B1.15 to gap 5, gap 2 revises B1.7, and gap 6 is open.  
   **Fix:** correct the gap-to-id mapping.

7. **Severity: significant. Where: §9.**  
   **What is wrong:** the claim that `backup.sh` gives B1.9 is contradicted by the script, which contains no scheduler or liveness mechanism.  
   **Why:** §9: “`backup.sh` gives … B1.9”; the script is only a command, with a comment “Nightly backup” but no timer or guarantee.  
   **Fix:** qualify B1.9 as dependent on external scheduling, not the script itself.

8. **Severity: significant. Where: §9.**  
   **What is wrong:** “part of B1.7” is claimed for `backup.sh`, but the script has no plaza notice, no off-S checker, and no staleness detection.  
   **Why:** §9: “part of B1.7”; script only appends JSON status lines.  
   **Fix:** remove the claim or define exactly which non-normative logging part is meant.

9. **Severity: significant. Where: §9 vs T5/T6/T15.**  
   **What is wrong:** formal claims that `backup.sh` satisfies contract clauses are contradicted by the script’s timestamp naming and lack of sequence numbers.  
   **Why:** T5: “Runs are numbered by a **sequence number**”; script: `TS="$(date -u +%Y%m%dT%H%M%SZ)"` and status lines use `"run":"$TS"`.  
   **Fix:** state that §9 compares behaviour informally, not contract-defined terms.

10. **Severity: significant. Where: §9; `backup.sh` ERR trap.**  
   **What is wrong:** the script can write `ok`, then on a later error delete the acknowledged snapshot and write `failed`, contradicting any claim of stable acknowledgement underlying B1.6/B1.9.  
   **Why:** script: `trap 'status failed "$STAGE"; rm -rf "$OUT"; ssh … rm -rf …' ERR` remains active after `status ok done`.  
   **Fix:** narrow §9 claims or note this failure mode.

11. **Severity: significant. Where: B1.5, T2, T13; §9 claim about `backup.sh`.**  
   **What is wrong:** credential exclusion is by filename in an extracted copy and does not inspect git bundles/archives; credentials in git history or `tupay-private/` can leave S.  
   **Why:** T13: “a file matching the credential patterns”; script: `git bundle create … --all`; no-credentials check is `find "$OUT" … -name …`, which cannot see inside `tupay.bundle`.  
   **Fix:** state a no-secrets-in-repo/private assumption or define content-level credential scanning.

12. **Severity: significant. Where: B1.9.**  
   **What is wrong:** the premise “long enough” is undefined and has no parameter, making the clause effectively vacuous.  
   **Why:** B1.9: “If S and R stay up, connected and not full long enough…”  
   **Fix:** define a minimum-duration parameter for the premise.

13. **Severity: significant. Where: §1; B1.7, B1.8, B1.12, B1.13, B1.15.**  
   **What is wrong:** “within X” clauses do not name their clock and start event as required.  
   **Why:** §1: “‘within *X*’ always names its clock and its start event (T12)”; B1.7: “a notice reaches the plaza within *D*” without clock/start.  
   **Fix:** add clock/start event to each deadline or explicitly incorporate T12 if that is intended.

14. **Severity: significant. Where: B1.9, B1.4.**  
   **What is wrong:** bare quantities violate the parameter rule.  
   **Why:** §1: “every quantity is a named parameter (§6), never a bare number”; B1.9: “within 24 h + *X*”; B1.4: “one per month”.  
   **Fix:** name the base interval and monthly-count quantities as parameters.

15. **Severity: significant. Where: multiple.**  
   **What is wrong:** essential terms are undefined or used without definition.  
   **Why:** examples: B1.7 “freshness check”; BF1.7 “Hamut’ay”; T4 “the box”; T2 “caches”; B1.11 “daily check”; B1.4 “daily snapshot”; B1.12 “damaged”; B1.8 “not restore-checked”; B1.15 “source tree” and “logged reason”; §8 “Arariwa”; §9 “restic”.  
   **Fix:** add definitions or remove normative reliance on them.

16. **Severity: significant. Where: §6 `Dmax`; B1.15; B1.9.**  
   **What is wrong:** `Dmax` derivation does not follow: “one run interval” is undefined and the derivation ignores the liveness slack `X`.  
   **Why:** “*Dmax* = *D* + one run interval = 25 h”; B1.9 allows “24 h + *X*” with `X = 2 h`; B1.15: “The notice is what B1.4’s *Dmax* is measured from.”  
   **Fix:** derive `Dmax` from the maximum acknowledged-to-acknowledged interval.

17. **Severity: significant. Where: I-B1.8.**  
   **What is wrong:** the interpretation formula allows `marked_not_checked` to discharge the obligation, contradicting its own prose.  
   **Why:** I-B1.8: `◇≤M restore_checked(n) ∨ marked_not_checked(n)`; but also: “Marking a snapshot as not checked does not discharge the obligation.”  
   **Fix:** make the formula require `restore_checked(n)` by `M`.

18. **Severity: significant. Where: §5 BF1.6/B1.4.**  
   **What is wrong:** the row is marked H but its text says ages are W.  
   **Why:** row effect: “H”; obligation text: “Ages used for *K* and *Mo* are W, as above.”  
   **Fix:** mark the pair W or split the row.

19. **Severity: significant. Where: BF1.10/B1.13 H.**  
   **What is wrong:** H assumes some run/check enumerates all acknowledged, unpruned snapshots; no clause obligates that.  
   **Why:** B1.13: “first run or check that could observe it”; I-B1.13 witness: “reimage a scratch R.”  
   **Fix:** state the inventory/observation obligation or change the effect.

20. **Severity: significant. Where: BF1.10/B1.4 S.**  
   **What is wrong:** the retained span cannot be rebuilt to `T`/`K`/`Mo` at the next run; the suspension lacks a feasible end event.  
   **Why:** “The retained span is lost. It rebuilds from the next run.”  
   **Fix:** suspend B1.4 until the span can actually reach the required age/coverage.

21. **Severity: significant. Where: BF1.2; B1.12.**  
   **What is wrong:** no effect is listed for B1.12 under partition; default H depends on unstated R-local autonomy/reporting.  
   **Why:** BF1.2: “A partition between any two of S, R and the restore host”; B1.12: “verified again at R at least every *P*.”  
   **Fix:** add S/W for B1.12 or state that R can verify and report without S.

22. **Severity: significant. Where: BF1.8; B1.8, B1.12, B1.11.**  
   **What is wrong:** timer failure can breach scheduled restore checks, re-verifications, and daily checks, but only B1.7/B1.9 effects are listed.  
   **Why:** BF1.8: “A timer does not fire…”; B1.8/B1.12 have deadlines.  
   **Fix:** add effects/cells for check timers.

23. **Severity: significant. Where: BF1.8(checker)/B1.7 W.**  
   **What is wrong:** the effect says B1.7 holds through S’s failure notices, but B1.7 requires the checker to be off S and defines no S notices.  
   **Why:** effect: “B1.7 holds only through S’s own failure notices”; B1.7: “The freshness check runs on a host other than S.”  
   **Fix:** correct the effect or add a clause for S-originated notices.

24. **Severity: significant. Where: B1.6, B1.7.**  
   **What is wrong:** B1.6 requires the next run or off-S freshness check to record “failed, stage unknown”, but no status-record location, visibility, or write path is stated.  
   **Why:** B1.6: “recorded … by the next run or the next freshness check (B1.7)”; B1.7: checker is off S.  
   **Fix:** define where the status record lives and who may write it.

25. **Severity: significant. Where: B1.3, I-B1.3.**  
   **What is wrong:** the interpretation adds a `damaged` exception that the normative clause does not state.  
   **Why:** B1.3: “Every acknowledged snapshot that is not pruned is restorable…”; I-B1.3: `¬damaged(n)`.  
   **Fix:** amend B1.3 to include the damaged exception or remove it from the interpretation.

26. **Severity: significant. Where: B1.4.**  
   **What is wrong:** no ramp-up grace is stated; a new service cannot keep `K` days and `Mo` months of history before that history exists.  
   **Why:** B1.4: “keeps a retained span reaching back at least *T* … every daily snapshot for *K* days and one per month for *Mo* months.”  
   **Fix:** state initial suspension or inherited-history assumption.

27. **Severity: significant. Where: B1.15, BF1.9.**  
   **What is wrong:** “the snapshot is still taken” may be impossible if the source is moved or unreadable.  
   **Why:** B1.15: “The snapshot is still taken and acknowledged”; BF1.9: “A source is moved, emptied or truncated.”  
   **Fix:** limit B1.15 to readable damaged sources or treat unreadable sources as failed runs.

28. **Severity: significant. Where: §5 cells.**  
   **What is wrong:** no cell names partial accidental deletion of a snapshot at R, although the interpretation witness tests exactly that.  
   **Why:** I-B1.13: “delete a snapshot directory at R”; BF1.10 covers R reimaged/replaced, not partial deletion.  
   **Fix:** add a partial-loss/deletion cell.

29. **Severity: significant. Where: §5 cells; T15, B1.6.**  
   **What is wrong:** no cell names loss/corruption of status record or sequence metadata, which the contract depends on.  
   **Why:** T15 defines the status record; BF1.3 only covers “stored bytes at R.”  
   **Fix:** add a metadata/status-record loss cell.

30. **Severity: significant. Where: B1.14; BF1.11.**  
   **What is wrong:** no cell names loss of Tony’s outside key copy, despite B1.14 requiring it.  
   **Why:** B1.14: “At least one copy of the key is held outside S, R and the restore host (Tony’s)”; BF1.11: only restore-host or S copy lost.  
   **Fix:** add a Tony-copy-loss cell or mark it EX/AI.

31. **Severity: significant. Where: BF1.11; B1.3, B1.14.**  
   **What is wrong:** loss of the restore host’s key copy has no effect on B1.3; H assumes Tony’s copy can be imported/used, while B1.14 says restore checks use the restore host’s copy.  
   **Why:** BF1.11 row only affects B1.8; B1.14: “The restore check uses the restore host’s escrowed copy of the key.”  
   **Fix:** add an effect or state the key-restoration assumption.

32. **Severity: significant. Where: intro; B1.7, B1.14, B1.8, B1.6.**  
   **What is wrong:** the draft says it prescribes no protocol, but it prescribes hosts, key copies, record markings, and recovery behaviour.  
   **Why:** “It prescribes no protocol”; B1.7: “The freshness check runs on a host other than S”; B1.14: “uses … never S’s”; B1.8: “the status record marks it…”  
   **Fix:** remove the no-protocol claim or move implementation prescriptions out of the contract.

33. **Severity: significant. Where: B1.7, I-B1.7.**  
   **What is wrong:** the plaza-down fallback record has no named reader, so the obligation depends on an unstated human/process assumption.  
   **Why:** B1.7: “the failure is recorded where the freshness check reads it”; I-B1.7: “nothing yet says who reads the checker’s record.”  
   **Fix:** name the reader/escalation path or mark the case EX.

34. **Severity: minor. Where: B1.6.**  
   **What is wrong:** “stage unknown” conflicts with the requirement that every failed entry names its stage unless “unknown” is defined as a stage.  
   **Why:** B1.6: “Every *failed* entry names its stage”; also: “failed, stage unknown.”  
   **Fix:** define `unknown` as an allowed stage value.

35. **Severity: minor. Where: I-B1.1.**  
   **What is wrong:** the assumption that the status record is written only by the run contradicts B1.6, where the next run/check writes an entry.  
   **Why:** I-B1.1: “Assumes the status record is written only by the run”; B1.6: “recorded … by the next run or the next freshness check.”  
   **Fix:** narrow the assumption to `ok` entries only.

36. **Severity: minor. Where: I-B1.13.**  
   **What is wrong:** the interpretation omits the clause’s `within D` delay and reads as immediate notice.  
   **Why:** B1.13: “within *D*”; I-B1.13: “or a notice has been sent.”  
   **Fix:** include the `D` bound in the interpretation.

37. **Severity: minor. Where: I-B1.9.**  
   **What is wrong:** `ok(n+1)` assumes the next sequence entry is acknowledged; the clause requires a new acknowledged snapshot, not necessarily the next sequence number.  
   **Why:** I-B1.9: `◇≤(24h+X) ok(n+1)`; B1.9: “a new acknowledged snapshot exists.”  
   **Fix:** use “next acknowledged sequence” rather than `n+1`.

38. **Severity: minor. Where: B1.8, B1.12, B1.15; §8.**  
   **What is wrong:** several §1 writing rules are violated: multiple obligations per sentence, passive voice without actor, and “should” in a normative-sounding section.  
   **Why:** B1.8: “restore-checked … and the result is recorded”; B1.12: “marked damaged …, and a notice reaches…”; §8: “It should raise these…”  
   **Fix:** split sentences, name actors, and remove “should.”

39. **Severity: minor. Where: BF1.6; B1.9.**  
   **What is wrong:** clock steps can affect B1.9’s time bound, but BF1.6/B1.9 is unlisted and therefore default H.  
   **Why:** BF1.6: “Clock steps…”; B1.9: “within 24 h + *X*.”  
   **Fix:** add a W/H row with the clock-error qualification.

40. **Severity: minor. Where: B1.10, T10.**  
   **What is wrong:** “any further copy” may cover restore-host decrypted copies at rest, conflicting with restore checks that decrypt files.  
   **Why:** B1.10: “at R and at any further copy are encrypted”; T10: “decrypted with the escrowed key.”  
   **Fix:** clarify an in-use/temporary plaintext exception.

Sound areas: the T8/T10 distinction that verification and restore-check are events, not lasting properties, is clear.  
Sound area: T17/T18 pruning definitions are internally clear.  
Sound area: the failure-cell names mostly cover plausible failure shapes, aside from the missing cells listed above.