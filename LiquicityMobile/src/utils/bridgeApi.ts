import axios, { AxiosRequestConfig, Method } from 'axios';
import { v4 as uuidv4 } from 'uuid';

const API_KEY = process.env.BRIDGE_API_KEY || '<your-bridge-api-key-here>';
const BASE_URL = 'https://api.bridge.xyz/v0';

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