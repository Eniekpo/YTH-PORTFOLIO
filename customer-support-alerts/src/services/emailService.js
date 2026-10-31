import nodemailer from 'nodemailer';
import { config } from '../config.js';
import { escapeHtml } from '../utils/html.js';

let transporter;

function getTransporter() {
  if (!transporter) {
    transporter = nodemailer.createTransport({
      host: config.smtp.host,
      port: config.smtp.port,
      secure: config.smtp.secure,
      auth: {
        user: config.smtp.user,
        pass: config.smtp.pass
      }
    });
  }
  return transporter;
}

export async function sendEmailAlert({ to, ticket }) {
  if (config.mockMode) {
    await new Promise((resolve) => setTimeout(resolve, 250));
    return {
      provider: 'mock-email',
      messageId: `mock-email-${ticket.id}-${Date.now()}`
    };
  }

  if (!config.smtp.host || !config.smtp.user || !config.smtp.pass || !config.smtp.from) {
    throw new Error('Email is not configured. Check SMTP settings in .env.');
  }

  const priority = ticket.priority.toUpperCase();
  const safeName = escapeHtml(ticket.customerName);
  const safeSubject = escapeHtml(ticket.subject);
  const safeMessage = escapeHtml(ticket.message).replaceAll('\n', '<br>');
  const safeTicketId = escapeHtml(ticket.id);

  const info = await getTransporter().sendMail({
    from: config.smtp.from,
    to,
    replyTo: config.support.email,
    subject: `[${priority}] ${ticket.subject} (${ticket.id})`,
    text: [
      `Hello ${ticket.customerName},`,
      '',
      ticket.message,
      '',
      `Ticket: ${ticket.id}`,
      `Priority: ${priority}`,
      '',
      `${config.support.name}`
    ].join('\n'),
    html: `
      <div style="font-family:Arial,sans-serif;max-width:640px;margin:auto;color:#172033;line-height:1.55">
        <h2 style="margin-bottom:4px">${safeSubject}</h2>
        <p style="margin-top:0;color:#667085">Ticket ${safeTicketId} · Priority ${priority}</p>
        <p>Hello ${safeName},</p>
        <p>${safeMessage}</p>
        <hr style="border:none;border-top:1px solid #e4e7ec;margin:24px 0">
        <p style="font-size:13px;color:#667085">Sent by ${escapeHtml(config.support.name)}</p>
      </div>
    `
  });

  return {
    provider: 'smtp',
    messageId: info.messageId
  };
}
