import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const dataDir = path.resolve(currentDir, '../../data');
const dbPath = path.join(dataDir, 'db.json');
const initialDb = { tickets: [], notifications: [] };
let mutationQueue = Promise.resolve();

async function ensureDatabase() {
  await fs.mkdir(dataDir, { recursive: true });
  try {
    await fs.access(dbPath);
  } catch {
    await fs.writeFile(dbPath, JSON.stringify(initialDb, null, 2), 'utf8');
  }
}

async function readDb() {
  await ensureDatabase();
  const raw = await fs.readFile(dbPath, 'utf8');
  try {
    const parsed = JSON.parse(raw);
    return {
      tickets: Array.isArray(parsed.tickets) ? parsed.tickets : [],
      notifications: Array.isArray(parsed.notifications) ? parsed.notifications : []
    };
  } catch {
    const backupPath = `${dbPath}.corrupt-${Date.now()}`;
    await fs.copyFile(dbPath, backupPath);
    await fs.writeFile(dbPath, JSON.stringify(initialDb, null, 2), 'utf8');
    return structuredClone(initialDb);
  }
}

async function writeDb(db) {
  const tempPath = `${dbPath}.tmp`;
  await fs.writeFile(tempPath, JSON.stringify(db, null, 2), 'utf8');
  await fs.rename(tempPath, dbPath);
}

export async function queryDb(selector) {
  const db = await readDb();
  return selector(structuredClone(db));
}

export function mutateDb(mutator) {
  const operation = mutationQueue.then(async () => {
    const db = await readDb();
    const result = await mutator(db);
    await writeDb(db);
    return structuredClone(result);
  });

  mutationQueue = operation.catch(() => undefined);
  return operation;
}
