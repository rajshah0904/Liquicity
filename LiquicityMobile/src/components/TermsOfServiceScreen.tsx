import React, { useState } from 'react';
import { View, Text, TouchableOpacity, SafeAreaView, StyleSheet } from 'react-native';
import WebView from 'react-native-webview';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../RootStackParamList';
import { requestTosLink } from '../lib/bridgeClient';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

function appendRedirectUri(url: string, redirectUri: string): string {
  return url.includes('?')
    ? `${url}&redirect_uri=${encodeURIComponent(redirectUri)}`
    : `${url}?redirect_uri=${encodeURIComponent(redirectUri)}`;
}

const TermsOfServiceScreen = () => {
  const [tosUrl, setTosUrl] = useState<string | null>(null);
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList, 'TermsOfService'>>();

  const handleStartTos = async () => {
    try {
      const url = await requestTosLink();
      setTosUrl(appendRedirectUri(url, 'myapp://kyc'));
    } catch (e) {
      // Handle error (show alert, etc.)
    }
  };

  const handleNavChange = (navState: any) => {
    if (navState.url.includes('signed_agreement_id=')) {
      try {
        const url = new URL(navState.url);
        const signed_agreement_id = url.searchParams.get('signed_agreement_id');
        if (signed_agreement_id) {
          navigation.navigate('KYCStart', { signed_agreement_id });
        }
      } catch (e) {
        // fallback for React Native URL parsing
        const match = navState.url.match(/signed_agreement_id=([^&]+)/);
        if (match) {
          navigation.navigate('KYCStart', { signed_agreement_id: match[1] });
        }
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
        {!tosUrl ? (
          <View style={styles.content}>
            <Text style={styles.title}>Terms of Service</Text>
            <Text style={styles.description}>
              Before continuing, please review and accept the Terms of Service.
            </Text>
            <TouchableOpacity style={styles.button} onPress={handleStartTos}>
              <Text style={styles.buttonText}>Review Terms of Service</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <WebView
            source={{ uri: tosUrl }}
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
