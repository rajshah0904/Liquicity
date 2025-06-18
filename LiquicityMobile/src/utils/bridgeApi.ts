import axios, { AxiosRequestConfig, Method } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import Config from 'react-native-config';

const API_KEY = Config.BRIDGE_API_KEY || '';
const BASE_URL = Config.BRIDGE_API_URL || 'https://api.sandbox.bridge.xyz/v0';

const bridgeApi = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Api-Key': API_KEY,
    'Content-Type': 'application/json',
  },
});

// Helper to make requests with idempotency for POST
export async function bridgeRequest<T = any>(
  method: Method,
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> {
  const headers: Record<string, string> = {
    'Api-Key': API_KEY,
    'Content-Type': 'application/json',
  };
  // Only add Idempotency-Key for POST
  if (method.toUpperCase() === 'POST') {
    headers['Idempotency-Key'] = uuidv4();
  }
  const response = await bridgeApi.request<T>({
    method,
    url,
    data,
    headers,
    ...config,
  });
  return response.data;
}

// Usage example:
// await bridgeRequest('POST', '/customers', { ...customerData }); 

export async function requestTosLink(): Promise<string> {
  try {
    const response = await bridgeApi.post('/customers/tos_links', {}, {
      headers: {
        'Api-Key': API_KEY,
        'Content-Type': 'application/json',
        'Idempotency-Key': uuidv4(),
      },
    });
    return response.data.url;
  } catch (e) {
    const err = e as any;
    console.error('requestTosLink error:', err, err.response, err.request, err.config);
    throw err;
  }
} 