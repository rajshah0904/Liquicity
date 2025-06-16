import React, { useEffect, useState } from 'react';
import { NavigationContainer, useNavigation } from '@react-navigation/native';
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
import { fetchKycStatus } from './src/utils/kyc';
import { createNavigationContainerRef, StackActions } from '@react-navigation/native';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

type RootStackParamList = {
  Home: undefined;
  KYCStart: undefined;
  Dashboard: undefined;
  Wallet: undefined;
  Send: undefined;
  Receive: undefined;
  Activity: undefined;
};

export const navigationRef = createNavigationContainerRef<RootStackParamList>();

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
    <Stack.Screen name="KYCStart" component={require('./src/components/KYCStart').default} />
  </Stack.Navigator>
);

const App = () => {
  const { user, isLoading } = useAuth0();

  useEffect(() => {
    const checkKyc = async () => {
      if (user && user.id) {
        const status = await fetchKycStatus(user.id);
        if (status !== 'approved' && navigationRef.isReady()) {
          navigationRef.navigate('KYCStart');
        }
      }
    };
    checkKyc();
  }, [user]);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }}>
        <ActivityIndicator size="large" color="#fff" />
      </View>
    );
  }

  return (
    <NavigationContainer ref={navigationRef}>
      {user ? <MainTabs /> : <AuthStack />}
    </NavigationContainer>
  );
};

export default App;
