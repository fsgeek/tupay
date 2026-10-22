---- MODULE Run ----
EXTENDS Sequences, Integers

CONSTANTS m1, m2, m3, m4, m5, Nil

VARIABLES
  servers, msgs, down, pending,
  leaders, committed, breach,
  seq, grantSeq, appAt, envSeq, lastObs,
  step, triggerLive, resolved, events, doneAt, coord, crashed,
  crashCount, changeCount, cmdCount, dropCount, redeliverCount

InitConfig == {m1, m2, m3, m4}
MaxTerm == 2
MaxLog == 3
MaxMsgs == 4
MaxEvents == 400
Settle == 100
Bug == "none"
Mode == "scenario"
NumSteps == 5
MaxCmds == 0
MaxChanges == 0
MaxCrashes == 0
MaxDown == 20
MaxDrops == 0
MaxRedelivers == 0
AmbientLoss == FALSE
Triggers == <<
  [event |-> "Elected", member |-> "m1", index |-> -1, epoch |-> -1, kind |-> "", status |-> "", op |-> "", target |-> ""],
  [event |-> "ChangeRequested", member |-> "m1", index |-> -1, epoch |-> -1, kind |-> "", status |-> "", op |-> "", target |-> ""],
  [event |-> "Appended", member |-> "m5", index |-> -1, epoch |-> -1, kind |-> "config", status |-> "", op |-> "", target |-> ""],
  [event |-> "Elected", member |-> "m2", index |-> -1, epoch |-> -1, kind |-> "", status |-> "", op |-> "", target |-> ""],
  [event |-> "Committed", member |-> "m2", index |-> -1, epoch |-> -1, kind |-> "", status |-> "", op |-> "", target |-> ""]
>>
Actions == <<
  [kind |-> "add", at |-> "m1", target |-> "m5", cmd |-> "", links |-> <<>>],
  [kind |-> "cut", at |-> "", target |-> "", cmd |-> "", links |-> <<<<"m1", "m2">>, <<"m1", "m3">>, <<"m1", "m4">>>>],
  [kind |-> "cut", at |-> "", target |-> "", cmd |-> "", links |-> <<<<"m3", "m4">>>>],
  [kind |-> "remove", at |-> "m2", target |-> "m4", cmd |-> "", links |-> <<>>],
  [kind |-> "heal", at |-> "", target |-> "", cmd |-> "", links |-> <<>>]
>>

R == INSTANCE Raft WITH
  m1 <- m1, m2 <- m2, m3 <- m3, m4 <- m4, m5 <- m5, Nil <- Nil,
  InitConfig <- InitConfig, MaxTerm <- MaxTerm, MaxLog <- MaxLog,
  MaxMsgs <- MaxMsgs, MaxEvents <- MaxEvents, Settle <- Settle,
  Bug <- Bug, Mode <- Mode, NumSteps <- NumSteps,
  Triggers <- Triggers, Actions <- Actions,
  MaxCmds <- MaxCmds, MaxChanges <- MaxChanges, MaxCrashes <- MaxCrashes,
  MaxDown <- MaxDown, MaxDrops <- MaxDrops, MaxRedelivers <- MaxRedelivers,
  AmbientLoss <- AmbientLoss,
  servers <- servers, msgs <- msgs, down <- down, pending <- pending,
  leaders <- leaders, committed <- committed, breach <- breach,
  seq <- seq, grantSeq <- grantSeq, appAt <- appAt, envSeq <- envSeq,
  lastObs <- lastObs, step <- step, triggerLive <- triggerLive,
  resolved <- resolved, events <- events, doneAt <- doneAt,
  coord <- coord, crashed <- crashed, crashCount <- crashCount,
  changeCount <- changeCount, cmdCount <- cmdCount,
  dropCount <- dropCount, redeliverCount <- redeliverCount

Spec == R!Spec
J11 == R!J11
J13 == R!J13
J15 == R!J15
StateBound == R!StateBound
View == R!View
====
