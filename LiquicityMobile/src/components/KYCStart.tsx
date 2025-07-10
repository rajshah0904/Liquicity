import React, { useEffect, useState } from 'react';
import { View, Button, ActivityIndicator, Alert, Text, StyleSheet } from 'react-native';
import { useAuth0 } from 'react-native-auth0';
import WebView from 'react-native-webview';
import { useNavigation } from '@react-navigation/native';

const KYCStart = ({ navigation, route }: any) => {
  const { getCredentials } = useAuth0();
  const [kycData, setKycData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showWebView, setShowWebView] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const fetchKycStatus = async () => {
      setLoading(true);
      try {
        const credentials = await getCredentials();
        if (!credentials || !credentials.accessToken) {
          Alert.alert('Not authenticated', 'Please log in to continue.');
          navigation.navigate('Home');
          return;
        }

        // Get KYC status from backend
        const res = await fetch('http://192.168.86.31:8000/kyc/status', {
          headers: {
            'Authorization': `Bearer ${credentials.accessToken}`,
            'Content-Type': 'application/json'
          }
        });

        if (!res.ok) {
          if (res.status === 404) {
            // No KYC link exists yet, generate one
            await generateKycLink(credentials.accessToken);
            return;
          }
          throw new Error('Failed to fetch KYC status');
        }

        const data = await res.json();
        console.log('[KYC] Status:', data);
        setKycData(data);

        // If KYC is approved, navigate to main app
        if (data.kyc_status === 'approved') {
          navigation.navigate('MainTabs');
          return;
        }

        // Start polling for status updates if KYC is in progress
        if (data.kyc_status === 'pending' || data.kyc_status === 'under_review') {
          startPolling(credentials.accessToken);
        }

      } catch (e: any) {
        console.error('[KYC] Error:', e);
        Alert.alert('Error', e?.message || String(e));
      }
      setLoading(false);
    };

    fetchKycStatus();

    // Cleanup polling on unmount
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, []);

  const generateKycLink = async (token: string) => {
    try {
      const res = await fetch('http://192.168.86.31:8000/kyc/link', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!res.ok) throw new Error('Failed to generate KYC link');
      const data = await res.json();
      setKycData(data);
      startPolling(token);
    } catch (e: any) {
      Alert.alert('Error', e?.message || 'Failed to generate KYC link');
    }
  };

  const startPolling = (token: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://192.168.86.31:8000/kyc/link-status', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (res.ok) {
          const data = await res.json();
          setKycData(data);

          if (data.kyc_status === 'approved') {
            clearInterval(interval);
            navigation.navigate('MainTabs');
          } else if (data.kyc_status === 'rejected') {
            clearInterval(interval);
            Alert.alert('KYC Rejected', 'Your KYC application was rejected. Please try again.');
          }
        }
      } catch (e) {
        console.error('[KYC] Polling error:', e);
      }
    }, 5000); // Poll every 5 seconds

    setPollingInterval(interval);
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#fff" />
        <Text style={styles.loadingText}>Loading KYC status...</Text>
      </View>
    );
  }

  if (showWebView && kycData?.kyc_link) {
    return (
      <WebView
        source={{ uri: kycData.kyc_link }}
        style={{ flex: 1 }}
        onNavigationStateChange={navState => {
          // Handle KYC completion
          if (navState.url && navState.url.includes('kyc-verification')) {
            // KYC was completed, start polling for status
            getCredentials().then(credentials => {
              if (credentials?.accessToken) {
                startPolling(credentials.accessToken);
              }
            });
          }
        }}
      />
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>KYC Verification</Text>
      
      {kycData?.kyc_status === 'pending' && (
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>Ready to start KYC verification</Text>
          <Button
            title="Start KYC Verification"
            onPress={() => setShowWebView(true)}
          />
        </View>
      )}

      {kycData?.kyc_status === 'under_review' && (
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>KYC is under review</Text>
          <Text style={styles.subText}>Please wait while we verify your information...</Text>
          <ActivityIndicator size="large" color="#fff" style={{ marginTop: 20 }} />
        </View>
      )}

      {kycData?.kyc_status === 'rejected' && (
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>KYC was rejected</Text>
          <Text style={styles.subText}>
            {kycData.rejection_reasons?.map((reason: any, index: number) => 
              `${index + 1}. ${reason.reason}`
            ).join('\n')}
          </Text>
          <Button
            title="Try Again"
            onPress={() => {
              setShowWebView(true);
            }}
          />
        </View>
      )}

      {!kycData?.kyc_link && (
        <View style={styles.statusContainer}>
          <Text style={styles.statusText}>No KYC link available</Text>
          <Button
            title="Generate KYC Link"
            onPress={() => {
              getCredentials().then(credentials => {
                if (credentials?.accessToken) {
                  generateKycLink(credentials.accessToken);
                }
              });
            }}
          />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 30,
  },
  statusContainer: {
    alignItems: 'center',
    width: '100%',
  },
  statusText: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 10,
    textAlign: 'center',
  },
  subText: {
    fontSize: 14,
    color: '#aaa',
    textAlign: 'center',
    marginBottom: 20,
  },
  loadingText: {
    color: '#fff',
    marginTop: 10,
  },
});

export default KYCStart; 