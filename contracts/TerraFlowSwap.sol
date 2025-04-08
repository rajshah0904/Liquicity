// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title TerraFlowSwap
 * @dev Contract for cross-currency stablecoin swaps with oracle-based rates
 */
contract TerraFlowSwap is ReentrancyGuard, Pausable, AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant RATE_PROVIDER_ROLE = keccak256("RATE_PROVIDER_ROLE");
    
    struct StablecoinConfig {
        bool isSupported;
        uint8 decimals;
        // Positive = premium, negative = discount
        int16 exchangeRatePremiumBps; // Basis points adjustment for the exchange rate
    }
    
    // Fee settings
    uint256 public swapFeeBps = 20; // 0.2% in basis points
    uint256 public constant MAX_FEE_BPS = 100; // 1%
    address public feeCollector;
    
    // Token configurations
    mapping(address => StablecoinConfig) public stablecoins;
    
    // Price feed configurations
    mapping(address => mapping(address => address)) public priceFeedRegistry;
    
    // Custom exchange rates (if no oracle available)
    mapping(address => mapping(address => uint256)) public manualExchangeRates;
    
    // Events
    event SwapExecuted(
        address indexed user,
        address indexed sourceToken,
        address indexed targetToken,
        uint256 sourceAmount,
        uint256 targetAmount,
        uint256 fee
    );
    
    event StablecoinUpdated(address token, bool isSupported, uint8 decimals, int16 premiumBps);
    event FeeUpdated(uint256 newFeeBps);
    event FeeCollectorUpdated(address newCollector);
    event PriceFeedUpdated(address sourceToken, address targetToken, address priceFeed);
    event ManualRateUpdated(address sourceToken, address targetToken, uint256 rate);
    
    constructor(address _feeCollector) {
        require(_feeCollector != address(0), "Fee collector cannot be zero");
        feeCollector = _feeCollector;
        
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(ADMIN_ROLE, msg.sender);
        _setupRole(RATE_PROVIDER_ROLE, msg.sender);
    }
    
    /**
     * @dev Swaps one stablecoin for another
     * @param sourceToken Address of the source token
     * @param targetToken Address of the target token
     * @param sourceAmount Amount of source tokens to swap
     * @param minTargetAmount Minimum amount of target tokens to receive (slippage protection)
     */
    function swapStablecoins(
        address sourceToken,
        address targetToken,
        uint256 sourceAmount,
        uint256 minTargetAmount
    ) 
        external
        nonReentrant
        whenNotPaused
        returns (uint256)
    {
        require(stablecoins[sourceToken].isSupported, "Source token not supported");
        require(stablecoins[targetToken].isSupported, "Target token not supported");
        require(sourceAmount > 0, "Amount must be greater than zero");
        
        // Calculate target amount including the exchange rate and fees
        uint256 targetAmount = calculateTargetAmount(sourceToken, targetToken, sourceAmount);
        require(targetAmount >= minTargetAmount, "Slippage tolerance exceeded");
        
        // Calculate fee
        uint256 fee = (targetAmount * swapFeeBps) / 10000;
        uint256 amountAfterFee = targetAmount - fee;
        
        // Transfer source tokens from user to contract
        IERC20(sourceToken).transferFrom(msg.sender, address(this), sourceAmount);
        
        // Send target tokens minus fee to user
        IERC20(targetToken).transfer(msg.sender, amountAfterFee);
        
        // Send fee to collector
        if (fee > 0) {
            IERC20(targetToken).transfer(feeCollector, fee);
        }
        
        emit SwapExecuted(
            msg.sender,
            sourceToken,
            targetToken,
            sourceAmount,
            amountAfterFee,
            fee
        );
        
        return amountAfterFee;
    }
    
    /**
     * @dev Calculate target amount based on exchange rate
     * @param sourceToken Address of the source token
     * @param targetToken Address of the target token
     * @param sourceAmount Amount of source tokens
     */
    function calculateTargetAmount(
        address sourceToken,
        address targetToken,
        uint256 sourceAmount
    ) 
        public
        view
        returns (uint256)
    {
        uint256 exchangeRate = getExchangeRate(sourceToken, targetToken);
        
        // Adjust for decimal differences between tokens
        uint8 sourceDecimals = stablecoins[sourceToken].decimals;
        uint8 targetDecimals = stablecoins[targetToken].decimals;
        
        uint256 normalizedAmount;
        if (sourceDecimals > targetDecimals) {
            normalizedAmount = sourceAmount / (10 ** (sourceDecimals - targetDecimals));
        } else if (targetDecimals > sourceDecimals) {
            normalizedAmount = sourceAmount * (10 ** (targetDecimals - sourceDecimals));
        } else {
            normalizedAmount = sourceAmount;
        }
        
        // Apply the exchange rate
        uint256 baseTargetAmount = (normalizedAmount * exchangeRate) / 1e18;
        
        // Apply premium/discount
        int16 premium = stablecoins[targetToken].exchangeRatePremiumBps;
        if (premium > 0) {
            return baseTargetAmount + ((baseTargetAmount * uint256(premium)) / 10000);
        } else if (premium < 0) {
            return baseTargetAmount - ((baseTargetAmount * uint256(-premium)) / 10000);
        } else {
            return baseTargetAmount;
        }
    }
    
    /**
     * @dev Get exchange rate between two tokens with 18 decimals precision
     * @param sourceToken Address of the source token
     * @param targetToken Address of the target token
     */
    function getExchangeRate(address sourceToken, address targetToken) 
        public
        view
        returns (uint256)
    {
        // Check if we have a Chainlink price feed
        address priceFeed = priceFeedRegistry[sourceToken][targetToken];
        
        if (priceFeed != address(0)) {
            return getChainlinkRate(priceFeed);
        }
        
        // Check if we have a manual rate
        uint256 manualRate = manualExchangeRates[sourceToken][targetToken];
        if (manualRate > 0) {
            return manualRate;
        }
        
        // For stablecoins, default to 1:1 (with 18 decimals precision)
        return 1e18;
    }
    
    /**
     * @dev Get rate from Chainlink price feed with 18 decimals precision
     * @param priceFeed Address of the Chainlink price feed
     */
    function getChainlinkRate(address priceFeed) internal view returns (uint256) {
        AggregatorV3Interface feed = AggregatorV3Interface(priceFeed);
        (, int256 price, , , ) = feed.latestRoundData();
        uint8 decimals = feed.decimals();
        
        // Convert to 18 decimals
        if (decimals < 18) {
            return uint256(price) * (10 ** (18 - decimals));
        } else if (decimals > 18) {
            return uint256(price) / (10 ** (decimals - 18));
        } else {
            return uint256(price);
        }
    }
    
    /**
     * @dev Update stablecoin configuration
     * @param token Token address
     * @param isSupported Whether the token is supported
     * @param decimals Token decimals
     * @param premiumBps Exchange rate premium/discount in basis points
     */
    function updateStablecoin(
        address token,
        bool isSupported,
        uint8 decimals,
        int16 premiumBps
    ) 
        external
        onlyRole(ADMIN_ROLE)
    {
        require(token != address(0), "Invalid token address");
        require(premiumBps >= -1000 && premiumBps <= 1000, "Premium out of range"); // ±10% max
        
        stablecoins[token] = StablecoinConfig({
            isSupported: isSupported,
            decimals: decimals,
            exchangeRatePremiumBps: premiumBps
        });
        
        emit StablecoinUpdated(token, isSupported, decimals, premiumBps);
    }
    
    /**
     * @dev Update price feed
     * @param sourceToken Source token
     * @param targetToken Target token
     * @param priceFeed Chainlink price feed address
     */
    function updatePriceFeed(
        address sourceToken,
        address targetToken,
        address priceFeed
    )
        external
        onlyRole(ADMIN_ROLE)
    {
        priceFeedRegistry[sourceToken][targetToken] = priceFeed;
        emit PriceFeedUpdated(sourceToken, targetToken, priceFeed);
    }
    
    /**
     * @dev Update manual exchange rate
     * @param sourceToken Source token
     * @param targetToken Target token
     * @param rate Exchange rate with 18 decimals precision
     */
    function updateManualRate(
        address sourceToken,
        address targetToken,
        uint256 rate
    )
        external
        onlyRole(RATE_PROVIDER_ROLE)
    {
        require(rate > 0, "Rate must be positive");
        manualExchangeRates[sourceToken][targetToken] = rate;
        emit ManualRateUpdated(sourceToken, targetToken, rate);
    }
    
    /**
     * @dev Update swap fee
     * @param newFeeBps New fee in basis points
     */
    function updateSwapFee(uint256 newFeeBps) external onlyRole(ADMIN_ROLE) {
        require(newFeeBps <= MAX_FEE_BPS, "Fee exceeds maximum");
        swapFeeBps = newFeeBps;
        emit FeeUpdated(newFeeBps);
    }
    
    /**
     * @dev Update fee collector
     * @param newCollector New fee collector address
     */
    function updateFeeCollector(address newCollector) external onlyRole(ADMIN_ROLE) {
        require(newCollector != address(0), "Invalid address");
        feeCollector = newCollector;
        emit FeeCollectorUpdated(newCollector);
    }
    
    /**
     * @dev Pause the contract
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause the contract
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Emergency function to recover tokens
     * @param token Token address
     * @param to Recipient address
     * @param amount Amount to recover
     */
    function recoverERC20(address token, address to, uint256 amount) 
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        IERC20(token).transfer(to, amount);
    }
} 