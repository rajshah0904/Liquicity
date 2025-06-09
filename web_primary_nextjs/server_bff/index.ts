import dotenv from 'dotenv';
import express from 'express';
import { createServer } from 'http';
import next from 'next';

// Load environment variables
dotenv.config();

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev });
const handle = app.getRequestHandler();
const PORT = process.env.PORT || 8000;

console.log('Liquicity Payment System');
console.log('Environment:', process.env.NODE_ENV || 'development');

// Main application function
async function main() {
  try {
    console.log('Application starting...');
    
    // Prepare Next.js
    await app.prepare();
    
    const server = express();
    
    // Middleware
    server.use(express.json());
    server.use(express.urlencoded({ extended: true }));
    
    // CORS middleware
    server.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
      
      if (req.method === 'OPTIONS') {
        return res.status(200).end();
      }
      next();
    });
    
    // API Routes
    server.get('/api/health', (req, res) => {
      res.json({ status: 'healthy', database: 'connected', version: '0.1.0' });
    });
    
    // User API Routes - handle both /user/register and /user/register/ paths
    server.post(['/user/register', '/user/register/'], (req, res) => {
      console.log('User registration request received:', req.body);
      
      // Always return success response regardless of input
      res.json({
        id: '12345',
        email: req.body.email || 'user@example.com',
        status: 'created',
        created_at: new Date().toISOString()
      });
    });
    
    // User login endpoint
    server.post(['/user/login', '/user/login/'], (req, res) => {
      console.log('User login request received:', req.body);
      
      // Return mock login success
      res.json({
        token: 'mock-jwt-token-for-testing',
        user: {
          id: '12345',
          email: req.body.email || 'user@example.com',
          name: 'Test User'
        }
      });
    });
    
    // Handle all other routes with Next.js
    server.all('*', (req, res) => {
      return handle(req, res);
    });
    
    // Start the server
    createServer(server).listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
    
    console.log('Application initialized successfully.');
  } catch (error) {
    console.error('Error starting application:', error);
    process.exit(1);
  }
}

// Run the application
main().catch(console.error); 