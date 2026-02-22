const { execFile } = require('child_process');

const SCRIPT = '/home/odominguez7/okr-bot/append_kr_update.py';

function parseFormatB(text) {
  // Accept either with or without leading 'OKR'
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const startIdx = (lines[0] || '').toUpperCase() === 'OKR' ? 1 : 0;
  const rest = lines.slice(startIdx);

  const out = { objective: '', kr: '', update: '' };
  for (const l of rest) {
    const m = l.match(/^(Objective|KR|Update)\s*:\s*(.*)$/i);
    if (!m) continue;
    const key = m[1].toLowerCase();
    const val = m[2].trim();
    if (key === 'objective') out.objective = val;
    if (key === 'kr') out.kr = val;
    if (key === 'update') out.update = val;
  }
  if (!out.objective || !out.kr || !out.update) {
    throw new Error('Missing required fields. Use:\nOKR\nObjective: ...\nKR: ...\nUpdate: ...');
  }
  return out;
}

function appendToSheet({ objective, kr, update }) {
  return new Promise((resolve, reject) => {
    const args = ['--objective', objective, '--kr', kr, '--progress', update];
    execFile('python3', [SCRIPT, ...args], { timeout: 60_000 }, (err, stdout, stderr) => {
      if (err) {
        const msg = (stderr || stdout || err.message || String(err)).toString();
        return reject(new Error(msg));
      }
      resolve({ stdout: String(stdout || ''), stderr: String(stderr || '') });
    });
  });
}

async function main() {
  const input = await new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (c) => (data += c));
    process.stdin.on('end', () => resolve(data));
  });

  const payload = parseFormatB(input);
  await appendToSheet(payload);

  // Keep output short; caller can send this back to WhatsApp
  process.stdout.write(`Logged OKR update:\nObjective: ${payload.objective}\nKR: ${payload.kr}`);
}

main().catch((e) => {
  process.stderr.write(String(e.message || e));
  process.exit(2);
});
