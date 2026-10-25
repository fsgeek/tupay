# Brief: the service contracts Raft relies on

You have one source: `source/OngaroPhD.txt` (Diego Ongaro, *Consensus: Bridging Theory and Practice*, Stanford, August 2014; the PDF beside it is the same text). Read nothing else in this checkout except this brief and `AGENTS.md`. You have no web access and need none.

## Task
Raft makes promises (safety: election safety, log matching, leader completeness, state machine safety, linearizable reads where the text claims them; liveness: progress when a majority can communicate). Those promises rest on things Raft assumes of its **environment**: storage, the network, clocks and timers, processes and restarts, node identity, configuration and operators, the state machine and its snapshots, the host and its resources, and anything else you find. Some assumptions the text states; some it only implies. List every one you can find, as a **service contract**: an obligation on something Raft depends on, stated so that a deployment either meets it or violates it.

For each contract, give:
- **id**: `E<n>`, numbered from 1 in the order you write them.
- **contract**: one sentence, an obligation on the depended-on service.
- **source**: section number and a quotation of at most two lines that states or implies it.
- **stated or implicit**.
- **violation**: what violating it looks like in a deployment, concretely.
- **at risk**: which of Raft's promises fails, by your reasoning, if it is violated, and why (one or two sentences; say if you are unsure).
- **detectable**: `yes`, `partly` or `no`: could a Raft implementation notice the violation at run time, and how.
- **silent**: 1 to 5: how often, in your judgement, ordinary deployments violate it **without** an error that the operator or the implementation sees. 1 rare, 3 occasional, 5 routine. Give one line of reason.

## Rules
- Be exhaustive within the source. Several fine-grained contracts are better than one broad one.
- Do not rank by how interesting a contract is; rate each against the anchors.
- If you recognise a contract as one behind a bug you know was reported in some Raft implementation, do not leave it out and do not shape your list around it: list it like the others, and name what you recognise in a final section, **Recognised**, one line each. Saying you recognise nothing is also an answer.
- Write the list to `enumeration.md` in the checkout root and commit it. Your report at the end: how many contracts, how long you read, anything you could not decide.
