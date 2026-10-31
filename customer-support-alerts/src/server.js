import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express from 'express';
import helmet from 'helmet';
import { rateLimit } from 'express-rate-limit';
import { config, getConfigurationStatus } from './config.js';
import { createTicket, listNotifications, listTickets, updateTicketStatus } from './services/ticketService.js';
import { validateStatus, validateTicketPayload } from './utils/validation.js';

const app = express();
const currentDir = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(currentDir, '../public');

app.disable('x-powered-by');
app.use(helmet());
app.use(express.json({ limit: '64kb' }));
app.use(express.urlencoded({ extended: false, limit: '64kb' }));
app.use('/api', rateLimit({
  windowMs: 60_000,
  limit: 120,
  standardHeaders: 'draft-8',
  legacyHeaders: false
}));

app.get('/api/health', (req, res) => {
  res.json({
    ok: true,
    service: 'customer-support-alerts',
    timestamp: new Date().toISOString()
  });
});

app.get('/api/config', (req, res) => {
  res.json(getConfigurationStatus());
});

app.get('/api/tickets', async (req, res, next) => {
  try {
    const requested = Number.parseInt(req.query.limit, 10);
    const limit = Number.isFinite(requested) ? Math.min(Math.max(requested, 1), 100) : 25;
    res.json({ tickets: await listTickets(limit) });
  } catch (error) {
    next(error);
  }
});

app.get('/api/notifications', async (req, res, next) => {
  try {
    const requested = Number.parseInt(req.query.limit, 10);
    const limit = Number.isFinite(requested) ? Math.min(Math.max(requested, 1), 100) : 50;
    res.json({ notifications: await listNotifications(limit) });
  } catch (error) {
    next(error);
  }
});

app.post('/api/tickets', async (req, res, next) => {
  try {
    const validation = validateTicketPayload(req.body);
    if (!validation.valid) {
      return res.status(400).json({ error: 'Validation failed.', details: validation.errors });
    }

    const ticket = await createTicket(validation.value);
    const hasFailure = ticket.deliveries.some((item) => item.status === 'failed');
    return res.status(hasFailure ? 207 : 201).json({
      message: hasFailure
        ? 'Ticket created, but one or more alert deliveries failed.'
        : 'Ticket created and alerts processed successfully.',
      ticket
    });
  } catch (error) {
    next(error);
  }
});

app.patch('/api/tickets/:ticketId/status', async (req, res, next) => {
  try {
    const validation = validateStatus(req.body.status);
    if (!validation.valid) {
      return res.status(400).json({ error: 'Status must be open, in-progress, or closed.' });
    }
    const ticket = await updateTicketStatus(req.params.ticketId, validation.value);
    if (!ticket) return res.status(404).json({ error: 'Ticket not found.' });
    return res.json({ message: 'Ticket status updated.', ticket });
  } catch (error) {
    next(error);
  }
});

app.use(express.static(publicDir, { extensions: ['html'] }));

app.use((req, res) => {
  if (req.path.startsWith('/api/')) {
    return res.status(404).json({ error: 'API route not found.' });
  }
  return res.sendFile(path.join(publicDir, 'index.html'));
});

app.use((error, req, res, next) => {
  console.error(`[${new Date().toISOString()}]`, error);
  if (res.headersSent) return next(error);
  return res.status(500).json({ error: 'Unexpected server error.' });
});

const server = app.listen(config.port, () => {
  const mode = config.mockMode ? 'MOCK' : 'LIVE';
  console.log(`\nCustomer Support Alerts is running in ${mode} mode.`);
  console.log(`Open http://localhost:${config.port}`);
  console.log(`Health check: http://localhost:${config.port}/api/health\n`);
});

function shutdown(signal) {
  console.log(`\nReceived ${signal}. Shutting down...`);
  server.close(() => process.exit(0));
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
