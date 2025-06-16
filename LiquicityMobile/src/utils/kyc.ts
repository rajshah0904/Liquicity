import axios from 'axios';

// Fetch KYC status for a user from the backend
export async function fetchKycStatus(userId: string | number): Promise<string> {
  try {
    const res = await axios.get(`/user/kyc/${userId}/status`);
    return res.data.status;
  } catch (e) {
    // Default to 'pending' if error
    return 'pending';
  }
} 