# Synthetic Dataset Schema

The benchmark generates two CSV files. No real user data, documents or agent logs are included.

## episode_metrics.csv
- `episode_id`: stable synthetic episode identifier.
- `seed`: random seed.
- `policy`: baseline policy name.
- `steps`: number of workflow steps.
- `wrong_steps`: count of steps with an incorrect intermediate state.
- `episode_success`: 1 only when no step is wrong; otherwise 0.
- `propagated_errors`: count of propagation events under the simulator's propagation rule.
- `retrievals`: number of refresh/retrieval operations.
- `recoveries`: count of simulated successful recovery events.
- `unnecessary_refreshes`: refreshes triggered when no stale/contradictory/upstream-error condition existed.

## step_traces.csv
- `episode_id`, `seed`, `policy`: episode keys.
- `step`: 1-based workflow step.
- `stale_evidence`: whether stale evidence remained after any refresh.
- `contradiction`: whether contradiction remained after any refresh.
- `confidence`: noisy confidence score before refresh (bad evidence 0.40 to 0.90, good evidence 0.60 to 1.00).
- `refresh_triggered`: whether policy initiated refresh.
- `step_error`: whether current step ended in error.
- `error_propagated`: indicator emitted by current simulator implementation when a propagation event has occurred and the current step is erroneous; interpret with the source code and do not treat it as a causal ground-truth annotation.

## Intended future real-data schema
For external trace adapters, proposed fields include task_id, step_id, parent_step_id, agent_id, timestamp, query, retrieved_document_ids, source_timestamp, evidence_claims, contradiction_flags, tool_name, tool_input_hash, tool_output_hash, verification_outcome, recovery_action, final_outcome, and data_rights. Collect only data with appropriate permission and remove secrets/personal data.
