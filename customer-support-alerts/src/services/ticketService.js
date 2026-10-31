import { randomBytes } from 'node:crypto';
import { mutateDb, queryDb } from '../utils/storage.js';
import { sendTicketAlerts } from './notificationService.js';

function createTicketId() {
  const date = new Date().toISOString().slice(0, 10).replaceAll('-', '');
  const suffix = randomBytes(8).toString('hex').toUpperCase();
  return `TKT-${date}-${suffix}`;
}

export async function createTicket(input) {
  const now = new Date().toISOString();
  const ticket = {
    id: createTicketId(),
    ...input,
    status: 'open',
    createdAt: now,
    updatedAt: now,
    deliveries: []
  };

  await mutateDb((db) => {
    db.tickets.unshift(ticket);
    db.tickets = db.tickets.slice(0, 500);
    return ticket;
  });

  const deliveries = await sendTicketAlerts(ticket);
  const updated = await mutateDb((db) => {
    const index = db.tickets.findIndex((item) => item.id === ticket.id);
    if (index >= 0) {
      db.tickets[index].deliveries = deliveries;
      db.tickets[index].updatedAt = new Date().toISOString();
      return db.tickets[index];
    }
    return { ...ticket, deliveries };
  });

  return updated;
}

export async function listTickets(limit = 25) {
  return queryDb((db) => db.tickets.slice(0, limit));
}

export async function listNotifications(limit = 50) {
  return queryDb((db) => db.notifications.slice(0, limit));
}

export async function updateTicketStatus(ticketId, status) {
  return mutateDb((db) => {
    const ticket = db.tickets.find((item) => item.id === ticketId);
    if (!ticket) return null;
    ticket.status = status;
    ticket.updatedAt = new Date().toISOString();
    return ticket;
  });
}
