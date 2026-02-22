const fs = require('fs');
const path = require('path');
const express = require('express');
const open = require('open');
const { google } = require('googleapis');

const CLIENT_PATH = process.env.GDOCS_OAUTH_CLIENT || path.join(__dirname, '..', 'tmp', 'gdocs_oauth_client.json');
const TOKEN_PATH  = process.env.GDOCS_OAUTH_TOKEN  || path.join(__dirname, '..', 'tmp', 'gdocs_oauth_token.json');
const PORT = parseInt(process.env.GDOCS_OAUTH_PORT || '8766', 10);

const SCOPES = [
  'https://www.googleapis.com/auth/documents',
  'https://www.googleapis.com/auth/drive',
];

function loadClient() {
  const raw = fs.readFileSync(CLIENT_PATH, 'utf8');
  const creds = JSON.parse(raw);
  const cfg = creds.installed || creds.web;
  if (!cfg) throw new Error('OAuth client JSON must contain installed or web');
  return cfg;
}

async function main() {
  const cfg = loadClient();

  const redirectUri = `http://localhost:${PORT}/oauth2callback`;
  const oAuth2Client = new google.auth.OAuth2(cfg.client_id, cfg.client_secret, redirectUri);

  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent',
  });

  console.log('AUTH_URL:', authUrl);

  const app = express();
  app.get('/', (_req, res) => {
    res.type('text/plain').send('OAuth server running. Visit /oauth2callback after consent.');
  });

  const server = app.listen(PORT, () => {
    console.log(`Listening on http://localhost:${PORT}`);
  });

  app.get('/oauth2callback', async (req, res) => {
    try {
      const code = req.query.code;
      if (!code) throw new Error('Missing code');
      const { tokens } = await oAuth2Client.getToken(code);
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens, null, 2));
      res.type('text/plain').send('OAuth success. You can close this tab.');
      console.log('SAVED_TOKEN:', TOKEN_PATH);
      server.close(() => process.exit(0));
    } catch (err) {
      console.error('OAUTH_ERROR:', err);
      res.status(500).type('text/plain').send(String(err));
      server.close(() => process.exit(1));
    }
  });

  try {
    await open(authUrl, { wait: false });
  } catch {}
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
