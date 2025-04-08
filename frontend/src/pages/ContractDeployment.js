import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Box, Button, TextField, Grid, Paper, 
  Stepper, Step, StepLabel, CircularProgress, Alert, Divider,
  FormControl, InputLabel, Select, MenuItem, Tabs, Tab
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(3),
  color: theme.palette.text.primary,
  height: '100%',
}));

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`deployment-tabpanel-${index}`}
      aria-labelledby={`deployment-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ContractDeployment = () => {
  const { currentUser, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [deploymentId, setDeploymentId] = useState(null);
  const [deploymentStatus, setDeploymentStatus] = useState(null);
  const [statusInterval, setStatusInterval] = useState(null);
  
  // Token deployment form
  const [tokenDeployer, setTokenDeployer] = useState('');
  const [tokenPrivateKey, setTokenPrivateKey] = useState('');
  const [tokenNetwork, setTokenNetwork] = useState('ethereum');
  const [tokenTestnet, setTokenTestnet] = useState(true);
  
  // Payment processor deployment form
  const [processorDeployer, setProcessorDeployer] = useState('');
  const [processorFeeRecipient, setProcessorFeeRecipient] = useState('');
  const [processorPrivateKey, setProcessorPrivateKey] = useState('');
  const [processorNetwork, setProcessorNetwork] = useState('ethereum');
  const [processorTestnet, setProcessorTestnet] = useState(true);
  
  // Configure processor form
  const [configProcessorAddress, setConfigProcessorAddress] = useState('');
  const [configTokenAddress, setConfigTokenAddress] = useState('');
  const [configDeployer, setConfigDeployer] = useState('');
  const [configPrivateKey, setConfigPrivateKey] = useState('');
  const [configNetwork, setConfigNetwork] = useState('ethereum');
  const [configTestnet, setConfigTestnet] = useState(true);
  const [isTokenSupported, setIsTokenSupported] = useState(true);
  const [configSuccess, setConfigSuccess] = useState(null);
  
  // Token list for configuration
  const [tokens, setTokens] = useState([
    { address: '0xdAC17F958D2ee523a2206206994597C13D831ec7', symbol: 'USDT', name: 'Tether USD' },
    { address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', symbol: 'USDC', name: 'USD Coin' },
    { address: '0x6B175474E89094C44Da98b954EedeAC495271d0F', symbol: 'DAI', name: 'Dai Stablecoin' }
  ]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    return () => {
      // Clean up interval when component unmounts
      if (statusInterval) {
        clearInterval(statusInterval);
      }
    };
  }, [navigate, statusInterval, isAuthenticated]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError(null);
    setSuccess(null);
    setConfigSuccess(null);
  };

  const validateEthereumAddress = (address) => {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
  };

  const validateTokenForm = () => {
    if (!validateEthereumAddress(tokenDeployer)) {
      setError('Invalid deployer address format');
      return false;
    }
    
    if (!tokenPrivateKey || tokenPrivateKey.length < 64) {
      setError('Invalid private key');
      return false;
    }
    
    return true;
  };

  const validateProcessorForm = () => {
    if (!validateEthereumAddress(processorDeployer)) {
      setError('Invalid deployer address format');
      return false;
    }
    
    if (!validateEthereumAddress(processorFeeRecipient)) {
      setError('Invalid fee recipient address format');
      return false;
    }
    
    if (!processorPrivateKey || processorPrivateKey.length < 64) {
      setError('Invalid private key');
      return false;
    }
    
    return true;
  };

  const validateConfigForm = () => {
    if (!validateEthereumAddress(configProcessorAddress)) {
      setError('Invalid processor address format');
      return false;
    }
    
    if (!validateEthereumAddress(configTokenAddress)) {
      setError('Invalid token address format');
      return false;
    }
    
    if (!validateEthereumAddress(configDeployer)) {
      setError('Invalid deployer address format');
      return false;
    }
    
    if (!configPrivateKey || configPrivateKey.length < 64) {
      setError('Invalid private key');
      return false;
    }
    
    return true;
  };

  const deployToken = async () => {
    if (!validateTokenForm()) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      const response = await api.post('/deployment/token', {
        deployer_address: tokenDeployer,
        private_key: tokenPrivateKey,
        network: tokenNetwork,
        testnet: tokenTestnet
      });

      if (response.status === 200 || response.status === 201) {
        const data = response.data;
        setDeploymentId(data.deployment_id);
        setSuccess(`Token deployment started with ID: ${data.deployment_id}`);
        
        // Start checking status
        const interval = setInterval(() => {
          checkDeploymentStatus(data.deployment_id);
        }, 5000);
        
        setStatusInterval(interval);
      } else {
        setError('Failed to start token deployment');
      }
    } catch (err) {
      setError('An error occurred while starting deployment');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deployProcessor = async () => {
    if (!validateProcessorForm()) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      const response = await api.post('/deployment/processor', {
        deployer_address: processorDeployer,
        fee_recipient: processorFeeRecipient,
        private_key: processorPrivateKey,
        network: processorNetwork,
        testnet: processorTestnet
      });

      if (response.status === 200 || response.status === 201) {
        const data = response.data;
        setDeploymentId(data.deployment_id);
        setSuccess(`Payment processor deployment started with ID: ${data.deployment_id}`);
        
        // Start checking status
        const interval = setInterval(() => {
          checkDeploymentStatus(data.deployment_id);
        }, 5000);
        
        setStatusInterval(interval);
      } else {
        setError('Failed to start payment processor deployment');
      }
    } catch (err) {
      setError('An error occurred while starting deployment');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const configureProcessor = async () => {
    if (!validateConfigForm()) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setConfigSuccess(null);
      
      const response = await api.post('/deployment/processor/configure', {
        processor_address: configProcessorAddress,
        token_address: configTokenAddress,
        deployer_address: configDeployer,
        private_key: configPrivateKey,
        network: configNetwork,
        testnet: configTestnet,
        is_supported: isTokenSupported
      });

      if (response.status === 200 || response.status === 201) {
        const data = response.data;
        setConfigSuccess(`Processor configuration successful! Transaction hash: ${data.transaction_hash}`);
      } else {
        setError('Failed to configure payment processor');
      }
    } catch (err) {
      setError('An error occurred while configuring the processor');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const checkDeploymentStatus = async (id) => {
    try {
      const response = await api.get(`/deployment/status/${id}`);
      
      if (response.status === 200) {
        const status = response.data;
        setDeploymentStatus(status);
        
        // If deployment is completed or failed, clear the interval
        if (status.status === 'completed' || status.status === 'failed') {
          if (statusInterval) {
            clearInterval(statusInterval);
            setStatusInterval(null);
          }
        }
      }
    } catch (err) {
      console.error('Error checking deployment status:', err);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Typography variant="h4" gutterBottom>
          Smart Contract Deployment
        </Typography>
        
        <Typography variant="body1" gutterBottom color="textSecondary">
          Deploy and manage TerraFlow smart contracts.
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 4 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="deployment tabs"
          >
            <Tab label="Deploy Token" />
            <Tab label="Deploy Payment Processor" />
            <Tab label="Configure Processor" />
            <Tab label="Deployment Status" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Deploy TerraFlow Token Contract
          </Typography>
          
          <Typography variant="body2" paragraph>
            This will deploy the TerraFlow ERC20 token contract to the selected network.
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ my: 2 }}>
              {error}
            </Alert>
          )}
          
          {success && !error && (
            <Alert severity="success" sx={{ my: 2 }}>
              {success}
            </Alert>
          )}
          
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Deployer Address"
                value={tokenDeployer}
                onChange={(e) => setTokenDeployer(e.target.value)}
                placeholder="0x..."
                helperText="Ethereum address that will deploy the contract"
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Network</InputLabel>
                <Select
                  value={tokenNetwork}
                  label="Network"
                  onChange={(e) => setTokenNetwork(e.target.value)}
                >
                  <MenuItem value="ethereum">Ethereum</MenuItem>
                  <MenuItem value="polygon">Polygon</MenuItem>
                  <MenuItem value="avalanche">Avalanche</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Environment</InputLabel>
                <Select
                  value={tokenTestnet}
                  label="Environment"
                  onChange={(e) => setTokenTestnet(e.target.value)}
                >
                  <MenuItem value={true}>Testnet</MenuItem>
                  <MenuItem value={false}>Mainnet (Use with caution!)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="password"
                label="Private Key"
                value={tokenPrivateKey}
                onChange={(e) => setTokenPrivateKey(e.target.value)}
                helperText="The private key is only used to sign transactions and is never stored"
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={deployToken}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Deploy Token Contract'}
              </Button>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Deploy Payment Processor Contract
          </Typography>
          
          <Typography variant="body2" paragraph>
            This will deploy the TerraFlow payment processor contract to the selected network.
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ my: 2 }}>
              {error}
            </Alert>
          )}
          
          {success && !error && (
            <Alert severity="success" sx={{ my: 2 }}>
              {success}
            </Alert>
          )}
          
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Deployer Address"
                value={processorDeployer}
                onChange={(e) => setProcessorDeployer(e.target.value)}
                placeholder="0x..."
                helperText="Ethereum address that will deploy the contract"
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Fee Recipient Address"
                value={processorFeeRecipient}
                onChange={(e) => setProcessorFeeRecipient(e.target.value)}
                placeholder="0x..."
                helperText="Ethereum address that will receive processing fees"
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Network</InputLabel>
                <Select
                  value={processorNetwork}
                  label="Network"
                  onChange={(e) => setProcessorNetwork(e.target.value)}
                >
                  <MenuItem value="ethereum">Ethereum</MenuItem>
                  <MenuItem value="polygon">Polygon</MenuItem>
                  <MenuItem value="avalanche">Avalanche</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Environment</InputLabel>
                <Select
                  value={processorTestnet}
                  label="Environment"
                  onChange={(e) => setProcessorTestnet(e.target.value)}
                >
                  <MenuItem value={true}>Testnet</MenuItem>
                  <MenuItem value={false}>Mainnet (Use with caution!)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="password"
                label="Private Key"
                value={processorPrivateKey}
                onChange={(e) => setProcessorPrivateKey(e.target.value)}
                helperText="The private key is only used to sign transactions and is never stored"
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={deployProcessor}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Deploy Payment Processor'}
              </Button>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Configure Payment Processor
          </Typography>
          
          <Typography variant="body2" paragraph>
            Add or remove supported tokens from an existing payment processor contract.
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ my: 2 }}>
              {error}
            </Alert>
          )}
          
          {configSuccess && !error && (
            <Alert severity="success" sx={{ my: 2 }}>
              {configSuccess}
            </Alert>
          )}
          
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Payment Processor Address"
                value={configProcessorAddress}
                onChange={(e) => setConfigProcessorAddress(e.target.value)}
                placeholder="0x..."
                helperText="Address of the deployed payment processor contract"
                required
              />
            </Grid>
            
            <Grid item xs={12} md={8}>
              <FormControl fullWidth>
                <InputLabel>Token</InputLabel>
                <Select
                  value={configTokenAddress}
                  label="Token"
                  onChange={(e) => setConfigTokenAddress(e.target.value)}
                >
                  {tokens.map(token => (
                    <MenuItem key={token.address} value={token.address}>
                      {token.symbol} - {token.name} ({token.address})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Token Status</InputLabel>
                <Select
                  value={isTokenSupported}
                  label="Token Status"
                  onChange={(e) => setIsTokenSupported(e.target.value)}
                >
                  <MenuItem value={true}>Supported</MenuItem>
                  <MenuItem value={false}>Not Supported</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Owner Address"
                value={configDeployer}
                onChange={(e) => setConfigDeployer(e.target.value)}
                placeholder="0x..."
                helperText="Owner address of the payment processor contract"
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Network</InputLabel>
                <Select
                  value={configNetwork}
                  label="Network"
                  onChange={(e) => setConfigNetwork(e.target.value)}
                >
                  <MenuItem value="ethereum">Ethereum</MenuItem>
                  <MenuItem value="polygon">Polygon</MenuItem>
                  <MenuItem value="avalanche">Avalanche</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Environment</InputLabel>
                <Select
                  value={configTestnet}
                  label="Environment"
                  onChange={(e) => setConfigTestnet(e.target.value)}
                >
                  <MenuItem value={true}>Testnet</MenuItem>
                  <MenuItem value={false}>Mainnet</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="password"
                label="Private Key"
                value={configPrivateKey}
                onChange={(e) => setConfigPrivateKey(e.target.value)}
                helperText="The private key of the contract owner"
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button
                variant="contained"
                color="primary"
                onClick={configureProcessor}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Configure Payment Processor'}
              </Button>
            </Grid>
          </Grid>
        </TabPanel>
        
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Deployment Status
          </Typography>
          
          {!deploymentId && (
            <Alert severity="info" sx={{ my: 2 }}>
              No active deployment. Start a deployment from the "Deploy Token" or "Deploy Payment Processor" tab.
            </Alert>
          )}
          
          {deploymentId && !deploymentStatus && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          )}
          
          {deploymentStatus && (
            <Paper sx={{ p: 3, mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Deployment ID: {deploymentStatus.deployment_id}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Contract:</Typography>
                  <Typography variant="body1">
                    {deploymentStatus.contract_name}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2">Status:</Typography>
                  <Typography 
                    variant="body1" 
                    color={
                      deploymentStatus.status === 'completed' ? 'success.main' : 
                      deploymentStatus.status === 'failed' ? 'error.main' : 
                      'primary.main'
                    }
                    fontWeight="bold"
                  >
                    {deploymentStatus.status.charAt(0).toUpperCase() + deploymentStatus.status.slice(1)}
                  </Typography>
                </Grid>
                
                {deploymentStatus.address && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2">Contract Address:</Typography>
                    <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                      {deploymentStatus.address}
                    </Typography>
                  </Grid>
                )}
                
                {deploymentStatus.transaction_hash && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2">Transaction Hash:</Typography>
                    <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                      {deploymentStatus.transaction_hash}
                    </Typography>
                  </Grid>
                )}
                
                {deploymentStatus.error_message && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="error">Error:</Typography>
                    <Typography variant="body2" color="error">
                      {deploymentStatus.error_message}
                    </Typography>
                  </Grid>
                )}
                
                {deploymentStatus.details && deploymentStatus.details.block_number && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Block Number:</Typography>
                    <Typography variant="body2">
                      {deploymentStatus.details.block_number}
                    </Typography>
                  </Grid>
                )}
                
                {deploymentStatus.details && deploymentStatus.details.gas_used && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Gas Used:</Typography>
                    <Typography variant="body2">
                      {deploymentStatus.details.gas_used}
                    </Typography>
                  </Grid>
                )}
                
                {deploymentStatus.details && deploymentStatus.details.network && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Network:</Typography>
                    <Typography variant="body2">
                      {deploymentStatus.details.network} {deploymentStatus.details.testnet ? '(Testnet)' : '(Mainnet)'}
                    </Typography>
                  </Grid>
                )}
              </Grid>
              
              {deploymentStatus.status === 'pending' || deploymentStatus.status === 'in_progress' ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <CircularProgress size={24} sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Deployment in progress... This may take a few minutes.
                  </Typography>
                </Box>
              ) : null}
            </Paper>
          )}
        </TabPanel>
      </Box>
    </Container>
  );
};

export default ContractDeployment; 