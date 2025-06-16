import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Linking,
  ActivityIndicator,
  Alert,
  Modal,
  SafeAreaView,
} from 'react-native';
import { useAuth0 } from 'react-native-auth0';
import Icon from 'react-native-vector-icons/FontAwesome';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import KYCStart from './KYCStart';
import { postWithIdempotency, requestTosLink } from '../lib/bridgeClient';
import WebView from 'react-native-webview';

type RootStackParamList = {
  Home: undefined;
  Dashboard: undefined;
};

type HomeScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

const Home = () => {
  const navigation = useNavigation<HomeScreenNavigationProp & { navigate: (screen: string, params?: any) => void }>();
  const route = useRoute();
  const { authorize, clearSession, user, isLoading, error } = useAuth0();
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [tosModalVisible, setTosModalVisible] = useState(false);
  const [tosUrl, setTosUrl] = useState<string | null>(null);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }}>
        <ActivityIndicator size="large" color="#fff" />
      </View>
    );
  }

  // Universal Login: Login (email/password or passwordless)
  const handleEmailLogin = async () => {
    setEmailLoading(true);
    try {
      await authorize();
    } catch (e: any) {
      Alert.alert('Error', e?.message || 'Login failed');
    }
    setEmailLoading(false);
  };

  // Universal Login: Sign Up
  const handleSignUp = async () => {
    try {
      // Clear any existing Auth0 session first
      await clearSession();
      // Now call authorize with signup hint
      await authorize({ screen_hint: 'signup' } as any);
      // After successful signup, navigate to KYCStart
      navigation.navigate('KYCStart');
    } catch (e: any) {
      Alert.alert('Error', e?.message || 'Sign up failed');
    }
  };

  const handleLogout = async () => {
    try {
      await clearSession();
      navigation.replace('Home');
    } catch (e) {
      console.log(e);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Liquicity</Text>
        {/* Only show login/signup UI, never the welcome message for authenticated users */}
        <TouchableOpacity style={styles.googleButton} onPress={async () => { await authorize({ connection: 'google-oauth2' }); }}>
          <Icon name="google" size={20} color="#fff" style={{ marginRight: 8 }} />
          <Text style={styles.buttonText}>Sign in with Google</Text>
        </TouchableOpacity>
        <View style={styles.dividerRow}>
          <View style={styles.divider} />
          <Text style={styles.orText}>OR</Text>
          <View style={styles.divider} />
        </View>
        <TextInput
          style={styles.input}
          placeholder="Email address"
          placeholderTextColor="#aaa"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TouchableOpacity style={styles.button} onPress={handleEmailLogin} disabled={emailLoading}>
          {emailLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Continue with Email</Text>
          )}
        </TouchableOpacity>
        <TouchableOpacity style={styles.outlineButton} onPress={handleSignUp}>
          <Text style={styles.outlineButtonText}>Sign Up</Text>
        </TouchableOpacity>
        {/* Test KYC Flow Button for development/testing */}
        <TouchableOpacity style={styles.outlineButton} onPress={async () => {
          try {
            const url = await requestTosLink();
            setTosUrl(url);
            setTosModalVisible(true);
          } catch (e: any) {
            console.log('Bridge API Error:', e, e.response, e.request, e.config);
            Alert.alert('Bridge API Error', e?.message || String(e));
          }
        }}>
          <Text style={styles.outlineButtonText}>Test KYC Flow</Text>
        </TouchableOpacity>
        <Modal
          visible={tosModalVisible}
          animationType="slide"
          onRequestClose={() => setTosModalVisible(false)}
        >
          <SafeAreaView style={{ flex: 1, backgroundColor: '#000' }}>
            {tosUrl && (
              <WebView
                source={{ uri: tosUrl }}
                style={{ flex: 1 }}
                onNavigationStateChange={(navState: any) => {
                  // If the user accepts TOS and Bridge redirects, close modal and go to KYCStart
                  if (navState.url.includes('signed_agreement_id')) {
                    setTosModalVisible(false);
                    setTimeout(() => navigation.navigate('KYCStart'), 300);
                  }
                }}
              />
            )}
            <TouchableOpacity style={[styles.outlineButton, { margin: 16 }]} onPress={() => setTosModalVisible(false)}>
              <Text style={styles.outlineButtonText}>Close</Text>
            </TouchableOpacity>
          </SafeAreaView>
        </Modal>
        <Text style={styles.termsText}>
          By clicking continue, you agree to our{' '}
          <Text style={styles.link} onPress={() => Linking.openURL('https://your-terms-url.com')}>Terms of Service</Text>
          {' '}and{' '}
          <Text style={styles.link} onPress={() => Linking.openURL('https://your-privacy-url.com')}>Privacy Policy</Text>
        </Text>
        {isLoading && <ActivityIndicator color="#fff" style={{ marginTop: 16 }} />}
        {error && <Text style={styles.error}>{error.message}</Text>}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 24,
    width: '90%',
    maxWidth: 400,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
  },
  title: {
    color: '#fff',
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 24,
  },
  googleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#000',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginBottom: 16,
    width: '100%',
    borderWidth: 1,
    borderColor: '#fff',
    justifyContent: 'center',
  },
  button: {
    backgroundColor: '#000',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginTop: 12,
    width: '100%',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#fff',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  outlineButton: {
    backgroundColor: 'transparent',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginTop: 12,
    width: '100%',
    alignItems: 'center',
  },
  outlineButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#222',
    color: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 16,
    width: '100%',
    marginTop: 12,
    fontSize: 16,
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    marginVertical: 16,
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: '#fff',
    opacity: 0.2,
  },
  orText: {
    color: '#fff',
    marginHorizontal: 8,
    fontWeight: '600',
    opacity: 0.7,
  },
  termsText: {
    color: '#aaa',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 16,
  },
  link: {
    color: '#fff',
    textDecorationLine: 'underline',
  },
  error: {
    color: 'red',
    marginTop: 12,
    textAlign: 'center',
  },
});

export default Home;
