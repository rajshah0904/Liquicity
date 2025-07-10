import React, { useEffect, useState } from 'react';
import { View, Text, Button, ActivityIndicator, Alert } from 'react-native';
import { useAuth0 } from 'react-native-auth0';

const POLL_INTERVAL = 10000; // 10 seconds

const KYCStatusScreen = ({ navigation }: any) => {
  const { getCredentials } = useAuth0();
  const [status, setStatus] = useState<string | null>(null);
  const [rejectionReasons, setRejectionReasons] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const credentials = await getCredentials();
      if (!credentials || !credentials.accessToken) {
        Alert.alert('Error', 'No access token found.');
        setLoading(false);
        return;
      }
      const res = await fetch('http://192.168.86.26:8000/kyc/status', {
        headers: {
          'Authorization': `Bearer ${credentials.accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      if (!res.ok) throw new Error('Failed to fetch KYC status');
      const data = await res.json();
      setStatus(data.kyc_status);
      setRejectionReasons(data.rejection_reasons || []);
    } catch (e: any) {
      Alert.alert('Error', e?.message || String(e));
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <ActivityIndicator />;

  if (status === 'approved' || status === 'active') {
    return (
      <View>
        <Text>KYC Approved!</Text>
        <Text>You can now use all features.</Text>
        <Button title="Continue" onPress={() => navigation.navigate('MainTabs')} />
      </View>
    );
  }

  if (status === 'rejected') {
    return (
      <View>
        <Text>KYC Rejected</Text>
        {rejectionReasons.map((reason, idx) => (
          <Text key={idx}>{reason}</Text>
        ))}
        <Button title="Retry" onPress={fetchStatus} />
      </View>
    );
  }

  return (
    <View>
      <Text>KYC Status: {status || 'pending'}</Text>
      <Text>Please wait while we verify your information...</Text>
      <Button title="Check Again" onPress={fetchStatus} />
    </View>
  );
};

export default KYCStatusScreen;
