import 'dotenv/config';

const toBool = (value, fallback = false) => {
  if (value === undefined) return fallback;
  return String(value).toLowerCase() === 'true';
};

const toInt = (value, fallback) => {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export const config = {
  port: toInt(process.env.PORT, 3000),
  nodeEnv: process.env.NODE_ENV || 'development',
  mockMode: toBool(process.env.MOCK_MODE, true),
  support: {
    name: process.env.SUPPORT_NAME || 'Customer Support',
    email: process.env.SUPPORT_EMAIL || 'support@example.com'
  },
  smtp: {
    host: process.env.SMTP_HOST || '',
    port: toInt(process.env.SMTP_PORT, 587),
    secure: toBool(process.env.SMTP_SECURE, false),
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
