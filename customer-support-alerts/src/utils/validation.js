const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_PATTERN = /^[1-9]\d{7,14}$/;
const ALLOWED_PRIORITIES = new Set(['low', 'normal', 'high', 'urgent']);
const ALLOWED_CHANNELS = new Set(['email', 'whatsapp']);
const ALLOWED_STATUSES = new Set(['open', 'in-progress', 'closed']);

const normalizeText = (value) => typeof value === 'string' ? value.trim() : '';

export function normalizePhone(value = '') {
  return String(value).trim().replace(/[\s()+\-.]/g, '');
}

export function validateTicketPayload(payload = {}) {
  const errors = [];
  const source = payload && typeof payload === 'object' && !Array.isArray(payload) ? payload : {};
  const customerName = normalizeText(source.customerName);
  const subject = normalizeText(source.subject);
  const message = normalizeText(source.message);
  const email = normalizeText(source.email);
  const whatsapp = normalizePhone(typeof source.whatsapp === 'string' ? source.whatsapp : '');
  const priority = source.priority === undefined
    ? 'normal'
    : normalizeText(source.priority).toLowerCase();
  const channels = Array.isArray(source.channels)
    ? [...new Set(source.channels.map((item) => normalizeText(item).toLowerCase()))]
    : [];

  if (customerName.length < 2 || customerName.length > 100) {
    errors.push('Customer/recipient name must be between 2 and 100 characters.');
  }
  if (subject.length < 3 || subject.length > 160) {
    errors.push('Subject must be between 3 and 160 characters.');
  }
  if (message.length < 5 || message.length > 5000) {
    errors.push('Message must be between 5 and 5000 characters.');
  }
  if (!ALLOWED_PRIORITIES.has(priority)) {
    errors.push('Priority must be low, normal, high, or urgent.');
  }
  if (channels.length === 0 || channels.some((channel) => !ALLOWED_CHANNELS.has(channel))) {
    errors.push('Select at least one valid channel: email or whatsapp.');
  }
  if (channels.includes('email') && (
    email.length > 254
    || email.slice(0, email.indexOf('@')).length > 64
    || !EMAIL_PATTERN.test(email)
  )) {
    errors.push('A valid email address is required for email alerts.');
  }
  if (channels.includes('whatsapp') && !PHONE_PATTERN.test(whatsapp)) {
    errors.push('A valid WhatsApp number is required in international format, e.g. 2348012345678.');
  }

  return {
    valid: errors.length === 0,
    errors,
    value: { customerName, subject, message, email, whatsapp, priority, channels }
  };
}

export function validateStatus(status) {
  const normalized = String(status || '').trim().toLowerCase();
  return {
    valid: ALLOWED_STATUSES.has(normalized),
    value: normalized
  };
}
