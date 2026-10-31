const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_PATTERN = /^\d{8,15}$/;
const ALLOWED_PRIORITIES = new Set(['low', 'normal', 'high', 'urgent']);
const ALLOWED_CHANNELS = new Set(['email', 'whatsapp']);
const ALLOWED_STATUSES = new Set(['open', 'in-progress', 'closed']);

export function normalizePhone(value = '') {
  return String(value).trim().replace(/[\s()+\-.]/g, '');
}

export function validateTicketPayload(payload = {}) {
  const errors = [];
  const customerName = String(payload.customerName || '').trim();
  const subject = String(payload.subject || '').trim();
  const message = String(payload.message || '').trim();
  const email = String(payload.email || '').trim();
  const whatsapp = normalizePhone(payload.whatsapp || '');
  const priority = String(payload.priority || 'normal').trim().toLowerCase();
  const channels = Array.isArray(payload.channels)
    ? [...new Set(payload.channels.map((item) => String(item).toLowerCase()))]
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
  if (channels.includes('email') && !EMAIL_PATTERN.test(email)) {
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
