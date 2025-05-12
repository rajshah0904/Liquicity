import React, { createContext, useContext, useState, useEffect } from 'react';

// Create a context for mock data
const MockDataContext = createContext();

// Mock data for wallets
const mockWallets = [
  {
    wallet_id: 'w-001',
    currency: 'usd',
    balance: 1250.00,
    local_currency: 'usd',
    local_balance: 1250.00,
    created_at: '2023-06-15T14:23:45Z',
    status: 'active'
  },
  {
    wallet_id: 'w-002',
    currency: 'eur',
    balance: 850.00,
    local_currency: 'usd',
    local_balance: 924.50,
    created_at: '2023-06-15T14:23:45Z',
    status: 'active'
  }
];

// Mock data for transactions
const mockTransactions = [
  {
    id: 't-001',
    type: 'DEPOSIT',
    amount: 500.00,
    currency: 'USD',
    date: new Date(Date.now() - 86400000).toISOString(),
    description: 'Bank deposit',
    status: 'completed'
  },
  {
    id: 't-002',
    type: 'SEND',
    amount: 120.00,
    currency: 'USD',
    date: new Date(Date.now() - 172800000).toISOString(),
    description: 'Payment to Sarah',
    status: 'completed'
  },
  {
    id: 't-003',
    type: 'RECEIVE',
    amount: 75.50,
    currency: 'USD',
    date: new Date(Date.now() - 345600000).toISOString(),
    description: 'Payment from John',
    status: 'completed'
  },
  {
    id: 't-004',
    type: 'WITHDRAW',
    amount: 200.00,
    currency: 'USD',
    date: new Date(Date.now() - 518400000).toISOString(),
    description: 'Withdrawal to bank account',
    status: 'completed'
  },
  {
    id: 't-005',
    type: 'EXCHANGE',
    amount: 150.00,
    currency: 'USD',
    date: new Date(Date.now() - 604800000).toISOString(),
    description: 'Convert to EUR',
    status: 'completed'
  }
];

// Mock requests
const mockRequests = [
  {
    id: 'r-001',
    amount: 50.00,
    currency: 'USD',
    status: 'pending',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    note: 'Dinner last night'
  }
];

// Mock data provider component
export const MockDataProvider = ({ children }) => {
  const [mockData, setMockData] = useState({
    wallets: mockWallets,
    transactions: mockTransactions,
    requests: mockRequests,
    user: {
      id: 'u-001',
      email: 'user@example.com',
      first_name: 'Raj',
      last_name: 'Shah',
      username: 'rajshah',
      nickname: 'Raj',
      profile: {
        avatar_url: null,
        country: 'US',
        currency: 'USD'
      }
    }
  });

  // Simulate API endpoints
  const mockAPI = {
    walletAPI: {
      getOverview: () => Promise.resolve({ data: { wallets: mockData.wallets } }),
      getAllTransactions: () => Promise.resolve({ data: { transactions: mockData.transactions } })
    },
    transferAPI: {
      send: (payload) => {
        const newTransaction = {
          id: `t-${Math.floor(Math.random() * 1000)}`,
          type: 'SEND',
          amount: payload.amount,
          currency: mockData.user.profile.currency,
          date: new Date().toISOString(),
          description: `Payment to user ${payload.recipient_user_id}`,
          status: 'completed'
        };
        
        setMockData(prev => ({
          ...prev,
          transactions: [newTransaction, ...prev.transactions]
        }));
        
        return Promise.resolve({ data: newTransaction });
      }
    },
    requestsAPI: {
      create: (payload) => {
        const newRequest = {
          id: `r-${Math.floor(Math.random() * 1000)}`,
          amount: payload.amount,
          currency: 'USD',
          status: 'pending',
          created_at: new Date().toISOString(),
          note: payload.note || ''
        };
        
        setMockData(prev => ({
          ...prev,
          requests: [newRequest, ...prev.requests]
        }));
        
        return Promise.resolve({ data: newRequest });
      },
      list: () => Promise.resolve({ data: { requests: mockData.requests } })
    }
  };

  useEffect(() => {
    // Override the global API calls with our mock functions
    // This is a simple way to inject mock data without changing existing components
    window.mockOverrides = mockAPI;
    
    return () => {
      // Clean up
      delete window.mockOverrides;
    };
  }, [mockData]);

  return (
    <MockDataContext.Provider value={{ mockData, setMockData }}>
      {children}
    </MockDataContext.Provider>
  );
};

// Hook to use mock data
export const useMockData = () => {
  const context = useContext(MockDataContext);
  if (context === undefined) {
    throw new Error('useMockData must be used within a MockDataProvider');
  }
  return context;
};

export default MockDataProvider; 