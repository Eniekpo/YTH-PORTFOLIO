import { config } from '../config.js';

export async function sendWhatsAppAlert({ to, ticket }) {
  if (config.mockMode) {
    await new Promise((resolve) => setTimeout(resolve, 250));
    return {
      provider: 'mock-whatsapp',
      messageId: `mock-wa-${ticket.id}-${Date.now()}`
    };
  }

  const { graphVersion, phoneNumberId, accessToken } = config.whatsapp;
  if (!graphVersion || !phoneNumberId || !accessToken) {
    throw new Error('WhatsApp is not configured. Check Meta Cloud API settings in .env.');
  }

  const body = [
    `*${ticket.subject}*`,
    `Ticket: ${ticket.id}`,
    `Priority: ${ticket.priority.toUpperCase()}`,
    '',
    ticket.message,
    '',
    `- ${config.support.name}`
  ].join('\n');

  const response = await fetch(
    `https://graph.facebook.com/${graphVersion}/${phoneNumberId}/messages`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messaging_product: 'whatsapp',
        recipient_type: 'individual',
        to,
        type: 'text',
        text: {
          preview_url: false,
          body
        }
      }),
      signal: AbortSignal.timeout(15000)
    }
  );

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data?.error?.message || `WhatsApp API returned HTTP ${response.status}.`;
    throw new Error(detail);
  }

  return {
    provider: 'meta-whatsapp-cloud-api',
    messageId: data?.messages?.[0]?.id || null
  };
}
