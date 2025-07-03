import React, { useEffect, useState } from 'react';
import { View, Text, Button, ActivityIndicator, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { bridgeRequest } from '../lib/bridgeClient';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../RootStackParamList';

const POLL_INTERVAL = 10000; // 10 seconds

type KYCStatusScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'KYCStatusScreen'>;
};

const KYCStatusScreen: React.FC<KYCStatusScreenProps> = ({ navigation }) => {
  const [status, setStatus] = useState<string | null>(null);
  const [rejectionReasons, setRejectionReasons] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    setLoading(true);
    const customerId = await AsyncStorage.getItem('customer_id');
    if (!customerId) {
      Alert.alert('Error', 'No customer ID found.');
      setLoading(false);
      return;
    }
    try {
      const res = await bridgeRequest('GET', `/customers/${customerId}`);
      setStatus(res.kyc_status || res.status);
      if (res.kyc_status === 'rejected' || res.status === 'rejected') {
        setRejectionReasons(res.rejection_reasons?.map((r: { reason: string }) => r.reason) || []);
      }
      await AsyncStorage.setItem('customer_id', customerId);
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
        <Button title="Retry" onPress={() => {
          AsyncStorage.getItem('customer_id').then(customerId => {
            navigation.navigate('KYCUploadID', { customerId: customerId || '' });
          });
        }} />
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
