import React, { useEffect, useState } from 'react';
import { NavigationContainer, useNavigation, RouteProp } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Auth0Provider } from 'react-native-auth0';
import config from './src/auth0-configuration';
import Home from './src/components/Home';
import Dashboard from './src/components/Dashboard';
import Wallet from './src/components/Wallet';
import Send from './src/components/Send';
import Receive from './src/components/Receive';
import Activity from './src/components/Activity';
import { useAuth0 } from 'react-native-auth0';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View, Alert } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { createNavigationContainerRef, StackActions } from '@react-navigation/native';
import { RootStackParamList } from './src/RootStackParamList';;
import TermsOfServiceScreen from './src/components/TermsOfServiceScreen';
import KYCStart from './src/components/KYCStart';
import KYCUploadID from './src/components/KYCUploadID';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator<RootStackParamList>();

export const navigationRef = createNavigationContainerRef<RootStackParamList>();

type KYCStartRouteProp = RouteProp<RootStackParamList, 'KYCStart'>;

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={{
      headerShown: false,
      tabBarStyle: { backgroundColor: '#000' },
      tabBarActiveTintColor: '#fff',
      tabBarInactiveTintColor: '#888',
    }}
  >
    <Tab.Screen
      name="Dashboard"
      component={Dashboard}
      options={{
        tabBarIcon: ({ color, size }) => (
          <Icon name="view-dashboard-outline" color={color} size={size} />
        ),
      }}
    />
    <Tab.Screen
      name="Wallet"
      component={Wallet}
      options={{
        tabBarIcon: ({ color, size }) => (
          <Icon name="wallet-outline" color={color} size={size} />
        ),
      }}
    />
    <Tab.Screen
      name="Send"
      component={Send}
      options={{
        tabBarIcon: ({ color, size }) => (
          <Icon name="send" color={color} size={size} />
        ),
      }}
    />
    <Tab.Screen
      name="Receive"
      component={Receive}
      options={{
        tabBarIcon: ({ color, size }) => (
          <Icon name="qrcode-scan" color={color} size={size} />
        ),
      }}
    />
    <Tab.Screen
      name="Activity"
      component={Activity}
      options={{
        tabBarIcon: ({ color, size }) => (
          <Icon name="calendar-outline" color={color} size={size} />
        ),
      }}
    />
  </Tab.Navigator>
);

const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Home" component={Home} />
    <Stack.Screen name="TermsOfService" component={TermsOfServiceScreen} />
  </Stack.Navigator>
);

const App = () => {
  const { user, isLoading, error } = useAuth0();
  const [userStatus, setUserStatus] = useState<'checking' | 'new' | 'existing' | 'kyc_pending' | 'ready'>('checking');
  const [customerId, setCustomerId] = useState<string>('');

  // Comprehensive Auth0 state logging
  useEffect(() => {
    console.log('[Auth0 State] === AUTH0 STATE CHANGE ===');
    console.log('[Auth0 State] user:', user);
    console.log('[Auth0 State] isLoading:', isLoading);
    console.log('[Auth0 State] error:', error);
    console.log('[Auth0 State] userStatus:', userStatus);
    console.log('[Auth0 State] navigation ready:', navigationRef.isReady());
    console.log('[Auth0 State] =========================');
  }, [user, isLoading, error, userStatus]);

  console.log('App render - isLoading:', isLoading, 'user:', user, 'userStatus:', userStatus);

  useEffect(() => {
    const checkUserStatus = async () => {
      console.log('[User Check] Starting user status check...');
      console.log('[User Check] Auth0 user:', user);
      console.log('[User Check] Auth0 isLoading:', isLoading);
      console.log('[User Check] Navigation ready:', navigationRef.isReady());
      
      if (!user) {
        // User is not authenticated - show login screen
        console.log('[User Check] User not authenticated, showing login screen');
        setUserStatus('new');
        return;
      }
      
      if (user.id && navigationRef.isReady()) {
        try {
          console.log('[User Check] Checking user status with backend...');
          const response = await fetch(`http://192.168.86.31:8000/user/check`, {
            headers: {
              'Authorization': `Bearer ${user.accessToken}`,
              'Content-Type': 'application/json'
            }
          });
          console.log('[User Check] Backend response status:', response.status);
          if (response.ok) {
            const userData = await response.json();
            console.log('[User Check] User data from backend:', userData);
            
            if (!userData.exists) {
              console.log('[User Check] User does not exist, setting status to new');
              setUserStatus('new');
            } else if (userData.next_step === 'done' && userData.kyc_complete) {
              console.log('[User Check] User is ready (KYC complete)');
              setUserStatus('ready');
            } else if (userData.next_step === 'tos') {
              console.log('[User Check] User needs ToS acceptance');
              setUserStatus('kyc_pending'); // Use kyc_pending for any onboarding step
            } else if (userData.next_step === 'kyc') {
              console.log('[User Check] User needs KYC completion');
              setUserStatus('kyc_pending');
            } else {
              console.log('[User Check] User exists but in unknown state:', userData.next_step);
              setUserStatus('kyc_pending');
            }
          } else {
            console.log('[User Check] Backend returned error status, setting user to new');
            setUserStatus('new');
          }
        } catch (error) {
          console.error('[User Check] Error checking user status:', error);
          setUserStatus('new');
        }
      } else {
        console.log('[User Check] User not ready or navigation not ready', { user, navReady: navigationRef.isReady() });
      }
    };
    checkUserStatus();
  }, [user, isLoading]);

  console.log('Before render check - isLoading:', isLoading, 'userStatus:', userStatus);
  
  if (isLoading || userStatus === 'checking') {
    console.log('Showing loading screen');
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }}>
        <ActivityIndicator size="large" color="#fff" />
      </View>
    );
  }

  console.log('Showing main app - user:', !!user, 'userStatus:', userStatus);

  return (
    <NavigationContainer ref={navigationRef}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!user ? (
          <>
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="TermsOfService" component={TermsOfServiceScreen} />
          </>
        ) : userStatus === 'ready' ? (
          <Stack.Screen name="MainTabs" component={MainTabs} />
        ) : userStatus === 'kyc_pending' ? (
          <>
            <Stack.Screen name="KYCStart" component={KYCStart} />
            <Stack.Screen name="KYCUploadID" component={KYCUploadID} />
          </>
        ) : (
          // For authenticated users who are not ready (new users after registration)
          <>
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="TermsOfService" component={TermsOfServiceScreen} />
            <Stack.Screen name="KYCStart" component={KYCStart} />
            <Stack.Screen name="KYCUploadID" component={KYCUploadID} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
