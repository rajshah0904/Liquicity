import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  TextField,
  Grid,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ArrowBack, AccountBalance, Link as LinkIcon } from '@mui/icons-material';
import { externalAccountsAPI } from '../../utils/api';
import { SEPA_COUNTRIES, getCountryCodeFromName } from '../../utils/bankingRegions';

export default function LinkBankEU() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [linkingMethod, setLinkingMethod] = useState('method-selection'); // 'method-selection', 'plaid', 'manual'
  
  // Address autocomplete ref
  const addressInputRef = useRef(null);
  const autocompleteRef = useRef(null);

  const [formData, setFormData] = useState({
    bank_name: '',
    first_name: '',
    last_name: '',
    account_name: '',
    iban_account_number: '',
    bic: '',
    iban_country: '',
    address: '',
    // Parsed address components (filled by Google Maps)
    parsed_address: {
      street_line_1: '',
      city: '',
      state: '',
      postal_code: '',
      country: ''
    }
  });

  const handleBack = () => {
    if (linkingMethod === 'method-selection') {
      navigate('/wallet/link-bank');
    } else {
      setLinkingMethod('method-selection');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Load Google Maps API and initialize autocomplete
  useEffect(() => {
    const loadGoogleMapsAPI = () => {
      return new Promise((resolve, reject) => {
        if (window.google && window.google.maps && window.google.maps.places) {
          resolve();
          return;
        }

        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&libraries=places`;
        script.async = true;
        script.defer = true;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    };

    const initializeAutocomplete = () => {
      if (addressInputRef.current && window.google && window.google.maps && window.google.maps.places) {
        autocompleteRef.current = new window.google.maps.places.Autocomplete(
          addressInputRef.current,
          {
            types: ['address'],
            fields: ['address_components', 'formatted_address']
          }
        );

        autocompleteRef.current.addListener('place_changed', () => {
          const place = autocompleteRef.current.getPlace();
          if (place.address_components) {
            const addressComponents = place.address_components;
            const parsed = {
              street_line_1: '',
              city: '',
              state: '',
              postal_code: '',
              country: ''
            };

            // Parse address components
            addressComponents.forEach(component => {
              const types = component.types;
              if (types.includes('street_number')) {
                parsed.street_line_1 = component.long_name + ' ' + parsed.street_line_1;
              }
              if (types.includes('route')) {
                parsed.street_line_1 += component.long_name;
              }
              if (types.includes('locality')) {
                parsed.city = component.long_name;
              }
              if (types.includes('administrative_area_level_1')) {
                parsed.state = component.long_name;
              }
              if (types.includes('postal_code')) {
                parsed.postal_code = component.long_name;
              }
              if (types.includes('country')) {
                parsed.country = component.short_name;
              }
            });

            setFormData(prev => ({
              ...prev,
              address: place.formatted_address,
              parsed_address: {
                ...parsed,
                street_line_1: parsed.street_line_1.trim()
              }
            }));
          }
        });
      }
    };

    if (linkingMethod === 'manual') {
      loadGoogleMapsAPI()
        .then(() => {
          // Small delay to ensure the input ref is available
          setTimeout(initializeAutocomplete, 100);
        })
        .catch(error => {
          console.error('Failed to load Google Maps API:', error);
          setError('Failed to load address autocomplete. You can still enter your address manually.');
        });
    }

    // Cleanup
    return () => {
      if (autocompleteRef.current) {
        window.google.maps.event.clearInstanceListeners(autocompleteRef.current);
      }
    };
  }, [linkingMethod]);

  // Initialize Plaid Link for EU (Payment Initiation)
  const initializePlaidEU = async () => {
    try {
      setLoading(true);
      setError(null);

      // Ensure Plaid script is present
      if (!window.Plaid) {
        // Dynamically load Plaid script if missing
        await new Promise((resolve, reject) => {
          const existing = document.getElementById('plaid-script');
          if (existing) {
            existing.addEventListener('load', resolve);
            existing.addEventListener('error', () => reject(new Error('Plaid script failed to load')));
          } else {
            const script = document.createElement('script');
            script.id = 'plaid-script';
            script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
            script.async = true;
            script.onload = resolve;
            script.onerror = () => reject(new Error('Plaid script failed to load'));
            document.body.appendChild(script);
          }
        });
        if (!window.Plaid) throw new Error('Plaid script not available after load');
      }

      // Build redirect URI for OAuth institutions (e.g., Wise)
      const configuredRedirect = process.env.REACT_APP_PLAID_REDIRECT_URI;
      const hasHttpsRedirect = configuredRedirect && configuredRedirect.startsWith('https://');
      const redirectUri = hasHttpsRedirect ? configuredRedirect : undefined;

      // For linking-only: request an EU Auth link token (with Identity) for supported markets (excluding GB)
      const resp = await externalAccountsAPI.getPlaidLinkTokenEU({
        params: {
          mode: 'auth',
          countries: 'AT,BE,DK,EE,FI,FR,DE,IE,IT,LV,LT,NO,PL,PT,ES,SE,NL',
          ...(redirectUri ? { redirect_uri: redirectUri } : {})
        }
      });
      const linkTokenUsed = resp?.data?.link_token;
      if (!linkTokenUsed) throw new Error('Failed to get Plaid EU link token');

      // Detect OAuth redirect return
      const isOAuthRedirect = window.location.href.includes('oauth_state_id=');

      const handler = window.Plaid.create({
        token: linkTokenUsed,
        receivedRedirectUri: isOAuthRedirect ? window.location.href : undefined,
        onSuccess: async (publicToken, metadata) => {
          try {
            const institutionName = metadata?.institution?.name || 'Unknown Bank';
            const institutionId = metadata?.institution?.institution_id || null;
            await externalAccountsAPI.exchangePlaidTokenEUAuth(publicToken, {
              institution_name: institutionName,
              institution_id: institutionId,
            });
            // On success, navigate back and refresh
            navigate('/wallet');
          } catch (err) {
            console.error('Error exchanging Plaid EU token:', err);
            setError('Failed to link bank via Plaid EU. Please try manual entry.');
          }
        },
        onExit: (err) => {
          if (err) {
            console.error('Plaid EU Link exit with error:', err);
            setError('Plaid EU linking canceled or failed. You can try manual entry.');
          }
        },
        onEvent: (eventName, metadata) => {
          console.log('Plaid EU Link Event:', eventName, metadata);
        }
      });

      handler.open();
    } catch (err) {
      console.error('Error initializing Plaid EU:', err);
      setError(err.message || 'Failed to initialize Plaid EU. Please try manual entry.');
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.bank_name || !formData.first_name || !formData.last_name || 
          !formData.iban_account_number || !formData.bic || !formData.iban_country || 
          !formData.address) {
        throw new Error('Please fill in all required fields');
      }

      // Prepare API payload for Bridge API (original Bridge format)
      const payload = {
        currency: 'eur',
        account_type: 'iban',
        bank_name: formData.bank_name,
        account_owner_name: `${formData.first_name} ${formData.last_name}`,
        account_name: formData.account_name || formData.bank_name,
        first_name: formData.first_name,
        last_name: formData.last_name,
        account_owner_type: 'individual',
        iban: {
          account_number: formData.iban_account_number,
          bic: formData.bic,
          country: getCountryCodeFromName(formData.iban_country)
        },
        address: {
          street_line_1: formData.parsed_address.street_line_1 || formData.address,
          city: formData.parsed_address.city,
          state: formData.parsed_address.state,
          postal_code: formData.parsed_address.postal_code,
          country: formData.parsed_address.country
        }
      };

      const response = await externalAccountsAPI.createAccount(payload);
      
      // Navigate back to wallet on success
      navigate('/wallet');
    } catch (err) {
      console.error('Error linking bank account:', err);
      setError(err.message || 'Failed to link your bank account. Please check your information and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={handleBack}
          sx={{ mb: 2 }}
        >
          {linkingMethod === 'method-selection' ? 'Back to Country Selection' : 'Back to Method Selection'}
        </Button>
        
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <AccountBalance sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" fontWeight={600} gutterBottom>
            Link European Bank Account
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Connect your SEPA bank account securely
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Method Selection */}
      {linkingMethod === 'method-selection' && (
        <Stack spacing={3}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Stack spacing={2} alignItems="center" textAlign="center">
                <LinkIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    Connect with Plaid EU
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Securely connect your European bank account (Coming Soon)
                  </Typography>
                </Box>
                <Button 
                  variant="outlined" 
                  fullWidth
                  onClick={initializePlaidEU}
                  disabled={loading}
                >
                  {loading ? 'Connecting…' : 'Connect with Plaid EU'}
                </Button>
              </Stack>
            </CardContent>
          </Card>

          <Divider>
            <Typography variant="body2" color="text.secondary">or</Typography>
          </Divider>

          <Card>
            <CardContent sx={{ p: 3 }}>
              <Stack spacing={2} alignItems="center" textAlign="center">
                <AccountBalance sx={{ fontSize: 40, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    Enter Bank Details Manually
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Manually enter your IBAN and bank information
                  </Typography>
                </Box>
                <Button 
                  variant="contained" 
                  fullWidth
                  onClick={() => setLinkingMethod('manual')}
                >
                  Enter Details Manually
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      )}

      {/* Manual Entry Form */}
      {linkingMethod === 'manual' && (
        <Card>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h6" fontWeight="600" sx={{ mb: 3 }}>
              Bank Account Details
            </Typography>
            
            <form onSubmit={handleManualSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Bank Name"
                    name="bank_name"
                    value={formData.bank_name}
                    onChange={handleInputChange}
                    required
                    variant="outlined"
                  />
                </Grid>
                
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    required
                    variant="outlined"
                  />
                </Grid>
                
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    required
                    variant="outlined"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Account Name (optional)"
                    name="account_name"
                    value={formData.account_name}
                    onChange={handleInputChange}
                    variant="outlined"
                    helperText="A nickname for your account, e.g., 'Personal Checking'"
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant="subtitle2" sx={{ mb: 2 }}>
                    IBAN Details
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="IBAN Account Number"
                    name="iban_account_number"
                    value={formData.iban_account_number}
                    onChange={handleInputChange}
                    required
                    variant="outlined"
                    placeholder="GB82 WEST 1234 5698 7654 32"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="BIC Code"
                    name="bic"
                    value={formData.bic}
                    onChange={handleInputChange}
                    required
                    variant="outlined"
                    placeholder="ABCDGB2L"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Country</InputLabel>
                    <Select
                      value={formData.iban_country}
                      label="Country"
                      name="iban_country"
                      onChange={handleInputChange}
                    >
                      {SEPA_COUNTRIES.map((country) => (
                        <MenuItem key={country.code} value={country.name}>
                          {country.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                                 <Grid item xs={12}>
                   <Typography variant="subtitle2" sx={{ mb: 2 }}>
                     Address
                   </Typography>
                   <TextField
                     fullWidth
                     label="Address"
                     name="address"
                     value={formData.address}
                     onChange={handleInputChange}
                     required
                     variant="outlined"
                     placeholder="Start typing your address..."
                     inputRef={addressInputRef}
                     helperText="🔍 Start typing and select from Google Maps suggestions"
                     InputProps={{
                       autoComplete: 'off'
                     }}
                   />
                 </Grid>
                
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    sx={{ 
                      py: 1.8,
                      backgroundColor: 'primary.main',
                      '&:hover': {
                        backgroundColor: 'primary.dark',
                        boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
                      }
                    }}
                  >
                    {loading ? <CircularProgress size={24} color="inherit" /> : 'Link Bank Account'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </CardContent>
        </Card>
      )}

      
    </Container>
  );
} 