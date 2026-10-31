const form = document.querySelector('#ticketForm');
const formMessage = document.querySelector('#formMessage');
const submitButton = document.querySelector('#submitButton');
const ticketsContainer = document.querySelector('#tickets');
const emptyTemplate = document.querySelector('#emptyTemplate');
const refreshButton = document.querySelector('#refreshButton');
const emailChannel = document.querySelector('#emailChannel');
const whatsappChannel = document.querySelector('#whatsappChannel');
const emailInput = document.querySelector('#emailInput');
const whatsappInput = document.querySelector('#whatsappInput');

function setMessage(text, type) {
  formMessage.hidden = !text;
  formMessage.textContent = text;
  formMessage.className = `form-message ${type || ''}`;
}

function syncRequiredFields() {
  emailInput.required = emailChannel.checked;
  whatsappInput.required = whatsappChannel.checked;
  emailInput.disabled = !emailChannel.checked;
  whatsappInput.disabled = !whatsappChannel.checked;
}

function makePill(text, status) {
  const span = document.createElement('span');
  span.className = `pill ${status}`;
  span.textContent = text;
  return span;
}

function renderTickets(tickets) {
  ticketsContainer.replaceChildren();
  if (!tickets.length) {
    ticketsContainer.append(emptyTemplate.content.cloneNode(true));
    return;
  }

  for (const ticket of tickets) {
    const row = document.createElement('article');
    row.className = 'ticket';

    const main = document.createElement('div');
    main.className = 'ticket-main';
    const title = document.createElement('strong');
    title.textContent = ticket.subject;
    const sub = document.createElement('span');
    sub.textContent = `${ticket.id} · ${ticket.customerName}`;
    main.append(title, sub);

    const meta = document.createElement('div');
    meta.className = 'ticket-meta';
    const created = new Date(ticket.createdAt).toLocaleString();
    const priority = document.createElement('span');
    priority.textContent = `Priority: ${ticket.priority}`;
    const timestamp = document.createElement('span');
    timestamp.textContent = created;
    const status = makePill(ticket.status, ticket.status);
    meta.append(priority, timestamp, status);

    const deliveries = document.createElement('div');
    deliveries.className = 'ticket-deliveries';
    for (const item of ticket.deliveries || []) {
      deliveries.append(makePill(`${item.channel}: ${item.status}`, item.status));
    }
    if (!(ticket.deliveries || []).length) {
      deliveries.append(makePill('No delivery', 'failed'));
    }

    row.append(main, meta, deliveries);
    ticketsContainer.append(row);
  }
}

async function loadConfig() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) throw new Error('Could not load configuration.');
    const config = await response.json();
    const modeBadge = document.querySelector('#modeBadge');
    modeBadge.textContent = config.mockMode ? 'MOCK MODE · SAFE TESTING' : 'LIVE MODE';

    const emailStatus = document.querySelector('#emailStatus');
    emailStatus.textContent = config.emailReady ? 'Ready' : 'Not configured';
    emailStatus.className = config.emailReady ? 'ready' : 'not-ready';

    const waStatus = document.querySelector('#waStatus');
    waStatus.textContent = config.whatsappReady ? 'Ready' : 'Not configured';
    waStatus.className = config.whatsappReady ? 'ready' : 'not-ready';
    document.querySelector('#graphVersion').textContent = config.graphVersion;
  } catch {
    document.querySelector('#modeBadge').textContent = 'Configuration unavailable';
    document.querySelector('#emailStatus').textContent = 'Unavailable';
    document.querySelector('#waStatus').textContent = 'Unavailable';
  }
}

async function loadTickets() {
  refreshButton.disabled = true;
  ticketsContainer.setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/api/tickets?limit=20');
    if (!response.ok) throw new Error('Could not load tickets.');
    const data = await response.json();
    renderTickets(data.tickets || []);
  } catch (error) {
    ticketsContainer.textContent = error.message;
  } finally {
    refreshButton.disabled = false;
    ticketsContainer.setAttribute('aria-busy', 'false');
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setMessage('', '');
  const formData = new FormData(form);
  const channels = formData.getAll('channels');
  if (!channels.length) {
    setMessage('Select at least one alert channel.', 'error');
    return;
  }

  const payload = {
    customerName: formData.get('customerName'),
    priority: formData.get('priority'),
    subject: formData.get('subject'),
    message: formData.get('message'),
    email: formData.get('email') || '',
    whatsapp: formData.get('whatsapp') || '',
    channels
  };

  submitButton.disabled = true;
  submitButton.textContent = 'Processing…';
  try {
    const response = await fetch('/api/tickets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok && response.status !== 207) {
      const details = Array.isArray(data.details) ? ` ${data.details.join(' ')}` : '';
      throw new Error(`${data.error || 'Request failed.'}${details}`);
    }

    const failures = (data.ticket?.deliveries || []).filter((item) => item.status === 'failed');
    if (failures.length) {
      setMessage(`Ticket ${data.ticket.id} was created, but ${failures.length} delivery attempt(s) failed. Check your provider configuration.`, 'error');
    } else {
      setMessage(`Ticket ${data.ticket.id} was created and all selected alerts were processed.`, 'success');
      form.reset();
      emailChannel.checked = true;
      whatsappChannel.checked = true;
      syncRequiredFields();
    }
    await loadTickets();
  } catch (error) {
    setMessage(error.message, 'error');
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Create ticket & send alerts';
  }
});

emailChannel.addEventListener('change', syncRequiredFields);
whatsappChannel.addEventListener('change', syncRequiredFields);
refreshButton.addEventListener('click', loadTickets);

syncRequiredFields();
loadConfig();
loadTickets();
