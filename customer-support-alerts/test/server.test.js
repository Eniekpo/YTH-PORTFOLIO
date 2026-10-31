import assert from 'node:assert/strict';
import { once } from 'node:events';
import test, { after, before } from 'node:test';
import { app } from '../src/server.js';

let server;
let baseUrl;

before(async () => {
  server = app.listen(0, '127.0.0.1');
  await once(server, 'listening');
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(async () => {
  const closed = once(server, 'close');
  server.close();
  server.closeAllConnections();
  await closed;
});

test('health endpoint responds with service status and security headers', async () => {
  const response = await fetch(`${baseUrl}/api/health`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.service, 'customer-support-alerts');
  assert.equal(response.headers.get('x-powered-by'), null);
  assert.ok(response.headers.has('content-security-policy'));
});

test('invalid JSON receives a client error instead of an internal server error', async () => {
  const response = await fetch(`${baseUrl}/api/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: '{"customerName":'
  });

  assert.equal(response.status, 400);
  assert.deepEqual(await response.json(), { error: 'Invalid request body.' });
});

test('ticket status updates with a missing body receive a validation error', async () => {
  const response = await fetch(`${baseUrl}/api/tickets/TKT-invalid/status`, { method: 'PATCH' });

  assert.equal(response.status, 400);
  assert.deepEqual(await response.json(), {
    error: 'Status must be open, in-progress, or closed.'
  });
});

test('unknown non-API routes do not return the application page for non-GET requests', async () => {
  const response = await fetch(`${baseUrl}/unknown`, { method: 'POST' });

  assert.equal(response.status, 404);
  assert.equal(await response.text(), 'Not found.');
});

test('unknown API paths return a JSON 404 response', async () => {
  const response = await fetch(`${baseUrl}/api`);

  assert.equal(response.status, 404);
  assert.deepEqual(await response.json(), { error: 'API route not found.' });
});
