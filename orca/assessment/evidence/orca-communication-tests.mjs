import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  OrchestrationDb, reconcileLifecycleMessage, dispatchReportMailbox,
  sendFederatedControlMail, formatMessagePointer, reportWorkerTurnStop
} from './orca-communication-audit.mjs';

function fixture(fn) {
  return () => {
    const db = new OrchestrationDb(':memory:');
    const run = db.createRun({ objective: 'Communication audit', coordinatorHandle: 'coordinator', coordinatorPaneKey: 'coord:11111111-1111-4111-8111-111111111111' });
    try { return fn(db, run); } finally { db.close(); }
  };
}
function dispatch(db, run, spec = 'worker', handle = 'worker') {
  const task = db.createTask({ runId: run.id, spec });
  const pane = `${handle}:22222222-2222-4222-8222-222222222222`;
  const attempt = db.createDispatchContext({ taskId: task.id, assigneeHandle: handle, assigneePaneKey: pane, creator: { kind: 'system' }, maxDepth: 4 });
  return { task, attempt, pane };
}
function report(db, run, work, outcome = 'succeeded', pane = work.pane) {
  return db.insertMessage({ from: work.attempt.assignee_handle, to: `run:${run.id}`, runId: run.id, senderPaneKey: pane, type: 'worker_done', subject: 'Report', body: 'Evidence remains an agent claim', payload: JSON.stringify({ taskId: work.task.id, dispatchId: work.attempt.id, outcome }) });
}

test('a nudge delivery does not consume mail; normal take consumes FIFO, not priority order', fixture((db, run) => {
  const address = `run:${run.id}`;
  const first = db.insertMessage({ from: 'a', to: address, runId: run.id, subject: 'older', priority: 'normal' });
  db.insertMessage({ from: 'b', to: address, runId: run.id, subject: 'urgent newer', priority: 'urgent' });
  db.markAsDelivered([first.id], address);
  assert.equal(db.getMessageById(first.id).read, 0);
  const batch = db.takeRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation });
  assert.deepEqual(batch.messages.map(m => m.subject), ['older', 'urgent newer']);
  assert.equal(db.getUnreadRunMailbox(run.id).length, 0);
  assert.equal(db.takeRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation }), undefined);
}));

test('failure to save the consuming-check receipt rolls back consumption', fixture((db, run) => {
  const msg = db.insertMessage({ from: 'worker', to: `run:${run.id}`, runId: run.id, subject: 'retain me' });
  assert.throws(() => db.takeRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation, recordTaken() { throw new Error('simulated receipt failure'); } }), /receipt failure/);
  assert.equal(db.getMessageById(msg.id).read, 0);
  assert.equal(db.takeRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation }).messages[0].id, msg.id);
}));

test('mutation receipts replay identical request IDs and reject changed input', fixture((db) => {
  const identity = { callerFingerprint: 'caller', requestId: 'request', method: 'orchestration.send', payloadHash: 'hash' };
  assert.equal(db.beginMutationReceipt(identity).disposition, 'started');
  db.completeMutationReceipt({ ...identity, receipt: JSON.stringify({ messageId: 'fixed' }) });
  const replay = db.beginMutationReceipt(identity);
  assert.equal(replay.disposition, 'completed');
  assert.equal(JSON.parse(replay.row.receipt).messageId, 'fixed');
  assert.throws(() => db.beginMutationReceipt({ ...identity, payloadHash: 'different' }), e => e.code === 'request_mismatch');
}));

test('questions are correlated and idempotently answered; a conflicting answer is refused', fixture((db, run) => {
  const work = dispatch(db, run);
  const created = db.createQuestion({ runId: run.id, dispatchId: work.attempt.id, askerHandle: 'worker', question: 'Which contract?', options: ['A', 'B'] });
  assert.equal(db.getTask(work.task.id).status, 'dispatched');
  const params = { messageId: created.question.message_id, runId: run.id, consumerGeneration: run.consumer_generation, body: 'A' };
  const answered = db.answerQuestion(params);
  assert.equal(answered.duplicate, false);
  assert.equal(db.answerQuestion(params).duplicate, true);
  assert.throws(() => db.answerQuestion({ ...params, body: 'B' }), e => e.code === 'answer_conflict');
  assert.equal(answered.message.to_handle, `dispatch:${work.attempt.id}`);
}));

test('settling a dispatch closes its outstanding question', fixture((db, run) => {
  const work = dispatch(db, run);
  const asked = db.createQuestion({ runId: run.id, dispatchId: work.attempt.id, askerHandle: 'worker', question: 'Still needed?' });
  db.completeDispatch(work.attempt.id);
  assert.equal(db.getQuestion(asked.question.message_id).status, 'closed');
  assert.throws(() => db.answerQuestion({ messageId: asked.question.message_id, runId: run.id, consumerGeneration: run.consumer_generation, body: 'too late' }), e => e.code === 'dispatch_inactive');
}));

test('worker completion requires the owning pane and unlocks a dependent only on success', fixture((db, run) => {
  const work = dispatch(db, run);
  const qa = db.createTask({ runId: run.id, spec: 'QA', deps: [work.task.id] });
  const rejected = reconcileLifecycleMessage(db, report(db, run, work, 'succeeded', 'other:33333333-3333-4333-8333-333333333333'));
  assert.equal(rejected.action, 'rejected');
  assert.equal(rejected.code, 'sender_not_assignee');
  assert.equal(db.getTask(qa.id).status, 'pending');
  assert.equal(reconcileLifecycleMessage(db, report(db, run, work)).action, 'completed');
  assert.equal(db.getTask(qa.id).status, 'ready');
}));

test('a failed worker report does not unlock its dependent', fixture((db, run) => {
  const work = dispatch(db, run);
  const qa = db.createTask({ runId: run.id, spec: 'QA', deps: [work.task.id] });
  assert.equal(reconcileLifecycleMessage(db, report(db, run, work, 'failed')).action, 'failed');
  assert.equal(db.getTask(qa.id).status, 'pending');
}));

test('completion message and task transition roll back together', fixture((db, run) => {
  const work = dispatch(db, run);
  let messageId;
  assert.throws(() => db.commitWorkerDoneMessageMutation(() => {
    const msg = report(db, run, work);
    messageId = msg.id;
    assert.equal(reconcileLifecycleMessage(db, msg).action, 'completed');
    throw new Error('simulated completion-receipt failure');
  }), /receipt failure/);
  assert.equal(db.getMessageById(messageId), undefined);
  assert.equal(db.getTask(work.task.id).status, 'dispatched');
  assert.equal(db.getDispatchContextById(work.attempt.id).status, 'dispatched');
}));

test('heartbeat records liveness without placing unread work in the coordinator inbox', fixture((db, run) => {
  const work = dispatch(db, run);
  const msg = db.insertMessage({ from: 'worker', to: `run:${run.id}`, runId: run.id, type: 'heartbeat', subject: 'alive', senderPaneKey: work.pane, payload: JSON.stringify({ taskId: work.task.id, dispatchId: work.attempt.id }) });
  assert.equal(reconcileLifecycleMessage(db, msg).action, 'heartbeat_recorded');
  assert.equal(db.getUnreadRunMailbox(run.id).length, 0);
  assert.equal(db.getTask(work.task.id).status, 'dispatched');
}));

test('a helper reports to its live creator, then falls back to the Run home', fixture((db, run) => {
  const parent = dispatch(db, run, 'lead', 'lead');
  const task = db.createTask({ runId: run.id, spec: 'helper' });
  const child = db.createDispatchContext({ taskId: task.id, assigneeHandle: 'helper', assigneePaneKey: 'helper:44444444-4444-4444-8444-444444444444', creator: { kind: 'terminal', handle: 'lead', paneKey: parent.pane }, maxDepth: 4 });
  assert.equal(dispatchReportMailbox(db, child), `dispatch:${parent.attempt.id}`);
  db.completeDispatch(parent.attempt.id);
  assert.equal(dispatchReportMailbox(db, child), `run:${run.id}`);
}));

test('federated imports deduplicate, reject gaps, and roll back a failed cursor update', fixture((db, run) => {
  const task = db.createTask({ runId: run.id, spec: 'remote' });
  const started = db.createStartingWorkerDispatch({ creator: { kind: 'system' }, maxDepth: 4, taskId: task.id, startOptions: {}, federation: { environmentId: 'host', environmentName: 'Host', peerFingerprint: 'peer', protocolVersion: 3 } });
  const params = { dispatchId: started.dispatch.id, sequence: 1, message: { id: 'remote_message', runId: run.id, from: `dispatch:${started.dispatch.id}`, to: `run:${run.id}`, type: 'status', priority: 'normal', subject: 'remote update', body: '' }, lifecycle: { kind: 'none' } };
  db.db.exec("CREATE TRIGGER fail_cursor BEFORE UPDATE OF to_home_imported_sequence ON federated_dispatches BEGIN SELECT RAISE(ABORT, 'simulated cursor failure'); END;");
  assert.throws(() => db.importFederatedRelayItem(params), /cursor failure/);
  assert.equal(db.getMessageById(params.message.id), undefined);
  db.db.exec('DROP TRIGGER fail_cursor');
  assert.equal(db.importFederatedRelayItem(params).duplicate, false);
  assert.equal(db.importFederatedRelayItem(params).duplicate, true);
  assert.throws(() => db.importFederatedRelayItem({ ...params, sequence: 3, message: { ...params.message, id: 'gap' } }), e => e.code === 'operation_unknown');
}));

test('a finished federated worker refuses follow-up mail', () => {
  const db = { getFederatedDispatch: () => ({ protocol_version: 999, environment_name: 'Remote' }), getWorkerDispatch: () => ({ state: 'succeeded' }) };
  assert.throws(() => sendFederatedControlMail({ params: { subject: 'more work' }, runtime: {}, db, from: 'coordinator', to: 'dispatch:finished', withSendWarnings: x => x }), e => e.code === 'dispatch_inactive' && /cannot take follow-ups/.test(e.message));
});

test('automatic mailbox notices point to check rather than including message bodies', () => {
  const notice = formatMessagePointer(2, 'run:example');
  assert.match(notice, /2 orchestration messages/);
  assert.match(notice, /orchestration check --run example/);
});

test('an ended turn without worker_done escalates once and does not complete the task', fixture((db, run) => {
  const work = dispatch(db, run);
  const notifications = [];
  const deps = { getDb: () => db, isWaitingForMail: () => false, notify: (...args) => notifications.push(args) };
  const stop = { from: 'worker', stopKey: 'turn:one', reason: 'finished', lastOutput: 'I stopped here.' };
  reportWorkerTurnStop(db, { kind: 'local', dispatch: work.attempt }, stop, deps);
  reportWorkerTurnStop(db, { kind: 'local', dispatch: work.attempt }, stop, deps);
  const mail = db.getUnreadRunMailbox(run.id);
  assert.equal(mail.length, 1);
  assert.equal(mail[0].type, 'escalation');
  assert.equal(db.getTask(work.task.id).status, 'dispatched');
}));

test('a decision gate refuses to pretend an active supervised worker has been paused', fixture((db, run) => {
  const task = db.createTask({ runId: run.id, spec: 'running work' });
  const started = db.createStartingWorkerDispatch({ creator: { kind: 'system' }, maxDepth: 4, taskId: task.id, startOptions: {} });
  assert.throws(() => db.createGate({ taskId: task.id, question: 'Pause?' }), e => e.code === 'task_not_startable');
  assert.equal(db.getTask(task.id).status, 'dispatched');
  assert.equal(db.getWorkerDispatch(started.dispatch.id).state, 'starting');
}));
