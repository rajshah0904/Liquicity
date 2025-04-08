import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Container, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  Alert, 
  Grid, 
  Stepper,
  Step,
  StepLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  CircularProgress,
  Divider,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Autocomplete
} from '@mui/material';
import { 
  Visibility, 
  VisibilityOff, 
  CheckCircle,
  Help
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

// Helper function to generate a random Ethereum-like wallet address
const generateRandomWalletAddress = () => {
  const hexChars = '0123456789abcdef';
  let address = '0x';
  for (let i = 0; i < 40; i++) {
    address += hexChars.charAt(Math.floor(Math.random() * hexChars.length));
  }
  return address;
};

// Countries list with country codes and currencies
const countries = [
  { name: 'United States', code: 'US', currency: 'USD', idType: 'SSN' },
  { name: 'United Kingdom', code: 'GB', currency: 'GBP', idType: 'National Insurance Number' },
  { name: 'Canada', code: 'CA', currency: 'CAD', idType: 'SIN' },
  { name: 'Australia', code: 'AU', currency: 'AUD', idType: 'TFN' },
  { name: 'European Union', code: 'EU', currency: 'EUR', idType: 'National ID' },
  { name: 'Japan', code: 'JP', currency: 'JPY', idType: 'My Number' },
  { name: 'China', code: 'CN', currency: 'CNY', idType: 'Resident ID' },
  { name: 'India', code: 'IN', currency: 'INR', idType: 'Aadhaar' },
  { name: 'Brazil', code: 'BR', currency: 'BRL', idType: 'CPF' },
  { name: 'South Africa', code: 'ZA', currency: 'ZAR', idType: 'ID Number' },
  { name: 'Singapore', code: 'SG', currency: 'SGD', idType: 'NRIC' },
];

const documentTypes = [
  { value: 'passport', label: 'Passport' },
  { value: 'drivers_license', label: 'Driver\'s License' },
  { value: 'national_id', label: 'National ID Card' },
  { value: 'residence_permit', label: 'Residence Permit' },
];

const Register = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    // Basic info
    firstName: '',
    lastName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    
    // Identity verification
    dateOfBirth: '',
    country: '',
    countryObject: null,
    nationality: '',
    nationalityObject: null,
    idNumber: '',
    documentType: 'national_id',
    documentNumber: '',
    issuingCountry: '',
    
    // Address
    streetAddress: '',
    city: '',
    state: '',
    postalCode: '',
    
    // Additional data
    currencyPreference: '',
    agreeToTerms: false
  });
  
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [helpDialogOpen, setHelpDialogOpen] = useState(false);
  const [helpContent, setHelpContent] = useState({ title: '', content: '' });
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const steps = ['Basic Information', 'Identity Verification', 'Address Details', 'Review & Submit'];

  // Update currency when country changes
  useEffect(() => {
    if (formData.countryObject) {
      setFormData({
        ...formData,
        currencyPreference: formData.countryObject.currency
      });
    }
  }, [formData.countryObject]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Clear error when field is changed
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const handleCountryChange = (event, newValue) => {
    setFormData({
      ...formData,
      countryObject: newValue,
      country: newValue ? newValue.name : '',
      currencyPreference: newValue ? newValue.currency : ''
    });
    
    if (errors.country) {
      setErrors({
        ...errors,
        country: null
      });
    }
  };

  const handleNationalityChange = (event, newValue) => {
    setFormData({
      ...formData,
      nationalityObject: newValue,
      nationality: newValue ? newValue.name : ''
    });
    
    if (errors.nationality) {
      setErrors({
        ...errors,
        nationality: null
      });
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const openHelpDialog = (title, content) => {
    setHelpContent({ title, content });
    setHelpDialogOpen(true);
  };

  const closeHelpDialog = () => {
    setHelpDialogOpen(false);
  };

  const validateStep = (step) => {
    const newErrors = {};
    
    if (step === 0) {
      // Basic info validation
      if (!formData.firstName.trim()) {
        newErrors.firstName = 'First name is required';
      }
      
      if (!formData.lastName.trim()) {
        newErrors.lastName = 'Last name is required';
      }
      
      if (!formData.username.trim()) {
        newErrors.username = 'Username is required';
      } else if (formData.username.length < 3) {
        newErrors.username = 'Username must be at least 3 characters';
      }
      
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Email is invalid';
      }
      
      if (!formData.password) {
        newErrors.password = 'Password is required';
      } else if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters';
      } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
        newErrors.password = 'Password must include lowercase, uppercase, and numbers';
      }
      
      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }
    else if (step === 1) {
      // Identity verification validation
      if (!formData.dateOfBirth) {
        newErrors.dateOfBirth = 'Date of birth is required';
      }
      
      if (!formData.country) {
        newErrors.country = 'Country of residence is required';
      }
      
      if (!formData.nationality) {
        newErrors.nationality = 'Nationality is required';
      }
      
      // ID validation based on country
      if (formData.countryObject) {
        if (!formData.idNumber) {
          newErrors.idNumber = `${formData.countryObject.idType || 'ID number'} is required`;
        } else if (formData.countryObject.code === 'US' && !/^\d{3}-\d{2}-\d{4}$/.test(formData.idNumber)) {
          newErrors.idNumber = 'SSN must be in format XXX-XX-XXXX';
        }
      }
      
      if (!formData.documentType) {
        newErrors.documentType = 'Document type is required';
      }
      
      if (!formData.documentNumber) {
        newErrors.documentNumber = 'Document number is required';
      }
    }
    else if (step === 2) {
      // Address validation
      if (!formData.streetAddress) {
        newErrors.streetAddress = 'Street address is required';
      }
      
      if (!formData.city) {
        newErrors.city = 'City is required';
      }
      
      if (!formData.state) {
        newErrors.state = 'State/Province is required';
      }
      
      if (!formData.postalCode) {
        newErrors.postalCode = 'Postal code is required';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    if (validateStep(3)) {
      setIsSubmitting(true);
      setServerError(null);
      
      try {
        // Generate a random wallet address as a placeholder 
        const tempWalletAddress = generateRandomWalletAddress();
        
        console.log('Sending registration data:', {
          username: formData.username,
          email: formData.email,
          password: formData.password,
          wallet_address: tempWalletAddress,
          // Additional metadata could be saved later once user is created
          metadata: {
            firstName: formData.firstName,
            lastName: formData.lastName,
            dateOfBirth: formData.dateOfBirth,
            country: formData.country,
            countryCode: formData.countryObject?.code,
            nationality: formData.nationality,
            idNumber: formData.idNumber,
            documentType: formData.documentType,
            documentNumber: formData.documentNumber,
            streetAddress: formData.streetAddress,
            city: formData.city,
            state: formData.state,
            postalCode: formData.postalCode,
            currencyPreference: formData.currencyPreference
          }
        });
        
        // Call the register function with the correct parameters
        const success = await register(
          formData.username,
          formData.password,
          formData.email,
          tempWalletAddress,
          {
            firstName: formData.firstName,
            lastName: formData.lastName,
            country: formData.country,
            currencyPreference: formData.currencyPreference,
            countryCode: formData.countryObject?.code
          }
        );
        
        if (success) {
          navigate('/login', { state: { message: 'Registration successful! Please login.' } });
        } else {
          setServerError('Registration failed. Please try again.');
          setActiveStep(0);
        }
      } catch (err) {
        console.error('Registration error:', err);
        if (err.response?.data?.detail) {
          if (typeof err.response.data.detail === 'object') {
            // Handle validation errors from the server
            try {
              setServerError(JSON.stringify(err.response.data.detail));
            } catch (_) {
              setServerError('Registration failed due to validation errors.');
            }
          } else {
            setServerError(String(err.response.data.detail));
          }
        } else {
          setServerError('Registration failed. Please try again.');
        }
        setActiveStep(0);
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  // Step 1: Basic Information Form
  const renderBasicInfoForm = () => (
    <>
      <Typography variant="h6" gutterBottom>
        Create Your Account
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            name="firstName"
            label="First Name"
            fullWidth
            value={formData.firstName}
            onChange={handleChange}
            error={!!errors.firstName}
            helperText={errors.firstName}
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            name="lastName"
            label="Last Name"
            fullWidth
            value={formData.lastName}
            onChange={handleChange}
            error={!!errors.lastName}
            helperText={errors.lastName}
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            required
            name="username"
            label="Username"
            fullWidth
            value={formData.username}
            onChange={handleChange}
            error={!!errors.username}
            helperText={errors.username}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            required
            name="email"
            label="Email Address"
            fullWidth
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={!!errors.email}
            helperText={errors.email}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            required
            name="password"
            label="Password"
            type={showPassword ? "text" : "password"}
            fullWidth
            value={formData.password}
            onChange={handleChange}
            error={!!errors.password}
            helperText={errors.password}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={togglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            required
            name="confirmPassword"
            label="Confirm Password"
            type={showPassword ? "text" : "password"}
            fullWidth
            value={formData.confirmPassword}
            onChange={handleChange}
            error={!!errors.confirmPassword}
            helperText={errors.confirmPassword}
          />
        </Grid>
      </Grid>
    </>
  );

  // Step 2: Identity Verification Form
  const renderIdentityVerificationForm = () => (
    <>
      <Typography variant="h6" gutterBottom>
        Identity Verification
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        We need to verify your identity to comply with financial regulations.
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            required
            name="dateOfBirth"
            label="Date of Birth"
            type="date"
            fullWidth
            value={formData.dateOfBirth}
            onChange={handleChange}
            error={!!errors.dateOfBirth}
            helperText={errors.dateOfBirth}
            InputLabelProps={{ shrink: true }}
            placeholder="mm/dd/yyyy"
          />
        </Grid>
        <Grid item xs={12}>
          <Autocomplete
            id="country-select"
            options={countries}
            autoHighlight
            value={formData.countryObject}
            onChange={handleCountryChange}
            getOptionLabel={(option) => option.name}
            renderOption={(props, option) => (
              <Box component="li" {...props}>
                {option.name} ({option.currency})
              </Box>
            )}
            renderInput={(params) => (
              <TextField
                {...params}
                required
                label="Country of Residence"
                error={!!errors.country}
                helperText={errors.country}
              />
            )}
          />
        </Grid>
        <Grid item xs={12}>
          <Autocomplete
            id="nationality-select"
            options={countries}
            autoHighlight
            value={formData.nationalityObject}
            onChange={handleNationalityChange}
            getOptionLabel={(option) => option.name}
            renderOption={(props, option) => (
              <Box component="li" {...props}>
                {option.name}
              </Box>
            )}
            renderInput={(params) => (
              <TextField
                {...params}
                required
                label="Nationality"
                error={!!errors.nationality}
                helperText={errors.nationality}
              />
            )}
          />
        </Grid>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              required
              name="idNumber"
              label={formData.countryObject ? `${formData.countryObject.idType}` : "ID Number"}
              fullWidth
              value={formData.idNumber}
              onChange={handleChange}
              error={!!errors.idNumber}
              helperText={errors.idNumber}
              placeholder={formData.countryObject?.code === 'US' ? "XXX-XX-XXXX" : ""}
            />
            <IconButton 
              color="primary" 
              onClick={() => openHelpDialog(
                'Identity Verification', 
                `For ${formData.countryObject?.name || 'your country'}, we require your ${formData.countryObject?.idType || 'national identification number'} for verification purposes. This information is encrypted and securely stored.`
              )}
            >
              <Help />
            </IconButton>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Divider sx={{ my: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Document Information
            </Typography>
          </Divider>
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth error={!!errors.documentType}>
            <InputLabel>Document Type</InputLabel>
            <Select
              name="documentType"
              value={formData.documentType}
              onChange={handleChange}
              label="Document Type"
            >
              {documentTypes.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
            {errors.documentType && <FormHelperText>{errors.documentType}</FormHelperText>}
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            name="documentNumber"
            label="Document Number"
            fullWidth
            value={formData.documentNumber}
            onChange={handleChange}
            error={!!errors.documentNumber}
            helperText={errors.documentNumber}
          />
        </Grid>
        <Grid item xs={12}>
          <Autocomplete
            id="issuing-country-select"
            options={countries}
            autoHighlight
            value={countries.find(c => c.name === formData.issuingCountry) || null}
            onChange={(event, newValue) => {
              setFormData({
                ...formData,
                issuingCountry: newValue ? newValue.name : ''
              });
            }}
            getOptionLabel={(option) => option.name}
            renderOption={(props, option) => (
              <Box component="li" {...props}>
                {option.name}
              </Box>
            )}
            renderInput={(params) => (
              <TextField
                {...params}
                required
                label="Issuing Country"
                error={!!errors.issuingCountry}
                helperText={errors.issuingCountry}
              />
            )}
          />
        </Grid>
      </Grid>
    </>
  );

  // Step 3: Address Form
  const renderAddressForm = () => (
    <>
      <Typography variant="h6" gutterBottom>
        Address Information
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            required
            name="streetAddress"
            label="Street Address"
            fullWidth
            value={formData.streetAddress}
            onChange={handleChange}
            error={!!errors.streetAddress}
            helperText={errors.streetAddress}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            name="city"
            label="City"
            fullWidth
            value={formData.city}
            onChange={handleChange}
            error={!!errors.city}
            helperText={errors.city}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            name="state"
            label="State/Province"
            fullWidth
            value={formData.state}
            onChange={handleChange}
            error={!!errors.state}
            helperText={errors.state}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            required
            name="postalCode"
            label="Postal Code"
            fullWidth
            value={formData.postalCode}
            onChange={handleChange}
            error={!!errors.postalCode}
            helperText={errors.postalCode}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Preferred Currency</InputLabel>
            <Select
              name="currencyPreference"
              value={formData.currencyPreference}
              onChange={handleChange}
              label="Preferred Currency"
            >
              {countries.map((country) => (
                <MenuItem key={country.currency} value={country.currency}>
                  {country.currency} - {country.name}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>
              This will be your default transaction currency
            </FormHelperText>
          </FormControl>
        </Grid>
      </Grid>
    </>
  );

  // Step 4: Review Form
  const renderReviewForm = () => (
    <>
      <Typography variant="h6" gutterBottom>
        Review Your Information
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Personal Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Name:
                </Typography>
                <Typography variant="body1">
                  {formData.firstName} {formData.lastName}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Date of Birth:
                </Typography>
                <Typography variant="body1">
                  {formData.dateOfBirth}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Username:
                </Typography>
                <Typography variant="body1">
                  {formData.username}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Email:
                </Typography>
                <Typography variant="body1">
                  {formData.email}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Identity Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Country:
                </Typography>
                <Typography variant="body1">
                  {formData.country}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Nationality:
                </Typography>
                <Typography variant="body1">
                  {formData.nationality}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Document Type:
                </Typography>
                <Typography variant="body1">
                  {documentTypes.find(d => d.value === formData.documentType)?.label || formData.documentType}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Document Number:
                </Typography>
                <Typography variant="body1">
                  {formData.documentNumber}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Address
            </Typography>
            <Typography variant="body1" paragraph>
              {formData.streetAddress}, {formData.city}, {formData.state} {formData.postalCode}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Preferred Currency:
            </Typography>
            <Typography variant="body1">
              {formData.currencyPreference}
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12}>
          <FormControl required error={!!errors.agreeToTerms}>
            <FormHelperText>
              By clicking "Create Account", you agree to our Terms of Service and Privacy Policy, and affirm that the information provided is accurate.
            </FormHelperText>
          </FormControl>
        </Grid>
      </Grid>
    </>
  );

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          marginTop: 4,
          marginBottom: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            TerraFlow
          </Typography>
          
          <Stepper activeStep={activeStep} sx={{ mb: 4, mt: 2 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          {serverError && (
            <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
              {typeof serverError === 'string' ? serverError : 'An error occurred during registration. Please try again.'}
            </Alert>
          )}
          
          <Box component="form" onSubmit={(e) => { e.preventDefault(); activeStep === steps.length - 1 ? handleSubmit() : handleNext() }} sx={{ mt: 2 }}>
            {activeStep === 0 && renderBasicInfoForm()}
            {activeStep === 1 && renderIdentityVerificationForm()}
            {activeStep === 2 && renderAddressForm()}
            {activeStep === 3 && renderReviewForm()}
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
              <Button
                onClick={handleBack}
                sx={{ mr: 1 }}
                disabled={activeStep === 0}
              >
                Back
              </Button>
              <Box sx={{ flex: '1 1 auto' }} />
              {activeStep === steps.length - 1 ? (
                <Button
                  variant="contained"
                  color="primary"
                  type="submit"
                  disabled={isSubmitting}
                  startIcon={isSubmitting ? <CircularProgress size={20} /> : <CheckCircle />}
                >
                  {isSubmitting ? 'Creating Account...' : 'Create Account'}
                </Button>
              ) : (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleNext}
                >
                  Next
                </Button>
              )}
            </Box>
          </Box>
          
          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2">
              Already have an account?{' '}
              <Link to="/login" style={{ textDecoration: 'none' }}>
                Sign in
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
      
      {/* Help Dialog */}
      <Dialog
        open={helpDialogOpen}
        onClose={closeHelpDialog}
        aria-labelledby="help-dialog-title"
        aria-describedby="help-dialog-description"
      >
        <DialogTitle id="help-dialog-title">{helpContent.title}</DialogTitle>
        <DialogContent>
          <DialogContentText id="help-dialog-description">
            {helpContent.content}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeHelpDialog} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Register; 