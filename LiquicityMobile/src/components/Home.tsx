import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Linking,
  ActivityIndicator,
} from 'react-native';
import { useAuth0 } from 'react-native-auth0';
import Icon from 'react-native-vector-icons/FontAwesome';

const Home = () => {
  const { authorize, clearSession, user, isLoading, error } = useAuth0();
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);

  // Placeholder for email login/signup logic
  const handleEmailLogin = async () => {
    setEmailLoading(true);
    try {
      // You would use Auth0 passwordless/email login here
      // For now, just simulate
      setTimeout(() => setEmailLoading(false), 1000);
    } catch (e) {
      setEmailLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Liquicity</Text>
        {user ? (
          <>
            <Text style={styles.welcome}>Welcome, {user.name}</Text>
            <TouchableOpacity style={styles.button} onPress={() => clearSession()}>
              <Text style={styles.buttonText}>Log Out</Text>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <TouchableOpacity style={styles.googleButton} onPress={() => authorize({ connection: 'google-oauth2' })}>
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
            <TouchableOpacity style={styles.outlineButton} onPress={handleEmailLogin}>
              <Text style={styles.outlineButtonText}>Sign Up</Text>
            </TouchableOpacity>
            <Text style={styles.termsText}>
              By clicking continue, you agree to our{' '}
              <Text style={styles.link} onPress={() => Linking.openURL('https://your-terms-url.com')}>Terms of Service</Text>
              {' '}and{' '}
              <Text style={styles.link} onPress={() => Linking.openURL('https://your-privacy-url.com')}>Privacy Policy</Text>
            </Text>
          </>
        )}
        {isLoading && <ActivityIndicator color="#fff" style={{ marginTop: 16 }} />}
        {error && <Text style={styles.error}>{error.message}</Text>}
      </View>
      <Text style={styles.debug}>Debug Logs: {'\n'}App started!</Text>
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
  welcome: {
    color: '#fff',
    fontSize: 20,
    marginBottom: 16,
    textAlign: 'center',
  },
  debug: {
    color: '#fff',
    fontSize: 14,
    position: 'absolute',
    bottom: 16,
    left: 0,
    right: 0,
    textAlign: 'center',
    opacity: 0.7,
  },
});

export default Home;
