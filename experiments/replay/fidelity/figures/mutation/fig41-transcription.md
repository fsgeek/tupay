## Figure 4.1 (transcribed)

### AddServer RPC
Invoked by admin to add a server to the cluster configuration.
Arguments: newServer — address of server to add to configuration
Results: status — OK if server was added successfully; leaderHint — address of recent leader, if known
Receiver implementation:
1. Reply NOT_LEADER if not leader (§6.2)
2. Catch up new server for fixed number of rounds. Reply TIMEOUT if new server does not make progress for an election timeout or if the last round takes longer than the election timeout. (§4.2.1)
3. Wait until previous configuration in log is committed (§4.2)
4. Append new configuration entry to log (old configuration plus newServer), commit it using majority of new configuration (§4.1)
5. Reply OK

### RemoveServer RPC
Invoked by admin to remove a server from the cluster configuration.
Arguments: oldServer — address of server to remove from configuration
Results: status — OK if server was removed successfully; leaderHint — address of recent leader, if known
Receiver implementation:
1. Reply NOT_LEADER if not leader (§6.2)
2. Wait until previous configuration in log is committed (§4.2)
3. Append new configuration entry to log (old configuration without oldServer), commit it using majority of new configuration (§4.1)
4. Reply OK and, if this server was removed, step down (§4.2.2)

Figure 4.1: RPCs used to change cluster membership. The AddServer RPC is used to add a new server to the current configuration, and the RemoveServer RPC is used to remove a server from the current configuration. Section numbers such as §4.1 indicate where particular features are discussed. Section 4.4 discusses ways to use these RPCs in a complete system.

