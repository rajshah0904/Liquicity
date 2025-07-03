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
  const { user, isLoading, clearSession } = useAuth0();
  const [userStatus, setUserStatus] = useState<'checking' | 'new' | 'existing' | 'kyc_pending' | 'ready'>('checking');
  const [customerId, setCustomerId] = useState<string>('');

  useEffect(() => {
    // Force logout on app start (for dev/testing)
    clearSession().catch(() => {});
  }, []);

  useEffect(() => {
    const checkUserStatus = async () => {
      if (user && user.id && navigationRef.isReady()) {
        try {
          // Check if user exists in our backend
          const response = await fetch(`http://localhost:8000/user/check`, {
            headers: {
              'Authorization': `Bearer ${user.accessToken}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            
            if (!userData.exists) {
              // New user - they need to complete onboarding
              setUserStatus('new');
            } else if (userData.next_step === 'done' && userData.kyc_complete) {
              // User is fully onboarded and KYC is complete
              setUserStatus('ready');
            } else {
              // User exists but needs to complete KYC or other steps
              setUserStatus('kyc_pending');
            }
          } else {
            // If the request fails, assume user needs to complete onboarding
            setUserStatus('new');
          }
        } catch (error) {
          console.error('Error checking user status:', error);
          // On error, assume user needs to complete onboarding
          setUserStatus('new');
        }
      }
    };
    checkUserStatus();
  }, [user]);

  if (isLoading || userStatus === 'checking') {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }}>
        <ActivityIndicator size="large" color="#fff" />
      </View>
    );
  }

  return (
    <NavigationContainer ref={navigationRef}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!user ? (
          // Auth flow
          <>
            <Stack.Screen name="Home" component={Home} />
            <Stack.Screen name="TermsOfService" component={TermsOfServiceScreen} />
          </>
        ) : userStatus === 'ready' ? (
          // User is ready - show main app
          <Stack.Screen name="MainTabs" component={MainTabs} />
        ) : (
          // User needs KYC
          <>
            <Stack.Screen name="KYCStart" component={KYCStart} />
            <Stack.Screen 
              name="KYCUploadID" 
              component={KYCUploadID}
              initialParams={{ customerId: customerId }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
