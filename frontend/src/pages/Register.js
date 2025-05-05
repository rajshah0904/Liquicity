import React, { useState, useEffect, Suspense } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, 
  Container, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  Alert, 
  Grid, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  CircularProgress,
  Divider,
  InputAdornment,
  IconButton
} from '@mui/material';
import { 
  CheckCircle,
  Help,
  ArrowBack
} from '@mui/icons-material';
import { kycAPI } from '../utils/api';
import { AnimatedBackground } from '../components/ui/ModernUIComponents';
import { useAuth0 } from '@auth0/auth0-react';

// Helper function to generate a random Ethereum-like wallet address
const generateRandomWalletAddress = () => {
  const hexChars = '0123456789abcdef';
  let address = '0x';
  for (let i = 0; i < 40; i++) {
    address += hexChars.charAt(Math.floor(Math.random() * hexChars.length));
  }
  return address;
};

// Update the countries list with more details for country-specific fields
const countries = [
  { 
    name: 'United States', 
    code: 'US', 
    currency: 'USD', 
    idType: 'SSN',
    idFormat: 'XXX-XX-XXXX',
    idLabel: 'Social Security Number',
    region: 'North America',
    requiredFields: ['ssn', 'dob', 'address'],
    acceptedDocuments: ['passport', 'drivers_license']
  },
  { 
    name: 'United Kingdom', 
    code: 'GB', 
    currency: 'GBP', 
    idType: 'NINO',
    idFormat: 'AA999999A',
    idLabel: 'National Insurance Number',
    region: 'Europe',
    requiredFields: ['nino', 'dob', 'address', 'postal_code'],
    acceptedDocuments: ['passport', 'drivers_license', 'national_id']
  },
  { 
    name: 'Canada', 
    code: 'CA', 
    currency: 'CAD', 
    idType: 'SIN',
    idFormat: '999-999-999',
    idLabel: 'Social Insurance Number',
    region: 'North America',
    requiredFields: ['sin', 'dob', 'address'],
    acceptedDocuments: ['passport', 'drivers_license', 'pr_card']
  },
  { 
    name: 'Australia', 
    code: 'AU', 
    currency: 'AUD', 
    idType: 'TFN',
    idFormat: '999 999 999',
    idLabel: 'Tax File Number',
    region: 'Oceania',
    requiredFields: ['tfn', 'dob', 'address', 'medicare'],
    acceptedDocuments: ['passport', 'drivers_license', 'medicare_card']
  },
  { 
    name: 'Germany', 
    code: 'DE', 
    currency: 'EUR', 
    idType: 'TIN',
    idFormat: '99999999999',
    idLabel: 'Tax Identification Number',
    region: 'Europe',
    requiredFields: ['tax_id', 'dob', 'address'],
    acceptedDocuments: ['passport', 'national_id', 'residence_permit']
  },
  { 
    name: 'France', 
    code: 'FR', 
    currency: 'EUR', 
    idType: 'INSEE',
    idFormat: '9 99 99 99999 999 99',
    idLabel: 'INSEE Number',
    region: 'Europe',
    requiredFields: ['insee', 'dob', 'address'],
    acceptedDocuments: ['passport', 'national_id', 'residence_permit']
  },
  { 
    name: 'Japan', 
    code: 'JP', 
    currency: 'JPY', 
    idType: 'My Number',
    idFormat: '9999-9999-9999',
    idLabel: 'My Number',
    region: 'Asia',
    requiredFields: ['my_number', 'dob', 'address'],
    acceptedDocuments: ['passport', 'residence_card', 'my_number_card']
  },
  { 
    name: 'Singapore', 
    code: 'SG', 
    currency: 'SGD', 
    idType: 'NRIC',
    idFormat: 'S9999999A',
    idLabel: 'NRIC Number',
    region: 'Asia',
    requiredFields: ['nric', 'dob', 'address'],
    acceptedDocuments: ['passport', 'nric']
  },
  { 
    name: 'India', 
    code: 'IN', 
    currency: 'INR', 
    idType: 'Aadhaar',
    idFormat: '9999 9999 9999',
    idLabel: 'Aadhaar Number',
    region: 'Asia',
    requiredFields: ['aadhaar', 'dob', 'address', 'pan'],
    acceptedDocuments: ['passport', 'aadhaar_card', 'pan_card', 'voters_id']
  },
  { 
    name: 'Brazil', 
    code: 'BR', 
    currency: 'BRL', 
    idType: 'CPF',
    idFormat: '999.999.999-99',
    idLabel: 'CPF Number',
    region: 'South America',
    requiredFields: ['cpf', 'dob', 'address'],
    acceptedDocuments: ['passport', 'national_id', 'drivers_license']
  }
];

// Group countries by region
const regions = Array.from(new Set(countries.map(country => country.region))).sort();

const documentTypes = [
  { value: 'passport', label: 'Passport' },
  { value: 'drivers_license', label: 'Driver\'s License' },
  { value: 'national_id', label: 'National ID Card' },
  { value: 'residence_permit', label: 'Residence Permit' },
];

const Register = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, loginWithRedirect } = useAuth0();
  
  // Redirect to Auth0 login if user is not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      loginWithRedirect({ appState: { returnTo: window.location.pathname } });
    }
  }, [isAuthenticated, loginWithRedirect]);
  
  // Determine the user's email, preferring state passed from signup
  const userEmail = location.state?.email || user?.email || '';
  const isNewUser = location.state?.newUser || false;
  
  // Get a trimmed down form since we only need KYC info
  const [formData, setFormData] = useState({
    // Basic info (pre-filled)
    email: userEmail,
    
    // Identity verification
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    country: '',
    countryObject: null,
    nationality: '',
    nationalityObject: null,
    idNumber: '',
    documentType: 'passport',
    documentNumber: '',
    issuingCountry: '',
    
    // Additional data
    currencyPreference: '',
    streetAddress: '',
    city: '',
    state: '',
    postalCode: '',
  });
  
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  
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
  
  const validateForm = () => {
    const newErrors = {};
    
    // Basic validation
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }
    
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }
    
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
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleBack = () => {
    navigate('/login');
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setServerError(null);
    
    try {
      // In a real implementation, this would submit KYC data to the backend
      // For demo, we'll simulate a successful submission
      setTimeout(() => {
        setIsSuccess(true);
        // Redirect to dashboard or verification screen
        setTimeout(() => {
          navigate('/login', { 
            state: { 
              message: 'Your identity verification has been submitted successfully. You can now log in to your account.' 
            } 
          });
        }, 3000);
      }, 2000);
      
    } catch (err) {
      console.error('KYC submission error:', err);
      setServerError('Failed to submit identity verification. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderKycForm = () => {
    // Get countries for the selected region
    const filteredCountries = selectedRegion 
      ? countries.filter(country => country.region === selectedRegion) 
      : countries;
    
    // Determine required fields and accepted documents based on selected country
    const requiredFields = formData.countryObject?.requiredFields || [];
    const acceptedDocuments = formData.countryObject?.acceptedDocuments || 
      documentTypes.map(doc => doc.value);
      
    // Filtering document types based on selected country
    const filteredDocumentTypes = documentTypes.filter(
      docType => !formData.countryObject || 
        !formData.countryObject.acceptedDocuments || 
        formData.countryObject.acceptedDocuments.includes(docType.value)
    );
    
    return (
      <>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Personal Information
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="First Name"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              error={!!errors.firstName}
              helperText={errors.firstName}
              required
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Last Name"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              error={!!errors.lastName}
              helperText={errors.lastName}
              required
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }}>Identity Verification</Divider>
          </Grid>
          
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel id="region-label">Region</InputLabel>
              <Select
                labelId="region-label"
                id="region"
                name="region"
                value={selectedRegion}
                onChange={(e) => {
                  setSelectedRegion(e.target.value);
                  // Clear country selection if region changes
                  if (formData.country) {
                    setFormData({
                      ...formData,
                      country: '',
                      countryObject: null,
                      nationality: '',
                      nationalityObject: null,
                    });
                  }
                }}
                label="Region"
              >
                <MenuItem value="">All Regions</MenuItem>
                {regions.map((region) => (
                  <MenuItem key={region} value={region}>
                    {region}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Date of Birth"
              name="dateOfBirth"
              type="date"
              value={formData.dateOfBirth}
              onChange={handleChange}
              error={!!errors.dateOfBirth}
              helperText={errors.dateOfBirth}
              InputLabelProps={{
                shrink: true,
              }}
              required
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth error={!!errors.country} required>
              <InputLabel id="country-label">Country of Residence</InputLabel>
              <Select
                labelId="country-label"
                id="country"
                name="country"
                value={formData.country}
                onChange={(e) => {
                  handleChange(e);
                  const country = countries.find(c => c.name === e.target.value);
                  if (country) {
                    setFormData({
                      ...formData,
                      country: country.name,
                      countryObject: country,
                      currencyPreference: country.currency
                    });
                  }
                }}
                label="Country of Residence"
              >
                {filteredCountries.map((country) => (
                  <MenuItem key={country.code} value={country.name}>
                    {country.name}
                  </MenuItem>
                ))}
              </Select>
              {errors.country && <FormHelperText>{errors.country}</FormHelperText>}
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth error={!!errors.nationality} required>
              <InputLabel id="nationality-label">Nationality</InputLabel>
              <Select
                labelId="nationality-label"
                id="nationality"
                name="nationality"
                value={formData.nationality}
                onChange={(e) => {
                  handleChange(e);
                  const country = countries.find(c => c.name === e.target.value);
                  if (country) {
                    setFormData({
                      ...formData,
                      nationality: country.name,
                      nationalityObject: country
                    });
                  }
                }}
                label="Nationality"
              >
                {countries.map((country) => (
                  <MenuItem key={country.code} value={country.name}>
                    {country.name}
                  </MenuItem>
                ))}
              </Select>
              {errors.nationality && <FormHelperText>{errors.nationality}</FormHelperText>}
            </FormControl>
          </Grid>
          
          {/* Custom ID fields based on country */}
          {formData.countryObject && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="idNumber"
                label={formData.countryObject.idLabel}
                value={formData.idNumber}
                onChange={handleChange}
                error={!!errors.idNumber}
                helperText={errors.idNumber || `Format: ${formData.countryObject.idFormat}`}
                required={requiredFields.includes(formData.countryObject.idType.toLowerCase())}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        onClick={() => alert(`This is the ${formData.countryObject.idLabel} used in ${formData.countryObject.name}. Format: ${formData.countryObject.idFormat}`)}
                      >
                        <Help fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
          )}
          
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }}>Address Information</Divider>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Street Address"
              name="streetAddress"
              value={formData.streetAddress}
              onChange={handleChange}
              error={!!errors.streetAddress}
              helperText={errors.streetAddress}
              required
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="City"
              name="city"
              value={formData.city}
              onChange={handleChange}
              error={!!errors.city}
              helperText={errors.city}
              required
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="State/Province/Region"
              name="state"
              value={formData.state}
              onChange={handleChange}
              error={!!errors.state}
              helperText={errors.state}
              required
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Postal Code"
              name="postalCode"
              value={formData.postalCode}
              onChange={handleChange}
              error={!!errors.postalCode}
              helperText={errors.postalCode}
              required
              variant="outlined"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }}>Identity Document</Divider>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth error={!!errors.documentType} required>
              <InputLabel id="document-type-label">Document Type</InputLabel>
              <Select
                labelId="document-type-label"
                id="documentType"
                name="documentType"
                value={formData.documentType}
                onChange={handleChange}
                label="Document Type"
              >
                {filteredDocumentTypes.map((docType) => (
                  <MenuItem key={docType.value} value={docType.value}>
                    {docType.label}
                  </MenuItem>
                ))}
              </Select>
              {errors.documentType && <FormHelperText>{errors.documentType}</FormHelperText>}
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              name="documentNumber"
              label="Document Number"
              value={formData.documentNumber}
              onChange={handleChange}
              error={!!errors.documentNumber}
              helperText={errors.documentNumber}
              required
            />
          </Grid>
          
          {/* Additional region/country-specific fields */}
          {formData.countryObject && formData.countryObject.code === 'IN' && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="panCard"
                label="PAN Card Number"
                value={formData.panCard || ''}
                onChange={handleChange}
                error={!!errors.panCard}
                helperText={errors.panCard || 'Format: ABCDE1234F'}
                required={requiredFields.includes('pan')}
              />
            </Grid>
          )}
          
          {formData.countryObject && formData.countryObject.code === 'AU' && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="medicareNumber"
                label="Medicare Card Number"
                value={formData.medicareNumber || ''}
                onChange={handleChange}
                error={!!errors.medicareNumber}
                helperText={errors.medicareNumber}
                required={requiredFields.includes('medicare')}
              />
            </Grid>
          )}
        </Grid>
        
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
          <Button 
            variant="outlined"
            onClick={handleBack}
            startIcon={<ArrowBack />}
          >
            Back to Login
          </Button>
          <Button 
            type="submit"
            variant="contained" 
            color="primary"
            disabled={isSubmitting}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : <CheckCircle />}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Verification'}
          </Button>
        </Box>
      </>
    );
  };

  if (isSuccess) {
    return (
      <>
        <AnimatedBackground />
        <Container maxWidth="sm" sx={{ pt: 8, pb: 8 }}>
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <CheckCircle color="success" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Verification Submitted Successfully!
            </Typography>
            <Typography variant="body1" paragraph>
              Thank you for submitting your identity verification. We will review your information and notify you once the verification process is complete.
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              You will be redirected to the login page in a moment...
            </Typography>
            <CircularProgress size={24} sx={{ mt: 2 }} />
          </Paper>
        </Container>
      </>
    );
  }

  // If not a new user and not already logged in, redirect to login
  if (!isNewUser && !loginWithRedirect()) {
    navigate('/login');
    return null;
  }

  return (
    <>
      <AnimatedBackground />
      <Container maxWidth="md" sx={{ pt: 4, pb: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Identity Verification
          </Typography>
          
          <Typography variant="body1" align="center" paragraph sx={{ mb: 4 }}>
            We need to verify your identity to comply with financial regulations. Your information is encrypted and securely stored.
          </Typography>
          
          {serverError && (
            <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
              {typeof serverError === 'string' ? serverError : 'An error occurred. Please try again.'}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit}>
            {renderKycForm()}
          </Box>
        </Paper>
      </Container>
    </>
  );
};

export default Register; 