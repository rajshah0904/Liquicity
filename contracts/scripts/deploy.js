// Deployment script for Liquicity Contracts
// Run with: npx hardhat run scripts/deploy.js --network <network_name>

const hre = require("hardhat");

async function main() {
  console.log("Deploying Liquicity contracts...");
  
  // Get the deployer's address
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying contracts with the account: ${deployer.address}`);
  
  // Get contract factories
  const LiquicityToken = await ethers.getContractFactory("LiquicityToken");
  const LiquicityPaymentProcessor = await ethers.getContractFactory("LiquicityPaymentProcessor");
  const LiquicitySwap = await ethers.getContractFactory("LiquicitySwap");
  
  // Deploy Liquicity Token
  console.log("Deploying Liquicity Token...");
  const terraToken = await LiquicityToken.deploy();
  await terraToken.deployed();
  console.log(`Liquicity Token deployed to: ${terraToken.address}`);
  
  // Deploy Payment Processor with fee collector as the deployer
  console.log("Deploying Liquicity Payment Processor...");
  const paymentProcessor = await LiquicityPaymentProcessor.deploy(deployer.address);
  await paymentProcessor.deployed();
  console.log(`Liquicity Payment Processor deployed to: ${paymentProcessor.address}`);
  
  // Deploy Swap contract with fee collector as the deployer
  console.log("Deploying Liquicity Swap...");
  const terraSwap = await LiquicitySwap.deploy(deployer.address);
  await terraSwap.deployed();
  console.log(`Liquicity Swap deployed to: ${terraSwap.address}`);
  
  // Set up initial configuration
  
  // 1. Configure supported tokens in Payment Processor
  console.log("Configuring supported tokens in Payment Processor...");
  
  // Common stablecoin addresses (Ethereum mainnet)
  const USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7";
  const USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48";
  const DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F";
  
  // Add support for stablecoins in Payment Processor
  // Note: These will fail if on a testnet - handle that case in production code
  try {
    await paymentProcessor.setTokenSupport(USDT, true);
    await paymentProcessor.setTokenSupport(USDC, true);
    await paymentProcessor.setTokenSupport(DAI, true);
    console.log("Stablecoins configured in Payment Processor");
  } catch (error) {
    console.log("Error setting token support, might be on testnet:", error.message);
  }
  
  // 2. Configure supported tokens in Swap contract
  console.log("Configuring supported tokens in Swap contract...");
  
  try {
    // USDT: 6 decimals
    await terraSwap.updateStablecoin(USDT, true, 6, 0); 
    
    // USDC: 6 decimals
    await terraSwap.updateStablecoin(USDC, true, 6, 0);
    
    // DAI: 18 decimals
    await terraSwap.updateStablecoin(DAI, true, 18, 0);
    
    console.log("Stablecoins configured in Swap contract");
  } catch (error) {
    console.log("Error setting stablecoin config, might be on testnet:", error.message);
  }
  
  // 3. Mint some tokens for testing (only on testnets)
  if (network.name !== "mainnet") {
    console.log("On testnet, minting TERRA tokens for testing...");
    const mintAmount = ethers.utils.parseEther("1000000"); // 1 million tokens
    await terraToken.mint(deployer.address, mintAmount);
    console.log(`Minted ${ethers.utils.formatEther(mintAmount)} TERRA tokens to ${deployer.address}`);
  }
  
  // Print summary
  console.log("\nDeployment Summary:");
  console.log("====================");
  console.log(`Liquicity Token: ${terraToken.address}`);
  console.log(`Payment Processor: ${paymentProcessor.address}`);
  console.log(`Swap Contract: ${terraSwap.address}`);
  console.log(`Fee Collector: ${deployer.address}`);
  
  // Verify contracts on Etherscan if not on a local network
  if (network.name !== "hardhat" && network.name !== "localhost") {
    console.log("\nVerifying contracts on Etherscan...");
    
    try {
      await hre.run("verify:verify", {
        address: terraToken.address,
        constructorArguments: [],
      });
      
      await hre.run("verify:verify", {
        address: paymentProcessor.address,
        constructorArguments: [deployer.address],
      });
      
      await hre.run("verify:verify", {
        address: terraSwap.address,
        constructorArguments: [deployer.address],
      });
      
      console.log("Contract verification completed");
    } catch (error) {
      console.log("Error during contract verification:", error.message);
    }
  }
}

// We recommend this pattern to be able to use async/await everywhere
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 