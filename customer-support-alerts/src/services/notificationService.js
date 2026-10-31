import { sendEmailAlert } from './emailService.js';
import { sendWhatsAppAlert } from './whatsappService.js';
import { mutateDb } from '../utils/storage.js';

async function recordNotification(notification) {
  return mutateDb((db) => {
    db.notifications.unshift(notification);
    db.notifications = db.notifications.slice(0, 500);
    return notification;
  });
}

async function deliver(channel, recipient, ticket) {
  const startedAt = new Date().toISOString();
  try {
    const response = channel === 'email'
      ? await sendEmailAlert({ to: recipient, ticket })
      : await sendWhatsAppAlert({ to: recipient, ticket });

    const record = {
      id: `NTF-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
      ticketId: ticket.id,
      channel,
      recipient,
      status: 'sent',
      provider: response.provider,
      providerMessageId: response.messageId,
      error: null,
      createdAt: startedAt,
      completedAt: new Date().toISOString()
    };
    await recordNotification(record);
    return record;
  } catch (error) {
    const record = {
      id: `NTF-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
      ticketId: ticket.id,
      channel,
      recipient,
      status: 'failed',
      provider: null,
      providerMessageId: null,
      error: error instanceof Error ? error.message : 'Unknown delivery error',
      createdAt: startedAt,
      completedAt: new Date().toISOString()
    };
    await recordNotification(record);
    return record;
  }
}

export async function sendTicketAlerts(ticket) {
  const tasks = [];
  if (ticket.channels.includes('email')) {
    tasks.push(deliver('email', ticket.email, ticket));
  }
  if (ticket.channels.includes('whatsapp')) {
    tasks.push(deliver('whatsapp', ticket.whatsapp, ticket));
  }
  return Promise.all(tasks);
}
