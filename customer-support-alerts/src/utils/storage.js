import fs from 'node:fs/promises';
import { constants } from 'node:fs';
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
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (error) {
    const { mtimeMs } = await fs.stat(dbPath);
    const backupPath = `${dbPath}.corrupt-${Math.floor(mtimeMs)}`;
    try {
      await fs.copyFile(dbPath, backupPath, constants.COPYFILE_EXCL);
    } catch (backupError) {
      if (backupError.code !== 'EEXIST') throw backupError;
    }
    throw new Error(`Database JSON is invalid; the original was preserved and backed up to ${backupPath}.`, {
      cause: error
    });
  }

  if (
    !parsed
    || typeof parsed !== 'object'
    || !Array.isArray(parsed.tickets)
    || !Array.isArray(parsed.notifications)
  ) {
    throw new Error('Database structure is invalid; expected tickets and notifications arrays.');
  }

  return { tickets: parsed.tickets, notifications: parsed.notifications };
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
