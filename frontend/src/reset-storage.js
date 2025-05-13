// This file creates a function to reset localStorage
// The file can be imported anywhere to reset the data

export function resetAppData() {
  // Clear existing data
  localStorage.removeItem('mockUserBalances');
  localStorage.removeItem('mockTransactions');
  console.log('Storage cleared successfully');
  
  // Create new balances
  const initialBalances = {
    'user@example.com': { usd: 5000.00, eur: 0 },
    'rajshah11@gmail.com': { usd: 5000.00, eur: 0 },
    'hadeermotair@gmail.com': { usd: 0, eur: 2500.00 }
  };
  
  // Set new balances
  localStorage.setItem('mockUserBalances', JSON.stringify(initialBalances));
  console.log('New balances set:', initialBalances);
  
  // Reload page
  window.location.reload();
}

// Run this in browser console to reset:
// const resetFn = () => { localStorage.removeItem('mockUserBalances'); localStorage.removeItem('mockTransactions'); window.location.reload(); }; resetFn();
