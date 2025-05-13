import React, { createContext, useContext, useState, useEffect } from 'react';

// Create a context for mock data
const MockDataContext = createContext();

// Store user balances in localStorage for persistence
const getUserBalances = () => {
  const storedBalances = localStorage.getItem('mockUserBalances');
  if (storedBalances) {
    return JSON.parse(storedBalances);
  }
  
  return getInitialBalances();
};

// Initial balances to use when nothing in localStorage
const getInitialBalances = () => {
  return {
    'user@example.com': { usd: 5000.00, eur: 0 },
    'rajshah11@gmail.com': { usd: 5000.00, eur: 0 },
    'hadeermotair@gmail.com': { usd: 0, eur: 2500.00 }
  };
};

// Force reset balances to ensure everyone has money
const forceResetBalances = () => {
  const initialBalances = getInitialBalances();
  localStorage.setItem('mockUserBalances', JSON.stringify(initialBalances));
  console.log("💰 Forced balance reset with new money!", initialBalances);
  return initialBalances;
};

// Exchange rate for USD to EUR
const USD_TO_EUR_RATE = 0.85;

// Currency conversion fee (2%)
const CURRENCY_CONVERSION_FEE = 0.02;

// Generate wallet data based on user balances
const generateWallets = (email) => {
  const balances = getUserBalances();
  const userBalance = balances[email] || { usd: 0, eur: 0 };
  
  // For Hadeer, we want to show only EUR wallet
  if (email === 'hadeermotair@gmail.com') {
    return [
      {
        wallet_id: 'w-eur-' + email,
        currency: 'eur',
        balance: userBalance.eur,
        local_currency: 'eur',
        local_balance: userBalance.eur,
        created_at: '2023-06-15T14:23:45Z',
        status: 'active'
      }
    ];
  }
  
  // For other users, show both USD and EUR wallets
  return [
    {
      wallet_id: 'w-usd-' + email,
      currency: 'usd',
      balance: userBalance.usd,
      local_currency: 'usd',
      local_balance: userBalance.usd,
      created_at: '2023-06-15T14:23:45Z',
      status: 'active'
    },
    {
      wallet_id: 'w-eur-' + email,
      currency: 'eur',
      balance: userBalance.eur,
      local_currency: 'usd',
      local_balance: userBalance.eur * (1/USD_TO_EUR_RATE), // Convert EUR to USD for local display
      created_at: '2023-06-15T14:23:45Z',
      status: 'active'
    }
  ];
};

// Generate transaction history based on stored transactions
const getTransactionHistory = () => {
  const storedTransactions = localStorage.getItem('mockTransactions');
  if (storedTransactions) {
    return JSON.parse(storedTransactions);
  }
  
  // Default empty transactions if none in localStorage
  return [];
};

// Save a new transaction and update balances
const saveTransaction = (transaction, userEmail) => {
  // Save the transaction
  const transactions = getTransactionHistory();
  transactions.unshift(transaction);
  localStorage.setItem('mockTransactions', JSON.stringify(transactions.slice(0, 100))); // Keep only last 100
  
  // Update balances
  const balances = getUserBalances();
  localStorage.setItem('mockUserBalances', JSON.stringify(balances));
  
  return transaction;
};

// Mock data provider component
export const MockDataProvider = ({ children }) => {
  // Update balances when the app loads
  useEffect(() => {
    // First clear any existing data
    localStorage.removeItem('mockUserBalances');
    localStorage.removeItem('mockTransactions');
    
    // Directly set new balances in localStorage
    const initialBalances = {
      'user@example.com': { usd: 5000.00, eur: 0 },
      'rajshah11@gmail.com': { usd: 5000.00, eur: 0 },
      'hadeermotair@gmail.com': { usd: 0, eur: 2500.00 }
    };
    
    localStorage.setItem('mockUserBalances', JSON.stringify(initialBalances));
    console.log("💰 Forced balance reset with new money!", initialBalances);
    
    // Update state
    setBalances(initialBalances);
  }, []);

  const [balances, setBalances] = useState(getUserBalances());
  const [transactions, setTransactions] = useState(getTransactionHistory());
  const [user, setUser] = useState({
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
  });
  
  // Calculate total user balance
  const getUserTotalBalance = (email, currency = 'usd') => {
    const userBalances = balances[email] || { usd: 0, eur: 0 };
    if (currency === 'usd') {
      return userBalances.usd + (userBalances.eur * (1/USD_TO_EUR_RATE));
    } else if (currency === 'eur') {
      return userBalances.eur + (userBalances.usd * USD_TO_EUR_RATE);
    }
    return 0;
  };
  
  const [mockData, setMockData] = useState({
    wallets: generateWallets(user.email),
    transactions: transactions.filter(t => t.user_email === user.email),
    requests: [],
    user: user
  });
  
  // Update balances and save to localStorage
  const updateBalances = (newBalances) => {
    setBalances(newBalances);
    localStorage.setItem('mockUserBalances', JSON.stringify(newBalances));
  };
  
  // Simulate API endpoints
  const mockAPI = {
    walletAPI: {
      getOverview: () => {
        // Always get fresh data from localStorage
        const storedBalances = localStorage.getItem('mockUserBalances');
        let balances;
        
        if (storedBalances) {
          try {
            balances = JSON.parse(storedBalances);
            console.log("MockAPI: Using stored balances:", balances);
          } catch (e) {
            console.error("MockAPI: Error parsing stored balances", e);
            balances = getInitialBalances();
          }
        } else {
          // If no data in localStorage, initialize with default values
          balances = getInitialBalances();
          localStorage.setItem('mockUserBalances', JSON.stringify(balances));
          console.log("MockAPI: Initialized default balances:", balances);
        }
        
        // Generate wallets based on current user
        const email = mockData.user?.email;
        console.log("MockAPI: Current user email:", email);
        const wallets = generateWallets(email);
        console.log("MockAPI: Generated wallets:", wallets);
        return Promise.resolve({ data: { wallets } });
      },
      getAllTransactions: () => {
        // Filter transactions for current user
        const email = mockData.user?.email;
        const userTransactions = transactions.filter(t => t.user_email === email);
        return Promise.resolve({ data: { transactions: userTransactions } });
      }
    },
    authAPI: {
      getCurrentUser: () => Promise.resolve({ data: mockData.user }),
      searchUsers: (query) => {
        // Mock search for users - include Hadeer's account for testing
        const mockUsers = [
          { 
            id: 'user-1',
            email: 'hadeermotair@gmail.com',
            name: 'Hadeer Motair',
            has_wallet: true 
          },
          { 
            id: 'user-2',
            email: 'user@example.com',
            name: 'Example User',
            has_wallet: true 
          },
          { 
            id: 'user-3',
            email: 'rajshah11@gmail.com',
            name: 'Raj Shah',
            has_wallet: true 
          }
        ];
        
        // Filter based on query but ensure results are returned with empty query
        const results = query === '' ? 
          mockUsers : 
          mockUsers.filter(user => 
            user.email.toLowerCase().includes(query.toLowerCase()) || 
            user.name.toLowerCase().includes(query.toLowerCase())
          );
        
        return Promise.resolve({ data: { users: results } });
      }
    },
    transferAPI: {
      send: (payload) => {
        // Get current user's email
        const senderEmail = mockData.user?.email;
        
        // Figure out recipient email based on ID
        let recipientEmail;
        
        // Handle various ways Hadeer's ID might be formatted
        if (payload.recipient_user_id === 'user-1' || 
            payload.recipient_user_id === 'user-hadeer') {
          recipientEmail = 'hadeermotair@gmail.com';
        } else if (payload.recipient_user_id === 'user-2') {
          recipientEmail = 'user@example.com';
        } else if (payload.recipient_user_id === 'user-3') {
          recipientEmail = 'rajshah11@gmail.com';
        } else {
          // Default fallback
          recipientEmail = 'unknown@example.com';
        }
        
        // Determine currency 
        const senderCurrency = senderEmail === 'hadeermotair@gmail.com' ? 'eur' : 'usd';
        const recipientCurrency = recipientEmail === 'hadeermotair@gmail.com' ? 'eur' : 'usd';
        
        // Calculate fee based on speed option
        const amount = parseFloat(payload.amount);
        const isExpress = payload.speed_option === 'express';
        const feeRate = isExpress ? 0.015 : 0.005; // 1.5% for express, 0.5% for standard
        const fee = amount * feeRate;
        
        // Update balances
        const newBalances = {...balances};
        
        // For sender: subtract amount + fee
        if (senderCurrency === 'usd') {
          newBalances[senderEmail].usd = Math.max(0, (newBalances[senderEmail]?.usd || 0) - amount - fee);
        } else {
          newBalances[senderEmail].eur = Math.max(0, (newBalances[senderEmail]?.eur || 0) - amount - fee);
        }
        
        // For recipient: add amount (with currency conversion if needed)
        if (senderCurrency === recipientCurrency) {
          // Same currency transfer
          if (recipientCurrency === 'usd') {
            newBalances[recipientEmail].usd = (newBalances[recipientEmail]?.usd || 0) + amount;
          } else {
            newBalances[recipientEmail].eur = (newBalances[recipientEmail]?.eur || 0) + amount;
          }
        } else {
          // Currency conversion needed
          if (recipientCurrency === 'eur') {
            // USD to EUR conversion with 2% fee
            const conversionFee = amount * CURRENCY_CONVERSION_FEE;
            const eurAmount = (amount - conversionFee) * USD_TO_EUR_RATE;
            newBalances[recipientEmail].eur = (newBalances[recipientEmail]?.eur || 0) + eurAmount;
          } else {
            // EUR to USD conversion with 2% fee
            const conversionFee = amount * CURRENCY_CONVERSION_FEE;
            const usdAmount = (amount - conversionFee) * (1/USD_TO_EUR_RATE);
            newBalances[recipientEmail].usd = (newBalances[recipientEmail]?.usd || 0) + usdAmount;
          }
        }
        
        // Save the updated balances
        updateBalances(newBalances);
        
        // Create transaction records for sender and recipient
        const timestamp = new Date().toISOString();
        const transactionId = `t-${Math.floor(Math.random() * 10000)}`;
        
        // Sender's transaction record
        const senderTransaction = {
          id: transactionId,
          transaction_id: transactionId,
          type: 'SEND',
          amount: -amount,
          currency: senderCurrency.toUpperCase(),
          date: timestamp,
          description: senderCurrency !== recipientCurrency ? 
            `Payment to ${recipientEmail} (with currency conversion)` : 
            `Payment to ${recipientEmail}`,
          status: 'completed',
          user_email: senderEmail
        };
        
        // Recipient's transaction record
        let recipientAmount = amount;
        if (senderCurrency !== recipientCurrency) {
          // Apply conversion fee and exchange rate
          const conversionFee = amount * CURRENCY_CONVERSION_FEE;
          recipientAmount = senderCurrency === 'usd' ? 
            (amount - conversionFee) * USD_TO_EUR_RATE : 
            (amount - conversionFee) * (1/USD_TO_EUR_RATE);
        }
        
        const recipientTransaction = {
          id: `t-${Math.floor(Math.random() * 10000)}`,
          transaction_id: `t-${Math.floor(Math.random() * 10000)}`,
          type: 'RECEIVE',
          amount: recipientAmount,
          currency: recipientCurrency.toUpperCase(),
          date: timestamp,
          description: senderCurrency !== recipientCurrency ? 
            `Payment from ${senderEmail} (${senderCurrency.toUpperCase()} converted to ${recipientCurrency.toUpperCase()})` : 
            `Payment from ${senderEmail}`,
          status: 'completed',
          user_email: recipientEmail
        };
        
        // Save transactions
        const newTransactions = [senderTransaction, recipientTransaction, ...transactions];
        setTransactions(newTransactions);
        localStorage.setItem('mockTransactions', JSON.stringify(newTransactions));
        
        return Promise.resolve({ data: senderTransaction });
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

  // Update mock data when user changes
  useEffect(() => {
    setMockData({
      wallets: generateWallets(user.email),
      transactions: transactions.filter(t => t.user_email === user.email),
      requests: [],
      user: user
    });
  }, [user, transactions]);

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
    <MockDataContext.Provider value={{ mockData, setMockData, setUser }}>
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