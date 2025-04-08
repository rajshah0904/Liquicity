// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TerraFlowPaymentProcessor
 * @dev Contract for processing payments in various stablecoins
 */
contract TerraFlowPaymentProcessor is ReentrancyGuard, Pausable, Ownable {
    // Fee configuration
    uint256 public processingFeePercentage = 50; // 0.5% (in basis points, 10000 = 100%)
    uint256 public constant MAX_FEE_PERCENTAGE = 500; // 5% maximum fee
    
    // Platform fee recipient
    address public feeRecipient;
    
    // Supported tokens mapping (token address => supported)
    mapping(address => bool) public supportedTokens;
    
    // Events
    event PaymentProcessed(
        address indexed from,
        address indexed to,
        address indexed tokenAddress,
        uint256 amount,
        uint256 fee,
        string reference
    );
    
    event TokenSupportChanged(address tokenAddress, bool isSupported);
    event FeeUpdated(uint256 newFeePercentage);
    event FeeRecipientUpdated(address newFeeRecipient);
    
    constructor(address _feeRecipient) {
        require(_feeRecipient != address(0), "Fee recipient cannot be zero address");
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Process a payment in the specified token
     * @param tokenAddress The ERC20 token address to use for payment
     * @param recipient The payment recipient
     * @param amount The payment amount
     * @param reference A reference string for the payment
     */
    function processPayment(
        address tokenAddress,
        address recipient,
        uint256 amount,
        string memory reference
    ) 
        external
        nonReentrant
        whenNotPaused
    {
        require(supportedTokens[tokenAddress], "Token not supported");
        require(recipient != address(0), "Recipient cannot be zero address");
        require(amount > 0, "Amount must be greater than zero");
        
        IERC20 token = IERC20(tokenAddress);
        
        // Calculate fee
        uint256 fee = (amount * processingFeePercentage) / 10000;
        uint256 recipientAmount = amount - fee;
        
        // Transfer tokens from sender to contract
        require(token.transferFrom(msg.sender, address(this), amount), "Token transfer failed");
        
        // Send amount minus fee to recipient
        require(token.transfer(recipient, recipientAmount), "Recipient transfer failed");
        
        // Send fee to fee recipient
        if (fee > 0) {
            require(token.transfer(feeRecipient, fee), "Fee transfer failed");
        }
        
        emit PaymentProcessed(
            msg.sender,
            recipient,
            tokenAddress,
            amount,
            fee,
            reference
        );
    }
    
    /**
     * @dev Add or remove support for a token
     * @param tokenAddress The ERC20 token address
     * @param isSupported Whether the token is supported
     */
    function setTokenSupport(address tokenAddress, bool isSupported) external onlyOwner {
        require(tokenAddress != address(0), "Token address cannot be zero");
        supportedTokens[tokenAddress] = isSupported;
        emit TokenSupportChanged(tokenAddress, isSupported);
    }
    
    /**
     * @dev Update the processing fee percentage (in basis points)
     * @param newFeePercentage The new fee percentage
     */
    function updateFeePercentage(uint256 newFeePercentage) external onlyOwner {
        require(newFeePercentage <= MAX_FEE_PERCENTAGE, "Fee exceeds maximum");
        processingFeePercentage = newFeePercentage;
        emit FeeUpdated(newFeePercentage);
    }
    
    /**
     * @dev Update the fee recipient address
     * @param newFeeRecipient The new fee recipient
     */
    function updateFeeRecipient(address newFeeRecipient) external onlyOwner {
        require(newFeeRecipient != address(0), "Fee recipient cannot be zero address");
        feeRecipient = newFeeRecipient;
        emit FeeRecipientUpdated(newFeeRecipient);
    }
    
    /**
     * @dev Pause the contract
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause the contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Emergency function to recover any ERC20 tokens sent to this contract
     * @param tokenAddress The ERC20 token address
     * @param recipient The address to send the tokens to
     * @param amount The amount to recover
     */
    function recoverTokens(address tokenAddress, address recipient, uint256 amount) external onlyOwner {
        require(recipient != address(0), "Recipient cannot be zero address");
        IERC20 token = IERC20(tokenAddress);
        require(token.transfer(recipient, amount), "Token recovery failed");
    }
} 