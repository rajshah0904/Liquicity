import axios, { Method, AxiosRequestConfig } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Config from 'react-native-config';

const USE_MOCKS = Config.USE_MOCKS === 'true';
const API_KEY = USE_MOCKS
  ? 'MOCK_KEY'
  : Config.BRIDGE_API_KEY || 'sk-test-b68d29ce02c83ffb0353d9dfa6f84530';
const BASE_URL = USE_MOCKS
  ? 'http://192.168.86.26:3000'
  : Config.BRIDGE_API_URL || 'https://api.sandbox.bridge.xyz/v0';

console.log('[bridgeClient] BASE_URL:', BASE_URL);
console.log('[bridgeClient] API_KEY:', API_KEY);

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Api-Key': API_KEY,
  },
});

export async function bridgeRequest<T = any>(
  method: Method,
  path: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  const headers: Record<string, string> = {
    'Api-Key': API_KEY,
    'Content-Type': 'application/json',
  };
  if (method.toUpperCase() === 'POST') {
    headers['Idempotency-Key'] = uuidv4();
  }
  const resp = await client.request<T>({
    method,
    url: path,
    data,
    headers,
    ...config,
  });
  return resp.data;
}

// convenience wrapper for TOS link
export async function requestTosLink(): Promise<string> {
  if (USE_MOCKS) {
    // Use GET for mock mode
    const response = await client.get('/customers/tos_links');
    return response.data[0]?.url;
  } else {
    // Use POST for real/sandbox mode
    const { url } = await bridgeRequest<{ url: string }>(
      'POST',
      '/customers/tos_links',
      {} // no body
    );
    return url;
  }
} 