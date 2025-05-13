// Reset script for Liquicity balance issues
// This script will run automatically when included in the page

(function() {
  // Function to reset balances
  function resetBalances() {
    console.log("🔄 Checking and resetting Liquicity balances...");
    
    // Clear any existing data
    localStorage.removeItem('mockUserBalances');
    localStorage.removeItem('mockTransactions');
    
    // Set new balances with high values
    const newBalances = {
      'user@example.com': { usd: 5000.00, eur: 0 },
      'rajshah11@gmail.com': { usd: 5000.00, eur: 0 },
      'hadeermotair@gmail.com': { usd: 0, eur: 2500.00 }
    };
    
    // Save to localStorage
    localStorage.setItem('mockUserBalances', JSON.stringify(newBalances));
    console.log("💰 Balances reset with new values:", newBalances);
    
    // Create global reset function for debugging
    window.resetLiquicityData = function() {
      resetBalances();
      window.location.reload();
      return "Balances reset and page reloaded!";
    };
    
    console.log("✅ Reset complete! Use window.resetLiquicityData() in console to manually reset.");
  }
  
  // Run the reset function
  resetBalances();
})();
