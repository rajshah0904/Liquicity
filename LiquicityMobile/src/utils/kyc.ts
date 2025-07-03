import { backendRequest, API_ENDPOINTS } from './api';

// Fetch KYC status for a user from your backend
export async function fetchKycStatus(userId: string | number): Promise<string> {
  try {
    const response = await backendRequest('GET', `${API_ENDPOINTS.KYC_STATUS}/${userId}`);
    return response.status || 'pending';
  } catch (e) {
    console.error('Error fetching KYC status:', e);
    // Default to 'pending' if error
    return 'pending';
  }
}

// Create KYC link for user
export async function createKycLink(userData: any): Promise<string> {
  try {
    const response = await backendRequest('POST', API_ENDPOINTS.KYC_LINK, userData);
    return response.url || '';
  } catch (e) {
    console.error('Error creating KYC link:', e);
    throw e;
  }
} 