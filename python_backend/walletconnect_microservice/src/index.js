import cors from 'cors';
import { webcrypto } from 'crypto';
import dotenv from 'dotenv';
import express from 'express';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';

dotenv.config();

// Ensure WebCrypto API for WalletConnect utils in Node
if (!globalThis.crypto || !globalThis.crypto.getRandomValues) {
  globalThis.crypto = webcrypto;
}

const app = express();
app.use(helmet());
app.use(cors());
app.use(express.json());
app.set('trust proxy', 1);
app.use(
  rateLimit({
    windowMs: 60 * 1000,
    max: 120,
  standardHeaders: true,
  legacyHeaders: false,
  })
);

const PORT = process.env.WC_MS_PORT ? Number(process.env.WC_MS_PORT) : 3002;
const PROJECT_ID = process.env.WALLETCONNECT_PROJECT_ID;

if (!PROJECT_ID) {
  console.error('WALLETCONNECT_PROJECT_ID is required');
  process.exit(1);
}

const METADATA = {
  name: process.env.APP_NAME || 'Liquicity Backend',
  description: process.env.APP_DESCRIPTION || 'WalletConnect microservice for Liquicity',
  url: process.env.APP_URL || 'http://localhost',
  icons: [process.env.APP_ICON || 'https://walletconnect.com/walletconnect-logo.png'],
};

// Global SignClient (reuse connection)
let clientPromise;
async function resolveSignClientCtor() {
  const mod = await import('@walletconnect/sign-client');
  const candidates = [mod?.default, mod?.SignClient, mod];
  for (const c of candidates) {
    if (c && typeof c.init === 'function') return c;
  }
  console.error('SignClient module export keys:', Object.keys(mod || {}), 'default keys:', Object.keys((mod || {}).default || {}));
  throw new Error('SignClient.init not found');
}

async function getClient() {
  if (!clientPromise) {
    const Ctor = await resolveSignClientCtor();
    clientPromise = Ctor.init({ projectId: PROJECT_ID, metadata: METADATA });
  }
  return clientPromise;
}

// In-memory pairing/session status
const topicToStatus = new Map();

function parseTopicFromUri(uri) {
  // wc:{topic}@2?...
  const [scheme, rest] = uri.split(':');
  if (!rest) return null;
  const [topicWithVer] = rest.split('?');
  const [topic] = topicWithVer.split('@');
  return topic;
}

app.post('/pairing/create', async (req, res) => {
  try {
    const client = await getClient();

    // default EVM mainnet permissions if not provided
    const requiredNamespaces = req.body?.requiredNamespaces || {
      eip155: {
        methods: ['eth_sendTransaction', 'personal_sign', 'eth_signTypedData'],
        chains: ['eip155:1'],
        events: ['accountsChanged', 'chainChanged'],
      },
    };

    const { uri, approval } = await client.connect({ requiredNamespaces });

    if (!uri) {
      return res.status(500).json({ success: false, error: { message: 'Failed to create pairing URI' } });
    }

    const topic = parseTopicFromUri(uri);
    topicToStatus.set(topic, { status: 'pending', uri, accounts: [], chains: [] });

    // Attach approval resolution (non-blocking)
    (async () => {
      try {
        const session = await approval();
        const accounts = session?.namespaces?.eip155?.accounts || [];
        const chains = session?.namespaces?.eip155?.chains || [];
        topicToStatus.set(topic, { status: 'approved', uri, accounts, chains });
      } catch (err) {
        topicToStatus.set(topic, { status: 'rejected', uri, accounts: [], chains: [] });
      }
    })();

    return res.json({ success: true, data: { topic, uri } });
  } catch (e) {
    console.error('pairing/create error', e);
    return res.status(500).json({ success: false, error: { message: String(e?.message || e) } });
  }
});

app.get('/pairing/status/:topic', async (req, res) => {
  const { topic } = req.params;
  const entry = topicToStatus.get(topic);
  if (!entry) return res.status(404).json({ success: false, error: { message: 'Not found' } });
  return res.json({ success: true, data: entry });
});

app.delete('/pairing/:topic', async (req, res) => {
  try {
    const client = await getClient();
    const { topic } = req.params;
    // Try to delete pairing if exists
    try {
      const pairing = client.core.pairing.pairings.get(topic);
      if (pairing) await client.core.pairing.disconnect({ topic });
    } catch (_) {}
    topicToStatus.delete(topic);
    return res.json({ success: true });
  } catch (e) {
    return res.status(500).json({ success: false, error: { message: String(e?.message || e) } });
  }
});

app.listen(PORT, () => {
  console.log(`WalletConnect microservice running on http://127.0.0.1:${PORT}`);
});