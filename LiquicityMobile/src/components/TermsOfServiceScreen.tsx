import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, SafeAreaView, StyleSheet, Alert } from 'react-native';
import WebView from 'react-native-webview';
import { useNavigation, useRoute } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../RootStackParamList';
import { useAuth0 } from 'react-native-auth0';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

type TermsOfServiceRouteProp = {
  tosUrl?: string;
  returnTo?: string;
};

const TermsOfServiceScreen = () => {
  const [tosUrl, setTosUrl] = useState<string | null>(null);
  const [showWebView, setShowWebView] = useState(false);
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList, 'TermsOfService'>>();
  const route = useRoute();
  const { getCredentials } = useAuth0();
  
  const routeParams = route.params as TermsOfServiceRouteProp;
  const returnTo = routeParams?.returnTo || 'KYCStart';

  useEffect(() => {
    if (routeParams?.tosUrl) {
      setTosUrl(routeParams.tosUrl);
    }
  }, [routeParams]);

  const handleAcceptTos = async () => {
    try {
      const credentials = await getCredentials();
      if (!credentials?.accessToken) {
        Alert.alert('Error', 'Not authenticated');
        return;
      }

      // Call the backend ToS acceptance endpoint
      const response = await fetch('http://192.168.86.31:8000/onboard/tos/accepted', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${credentials.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          signed_agreement_id: null // We don't store this anymore
        })
      });

      if (!response.ok) {
        throw new Error('Failed to accept Terms of Service');
      }

      const data = await response.json();
      console.log('[ToS] Accepted successfully, KYC URL:', data.kyc_url);
      
      // Navigate to the next step
      if (returnTo === 'KYCStart') {
        navigation.navigate('KYCStart');
      } else if (returnTo === 'MainTabs') {
        navigation.navigate('MainTabs');
      } else {
        navigation.navigate('KYCStart');
      }
    } catch (error: any) {
      console.error('[ToS] Error accepting ToS:', error);
      Alert.alert('Error', error?.message || 'Failed to accept Terms of Service');
    }
  };

  const handleNavChange = (navState: any) => {
    // Handle Bridge ToS completion
    if (navState.url && navState.url.includes('signed_agreement_id=')) {
      try {
        const match = navState.url.match(/signed_agreement_id=([^&]+)/);
        if (match) {
          // ToS was completed via Bridge, now accept it with our backend
          handleAcceptTos();
        }
      } catch (e) {
        console.error('[ToS] Error parsing signed_agreement_id:', e);
      }
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={{ flex: 1, position: 'relative', pointerEvents: 'box-none' }}>
        {/* Back Arrow in top left */}
        <TouchableOpacity
          style={styles.backArrowButton}
          onPress={() => navigation.goBack()}
          hitSlop={{ top: 20, left: 20, right: 20, bottom: 20 }}
        >
          <MaterialCommunityIcons name="arrow-left" size={28} color="#fff" />
        </TouchableOpacity>
        
        {!showWebView ? (
          <View style={styles.content}>
            <Text style={styles.title}>Terms of Service</Text>
            <Text style={styles.description}>
              Before continuing, please review and accept the Terms of Service.
            </Text>
            <TouchableOpacity style={styles.button} onPress={() => setShowWebView(true)}>
              <Text style={styles.buttonText}>Review Terms of Service</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <WebView
            source={{ uri: tosUrl || '' }}
            style={styles.webview}
            onNavigationStateChange={handleNavChange}
          />
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  content: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 24, fontWeight: 'bold', color: '#fff', marginBottom: 16 },
  description: { fontSize: 16, color: '#fff', textAlign: 'center', marginBottom: 32 },
  button: { backgroundColor: '#007AFF', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  webview: { flex: 1 },
  backArrowButton: {
    position: 'absolute',
    top: 16,
    left: 16,
    zIndex: 10,
    backgroundColor: 'rgba(30,30,30,0.7)',
    borderRadius: 20,
    padding: 8,
  },
});

export default TermsOfServiceScreen;
