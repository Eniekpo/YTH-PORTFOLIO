import 'dotenv/config';

const toBool = (value, fallback, name) => {
  if (value === undefined) return fallback;
  const normalized = String(value).trim().toLowerCase();
  if (normalized === 'true') return true;
  if (normalized === 'false') return false;
  throw new Error(`${name} must be "true" or "false".`);
};

const toInt = (value, fallback, name, minimum, maximum) => {
  if (value === undefined) return fallback;
  const normalized = String(value).trim();
  if (!/^\d+$/.test(normalized)) {
    throw new Error(`${name} must be a whole number between ${minimum} and ${maximum}.`);
  }
  const parsed = Number(normalized);
  if (parsed < minimum || parsed > maximum) {
    throw new Error(`${name} must be a whole number between ${minimum} and ${maximum}.`);
  }
  return parsed;
};

export const config = {
  host: process.env.HOST || '127.0.0.1',
  port: toInt(process.env.PORT, 3000, 'PORT', 1, 65535),
  nodeEnv: process.env.NODE_ENV || 'development',
  mockMode: toBool(process.env.MOCK_MODE, true, 'MOCK_MODE'),
  support: {
    name: process.env.SUPPORT_NAME || 'Customer Support',
    email: process.env.SUPPORT_EMAIL || 'support@example.com'
  },
  smtp: {
    host: process.env.SMTP_HOST || '',
    port: toInt(process.env.SMTP_PORT, 587, 'SMTP_PORT', 1, 65535),
    secure: toBool(process.env.SMTP_SECURE, false, 'SMTP_SECURE'),
    user: process.env.SMTP_USER || '',
    pass: process.env.SMTP_PASS || '',
    from: process.env.EMAIL_FROM || 'Customer Support <support@example.com>'
  },
  whatsapp: {
    graphVersion: process.env.WHATSAPP_GRAPH_VERSION || 'v24.0',
    phoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID || '',
    accessToken: process.env.WHATSAPP_ACCESS_TOKEN || ''
  }
};

export function getConfigurationStatus() {
  return {
    mockMode: config.mockMode,
    emailReady: config.mockMode || Boolean(
      config.smtp.host && config.smtp.port && config.smtp.user && config.smtp.pass && config.smtp.from
    ),
    whatsappReady: config.mockMode || Boolean(
      config.whatsapp.graphVersion && config.whatsapp.phoneNumberId && config.whatsapp.accessToken
    ),
    graphVersion: config.whatsapp.graphVersion,
    supportName: config.support.name
  };
}
