# Automating Customer Support: Node.js WhatsApp and Email Alerts

A small, production-minded local Node.js application for creating customer-support tickets and automatically sending selected alerts through **email (SMTP)** and **WhatsApp (Meta WhatsApp Cloud API)**.

The app starts in **mock mode** by default, so you can run and test the complete workflow without external credentials. When you are ready, add your SMTP and Meta credentials to `.env` and set `MOCK_MODE=false`.

## What is included

- Responsive browser dashboard
- Ticket creation workflow
- Email alerts using Nodemailer/SMTP
- WhatsApp text alerts using Meta's official Cloud API `/messages` endpoint
- Email-only, WhatsApp-only, or dual-channel delivery
- Local JSON persistence for tickets and delivery history
- Per-channel success/failure records
- Health and configuration-status endpoints
- Request validation, rate limiting, Helmet security headers, and request-size limits
- Mock mode for safe local testing
- Windows and macOS/Linux start scripts
- Basic automated tests using Node's built-in test runner

## Requirements

- Node.js **20 or newer**
- npm (bundled with Node.js)
- For live email: an SMTP account/provider
- For live WhatsApp: a Meta Business/WhatsApp Business Platform setup, a phone-number ID, and an access token

## Fastest local start

### Windows

1. Unzip the project.
2. Double-click `start.bat`, or run it from Command Prompt.
3. Open `http://localhost:3000`.

### macOS / Linux

From the unzipped folder:

```bash
./start.sh
```

Then open `http://localhost:3000`.

The start scripts create `.env` from `.env.example` if needed and install dependencies on the first run. The default `MOCK_MODE=true` means no real messages are sent.
The server binds to `127.0.0.1` by default so the local-only dashboard is not exposed to other devices on your network. Set `HOST` explicitly only when you intend to make it reachable elsewhere; the app does not include user authentication.

## Manual start

```bash
cp .env.example .env
npm install
npm start
```

On Windows Command Prompt, use `copy .env.example .env` instead of `cp`.

## Enable live email

Edit `.env`:

```env
HOST=127.0.0.1
PORT=3000
MOCK_MODE=false
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your_username
SMTP_PASS=your_password_or_app_password
EMAIL_FROM="Customer Support <support@example.com>"
SUPPORT_EMAIL=support@example.com
```

For port 465, providers normally require `SMTP_SECURE=true`. For port 587, `SMTP_SECURE=false` normally allows STARTTLS when supported.

If you use Gmail, use the current Google-supported authentication method for your account (for many accounts that means an app password rather than your normal password).

## Enable live WhatsApp

Create/configure a WhatsApp Business Platform app in Meta, then add these values to `.env`:

```env
MOCK_MODE=false
WHATSAPP_GRAPH_VERSION=v24.0
WHATSAPP_PHONE_NUMBER_ID=YOUR_PHONE_NUMBER_ID
WHATSAPP_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
```

The Graph API version is deliberately configurable. Use the version currently supported by your Meta app instead of assuming the example value will remain current forever.

The app sends text messages to:

```text
POST https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages
```

with the bearer access token in the Authorization header.

### Important WhatsApp rule

A free-form text message is subject to WhatsApp Business Platform messaging rules. In particular, outside the permitted customer-service conversation window you may need an approved template or another currently permitted message type. This sample intentionally keeps the core implementation transparent and uses the official Cloud API rather than an unofficial WhatsApp Web automation library.

## API

### Health

```http
GET /api/health
```

### Configuration readiness

```http
GET /api/config
```

Secrets are never returned.

### List tickets

```http
GET /api/tickets?limit=25
```

### Create a ticket and dispatch alerts

```http
POST /api/tickets
Content-Type: application/json
```

Example:

```json
{
  "customerName": "Amina Yusuf",
  "subject": "Order delivery update",
  "message": "Your delivery has been rescheduled for tomorrow morning.",
  "priority": "high",
  "email": "amina@example.com",
  "whatsapp": "2348012345678",
  "channels": ["email", "whatsapp"]
}
```

Phone numbers are normalized and sent to Meta without a leading `+`.

### Update ticket status

```http
PATCH /api/tickets/TKT-.../status
Content-Type: application/json
```

```json
{ "status": "closed" }
```

Allowed values: `open`, `in-progress`, `closed`.

### List delivery records

```http
GET /api/notifications?limit=50
```

## Project structure

```text
customer-support-alerts/
├── data/
│   └── db.json
├── public/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── src/
│   ├── services/
│   │   ├── emailService.js
│   │   ├── notificationService.js
│   │   ├── ticketService.js
│   │   └── whatsappService.js
│   ├── utils/
│   │   ├── html.js
│   │   ├── storage.js
│   │   └── validation.js
│   ├── config.js
│   └── server.js
├── test/
│   └── validation.test.js
├── .env.example
├── .gitignore
├── package.json
├── README.md
├── start.bat
└── start.sh
```

## Run tests

```bash
npm test
```

## Security notes before public deployment

This package is designed to be easy to run locally. Before exposing it publicly, add authentication/authorization, HTTPS, CSRF protection where applicable, provider-specific credential management, audit retention rules, database-backed persistence, monitoring, and a production-grade queue/retry policy. Do not commit `.env` or API credentials to source control.

## Troubleshooting

**The app loads but no real messages are sent**  
Check that `MOCK_MODE=false` and that the relevant provider fields in `.env` are complete. Restart the Node.js process after changing `.env`.

**Email fails**  
Confirm SMTP host/port, authentication method, TLS requirements, and sender permissions with your email provider.

**WhatsApp returns an authorization error**  
Confirm the access token, phone-number ID, app/business permissions, recipient eligibility, and the Graph API version configured for your Meta app.

**Port 3000 is already used**  
Change `PORT=3000` in `.env`, for example to `PORT=8080`, then restart.

## Data location

Tickets and notification records are stored in `data/db.json`. This is intentionally simple for a local demo/learning app. Use a real database such as PostgreSQL for multi-user or production workloads.

If `data/db.json` contains invalid JSON, the app preserves the original and writes a timestamped `.corrupt-*` copy, then reports a database error rather than silently replacing potentially recoverable data with an empty database.
