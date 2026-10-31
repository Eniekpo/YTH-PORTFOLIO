import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizePhone, validateStatus, validateTicketPayload } from '../src/utils/validation.js';

test('normalizePhone strips common formatting', () => {
  assert.equal(normalizePhone('+234 (801) 234-5678'), '2348012345678');
});

test('invalid request bodies are rejected without throwing', () => {
  assert.equal(validateTicketPayload(null).valid, false);
  assert.equal(validateTicketPayload([]).valid, false);
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

test('channels are normalized and deduplicated', () => {
  const result = validateTicketPayload({
    customerName: 'Amina Yusuf',
    subject: 'Order update',
    message: 'Your support request has been received.',
    email: 'amina@example.com',
    channels: ['EMAIL', 'email']
  });

  assert.equal(result.valid, true);
  assert.deepEqual(result.value.channels, ['email']);
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

test('WhatsApp numbers must use a valid international digit range', () => {
  const valid = validateTicketPayload({
    customerName: 'Amina Yusuf',
    subject: 'Order update',
    message: 'Your support request has been received.',
    whatsapp: '2348012345678',
    channels: ['whatsapp']
  });
  const invalid = validateTicketPayload({
    customerName: 'Amina Yusuf',
    subject: 'Order update',
    message: 'Your support request has been received.',
    whatsapp: '00000000',
    channels: ['whatsapp']
  });

  assert.equal(valid.valid, true);
  assert.equal(invalid.valid, false);
});

test('non-string fields are not coerced into valid ticket data', () => {
  const result = validateTicketPayload({
    customerName: 123,
    subject: 'Order update',
    message: 'Your support request has been received.',
    email: 'amina@example.com',
    channels: ['email']
  });

  assert.equal(result.valid, false);
  assert.match(result.errors.join(' '), /name must be between/i);
});
