'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../assets/js/ta-progress-auto.js'), 'utf8');

function launch({ initial = {}, records = {} } = {}) {
  const values = new Map(Object.entries(initial));
  const writes = new Map();
  const callbacks = new Map();
  let reloads = 0;
  class Storage {
    getItem(key) { return values.has(key) ? values.get(key) : null; }
    setItem(key, value) { values.set(key, String(value)); }
    removeItem(key) { values.delete(key); }
    key(index) { return [...values.keys()][index] ?? null; }
    get length() { return values.size; }
  }
  const storage = new Storage();
  const cloud = {
    ready: true,
    user: async () => ({ id: 'student-1' }),
    save: async (key, payload) => { writes.set(key, payload); return true; },
    load: async key => records[key] ?? null,
    loadMany: async keys => new Map(keys.filter(k => Object.hasOwn(records, k)).map(k => [k, records[k]])),
    client: {
      from: () => ({
        select: () => ({
          eq: () => ({
            like: () => ({
              limit: async () => ({ data: [], error: null })
            })
          })
        })
      })
    }
  };
  const document = {
    readyState: 'loading',
    addEventListener: (name, fn) => callbacks.set(name, fn),
    querySelector: () => null,
    querySelectorAll: () => []
  };
  const location = {
    pathname: '/turkce-akademi/kitaplar/example/lesson.html',
    search: '',
    reload: () => { reloads++; }
  };
  const window = {
    TA_SUPABASE_URL: 'test',
    TA_SUPABASE_ANON_KEY: 'test',
    TAStudentCloud: cloud
  };
  const context = { window, document, location, Storage, localStorage: storage,
    setTimeout: (fn, delay) => setTimeout(fn, delay === 700 ? 0 : delay),
    clearTimeout, console, Map, Set, Object, Array, JSON, String };
  vm.runInNewContext(source, context, { filename: 'ta-progress-auto.js' });
  return {
    window, storage, values, writes, callbacks,
    get reloads() { return reloads; },
    async init() { callbacks.get('DOMContentLoaded')(); await new Promise(resolve => setTimeout(resolve, 35)); },
    async settle() { await new Promise(resolve => setTimeout(resolve, 35)); }
  };
}

test('assessment scores use canonical cloud key and raw JSON payload', async () => {
  const a = launch({ initial: { 'ta-activities-A1-1': JSON.stringify({ reading: { earned: 40, possible: 40 } }) } });
  a.storage.getItem('ta-activities-A1-1');
  await a.init();
  assert.deepEqual(a.writes.get('ta-activities-A1-1'), { reading: { earned: 40, possible: 40 } });
  assert.equal([...a.writes.keys()].filter(k => k.includes('ta-activities')).length, 1);
});

test('assessment scores hydrate from canonical cloud key', async () => {
  const answer = { reading: { earned: 32, possible: 40 } };
  const a = launch({ records: { 'ta-activities-A1-1': answer } });
  a.storage.getItem('ta-activities-A1-1');
  await a.init();
  assert.equal(a.storage.getItem('ta-activities-A1-1'), JSON.stringify(answer));
  assert.equal(a.reloads, 1);
});

test('updates to canonical scores retain JSON rather than value wrapper', async () => {
  const a = launch();
  a.storage.getItem('ta-activities-A1-1');
  await a.init();
  const results = { listening: { earned: 27, possible: 30 } };
  a.storage.setItem('ta-activities-A1-1', JSON.stringify(results));
  await a.settle();
  assert.deepEqual(a.writes.get('ta-activities-A1-1'), results);
});

test('ordinary page progress remains namespaced', async () => {
  const a = launch({ initial: { 'ta-example-position': '7' } });
  a.storage.getItem('ta-example-position');
  await a.init();
  const keys = [...a.writes.keys()].filter(k => k.includes('example-position'));
  assert.equal(keys.length, 1);
  assert.match(keys[0], /^ta-auto-[a-z0-9]+-ta-example-position$/);
  assert.deepEqual(a.writes.get(keys[0]), { value: '7' });
});
