/**
 * WalletConnect v2 Microservice
 * Production-level microservice for WalletConnect v2 integration
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { body, validationResult } from 'express-validator';
import WebSocket from 'ws';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import winston from 'winston';
import Joi from 'joi';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import Redis from 'redis';

// WalletConnect imports
import { Web3Wallet } from '@walletconnect/web3wallet';
import { Core } from '@walletconnect/core';
import { WebSocketProvider } from '@walletconnect/web3-provider';

// Load environment variables
dotenv.config();

// Configure logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'walletconnect-microservice' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:8000'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Initialize Redis client
const redisClient = Redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redisClient.on('error', (err) => logger.error('Redis Client Error', err));
redisClient.on('connect', () => logger.info('Connected to Redis'));

// Initialize WalletConnect
let web3wallet;
let core;

async function initializeWalletConnect() {
  try {
    core = new Core({
      projectId: process.env.WALLETCONNECT_PROJECT_ID,
      relayUrl: process.env.WALLETCONNECT_RELAY_URL || 'wss://relay.walletconnect.com'
    });

    web3wallet = await Web3Wallet.init({
      core,
      metadata: {
        name: 'Liquicity Bridge',
        description: 'Cross-border crypto payments',
        url: 'https://liquicity.com',
        icons: ['https://liquicity.com/icon.png']
      }
    });

    logger.info('WalletConnect initialized successfully');

    // Set up event listeners
    web3wallet.on('session_proposal', handleSessionProposal);
    web3wallet.on('session_request', handleSessionRequest);
    web3wallet.on('session_delete', handleSessionDelete);
    web3wallet.on('session_expire', handleSessionExpire);

  } catch (error) {
    logger.error('Failed to initialize WalletConnect:', error);
    process.exit(1);
  }
}

// Session storage (in production, use Redis)
const sessions = new Map();
const pendingRequests = new Map();

// Validation schemas
const createSessionSchema = Joi.object({
  user_id: Joi.string().required(),
  wallet_address: Joi.string().required(),
  chain_type: Joi.string().valid('evm', 'solana').required(),
  chain_id: Joi.string().required()
});

const transactionRequestSchema = Joi.object({
  session_id: Joi.string().required(),
  to_address: Joi.string().required(),
  amount: Joi.string().required(),
  currency: Joi.string().default('usdc'),
  gas_estimate: Joi.object().optional()
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'Internal server error',
      details: process.env.NODE_ENV === 'development' ? err.message : undefined
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'WalletConnect Microservice',
    version: '1.0.0'
  });
});

// Create WalletConnect session
app.post('/api/v1/sessions', 
  body('user_id').isString().notEmpty(),
  body('wallet_address').isString().notEmpty(),
  body('chain_type').isIn(['evm', 'solana']),
  body('chain_id').isString().notEmpty(),
  async (req, res) => {
    try {
      // Validate request
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid request data',
            details: errors.array()
          }
        });
      }

      const { user_id, wallet_address, chain_type, chain_id } = req.body;

      // Validate with Joi
      const { error } = createSessionSchema.validate(req.body);
      if (error) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid request data',
            details: error.details
          }
        });
      }

      // Create session
      const sessionId = uuidv4();
      const session = {
        id: sessionId,
        user_id,
        wallet_address,
        chain_type,
        chain_id,
        status: 'pending',
        topic: null,
        created_at: new Date(),
        expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours
      };

      // Store session
      sessions.set(sessionId, session);
      await redisClient.setEx(`session:${sessionId}`, 86400, JSON.stringify(session));

      // Generate QR code URI
      const uri = generateWalletConnectURI(session);

      logger.info(`Created session ${sessionId} for user ${user_id}`);

      res.json({
        success: true,
        data: {
          session_id: sessionId,
          uri,
          status: session.status,
          expires_at: session.expires_at.toISOString()
        }
      });

    } catch (error) {
      logger.error('Session creation error:', error);
      res.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Failed to create session'
        }
      });
    }
  }
);

// Get session status
app.get('/api/v1/sessions/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;

    // Try Redis first, then memory
    let sessionData = await redisClient.get(`session:${sessionId}`);
    let session = sessionData ? JSON.parse(sessionData) : sessions.get(sessionId);

    if (!session) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'SESSION_NOT_FOUND',
          message: 'Session not found'
        }
      });
    }

    // Check if expired
    if (new Date() > new Date(session.expires_at)) {
      session.status = 'expired';
      await redisClient.setEx(`session:${sessionId}`, 86400, JSON.stringify(session));
    }

    res.json({
      success: true,
      data: session
    });

  } catch (error) {
    logger.error('Session status error:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to get session status'
      }
    });
  }
});

// Create transaction request
app.post('/api/v1/transactions',
  body('session_id').isString().notEmpty(),
  body('to_address').isString().notEmpty(),
  body('amount').isString().notEmpty(),
  body('currency').optional().isString(),
  body('gas_estimate').optional().isObject(),
  async (req, res) => {
    try {
      // Validate request
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid request data',
            details: errors.array()
          }
        });
      }

      const { session_id, to_address, amount, currency = 'usdc', gas_estimate } = req.body;

      // Validate with Joi
      const { error } = transactionRequestSchema.validate(req.body);
      if (error) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid request data',
            details: error.details
          }
        });
      }

      // Check session
      let sessionData = await redisClient.get(`session:${session_id}`);
      let session = sessionData ? JSON.parse(sessionData) : sessions.get(session_id);

      if (!session) {
        return res.status(404).json({
          success: false,
          error: {
            code: 'SESSION_NOT_FOUND',
            message: 'Session not found'
          }
        });
      }

      if (session.status !== 'approved') {
        return res.status(400).json({
          success: false,
          error: {
            code: 'SESSION_NOT_APPROVED',
            message: 'Session not approved'
          }
        });
      }

      // Create transaction request
      const requestId = uuidv4();
      const transactionRequest = {
        id: requestId,
        session_id,
        to_address,
        amount,
        currency,
        gas_estimate,
        status: 'pending',
        created_at: new Date(),
        expires_at: new Date(Date.now() + 30 * 60 * 1000) // 30 minutes
      };

      // Store request
      pendingRequests.set(requestId, transactionRequest);
      await redisClient.setEx(`transaction:${requestId}`, 1800, JSON.stringify(transactionRequest));

      // Send to wallet via WalletConnect
      await sendTransactionRequest(session, transactionRequest);

      logger.info(`Created transaction request ${requestId} for session ${session_id}`);

      res.json({
        success: true,
        data: {
          request_id: requestId,
          status: transactionRequest.status,
          expires_at: transactionRequest.expires_at.toISOString()
        }
      });

    } catch (error) {
      logger.error('Transaction request error:', error);
      res.status(500).json({
        success: false,
        error: {
          code: 'INTERNAL_ERROR',
          message: 'Failed to create transaction request'
        }
      });
    }
  }
);

// Get transaction status
app.get('/api/v1/transactions/:requestId', async (req, res) => {
  try {
    const { requestId } = req.params;

    // Try Redis first, then memory
    let requestData = await redisClient.get(`transaction:${requestId}`);
    let transactionRequest = requestData ? JSON.parse(requestData) : pendingRequests.get(requestId);

    if (!transactionRequest) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'TRANSACTION_NOT_FOUND',
          message: 'Transaction request not found'
        }
      });
    }

    res.json({
      success: true,
      data: transactionRequest
    });

  } catch (error) {
    logger.error('Transaction status error:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to get transaction status'
      }
    });
  }
});

// Disconnect session
app.delete('/api/v1/sessions/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;

    // Try Redis first, then memory
    let sessionData = await redisClient.get(`session:${sessionId}`);
    let session = sessionData ? JSON.parse(sessionData) : sessions.get(sessionId);

    if (!session) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'SESSION_NOT_FOUND',
          message: 'Session not found'
        }
      });
    }

    // Disconnect from WalletConnect
    if (session.topic) {
      try {
        await web3wallet.disconnectSession({
          topic: session.topic,
          reason: {
            code: 6000,
            message: 'User disconnected'
          }
        });
      } catch (error) {
        logger.warn('Failed to disconnect WalletConnect session:', error);
      }
    }

    // Update session status
    session.status = 'disconnected';
    session.disconnected_at = new Date();

    // Store updated session
    await redisClient.setEx(`session:${sessionId}`, 86400, JSON.stringify(session));
    sessions.set(sessionId, session);

    logger.info(`Disconnected session ${sessionId}`);

    res.json({
      success: true,
      message: 'Session disconnected successfully'
    });

  } catch (error) {
    logger.error('Session disconnect error:', error);
    res.status(500).json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'Failed to disconnect session'
      }
    });
  }
});

// WalletConnect event handlers
async function handleSessionProposal(proposal) {
  try {
    logger.info('Session proposal received:', proposal.id);
    
    // In production, you might want to validate the proposal
    // For now, we'll auto-approve
    const session = await web3wallet.approveSession({
      id: proposal.id,
      namespaces: proposal.params.requiredNamespaces
    });

    logger.info('Session approved:', session.topic);

    // Find and update our session
    for (const [sessionId, sessionData] of sessions.entries()) {
      if (sessionData.status === 'pending') {
        sessionData.status = 'approved';
        sessionData.topic = session.topic;
        sessionData.approved_at = new Date();
        
        await redisClient.setEx(`session:${sessionId}`, 86400, JSON.stringify(sessionData));
        sessions.set(sessionId, sessionData);
        break;
      }
    }

  } catch (error) {
    logger.error('Session proposal handling error:', error);
  }
}

async function handleSessionRequest(requestEvent) {
  try {
    logger.info('Session request received:', requestEvent.id);
    
    // Handle different request types
    const { topic, request } = requestEvent;
    
    if (request.method === 'eth_sendTransaction') {
      // Handle EVM transaction
      await handleEVMTransaction(topic, request);
    } else if (request.method === 'solana_signTransaction') {
      // Handle Solana transaction
      await handleSolanaTransaction(topic, request);
    } else {
      // Reject unsupported methods
      await web3wallet.respondSessionRequest({
        topic,
        response: {
          id: request.id,
          jsonrpc: '2.0',
          error: {
            code: 4200,
            message: 'Method not supported'
          }
        }
      });
    }

  } catch (error) {
    logger.error('Session request handling error:', error);
  }
}

async function handleSessionDelete(session) {
  try {
    logger.info('Session deleted:', session.topic);
    
    // Update session status
    for (const [sessionId, sessionData] of sessions.entries()) {
      if (sessionData.topic === session.topic) {
        sessionData.status = 'disconnected';
        sessionData.disconnected_at = new Date();
        
        await redisClient.setEx(`session:${sessionId}`, 86400, JSON.stringify(sessionData));
        sessions.set(sessionId, sessionData);
        break;
      }
    }

  } catch (error) {
    logger.error('Session delete handling error:', error);
  }
}

async function handleSessionExpire(session) {
  try {
    logger.info('Session expired:', session.topic);
    
    // Update session status
    for (const [sessionId, sessionData] of sessions.entries()) {
      if (sessionData.topic === session.topic) {
        sessionData.status = 'expired';
        
        await redisClient.setEx(`session:${sessionId}`, 86400, JSON.stringify(sessionData));
        sessions.set(sessionId, sessionData);
        break;
      }
    }

  } catch (error) {
    logger.error('Session expire handling error:', error);
  }
}

// Helper functions
function generateWalletConnectURI(session) {
  const projectId = process.env.WALLETCONNECT_PROJECT_ID;
  const relayUrl = process.env.WALLETCONNECT_RELAY_URL || 'wss://relay.walletconnect.com';
  
  return `wc:${projectId}@2?relay-protocol=irn&symKey=${generateSymKey()}&chainId=${session.chain_id}&session_id=${session.id}`;
}

function generateSymKey() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

async function sendTransactionRequest(session, transactionRequest) {
  try {
    if (!session.topic) {
      throw new Error('Session not connected');
    }

    // Create transaction request for wallet
    const request = {
      id: transactionRequest.id,
      jsonrpc: '2.0',
      method: session.chain_type === 'evm' ? 'eth_sendTransaction' : 'solana_signTransaction',
      params: {
        from: session.wallet_address,
        to: transactionRequest.to_address,
        value: '0x0', // USDC transfers have 0 value
        data: '0x', // Would be actual transaction data
        gas: transactionRequest.gas_estimate?.gas_limit || '0x186a0',
        gasPrice: transactionRequest.gas_estimate?.gas_price || '0x'
      }
    };

    await web3wallet.requestSession({
      topic: session.topic,
      request
    });

    logger.info(`Sent transaction request ${transactionRequest.id} to wallet`);

  } catch (error) {
    logger.error('Failed to send transaction request:', error);
    throw error;
  }
}

async function handleEVMTransaction(topic, request) {
  try {
    // In production, you'd validate and process the transaction
    // For now, we'll just log it
    logger.info('EVM transaction request:', request);
    
    // Update transaction request status
    const requestId = request.id;
    let requestData = await redisClient.get(`transaction:${requestId}`);
    let transactionRequest = requestData ? JSON.parse(requestData) : pendingRequests.get(requestId);
    
    if (transactionRequest) {
      transactionRequest.status = 'signed';
      transactionRequest.signed_transaction = request.params[0];
      
      await redisClient.setEx(`transaction:${requestId}`, 1800, JSON.stringify(transactionRequest));
      pendingRequests.set(requestId, transactionRequest);
    }

  } catch (error) {
    logger.error('EVM transaction handling error:', error);
  }
}

async function handleSolanaTransaction(topic, request) {
  try {
    // In production, you'd validate and process the transaction
    // For now, we'll just log it
    logger.info('Solana transaction request:', request);
    
    // Update transaction request status
    const requestId = request.id;
    let requestData = await redisClient.get(`transaction:${requestId}`);
    let transactionRequest = requestData ? JSON.parse(requestData) : pendingRequests.get(requestId);
    
    if (transactionRequest) {
      transactionRequest.status = 'signed';
      transactionRequest.signed_transaction = request.params[0];
      
      await redisClient.setEx(`transaction:${requestId}`, 1800, JSON.stringify(transactionRequest));
      pendingRequests.set(requestId, transactionRequest);
    }

  } catch (error) {
    logger.error('Solana transaction handling error:', error);
  }
}

// Cleanup expired sessions and requests
async function cleanupExpired() {
  try {
    const now = new Date();
    
    // Clean up expired sessions
    for (const [sessionId, session] of sessions.entries()) {
      if (new Date(session.expires_at) < now) {
        sessions.delete(sessionId);
        await redisClient.del(`session:${sessionId}`);
        logger.info(`Cleaned up expired session ${sessionId}`);
      }
    }
    
    // Clean up expired transaction requests
    for (const [requestId, request] of pendingRequests.entries()) {
      if (new Date(request.expires_at) < now) {
        pendingRequests.delete(requestId);
        await redisClient.del(`transaction:${requestId}`);
        logger.info(`Cleaned up expired transaction request ${requestId}`);
      }
    }
    
  } catch (error) {
    logger.error('Cleanup error:', error);
  }
}

// Start server
async function startServer() {
  try {
    // Connect to Redis
    await redisClient.connect();
    
    // Initialize WalletConnect
    await initializeWalletConnect();
    
    // Start cleanup interval
    setInterval(cleanupExpired, 5 * 60 * 1000); // Every 5 minutes
    
    // Start server
    app.listen(PORT, () => {
      logger.info(`WalletConnect microservice running on port ${PORT}`);
      logger.info(`Health check: http://localhost:${PORT}/health`);
    });
    
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully');
  
  if (redisClient) {
    await redisClient.quit();
  }
  
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully');
  
  if (redisClient) {
    await redisClient.quit();
  }
  
  process.exit(0);
});

// Start the server
startServer(); 