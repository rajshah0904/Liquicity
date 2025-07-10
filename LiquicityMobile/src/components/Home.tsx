import React, { useState, useEffect, useRef } from 'react';
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
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import KYCStart from './KYCStart';
import { backendRequest, API_ENDPOINTS } from '../utils/api';
import WebView from 'react-native-webview';

type RootStackParamList = {
  Home: undefined;
  Dashboard: undefined;
};

type HomeScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

const AUTH0_AUDIENCE = 'https://api.liquicity.com';

// Helper function to decode JWT token (for debugging)
function decodeJWT(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('[JWT] Failed to decode token:', e);
    return null;
  }
}

async function registerUserWithBackend(token: string, userInfo?: any) {
  console.log('[Signup] Starting backend registration with token:', token ? 'Token present' : 'No token');
  console.log('[Signup] User info:', userInfo);
  
  // Debug: Decode and log JWT token contents
  const decodedToken = decodeJWT(token);
  console.log('[Signup] JWT Token contents:', decodedToken);
  console.log('[Signup] JWT Token email claim:', decodedToken?.email);
  console.log('[Signup] JWT Token sub claim:', decodedToken?.sub);
  console.log('[Signup] JWT Token aud claim:', decodedToken?.aud);
  
  try {
    console.log('[Signup] Making POST request to /onboard/register');
    
    // Include email in request body as fallback if not in JWT token
    const requestBody: any = {};
    if (decodedToken?.email) {
      console.log('[Signup] Using email from JWT token:', decodedToken.email);
      requestBody.email = decodedToken.email;
    } else if (userInfo?.email) {
      console.log('[Signup] Using email from user info:', userInfo.email);
      requestBody.email = userInfo.email;
    } else {
      console.log('[Signup] No email found in JWT token or user info');
    }
    
    const response = await backendRequest('POST', API_ENDPOINTS.REGISTER, requestBody, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log('[Signup] /onboard/register SUCCESS - Response:', response);
    return response;
  } catch (e: any) {
    console.error('[Signup] /onboard/register ERROR - Full error object:', e);
    console.error('[Signup] /onboard/register ERROR - Message:', e?.message);
    console.error('[Signup] /onboard/register ERROR - Status:', e?.response?.status);
    console.error('[Signup] /onboard/register ERROR - Response data:', e?.response?.data);
    console.error('[Signup] /onboard/register ERROR - Request config:', e?.config);
    
    // If 409 (already exists), that's fine, just continue
    if (e.response && e.response.status === 409) {
      console.log('[Signup] User already exists (409), continuing...');
      return;
    }
    
    // Handle 400 errors specifically
    if (e.response && e.response.status === 400) {
      const errorDetail = e?.response?.data?.detail || 'Bad request';
      console.error('[Signup] 400 Error detail:', errorDetail);
      
      if (errorDetail.includes('email claim missing') || errorDetail.includes('Email is required')) {
        throw new Error('Authentication token is missing email information. Please check Auth0 configuration or try signing up again.');
      } else if (errorDetail.includes('Authorization header')) {
        throw new Error('Authentication failed. Please try signing up again.');
      } else {
        throw new Error(`Registration failed: ${errorDetail}`);
      }
    }
    
    throw e;
  }
}

const Home = () => {
  const navigation = useNavigation<HomeScreenNavigationProp & { navigate: (screen: string, params?: any) => void }>();
  const route = useRoute();
  const { authorize, clearSession, user, isLoading, error, getCredentials } = useAuth0();
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [tosModalVisible, setTosModalVisible] = useState(false);
  const [tosUrl, setTosUrl] = useState<string | null>(null);
  const [showTosWebView, setShowTosWebView] = useState(false);
  const [canGoBackBridgeTos, setCanGoBackBridgeTos] = useState(false);
  const bridgeTosWebViewRef = useRef<WebView>(null);

  function appendRedirectUri(url: string, redirectUri: string): string {
    return url.includes('?')
      ? `${url}&redirect_uri=${encodeURIComponent(redirectUri)}`
      : `${url}?redirect_uri=${encodeURIComponent(redirectUri)}`;
  }

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
      await authorize({ audience: AUTH0_AUDIENCE, scope: 'openid profile email' });
      // After login, get token and register user in backend
      const credentials = await getCredentials();
      console.log('Auth0 credentials after login:', credentials);
      if (credentials && credentials.accessToken) {
        // Get user info to extract email
        const userInfo = await credentials.user;
        console.log('User info after login:', userInfo);
        
        await registerUserWithBackend(credentials.accessToken, userInfo);
        
        // Check if user needs ToS acceptance or can proceed to KYC
        const userCheckResponse = await fetch('http://192.168.86.31:8000/user/check', {
          headers: {
            'Authorization': `Bearer ${credentials.accessToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (userCheckResponse.ok) {
          const userData = await userCheckResponse.json();
          console.log('[Login] User status:', userData);
          
          if (userData.next_step === 'tos' && userData.tos_url) {
            navigation.navigate('TermsOfService', { 
              tosUrl: userData.tos_url,
              returnTo: 'KYCStart'
            });
          } else if (userData.next_step === 'kyc') {
            navigation.navigate('KYCStart');
          } else if (userData.next_step === 'done') {
            // User is fully onboarded, navigate to main app
            navigation.navigate('MainTabs');
          } else {
            navigation.navigate('KYCStart');
          }
        } else {
          navigation.navigate('KYCStart');
        }
      } else {
        Alert.alert('Error', 'No access token received from Auth0');
        setEmailLoading(false);
        return;
      }
    } catch (e: any) {
      Alert.alert('Error', e?.message || 'Login failed');
    }
    setEmailLoading(false);
  };

  // Universal Login: Sign Up
  const handleSignUp = async () => {
    console.log('[Signup] Starting signup process...');
    try {
      // Clear any existing Auth0 session first
      console.log('[Signup] Clearing existing Auth0 session...');
      await clearSession();
      console.log('[Signup] Auth0 session cleared successfully');
      
      // Now call authorize with signup hint, audience, and scope
      console.log('[Signup] Calling Auth0 authorize with signup hint...');
      await authorize({ audience: AUTH0_AUDIENCE, screen_hint: 'signup', scope: 'openid profile email' } as any);
      console.log('[Signup] Auth0 authorize completed successfully');
      
      // After signup, get token and register user in backend
      console.log('[Signup] Getting Auth0 credentials...');
      const credentials = await getCredentials();
      console.log('[Signup] Auth0 credentials received:', credentials ? 'Credentials present' : 'No credentials');
      console.log('[Signup] Auth0 credentials details:', credentials);
      
      if (credentials && credentials.accessToken) {
        console.log('[Signup] Access token present, registering with backend...');
        
        // Get user info to extract email
        const userInfo = await credentials.user;
        console.log('[Signup] User info:', userInfo);
        
        const backendResponse = await registerUserWithBackend(credentials.accessToken, userInfo);
        console.log('[Signup] Backend registration completed:', backendResponse);
        console.log('[Signup] ToS URL received:', backendResponse.tos_url);
        
        // After registration, show ToS acceptance instead of jumping to KYC
        if (backendResponse.tos_url) {
          console.log('[Signup] Navigating to Terms of Service...');
          navigation.navigate('TermsOfService', { 
            tosUrl: backendResponse.tos_url,
            returnTo: 'KYCStart'
          });
        } else {
          console.log('[Signup] No ToS URL, navigating to KYCStart...');
          setTimeout(() => {
            navigation.navigate('KYCStart');
          }, 500);
        }
      } else {
        console.error('[Signup] No access token received from Auth0');
        Alert.alert('Error', 'No access token received from Auth0');
        return;
      }
    } catch (e: any) {
      console.error('[Signup] Signup process failed:', e);
      console.error('[Signup] Error message:', e?.message);
      console.error('[Signup] Error code:', e?.code);
      console.error('[Signup] Error details:', e);
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
        <TouchableOpacity style={styles.googleButton} onPress={async () => { 
          try {
            await authorize({ audience: AUTH0_AUDIENCE, connection: 'google-oauth2', scope: 'openid profile email' });
            // After Google login, get token and register user in backend
            const credentials = await getCredentials();
            console.log('Auth0 credentials after Google login:', credentials);
            if (credentials && credentials.accessToken) {
              // Get user info to extract email
              const userInfo = await credentials.user;
              console.log('User info after Google login:', userInfo);
              
              await registerUserWithBackend(credentials.accessToken, userInfo);
              
              // Check if user needs ToS acceptance or can proceed to KYC
              const userCheckResponse = await fetch('http://192.168.86.31:8000/user/check', {
                headers: {
                  'Authorization': `Bearer ${credentials.accessToken}`,
                  'Content-Type': 'application/json'
                }
              });
              
              if (userCheckResponse.ok) {
                const userData = await userCheckResponse.json();
                console.log('[Google Login] User status:', userData);
                
                if (userData.next_step === 'tos' && userData.tos_url) {
                  navigation.navigate('TermsOfService', { 
                    tosUrl: userData.tos_url,
                    returnTo: 'KYCStart'
                  });
                } else if (userData.next_step === 'kyc') {
                  navigation.navigate('KYCStart');
                } else if (userData.next_step === 'done') {
                  // User is fully onboarded, navigate to main app
                  navigation.navigate('MainTabs');
                } else {
                  navigation.navigate('KYCStart');
                }
              } else {
                navigation.navigate('KYCStart');
              }
            } else {
              Alert.alert('Error', 'No access token received from Auth0');
            }
          } catch (e: any) {
            Alert.alert('Error', e?.message || 'Google login failed');
          }
        }}>
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
            // For testing, we'll use the registration endpoint which generates TOS link
            const response = await backendRequest('POST', API_ENDPOINTS.REGISTER, {});
            const url = response.tos_url;
            if (url) {
              setTosUrl(appendRedirectUri(url, 'https://myapp.local/kyc'));
              setTosModalVisible(true);
            } else {
              Alert.alert('Error', 'No TOS URL received from backend');
            }
          } catch (e: any) {
            console.log('Backend API Error:', e, e.response, e.request, e.config);
            Alert.alert('Backend API Error', e?.message || String(e));
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
            <View style={{ flex: 1, position: 'relative', pointerEvents: 'box-none' }}>
              <TouchableOpacity
                style={styles.backArrowButton}
                onPress={() => {
                  if (canGoBackBridgeTos && bridgeTosWebViewRef.current) {
                    bridgeTosWebViewRef.current.goBack();
                  } else {
                    setTosModalVisible(false);
                  }
                }}
                hitSlop={{ top: 20, left: 20, right: 20, bottom: 20 }}
              >
                <MaterialCommunityIcons name="arrow-left" size={28} color="#fff" />
              </TouchableOpacity>
              {tosUrl && (() => {
                console.log('Bridge ToS URL:', tosUrl);
                return (
                  <WebView
                    ref={bridgeTosWebViewRef}
                    source={{ uri: tosUrl }}
                    style={{ flex: 1 }}
                    onNavigationStateChange={navState => {
                      if (navState.url && navState.url.startsWith('https://myapp.local/kyc')) {
                        const match = navState.url.match(/signed_agreement_id=([^&]+)/);
                        if (match) {
                          setTosModalVisible(false);
                          setTimeout(() => navigation.navigate('KYCStart', { signed_agreement_id: match[1] }), 300);
                        }
                        return;
                      }
                      setCanGoBackBridgeTos(navState.canGoBack);
                    }}
                    onShouldStartLoadWithRequest={event => {
                      const url = event.url || event.mainDocumentURL;
                      if (url && url.startsWith('https://myapp.local/kyc')) {
                        const match = url.match(/signed_agreement_id=([^&]+)/);
                        if (match) {
                          setTosModalVisible(false);
                          setTimeout(() => navigation.navigate('KYCStart', { signed_agreement_id: match[1] }), 300);
                        }
                        return false;
                      }
                      return true;
                    }}
                  />
                );
              })()}
            </View>
          </SafeAreaView>
        </Modal>
        <Text style={styles.termsText}>
          By clicking continue, you agree to our{' '}
          <Text style={styles.link} onPress={() => setShowTosWebView(true)}>Terms of Service</Text>
          {' '}and{' '}
          <Text style={styles.link} onPress={() => Linking.openURL('https://your-privacy-url.com')}>Privacy Policy</Text>
        </Text>
        {isLoading && <ActivityIndicator color="#fff" style={{ marginTop: 16 }} />}
        {error && <Text style={styles.error}>{error.message}</Text>}
      </View>
      {/* TOS WebView Modal for Terms of Service link */}
      <Modal
        visible={showTosWebView}
        animationType="slide"
        onRequestClose={() => setShowTosWebView(false)}
      >
        <SafeAreaView style={{ flex: 1, backgroundColor: '#000' }}>
          <View style={{ flex: 1, position: 'relative', pointerEvents: 'box-none' }}>
            <TouchableOpacity
              style={styles.backArrowButton}
              onPress={() => setShowTosWebView(false)}
              hitSlop={{ top: 20, left: 20, right: 20, bottom: 20 }}
            >
              <MaterialCommunityIcons name="arrow-left" size={28} color="#fff" />
            </TouchableOpacity>
            <WebView
              source={{ uri: 'https://your-terms-url.com' }}
              style={{ flex: 1 }}
            />
          </View>
        </SafeAreaView>
      </Modal>
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

export default Home;
