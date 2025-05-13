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

// Get notifications from localStorage
const getNotificationsSync = () => {
  const storedNotifications = localStorage.getItem('mockNotifications');
  if (storedNotifications) {
    return JSON.parse(storedNotifications);
  }
  return [];
};

// Save notifications to localStorage
const saveNotifications = (notifications) => {
  localStorage.setItem('mockNotifications', JSON.stringify(notifications));
  return notifications;
};

// Add a new notification
const addNotification = (notification) => {
  const notifications = getNotificationsSync();
  notifications.unshift(notification); // Add to beginning of array
  saveNotifications(notifications.slice(0, 100)); // Keep only last 100
  return notifications;
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
    'user@example.com': { usd: 5000.00, eur: 0 },
    'rajshah11@gmail.com': { usd: 5000.00, eur: 0 },
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
const USD_TO_EUR_RATE = 0.85;
const EUR_TO_USD_RATE = 1 / USD_TO_EUR_RATE;

// Currency conversion fee (2%)
const CURRENCY_CONVERSION_FEE = 0.02;

// Format currency based on user preference
const formatCurrency = (amount, currency, userCurrency = null) => {
  if (!amount && amount !== 0) return '0.00';
  
  // Convert if currencies don't match
  let convertedAmount = amount;
  let displayCurrency = currency;
  
  if (userCurrency && userCurrency.toLowerCase() !== currency.toLowerCase()) {
    if (currency.toLowerCase() === 'usd' && userCurrency.toLowerCase() === 'eur') {
      convertedAmount = amount * USD_TO_EUR_RATE;
      displayCurrency = 'EUR';
    } else if (currency.toLowerCase() === 'eur' && userCurrency.toLowerCase() === 'usd') {
      convertedAmount = amount * EUR_TO_USD_RATE;
      displayCurrency = 'USD';
    }
  }
  
  // Format with 2 decimal places
  return `${displayCurrency === 'EUR' ? '€' : '$'}${Math.abs(convertedAmount).toFixed(2)}`;
};

// Generate wallet data based on user balances
const generateWallets = (email, balancesObj) => {
  const balances = balancesObj || getUserBalancesSync(); // Always get from sync to ensure consistency
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

// Get user's preferred currency
const getUserPreferredCurrency = (email) => {
  // Default preferences
  if (email === 'hadeermotair@gmail.com') {
    return 'EUR';
  }
  return 'USD';
};

// Recalculate all balances from transaction history
// This ensures consistent state between transactions and balances
const recalculateBalancesFromTransactions = () => {
  const transactions = getTransactionHistory();
  const balances = getInitialBalances(); // Start with initial balances
  
  // Process each transaction to update balances
  transactions.forEach(transaction => {
    const email = transaction.user_email;
    if (!balances[email]) {
      balances[email] = { usd: 0, eur: 0 };
    }
    
    // Update the balance based on transaction type and currency
    if (transaction.type === 'SEND') {
      // For send transactions, amount is already negative
      if (transaction.currency.toLowerCase() === 'usd') {
        balances[email].usd += transaction.amount;
      } else if (transaction.currency.toLowerCase() === 'eur') {
        balances[email].eur += transaction.amount;
      }
    } else if (transaction.type === 'RECEIVE') {
      // For receive transactions, amount is positive
      if (transaction.currency.toLowerCase() === 'usd') {
        balances[email].usd += transaction.amount;
      } else if (transaction.currency.toLowerCase() === 'eur') {
        balances[email].eur += transaction.amount;
      }
    }
  });
  
  // Save recalculated balances
  localStorage.setItem('mockUserBalances', JSON.stringify(balances));
  console.log('Recalculated balances from transactions:', balances);
  
  return balances;
};

// Mock data provider component
export const MockDataProvider = ({ children }) => {
  // Update balances when the app loads
  useEffect(() => {
    // Always recalculate balances from transactions to ensure consistency
    const recalculatedBalances = recalculateBalancesFromTransactions();
    setBalances(recalculatedBalances);
    
    // Patch walletAPI and other APIs to use mock versions
    walletAPI.getOverview = mockAPI.walletAPI.getOverview;
    walletAPI.getAllTransactions = mockAPI.walletAPI.getAllTransactions;
    transferAPI.send = mockAPI.transferAPI.send;
    authAPI.searchUsers = mockAPI.authAPI.searchUsers;
    
    // Add notification API if it doesn't exist
    if (!walletAPI.getNotifications) {
      walletAPI.getNotifications = mockAPI.walletAPI.getNotifications;
      walletAPI.markNotificationRead = mockAPI.walletAPI.markNotificationRead;
      walletAPI.markAllNotificationsRead = mockAPI.walletAPI.markAllNotificationsRead;
    }
    
    // Debug current state
    console.log('Initial transactions:', getTransactionHistory());
    console.log('Initial balances:', recalculatedBalances);
    console.log('Initial notifications:', getNotificationsSync());
  }, []);

  const [balances, setBalances] = useState(getUserBalancesSync());
  const [transactions, setTransactions] = useState(getTransactionHistory());
  const [notifications, setNotifications] = useState(getNotificationsSync());
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
  
  // Sync Auth0 user when authenticated
  const { user: authUser, isAuthenticated } = useAuth0();
  useEffect(() => {
    if (isAuthenticated && authUser && authUser.email) {
      const userEmail = authUser.email;
      
      // When user changes, ensure their balances are up-to-date
      const currentBalances = getUserBalancesSync();
      if (!currentBalances[userEmail]) {
        // Initialize if user doesn't exist in balances
        currentBalances[userEmail] = { usd: 0, eur: 0 };
        localStorage.setItem('mockUserBalances', JSON.stringify(currentBalances));
      }
      
      // Update user profile with preferred currency
      const preferredCurrency = getUserPreferredCurrency(userEmail);
      
      setUser(prev => ({
        ...prev,
        email: userEmail,
        first_name: authUser.given_name || prev.first_name,
        last_name: authUser.family_name || prev.last_name,
        nickname: authUser.nickname || prev.nickname,
        profile: {
          ...prev.profile,
          currency: preferredCurrency
        }
      }));
      
      // Debug log when user changes
      console.log(`User changed to ${userEmail}. Current balances:`, currentBalances[userEmail]);
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
  
  const [mockData, setMockData] = useState({
    wallets: generateWallets(user.email, balances),
    transactions: transactions.filter(t => t.user_email === user.email),
    notifications: notifications.filter(n => n.user_email === user.email),
    requests: [],
    user: user
  });
  
  // Update balances and save to localStorage
  const updateBalances = (newBalances) => {
    console.log('Updating balances:', newBalances);
    setBalances(newBalances);
    localStorage.setItem('mockUserBalances', JSON.stringify(newBalances));

    // persist to backend
    Object.entries(newBalances).forEach(async ([email,balance])=>{
      try {
        await fetch(`/mock/wallet/balances/${email}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(balance)});
      } catch(err){console.warn('Failed to sync balance',email,err);} 
    });
  };
  
  // Create and save a notification
  const createNotification = (userEmail, type, data) => {
    const timestamp = new Date().toISOString();
    const id = `n-${Math.floor(Math.random() * 1000000)}`;
    const preferredCurrency = getUserPreferredCurrency(userEmail);
    
    // Format amount in user's preferred currency if applicable
    let formattedAmount = null;
    if (data.amount && data.currency) {
      formattedAmount = formatCurrency(Math.abs(data.amount), data.currency, preferredCurrency);
    }
    
    // Create notification message based on type
    let message = '';
    let title = '';
    
    switch (type) {
      case 'SEND_MONEY':
        title = 'Money Sent';
        message = `You sent ${formattedAmount} to ${data.recipientName || data.recipientEmail}`;
        break;
      case 'RECEIVE_MONEY':
        title = 'Money Received';
        message = `${data.senderName || data.senderEmail} sent you ${formattedAmount}`;
        break;
      case 'MONEY_REQUEST':
        title = 'Money Request';
        message = `${data.requesterName || data.requesterEmail} requested ${formattedAmount} from you`;
        break;
      case 'REQUEST_FULFILLED':
        title = 'Request Fulfilled';
        message = `${data.senderName || data.senderEmail} fulfilled your request for ${formattedAmount}`;
        break;
      default:
        title = 'Notification';
        message = data.message || 'You have a new notification';
    }
    
    const notification = {
      id,
      user_email: userEmail,
      type,
      title,
      message,
      data,
      timestamp,
      read: false
    };
    
    // Save and update notifications
    const updatedNotifications = addNotification(notification);
    setNotifications(updatedNotifications);
    
    return notification;
  };
  
  // Mark a notification as read
  const markNotificationAsRead = (notificationId) => {
    const currentNotifications = getNotificationsSync();
    const updatedNotifications = currentNotifications.map(n => 
      n.id === notificationId ? { ...n, read: true } : n
    );
    
    saveNotifications(updatedNotifications);
    setNotifications(updatedNotifications);
    
    return updatedNotifications;
  };
  
  // Mark all notifications as read for a user
  const markAllNotificationsAsRead = (userEmail) => {
    const currentNotifications = getNotificationsSync();
    const updatedNotifications = currentNotifications.map(n => 
      n.user_email === userEmail ? { ...n, read: true } : n
    );
    
    saveNotifications(updatedNotifications);
    setNotifications(updatedNotifications);
    
    return updatedNotifications;
  };
  
  // Simulate API endpoints
  const mockAPI = {
    walletAPI: {
      getOverview: async () => {
        // Always get fresh data from localStorage
        const currentBalances = getUserBalancesSync();
        
        // Generate wallets based on current user
        const email = mockData.user?.email;
        console.log("MockAPI: Current user email:", email);
        console.log("MockAPI: Current balances:", currentBalances);
        
        const wallets = generateWallets(email, currentBalances);
        console.log("MockAPI: Generated wallets:", wallets);
        return Promise.resolve({ data: { wallets } });
      },
      getAllTransactions: () => {
        // Filter transactions for current user - both sent and received
        const email = mockData.user?.email;
        const userTransactions = transactions.filter(t => t.user_email === email);
        
        console.log(`Getting transactions for ${email}:`, userTransactions);
        return Promise.resolve({ data: { transactions: userTransactions } });
      },
      getNotifications: () => {
        // Filter notifications for current user
        const email = mockData.user?.email;
        const userNotifications = notifications.filter(n => n.user_email === email);
        
        return Promise.resolve({ data: { notifications: userNotifications } });
      },
      markNotificationRead: (id) => {
        const updatedNotifications = markNotificationAsRead(id);
        return Promise.resolve({ data: { success: true } });
      },
      markAllNotificationsRead: () => {
        const email = mockData.user?.email;
        const updatedNotifications = markAllNotificationsAsRead(email);
        return Promise.resolve({ data: { success: true } });
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
            email: 'rajshah11@gmail.com',
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
       *    • If `amount_from_wallet` is provided (wallet + bank split), the
       *      sender's USD wallet is set to 0 (representing "use everything
       *      in wallet").
       * 2. Apply fees: 0.5 % on wallet portion, 0.5 % (standard) or 2 %
       *    (express) on bank portion.
       * 3. Convert the net amount (after fees) to EUR at 0.9 USD→EUR when the
       *    recipient is Hadeer; otherwise keep it in USD.
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
          'user-2': 'user@example.com',
          'user-3': 'rajshah11@gmail.com',
          '2': 'user@example.com',
          '3': 'rajshah11@gmail.com',
        };
        
        // Map of names for notifications and descriptions
        const nameMap = {
          'hadeermotair@gmail.com': 'Hadeer Motair',
          'user@example.com': 'Example User',
          'rajshah11@gmail.com': 'Raj Shah',
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
        let recipientCurrency = 'USD';
        let recipientAmount = netAmount;
        
        if (recipientEmail === 'hadeermotair@gmail.com') {
          // Convert USD→EUR at 0.9
          recipientCurrency = 'EUR';
          recipientAmount = parseFloat((netAmount * 0.9).toFixed(2));
          currentBalances[recipientEmail].eur = (currentBalances[recipientEmail].eur || 0) + recipientAmount;
          
          console.log(`Crediting ${recipientEmail} with ${recipientAmount} EUR. New balance:`, 
                     currentBalances[recipientEmail]);
        } else {
          // Same currency
          currentBalances[recipientEmail].usd = (currentBalances[recipientEmail].usd || 0) + netAmount;
        }

        // Persist balances
        updateBalances(currentBalances);
        console.log('Updated balances after transfer:', currentBalances);

        // ---------- Record transaction (sender and recipient) ----------
        const timestamp = new Date().toISOString();
        const transactionId = `t-${Math.floor(Math.random() * 1000000)}`;
        
        // Get sender and recipient names
        const senderName = nameMap[senderEmail] || senderEmail;
        const recipientName = nameMap[recipientEmail] || recipientEmail;

        // Sender transaction record (negative)
        const senderTransaction = {
          id: transactionId,
          transaction_id: transactionId,
          type: 'SEND',
          amount: -amount, // Negative amount for sender
          currency: 'USD',
          date: timestamp,
          description: payload.memo || `Payment to ${recipientName}`,
          status: 'completed',
          user_email: senderEmail,
          recipient_email: recipientEmail,
          recipient_name: recipientName
        };

        // Recipient transaction record (positive)
        const recipientTransaction = {
          id: transactionId + '-r',
          transaction_id: transactionId,
          type: 'RECEIVE',
          amount: recipientAmount, // Positive amount for recipient in their currency
          currency: recipientCurrency,
          date: timestamp,
          description: payload.memo || `Payment from ${senderName}`,
          status: 'completed',
          user_email: recipientEmail,
          sender_email: senderEmail,
          sender_name: senderName
        };

        const newTransactions = [senderTransaction, recipientTransaction, ...transactions];
        setTransactions(newTransactions);
        localStorage.setItem('mockTransactions', JSON.stringify(newTransactions));
        console.log('New transactions after transfer:', newTransactions);
        
        // ---------- Create notifications ----------
        // Notification for sender
        createNotification(
          senderEmail,
          'SEND_MONEY',
          {
            transactionId,
            amount: -amount,
            currency: 'USD',
            recipientEmail,
            recipientName
          }
        );
        
        // Notification for recipient
        createNotification(
          recipientEmail,
          'RECEIVE_MONEY',
          {
            transactionId,
            amount: recipientAmount, // In recipient's currency
            currency: recipientCurrency,
            senderEmail,
            senderName
          }
        );

        return Promise.resolve({ data: senderTransaction });
      },
    },
    requestsAPI: {
      create: (payload) => {
        const requesterEmail = mockData.user?.email;
        const recipientEmail = payload.recipient_email || payload.email;
        
        // Map email to name for notifications
        const nameMap = {
          'hadeermotair@gmail.com': 'Hadeer Motair',
          'user@example.com': 'Example User',
          'rajshah11@gmail.com': 'Raj Shah',
        };
        
        const newRequest = {
          id: `r-${Math.floor(Math.random() * 1000)}`,
          amount: payload.amount,
          currency: 'USD',
          status: 'pending',
          created_at: new Date().toISOString(),
          requester_email: requesterEmail,
          recipient_email: recipientEmail,
          note: payload.note || ''
        };
        
        // Update requests in mockData
        setMockData(prev => ({
          ...prev,
          requests: [newRequest, ...prev.requests]
        }));
        
        // Create notification for request recipient
        createNotification(
          recipientEmail,
          'MONEY_REQUEST',
          {
            requestId: newRequest.id,
            amount: payload.amount,
            currency: 'USD',
            requesterEmail,
            requesterName: nameMap[requesterEmail] || requesterEmail,
            note: payload.note
          }
        );
        
        return Promise.resolve({ data: newRequest });
      },
      list: () => Promise.resolve({ data: { requests: mockData.requests } }),
      fulfill: (requestId, paymentDetails) => {
        // Find the request
        const request = mockData.requests.find(r => r.id === requestId);
        
        if (!request) {
          return Promise.reject({ error: 'Request not found' });
        }
        
        // Prepare payment payload
        const paymentPayload = {
          amount: request.amount,
          recipient_email: request.requester_email,
          memo: `Payment for request: ${request.note}`,
          ...paymentDetails
        };
        
        // Process the payment using the send function
        return mockAPI.transferAPI.send(paymentPayload)
          .then(result => {
            // Update request status
            const updatedRequests = mockData.requests.map(r => 
              r.id === requestId ? { ...r, status: 'fulfilled' } : r
            );
            
            setMockData(prev => ({
              ...prev,
              requests: updatedRequests
            }));
            
            // Create notification for requester
            createNotification(
              request.requester_email,
              'REQUEST_FULFILLED',
              {
                requestId,
                amount: request.amount,
                currency: 'USD',
                senderEmail: mockData.user?.email,
                senderName: mockData.user?.first_name + ' ' + mockData.user?.last_name
              }
            );
            
            return { data: { request: { ...request, status: 'fulfilled' } } };
          });
      }
    }
  };

  // Update mock data when user, transactions, balances, or notifications change
  useEffect(() => {
    const email = user.email;
    const currentBalances = getUserBalancesSync();
    
    // Ensure fresh wallet data is generated from current balances
    const wallets = generateWallets(email, currentBalances);
    
    // Get transactions for current user
    const userTransactions = transactions.filter(t => t.user_email === email);
    
    // Get notifications for current user
    const userNotifications = notifications.filter(n => n.user_email === email);
    
    setMockData({
      wallets: wallets,
      transactions: userTransactions,
      notifications: userNotifications,
      requests: mockData.requests.filter(r => r.recipient_email === email || r.requester_email === email),
      user: user
    });
    
    console.log(`Updated mockData for ${email}:`, {
      wallets: wallets,
      transactions: userTransactions.length,
      notifications: userNotifications.length,
      balances: currentBalances[email]
    });
  }, [user, transactions, balances, notifications]);

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
    <MockDataContext.Provider value={{ 
      mockData, 
      setMockData, 
      setUser,
      createNotification,
      markNotificationAsRead,
      markAllNotificationsAsRead,
      formatCurrency
    }}>
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