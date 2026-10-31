import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizePhone, validateStatus, validateTicketPayload } from '../src/utils/validation.js';

test('normalizePhone strips common formatting', () => {
  assert.equal(normalizePhone('+234 (801) 234-5678'), '2348012345678');
});

test('valid ticket payload is accepted', () => {
  const result = validateTicketPayload({
    customerName: 'Amina Yusuf',
    subject: 'Order update',
    message: 'Your support request has been received.',
    priority: 'high',
    email: 'amina@example.com',
    whatsapp: '+234 801 234 5678',
    channels: ['email', 'whatsapp']
  });

  assert.equal(result.valid, true);
  assert.equal(result.value.whatsapp, '2348012345678');
});

test('channel-specific recipient is required', () => {
  const result = validateTicketPayload({
    customerName: 'Amina Yusuf',
    subject: 'Order update',
    message: 'Your support request has been received.',
    channels: ['email'],
    email: ''
  });
  assert.equal(result.valid, false);
  assert.match(result.errors.join(' '), /valid email/i);
});

test('ticket status is constrained', () => {
  assert.equal(validateStatus('closed').valid, true);
  assert.equal(validateStatus('deleted').valid, false);
});
