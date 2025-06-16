import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Config from 'react-native-config';

const USE_MOCKS = Config.USE_MOCKS === 'true';
const BASE_URL = USE_MOCKS
  ? 'http://192.168.86.26:3000'
  : process.env.BRIDGE_API_URL || 'https://sandbox-api.bridge.xyz/v0';
const API_KEY = USE_MOCKS
  ? 'MOCK_KEY'
  : process.env.BRIDGE_API_KEY || '';

// NOTE: When USE_MOCKS is true, make sure your mock server is running at http://localhost:3000
// and accessible from your simulator/device. You may need to use your machine's IP address instead of localhost for iOS/Android simulators.

export const bridge = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Api-Key': API_KEY,
    'Content-Type': 'application/json',
    'Idempotency-Key': uuidv4(),
  },
});

// Helper for POST requests with idempotency
export async function postWithIdempotency(url: string, data: any, config = {}) {
  try {
    return await bridge.post(url, data, {
      ...config,
      headers: {
        'Api-Key': API_KEY,
        'Content-Type': 'application/json',
        'Idempotency-Key': uuidv4(),
      },
    });
  } catch (e) {
    const err = e as any;
    console.error('postWithIdempotency error:', err, err.response, err.request, err.config);
    throw err;
  }
}

// Request a TOS link for the customer
export async function requestTosLink(): Promise<string> {
  try {
    if (USE_MOCKS) {
      // Use GET for mock mode
      const response = await bridge.get('/tos_links', {
        headers: {
          'Api-Key': API_KEY,
          'Content-Type': 'application/json',
        },
      });
      // Return the first url in the array
      return response.data[0]?.url;
    } else {
      // Use POST for real/sandbox mode
      const response = await bridge.post('/tos_links', {}, {
        headers: {
          'Api-Key': API_KEY,
          'Content-Type': 'application/json',
          'Idempotency-Key': uuidv4(),
        },
      });
      return response.data.url;
    }
  } catch (e) {
    const err = e as any;
    console.error('requestTosLink error:', err, err.response, err.request, err.config);
    throw err;
  }
} 