// Reset script for Liquicity balance issues
// This script will run automatically when included in the page

(function() {
  // Function to reset balances
  async function resetBalances() {
    console.log("🔄 Checking and resetting Liquicity balances...");
    
    // Set new balances with high values
    const newBalances = {
      'user@example.com': { usd: 5000.00, eur: 0 },
      'rajshah11@gmail.com': { usd: 1000.00, eur: 0 },
      'hadeermotair@gmail.com': { usd: 0, eur: 0 }
    };
    
    // Save to localStorage as fallback
    localStorage.removeItem('mockUserBalances');
    localStorage.removeItem('mockTransactions');
    localStorage.setItem('mockUserBalances', JSON.stringify(newBalances));
    
    // Try to update balances on the backend
    try {
      for (const [email, balance] of Object.entries(newBalances)) {
        await fetch(`/mock/wallet/balances/${email}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(balance),
        });
      }
      console.log("💰 Balances reset with new values via backend API:", newBalances);
    } catch (error) {
      console.error("Error resetting balances via API:", error);
      console.log("Falling back to localStorage only");
    }
    
    // Create global reset function for debugging
    window.resetLiquicityData = async function() {
      await resetBalances();
      window.location.reload();
      return "Balances reset and page reloaded!";
    };
    
    console.log("✅ Reset complete! Use window.resetLiquicityData() in console to manually reset.");
  }
  
  // Only run automatic reset if no balances exist yet
  if (!localStorage.getItem('mockUserBalances')) {
    resetBalances();
  } else {
    // Still expose manual reset helper
    window.resetLiquicityData = async function() {
      await resetBalances();
      window.location.reload();
      return "Balances reset and page reloaded!";
    };
  }
})();
