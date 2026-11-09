import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import { OrchestrationDb } from './orca-orchestration-audit.mjs';

const coordinator = {
  objective: 'Assessment only',
  coordinatorHandle: 'term_coord',
  coordinatorPaneKey: 'tab_coord:11111111-1111-4111-8111-111111111111'
};

test('task DAG waits for all dependencies and rejects missing dependencies', () => {
  const db = new OrchestrationDb(':memory:');
  try {
    const run = db.createRun(coordinator);
    const a = db.createTask({ runId: run.id, spec: 'frontend' });
    const b = db.createTask({ runId: run.id, spec: 'backend' });
    const qa = db.createTask({ runId: run.id, spec: 'integration QA', deps: [a.id, b.id] });
    assert.equal(qa.status, 'pending');
    db.updateTaskStatus(a.id, 'completed');
    assert.equal(db.getTask(qa.id).status, 'pending');
    db.updateTaskStatus(b.id, 'completed');
    assert.equal(db.getTask(qa.id).status, 'ready');
    assert.throws(() => db.createTask({ runId: run.id, spec: 'invalid', deps: ['missing'] }));
  } finally { db.close(); }
});

test('decision gate blocks a task until resolved', () => {
  const db = new OrchestrationDb(':memory:');
  try {
    const run = db.createRun(coordinator);
    const task = db.createTask({ runId: run.id, spec: 'PM delivery approval' });
    const gate = db.createGate({ taskId: task.id, question: 'Accept delivery?', options: ['yes', 'no'] });
    assert.equal(db.getTask(task.id).status, 'blocked');
    db.resolveGate(gate.id, 'yes');
    assert.equal(db.getTask(task.id).status, 'ready');
  } finally { db.close(); }
});

test('mail replays until acknowledgment; duplicate acknowledgment preserves newer mail', () => {
  const db = new OrchestrationDb(':memory:');
  try {
    const run = db.createRun(coordinator);
    const address = `run:${run.id}`;
    const read = () => db.getOrCreateRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation });
    db.insertMessage({ from: 'worker', to: address, subject: 'first', runId: run.id });
    const first = read();
    assert.equal(read().delivery.id, first.delivery.id);
    db.insertMessage({ from: 'worker', to: address, subject: 'second', runId: run.id });
    const ack = () => db.acknowledgeRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation, deliveryId: first.delivery.id });
    assert.equal(ack().duplicate, false);
    assert.equal(ack().duplicate, true);
    assert.deepEqual(read().messages.map(m => m.subject), ['second']);
  } finally { db.close(); }
});

test('a new coordinator fences the old consumer generation', () => {
  const db = new OrchestrationDb(':memory:');
  try {
    const run = db.createRun(coordinator);
    db.insertMessage({ from: 'worker', to: `run:${run.id}`, subject: 'pending', runId: run.id });
    const old = db.getOrCreateRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation });
    const rebound = db.bindRun({ runId: run.id, coordinatorHandle: 'term_new', coordinatorPaneKey: 'tab_new:22222222-2222-4222-8222-222222222222' });
    assert.throws(() => db.acknowledgeRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation, deliveryId: old.delivery.id }), e => e.code === 'consumer_fenced');
    const next = db.getOrCreateRunDelivery({ runId: run.id, consumerGeneration: rebound.consumer_generation });
    assert.equal(next.messages[0].subject, 'pending');
  } finally { db.close(); }
});

test('starting a worker records a task attempt and refuses a duplicate active attempt', () => {
  const db = new OrchestrationDb(':memory:');
  try {
    const run = db.createRun(coordinator);
    const task = db.createTask({ runId: run.id, spec: 'developer work' });
    const options = { creator: { kind: 'system' }, maxDepth: 3, taskId: task.id, startOptions: { topology: 'current', agent: 'codex' } };
    const started = db.createStartingWorkerDispatch(options);
    assert.equal(started.worker.state, 'starting');
    assert.equal(db.getTask(task.id).status, 'dispatched');
    assert.throws(() => db.createStartingWorkerDispatch(options));
  } finally { db.close(); }
});

test('run, task, and unacknowledged mail survive reopening the database', () => {
  const scratch = fileURLToPath(new URL('../../../.run/', import.meta.url));
  mkdirSync(scratch, { recursive: true });
  const dir = mkdtempSync(join(scratch, 'orca-assessment-'));
  const path = join(dir, 'orchestration.db');
  let db = new OrchestrationDb(path);
  try {
    const run = db.createRun(coordinator);
    const task = db.createTask({ runId: run.id, spec: 'persistent work' });
    db.insertMessage({ from: 'worker', to: `run:${run.id}`, subject: 'retained', runId: run.id });
    const first = db.getOrCreateRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation });
    db.close();
    db = new OrchestrationDb(path);
    assert.equal(db.getTask(task.id).spec, 'persistent work');
    assert.equal(db.getRun(run.id).objective, coordinator.objective);
    assert.equal(db.getOrCreateRunDelivery({ runId: run.id, consumerGeneration: run.consumer_generation }).delivery.id, first.delivery.id);
  } finally { db.close(); rmSync(dir, { recursive: true }); }
});
