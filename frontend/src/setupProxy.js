const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Main API endpoints
  app.use(
    '/user',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true
    })
  );
  
  app.use(
    '/wallet',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true
    })
  );
  
  app.use(
    '/payment',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true
    })
  );
  
  app.use(
    '/kyc',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      pathRewrite: {
        '^/kyc': '/user/kyc'  // Rewrite /kyc to /user/kyc on the backend
      },
      changeOrigin: true
    })
  );
  
  // Handle the incorrect /submit path that should be /kyc/submit
  app.use(
    '/submit',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      pathRewrite: {
        '^/submit': '/user/kyc/submit'  // Rewrite /submit to /user/kyc/submit on the backend
      },
      changeOrigin: true
    })
  );
  
  // Add any other API routes you need to proxy
}; 