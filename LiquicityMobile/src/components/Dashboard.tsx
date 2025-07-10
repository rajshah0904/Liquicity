import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList, SafeAreaView, Alert } from 'react-native';
import Icon from 'react-native-vector-icons/Feather';
import { useAuth0 } from 'react-native-auth0';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const actions = [
  { label: 'Add Funds', icon: 'plus-circle' },
  { label: 'Withdraw Funds', icon: 'arrow-down-circle' },
  { label: 'Request', icon: 'corner-up-left' },
  { label: 'Transactions', icon: 'list' },
];

const activityData = [
  { id: '1', title: 'Fitness First', amount: '-€49.80' },
  { id: '2', title: 'TransferWise', amount: '+€50.00' },
];

const Dashboard = () => {
  const { clearSession, getCredentials } = useAuth0();
  const insets = useSafeAreaInsets();

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const credentials = await getCredentials();
        if (credentials && credentials.accessToken) {
          const accessToken = credentials.accessToken;
          // Use accessToken in your backend requests
          console.log('Access Token:', accessToken);
        } else {
          console.warn('No credentials or access token found');
        }
      } catch (e) {
        console.error('Failed to get credentials:', e);
      }
    };
    fetchToken();
  }, []);

  const handleLogout = async () => {
    try {
      await clearSession();
    } catch (e: any) {
      Alert.alert('Logout failed', e?.message || String(e));
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Logout Button Top Left */}
      <TouchableOpacity style={[styles.logoutButton, { top: insets.top + 10 }]} onPress={handleLogout}>
        <Text style={styles.logoutText}>Logout</Text>
      </TouchableOpacity>
      {/* Top: Greeting and Balance */}
      <View style={styles.header}>
        <Text style={styles.greeting}>Welcome back,</Text>
        <Text style={styles.username}>User</Text>
        <Text style={styles.balanceLabel}>Current balance</Text>
        <Text style={styles.balance}>$0.00</Text>
      </View>

      {/* 2x2 Grid of Actions */}
      <View style={styles.gridContainer}>
        {actions.map((action, idx) => (
          <TouchableOpacity key={action.label} style={styles.circleButton} activeOpacity={0.8}>
            <Icon name={action.icon} size={32} color="#fff" />
            <Text style={styles.circleLabel}>{action.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Send & Receive Buttons */}
      <View style={styles.sendReceiveContainer}>
        <TouchableOpacity style={styles.sendButton} activeOpacity={0.8}>
          <Text style={styles.sendReceiveText}>Send</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.receiveButton} activeOpacity={0.8}>
          <Text style={styles.sendReceiveText}>Receive</Text>
        </TouchableOpacity>
      </View>

      {/* Activity Box */}
      <View style={styles.activityBox}>
        <Text style={styles.activityTitle}>Recent Activity</Text>
        <FlatList
          data={activityData}
          keyExtractor={item => item.id}
          renderItem={({ item }) => (
            <View style={styles.activityItem}>
              <Text style={styles.activityName}>{item.title}</Text>
              <Text style={styles.activityAmount}>{item.amount}</Text>
            </View>
          )}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
        />
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingHorizontal: 20,
    paddingTop: 10,
  },
  logoutButton: {
    position: 'absolute',
    top: 18,
    left: 18,
    zIndex: 10,
    backgroundColor: 'rgba(30,30,30,0.7)',
    borderRadius: 20,
    padding: 8,
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: 1,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '300',
    letterSpacing: 1,
  },
  username: {
    color: '#fff',
    fontSize: 22,
    fontWeight: '600',
    marginBottom: 8,
  },
  balanceLabel: {
    color: '#aaa',
    fontSize: 14,
    marginTop: 8,
  },
  balance: {
    color: '#fff',
    fontSize: 36,
    fontWeight: 'bold',
    marginTop: 2,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 28,
  },
  circleButton: {
    width: '47%',
    aspectRatio: 1,
    backgroundColor: '#18181b',
    borderRadius: 100,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    shadowColor: '#fff',
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  circleLabel: {
    color: '#fff',
    fontSize: 14,
    marginTop: 10,
    fontWeight: '500',
    textAlign: 'center',
  },
  sendReceiveContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 28,
  },
  sendButton: {
    flex: 1,
    backgroundColor: '#222',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    marginRight: 8,
  },
  receiveButton: {
    flex: 1,
    backgroundColor: '#222',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    marginLeft: 8,
  },
  sendReceiveText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    letterSpacing: 1,
  },
  activityBox: {
    backgroundColor: '#18181b',
    borderRadius: 18,
    padding: 18,
    marginBottom: 16,
  },
  activityTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10,
  },
  activityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  activityName: {
    color: '#fff',
    fontSize: 15,
  },
  activityAmount: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '500',
  },
  separator: {
    height: 1,
    backgroundColor: '#222',
    opacity: 0.5,
  },
});

export default Dashboard; 