import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { walletAPI, authAPI, transferAPI } from '../utils/api';

// Create a context for mock data
const MockDataContext = createContext();

// Synchronous version (localStorage only)
const getUserBalancesSync = () => {
  const storedBalances = localStorage.getItem('mockUserBalances');
  if (storedBalances) {
    return JSON.parse(storedBalances);
  }
  return getInitialBalances();
};

// Async version attempts backend first
const fetchUserBalances = async () => {
  try {
    // Try to get balances from backend API
    const response = await fetch('/mock/wallet/balances');
    if (response.ok) {
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const data = await response.json();
        console.log("Retrieved balances from backend API:", data);
        return data;
      }
      console.warn('Balances API did not return JSON, falling back to localStorage');
    } else {
      console.error("Failed to fetch balances from API:", response.statusText);
    }
  } catch (error) {
    console.error("Error fetching balances from API:", error);
  }
  
  // Fallback to localStorage if API call fails
  return getUserBalancesSync();
};

// Initial balances to use when nothing in localStorage or backend
const getInitialBalances = () => {
  return {
    'rajsshah11@gmail.com': { usd: 5000.00, eur: 0 },
    'hadeermotair@gmail.com': { usd: 0, eur: 0 }
  };
};

// Force reset balances to ensure everyone has money
const forceResetBalances = async () => {
  const initialBalances = getInitialBalances();
  
  // Save to localStorage as fallback
  localStorage.setItem('mockUserBalances', JSON.stringify(initialBalances));
  
  // Try to update balances on the backend
  try {
    for (const [email, balance] of Object.entries(initialBalances)) {
      await fetch(`/mock/wallet/balances/${email}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(balance),
      });
    }
    console.log("💰 Forced balance reset with new money via backend API!");
  } catch (error) {
    console.error("Error resetting balances via API:", error);
  }
  
  return initialBalances;
};

// Exchange rate for USD to EUR
const USD_TO_EUR_RATE = 0.9;

// Currency conversion fee (2%)
const CURRENCY_CONVERSION_FEE = 0.02;

// Generate wallet data based on user balances
const generateWallets = (email, balancesObj) => {
  const balances = balancesObj || JSON.parse(localStorage.getItem('mockUserBalances') || '{}') || getInitialBalances();
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
  const balances = getUserBalancesSync();
  localStorage.setItem('mockUserBalances', JSON.stringify(balances));
  
  return transaction;
};

// Mock data provider component
export const MockDataProvider = ({ children }) => {
  // Update balances when the app loads
  useEffect(() => {
    // Seed balances only if they don't exist yet
    const existing = localStorage.getItem('mockUserBalances');
    if (!existing) {
      const initialBalances = {
        'rajsshah11@gmail.com': { usd: 5000.0, eur: 0 },
        'hadeermotair@gmail.com': { usd: 0, eur: 0 }
      };
      localStorage.setItem('mockUserBalances', JSON.stringify(initialBalances));
      console.log('💰 Seeded initial mock balances', initialBalances);
      setBalances(initialBalances);
    } else {
      setBalances(JSON.parse(existing));
    }

    // Patch walletAPI and other APIs to use mock versions
    walletAPI.getOverview = mockAPI.walletAPI.getOverview;
    walletAPI.getAllTransactions = mockAPI.walletAPI.getAllTransactions;
    transferAPI.send = mockAPI.transferAPI.send;
    authAPI.searchUsers = mockAPI.authAPI.searchUsers;
  }, []);

  const [balances, setBalances] = useState(getUserBalancesSync());
  const [transactions, setTransactions] = useState(getTransactionHistory());
  const [user, setUser] = useState({
      id: 'u-001',
      email: 'rajsshah11@gmail.com',
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
  
  // Sync Auth0 user when authenticated
  const { user: authUser, isAuthenticated } = useAuth0();
  useEffect(() => {
    if (isAuthenticated && authUser && authUser.email) {
      setUser(prev => ({
        ...prev,
        email: authUser.email,
        first_name: authUser.given_name || prev.first_name,
        last_name: authUser.family_name || prev.last_name,
        nickname: authUser.nickname || prev.nickname,
      }));
      localStorage.setItem('mockCurrentUserEmail', authUser.email);

      // Seed default balance for new user if not existing
      const currentBalances = getUserBalancesSync();
      if (!currentBalances[authUser.email]) {
        currentBalances[authUser.email] = { usd: 5000.0, eur: 0 };
        updateBalances(currentBalances);
      }
    }
  }, [isAuthenticated, authUser]);
  
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
  
  const initialBalancesSync = JSON.parse(localStorage.getItem('mockUserBalances') || '{}') || getInitialBalances();
  const [mockData, setMockData] = useState({
    wallets: generateWallets(user.email, initialBalancesSync),
    transactions: transactions.filter(t => t.user_email === user.email),
    requests: [],
    user: user
  });
  
  // Update balances and save to localStorage
  const updateBalances = (newBalances) => {
    setBalances(newBalances);
    localStorage.setItem('mockUserBalances', JSON.stringify(newBalances));

    // persist to backend
    Object.entries(newBalances).forEach(async ([email,balance])=>{
      try {
        await fetch(`/mock/wallet/balances/${email}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(balance)});
      } catch(err){console.warn('Failed to sync balance',email,err);} 
    });
  };

  // Simulate API endpoints
  const mockAPI = {
    walletAPI: {
      getOverview: async () => {
        // Use localStorage-backed balances for complete consistency across users
        const balances = getUserBalancesSync();

        // Determine which user is requesting overview
        const email = localStorage.getItem('mockCurrentUserEmail') || mockData.user?.email;
        const wallets = generateWallets(email, balances);
        return Promise.resolve({ data: { wallets } });
      },
      getAllTransactions: () => {
        const email = localStorage.getItem('mockCurrentUserEmail') || mockData.user?.email;
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
            has_wallet: true,
          },
          {
            id: 'user-raj',
            email: 'rajsshah11@gmail.com',
            name: 'Raj Shah',
            has_wallet: true,
          },
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
      /**
       * Fully-offline mock implementation of the `POST /transfer` endpoint.
       *
       * Business rules implemented:
       * 1. Deduct the total cost (amount + fees) from the sender's USD wallet.
       *    • If `amount_from_wallet` is provided (wallet + bank split), the
       *      sender's USD wallet is set to 0 (representing "use everything
       *      in wallet").
       * 2. Apply fees: 0.5 % on wallet portion, 0.5 % (standard) or 2 %
       *    (express) on bank portion.
       * 3. Convert the net amount (after fees) to EUR at 0.9 USD→EUR when the
       *    recipient is Hadeer; otherwise keep it in USD.
       * 4. Credit the recipient's wallet with that net amount.
       */
      send: async (payload) => {
        const senderEmail = mockData.user?.email;

        // Resolve recipient email from id
        const idMap = {
          // Hadeer
          'user-1': 'hadeermotair@gmail.com',
          'user-hadeer': 'hadeermotair@gmail.com',
          '1': 'hadeermotair@gmail.com',
          // Other demo users
          'user-2': 'rajsshah11@gmail.com',
          'user-3': 'rajsshah11@gmail.com',
          '2': 'rajsshah11@gmail.com',
          '3': 'rajsshah11@gmail.com',
        };
        let recipientEmail = payload.recipient_email;
        if (!recipientEmail) {
          if (payload.recipient_user_id?.includes('@')) {
            recipientEmail = payload.recipient_user_id;
          } else {
            recipientEmail = idMap[payload.recipient_user_id] || 'unknown@example.com';
          }
        }

        const amount = parseFloat(payload.amount);
        const walletPart = payload.amount_from_wallet !== undefined ? parseFloat(payload.amount_from_wallet) : amount;
        const bankPart = payload.amount_from_bank !== undefined ? parseFloat(payload.amount_from_bank) : 0;

        const isExpress = payload.speed_option === 'express';
        const walletFee = walletPart * 0.005; // 0.5 %
        const bankRate = isExpress ? 0.02 : 0.005; // 2 % or 0.5 %
        const bankFee = bankPart * bankRate;
        const totalFee = walletFee + bankFee;

        // ---------- Update balances ----------
        const currentBalances = getUserBalancesSync();
        const ensureUser = (email) => {
          if (!currentBalances[email]) {
            currentBalances[email] = { usd: 0, eur: 0 };
          }
        };

        ensureUser(senderEmail);
        ensureUser(recipientEmail);

        // 1. Deduct from sender USD wallet
        if (bankPart > 0) {
          // Wallet + bank: wallet drained to zero
          currentBalances[senderEmail].usd = 0;
        } else {
          currentBalances[senderEmail].usd = Math.max(
            0,
            (currentBalances[senderEmail].usd || 0) - (amount + totalFee)
          );
        }

        // 2. Credit recipient
        const netAmount = amount - totalFee; // amount actually delivered (USD)
        if (recipientEmail === 'hadeermotair@gmail.com') {
          // Convert USD→EUR at 0.9
          const eurAmount = parseFloat((netAmount * 0.9).toFixed(2));
          currentBalances[recipientEmail].eur = (currentBalances[recipientEmail].eur || 0) + eurAmount;
        } else {
          // Same currency
          currentBalances[recipientEmail].usd = (currentBalances[recipientEmail].usd || 0) + netAmount;
        }

        // Persist balances
        updateBalances(currentBalances);

        // ---------- Record transaction (sender side only for brevity) ----------
        const timestamp = new Date().toISOString();
        const transactionId = `t-${Math.floor(Math.random() * 1000000)}`;

        const senderTransaction = {
          id: transactionId,
          transaction_id: transactionId,
          type: 'SEND',
          amount: -amount,
          currency: 'USD',
          date: timestamp,
          description: payload.memo || `Payment to ${recipientEmail}`,
          status: 'completed',
          user_email: senderEmail,
        };

        // Recipient transaction record (positive)
        const recipientTransaction = {
          id: transactionId + '-r',
          transaction_id: transactionId,
          type: 'RECEIVE',
          amount: netAmount * (recipientEmail === 'hadeermotair@gmail.com' ? 0.9 : 1), // amount credited in recipient currency
          currency: recipientEmail === 'hadeermotair@gmail.com' ? 'EUR' : 'USD',
          date: timestamp,
          description: payload.memo || `Payment from ${senderEmail}`,
          status: 'completed',
          user_email: recipientEmail,
        };

        const newTransactions = [senderTransaction, recipientTransaction, ...transactions];
        setTransactions(newTransactions);
        localStorage.setItem('mockTransactions', JSON.stringify(newTransactions));

        // All users stay on mock balances; nothing else to forward.

        return Promise.resolve({ data: senderTransaction });
      },
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
      wallets: generateWallets(user.email, balances),
      transactions: transactions.filter(t => t.user_email === user.email),
      requests: [],
      user: user
    });
  }, [user, transactions, balances]);

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