---- MODULE MC ----
\* derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4
EXTENDS Journal

InitCfg == {"m1", "m2", "m3", "m4"}
MaxEpochC == 3
MaxLogLenC == 4
MaxRoundsC == 3
SettleC == 100
MaxEventsC == 400
MutationC == "none"
ExploreC == FALSE
MaxCrashesC == 0
MaxAdminC == 0
MaxLinkC == 0
CommandsC == {"c1"}
StepsC == <<
  [trigger |->
    [kind |-> "event",
     event |-> "Elected",
     member |-> "m1",
     index |-> -1,
     ekind |-> "",
     status |-> "",
     epoch |-> -1,
     op |-> "",
     target |-> ""],
   action |->
    [kind |-> "add",
     at |-> "m1",
     target |-> "m5",
     cmd |-> "",
     links |-> << >>]],
  [trigger |->
    [kind |-> "event",
     event |-> "ChangeRequested",
     member |-> "m1",
     index |-> -1,
     ekind |-> "",
     status |-> "",
     epoch |-> -1,
     op |-> "",
     target |-> ""],
   action |->
    [kind |-> "cut",
     at |-> "",
     target |-> "",
     cmd |-> "",
     links |-> << <<"m1", "m2">>, <<"m1", "m3">>, <<"m1", "m4">> >>]],
  [trigger |->
    [kind |-> "event",
     event |-> "Appended",
     member |-> "m5",
     index |-> -1,
     ekind |-> "config",
     status |-> "",
     epoch |-> -1,
     op |-> "",
     target |-> ""],
   action |->
    [kind |-> "cut",
     at |-> "",
     target |-> "",
     cmd |-> "",
     links |-> << <<"m3", "m4">> >>]],
  [trigger |->
    [kind |-> "event",
     event |-> "Elected",
     member |-> "m2",
     index |-> -1,
     ekind |-> "",
     status |-> "",
     epoch |-> -1,
     op |-> "",
     target |-> ""],
   action |->
    [kind |-> "remove",
     at |-> "m2",
     target |-> "m4",
     cmd |-> "",
     links |-> << >>]],
  [trigger |->
    [kind |-> "event",
     event |-> "Committed",
     member |-> "m2",
     index |-> -1,
     ekind |-> "",
     status |-> "",
     epoch |-> -1,
     op |-> "",
     target |-> ""],
   action |->
    [kind |-> "heal",
     at |-> "",
     target |-> "",
     cmd |-> "",
     links |-> << >>]]
>>
====
