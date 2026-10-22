| scenario | variant | outcome | E | T | T_pre | J | lost | settle | distinct states | exhausted | s | earlier attempts (UNEXPLAINED bound) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | SPEC | PASS | 3 | 3 | 2 | 1 | 1 | 2 | 32,656,628 | yes | 23 | none |
| S1 | GATED | PASS | 3 | 2 | 2 | 4 | 0 | 2 | 124,032,049 | yes | 56 | T=3,T_pre=2,lost=1: 683,317,319 states in 309s; T=3,T_pre=2,lost=0: 694,175,721 states in 309s |
| S2 | SPEC | PASS | 3 | 3 | 2 | 0 | 1 | 2 | 463,940 | yes | 10 | none |
| S2 | GATED | PASS | 3 | 3 | 2 | 3 | 1 | 2 | 108,429,616 | yes | 54 | none |
| S3 | SPEC | PASS | 3 | 2 | 1 | 2 | 1 | 2 | 5,707,089 | yes | 12 | T=3,T_pre=2,lost=1: 379,363,758 states in 189s |
| S3 | GATED | PASS | 3 | 2 | 1 | 4 | 1 | 2 | 21,921,380 | yes | 19 | T=3,T_pre=2,lost=1: 383,483,853 states in 189s |
| S4 | SPEC | PASS | 3 | 2 | 1 | 2 | 0 | 2 | 218,225,995 | yes | 100 | T=3,T_pre=2,lost=1: 436,765,824 states in 189s; T=2,T_pre=1,lost=1: 597,551,786 states in 309s |
| S4 | GATED | PASS | 3 | 1 | 1 | 4 | 0 | 2 | 162,898,529 | yes | 72 | T=3,T_pre=2,lost=1: 401,544,908 states in 189s; T=2,T_pre=1,lost=1: 607,071,576 states in 308s; T=2,T_pre=1,lost=0: 593,073,184 states in 309s |
| S5 | SPEC | PASS | 3 | 2 | 1 | 1 | 1 | 2 | 5,642,318 | yes | 12 | T=3,T_pre=2,lost=1: 380,688,625 states in 188s |
| S5 | GATED | PASS | 3 | 2 | 1 | 3 | 1 | 2 | 26,011,573 | yes | 19 | T=3,T_pre=2,lost=1: 443,109,642 states in 189s |
| S6 | SPEC | PASS | 3 | 3 | 2 | 1 | 1 | 2 | 29,164,888 | yes | 22 | none |
| S6 | GATED | PASS | 3 | 3 | 2 | 4 | 0 | 2 | 356,499,086 | yes | 180 | T=3,T_pre=2,lost=1: 606,317,739 states in 309s |
| S7 | SPEC | PASS | 3 | 3 | 2 | 2 | 1 | 2 | 11,085,880 | yes | 14 | none |
| S7 | GATED | PASS | 3 | 3 | 2 | 4 | 1 | 2 | 139,561,397 | yes | 78 | none |
| S8 | SPEC | PASS | 3 | 3 | 2 | 3 | 1 | 2 | 76,066,560 | yes | 41 | none |
| S8 | GATED | PASS | 3 | 2 | 1 | 5 | 1 | 2 | 8,605,697 | yes | 13 | T=3,T_pre=2,lost=1: 429,403,468 states in 189s |
| K1v3 | SPEC | FAIL J1.4(a) | 3 | 3 | 2 | 2 | 1 | 2 | 4,989 | no (stopped at FAIL) | 9 | none |
| K1v3 | GATED | PASS | 3 | 3 | 2 | 5 | 0 | 2 | 227,532,361 | yes | 145 | T=3,T_pre=2,lost=1: 476,755,973 states in 308s |
