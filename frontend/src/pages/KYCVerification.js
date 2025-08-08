import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  MenuItem, 
  FormControl, 
  InputLabel,
  Select,
  Alert,
  Snackbar,
  CircularProgress,
  FormHelperText,
  Stepper,
  Step,
  StepLabel,
  Paper,
  InputAdornment,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { AnimatedBackground } from '../components/ui/ModernUIComponents';
import api from '../utils/api';

// Regions for dropdown selection
const regions = [
  { code: 'US', name: 'United States', region: 'us', available: true },
  { code: 'EU', name: 'European Union', region: 'eu', available: false },
  { code: 'MX', name: 'Mexico', region: 'mexico', available: false },
  { code: 'BR', name: 'Brazil', region: 'brazil', available: false },
  { code: 'CO', name: 'Colombia', region: 'colombia', available: false },
  { code: 'PE', name: 'Peru', region: 'peru', available: false },
  { code: 'AR', name: 'Argentina', region: 'argentina', available: false },
];

// ID Types for Bridge API
const ID_TYPES = [
  { value: 'drivers_license', label: 'Driver\'s License' },
  { value: 'passport', label: 'Passport' }
];

const KYCVerification = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading, getAccessTokenSilently } = useAuth0();
  const addressRef = useRef(null);
  const autocompleteRef = useRef(null);
  
  // State management
  const [selectedRegion, setSelectedRegion] = useState('');
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    birth_date: '',
    street_line_1: '',
    city: '',
    subdivision: '', // state/province
    postal_code: '',
    country: '',
    ssn: '', // for US users
    id_type: '',
    id_number: '',
    id_image_front: null,
    id_image_back: null
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [activeStep, setActiveStep] = useState(0);
  const [googleMapsLoaded, setGoogleMapsLoaded] = useState(false);
  const [signedAgreementId, setSignedAgreementId] = useState('');
  const restoredFromSnapshotRef = useRef(false);
  const SNAPSHOT_KEY = 'kycFormSnapshot_v1';

  // Restore snapshot if returning from redirect (e.g., ToS)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(SNAPSHOT_KEY);
      if (raw) {
        const snapshot = JSON.parse(raw);
        if (snapshot.selectedRegion) setSelectedRegion(snapshot.selectedRegion);
        if (snapshot.formData) setFormData(snapshot.formData);
        if (typeof snapshot.activeStep === 'number') setActiveStep(snapshot.activeStep);
        restoredFromSnapshotRef.current = true;
      }
    } catch (e) {
      console.error('Failed to restore KYC snapshot', e);
    }
  }, []);

  // Capture signed_agreement_id from query params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sid = params.get('signed_agreement_id');
    if (sid) {
      setSignedAgreementId(sid);
    }
  }, []);
  
  // Initialize Google Maps API
  useEffect(() => {
    const loadGoogleMapsScript = () => {
      if (window.google && window.google.maps) {
        setGoogleMapsLoaded(true);
        return;
      }
      
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&libraries=places`;
      script.async = true;
      script.defer = true;
      script.onload = () => setGoogleMapsLoaded(true);
      script.onerror = () => console.error('Failed to load Google Maps API');
      document.head.appendChild(script);
    };
    
    loadGoogleMapsScript();
  }, []);
  
  // Initialize Google Places Autocomplete
  useEffect(() => {
    if (googleMapsLoaded && addressRef.current && !autocompleteRef.current) {
      autocompleteRef.current = new window.google.maps.places.Autocomplete(
        addressRef.current,
        {
          types: ['address'],
          componentRestrictions: selectedRegion === 'US' ? { country: 'us' } : undefined
        }
      );
      
      autocompleteRef.current.addListener('place_changed', () => {
        const place = autocompleteRef.current.getPlace();
        if (place.address_components) {
          parseGoogleAddress(place);
        }
      });
    }
  }, [googleMapsLoaded, selectedRegion]);
  
  // Parse Google Maps address into form fields
  const parseGoogleAddress = (place) => {
    const components = place.address_components;
    const addressData = {
      street_line_1: '',
      city: '',
      subdivision: '',
      postal_code: '',
      country: ''
    };
    
    // Build street address
    const streetNumber = components.find(c => c.types.includes('street_number'))?.long_name || '';
    const streetName = components.find(c => c.types.includes('route'))?.long_name || '';
    addressData.street_line_1 = `${streetNumber} ${streetName}`.trim();
    
    // Get other components
    addressData.city = components.find(c => c.types.includes('locality'))?.long_name || '';
    addressData.subdivision = components.find(c => 
      c.types.includes('administrative_area_level_1')
    )?.short_name || '';
    addressData.postal_code = components.find(c => c.types.includes('postal_code'))?.long_name || '';
    addressData.country = components.find(c => c.types.includes('country'))?.short_name || '';
    
    setFormData(prev => ({
      ...prev,
      ...addressData
    }));
    
    // Clear address-related errors
    const addressFields = ['street_line_1', 'city', 'subdivision', 'postal_code', 'country'];
    setErrors(prev => {
      const newErrors = { ...prev };
      addressFields.forEach(field => delete newErrors[field]);
      return newErrors;
    });
  };
  
  // Pre-populate user data when Auth0 user is available
  useEffect(() => {
    if (user && user.name) {
      const nameParts = user.name.split(' ');
      setFormData(prev => ({
        ...prev,
        first_name: nameParts[0] || '',
        last_name: nameParts.slice(1).join(' ') || ''
      }));
    }
  }, [user]);

  // Clear validation errors when region changes (preserve form data)
  useEffect(() => {
    setErrors({});
  }, [selectedRegion]);

  // Persist snapshot whenever region/form/step changes
  useEffect(() => {
    try {
      const snapshot = { selectedRegion, formData, activeStep };
      sessionStorage.setItem(SNAPSHOT_KEY, JSON.stringify(snapshot));
    } catch (e) {
      // ignore
    }
  }, [selectedRegion, formData, activeStep]);
  
  // Ensure user record exists (register if missing)
  useEffect(() => {
    const ensureRegistration = async () => {
      try {
        const token = await getAccessTokenSilently({ authorizationParams: { scope: 'openid profile email' } });
        const check = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });
        if (!check.data.exists && user?.email) {
          await api.post('/onboard/register', { email: user.email }, { headers: { Authorization: `Bearer ${token}` } });
        }
      } catch (e) {
        console.error('KYC: ensureRegistration failed', e);
      }
    };
    if (isAuthenticated) {
      ensureRegistration();
    }
  }, [isAuthenticated, getAccessTokenSilently, user]);
  
  // Ensure token is persisted and axios default header is set on mount so subsequent hooks use it.
  useEffect(() => {
    const ensureToken = async () => {
      try {
        const token = await getAccessTokenSilently({ authorizationParams: { scope: 'openid profile email' } });
        if (token) {
          localStorage.setItem('auth_token', token);
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
      } catch (e) {
        // ignore here; guards will handle auth redirects
      }
    };
    if (isAuthenticated) ensureToken();
  }, [isAuthenticated, getAccessTokenSilently]);
  
  // Handle region selection
  const handleRegionChange = async (e) => {
    const regionCode = e.target.value;
    setSelectedRegion(regionCode);
    
    // Check if region is available for KYC
    const region = regions.find(r => r.code === regionCode);
    if (!region?.available) {
      console.log(`KYC: Region '${regionCode}' not yet available - redirecting to coming soon`);
      navigate(`/coming-soon?country=${regionCode}&region=${region?.region}`);
      return;
    }
    
    // Set country based on region
    if (regionCode === 'US') {
      setFormData(prev => ({ ...prev, country: 'USA' }));
    }
    
    console.log(`KYC: Region '${regionCode}' selected locally (not saved until KYC complete)`);
    setActiveStep(1);
  };
  
  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Format SSN as user types
    let newValue = value;
    if (name === 'ssn') {
      const digits = value.replace(/\D/g, '').slice(0, 9);
      if (digits.length > 5) {
        newValue = digits.replace(/^(\d{3})(\d{2})(\d+)/, '$1-$2-$3');
      } else if (digits.length > 3) {
        newValue = digits.replace(/^(\d{3})(\d+)/, '$1-$2');
      } else {
        newValue = digits;
      }
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: newValue
    }));
    
    // Clear error when field is changed
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };
  
  // Handle file uploads
  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      const file = files[0];
      
      // Validate file type (images only)
      if (!file.type.startsWith('image/')) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Please select an image file'
        }));
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setErrors(prev => ({
          ...prev,
          [name]: 'File size must be less than 10MB'
        }));
        return;
      }
      
      setFormData(prev => ({
        ...prev,
        [name]: file
      }));
      
      if (errors[name]) {
        setErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    }
  };
  
  // Go back to region selection
  const handleBackToRegion = () => {
    setSelectedRegion('');
    setFormData({
      first_name: '',
      last_name: '',
      birth_date: '',
      street_line_1: '',
      city: '',
      subdivision: '',
      postal_code: '',
      country: '',
      ssn: '',
      id_type: '',
      id_number: '',
      id_image_front: null,
      id_image_back: null
    });
    setErrors({});
    setActiveStep(0);
  };
  
  // Handle ToS generation (snapshot before navigating)
  const handleGenerateTos = async () => {
    try {
      // snapshot explicitly
      sessionStorage.setItem(SNAPSHOT_KEY, JSON.stringify({ selectedRegion, formData, activeStep }));
      const token = await getAccessTokenSilently({ authorizationParams: { scope: 'openid profile email' } });
      const resp = await api.post('/kyc/tos_link', {}, { headers: { Authorization: `Bearer ${token}` } });
      const baseUrl = resp.data.url || resp.data.kyc_link || resp.data.tos_link || resp.data;
      if (baseUrl) {
        const redirect = encodeURIComponent(`${window.location.origin}/kyc-verification`);
        const sep = baseUrl.includes('?') ? '&' : '?';
        const url = `${baseUrl}${sep}redirect_uri=${redirect}`;
        window.location.href = url;
      }
    } catch (e) {
      console.error('Failed to generate ToS link', e);
      setSubmitError('Failed to generate Terms of Service link. Please try again.');
    }
  };
  
  // Form validation
  const validateForm = () => {
    const newErrors = {};
    
    // Required fields
    const requiredFields = [
      { field: 'first_name', label: 'First Name' },
      { field: 'last_name', label: 'Last Name' },
      { field: 'birth_date', label: 'Date of Birth' },
      { field: 'street_line_1', label: 'Street Address' },
      { field: 'city', label: 'City' },
      { field: 'subdivision', label: 'State/Province' },
      { field: 'postal_code', label: 'Postal Code' },
      { field: 'country', label: 'Country' },
      { field: 'id_type', label: 'ID Type' },
      { field: 'id_number', label: 'ID Number' }
    ];
    
    // Add SSN requirement for US users
    if (selectedRegion === 'US') {
      requiredFields.push({ field: 'ssn', label: 'Social Security Number' });
    }
    
    // Check required fields
    requiredFields.forEach(({ field, label }) => {
      if (!formData[field]) {
        newErrors[field] = `${label} is required`;
      }
    });
    
    // Validate SSN format for US users
    if (selectedRegion === 'US' && formData.ssn) {
      const ssnDigits = formData.ssn.replace(/\D/g, '');
      if (ssnDigits.length !== 9) {
        newErrors.ssn = 'Please enter a valid 9-digit SSN';
      }
    }
    
    // Validate birth date (must be 18 or older)
    if (formData.birth_date) {
      const birthDate = new Date(formData.birth_date);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 18) {
        newErrors.birth_date = 'You must be at least 18 years old';
      }
    }
    
    // Validate file uploads based on ID type
    if (formData.id_type) {
      if (!formData.id_image_front) {
        newErrors.id_image_front = 'Front image of ID is required';
      }
      
      if (formData.id_type === 'drivers_license' && !formData.id_image_back) {
        newErrors.id_image_back = 'Back image of driver\'s license is required';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Convert file to base64
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    setSubmitError('');
    
    try {
      // Get access token
      const token = await getAccessTokenSilently({
        authorizationParams: {
          scope: 'openid profile email'
        }
      });
      
      // Prepare data for Bridge customer creation
      const customerData = {
        type: 'individual',
        first_name: formData.first_name,
        last_name: formData.last_name,
        birth_date: formData.birth_date,
        residential_address: {
          street_line_1: formData.street_line_1,
          city: formData.city,
          subdivision: formData.subdivision,
          postal_code: formData.postal_code,
          country: formData.country
        },
        identifying_information: []
      };
      
      // Add SSN for US users
      if (selectedRegion === 'US' && formData.ssn) {
        customerData.identifying_information.push({
          type: 'ssn',
          issuing_country: 'usa',
          number: formData.ssn.replace(/\D/g, '') // Remove formatting
        });
      }
      
      // Add ID document
      const idDoc = {
        type: formData.id_type,
        issuing_country: formData.country.toLowerCase(),
        number: formData.id_number
      };
      
      // Convert images to base64
      if (formData.id_image_front) {
        const frontBase64 = await fileToBase64(formData.id_image_front);
        idDoc.image_front = frontBase64;
      }
      
      if (formData.id_image_back) {
        const backBase64 = await fileToBase64(formData.id_image_back);
        idDoc.image_back = backBase64;
      }
      
      customerData.identifying_information.push(idDoc);
      
      // Also include the selected region for our backend
      customerData.region = selectedRegion.toLowerCase();

      if (signedAgreementId) {
        customerData.signed_agreement_id = signedAgreementId;
      }
      
      console.log('Submitting KYC data to backend...');
      
      // Submit to our backend (which will handle Bridge API call)
      const response = await api.post(
        '/user/kyc/submit',
        customerData,
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );
      
      console.log('KYC submission response:', response.data);
      setSubmitSuccess(true);
      setActiveStep(2);
      sessionStorage.removeItem(SNAPSHOT_KEY);
      
      // Redirect to dashboard after success
      setTimeout(() => navigate('/dashboard'), 3000);
      
    } catch (error) {
      console.error('KYC submission error:', error);
      
      if (error.response) {
        const statusCode = error.response.status;
        const errorMessage = error.response.data?.detail || 'Unknown server error';
        
        if (statusCode === 401) {
          setSubmitError('Authentication error. Please log out and log back in.');
        } else if (statusCode === 400) {
          setSubmitError(`Invalid data: ${errorMessage}`);
        } else {
          setSubmitError(`Server error (${statusCode}): ${errorMessage}`);
        }
      } else if (error.request) {
        setSubmitError('Network error. Please check your connection and try again.');
      } else {
        setSubmitError('Failed to submit verification. Please try again or contact support.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // After submission (activeStep === 2), poll for completion
  useEffect(() => {
    let intervalId;
    let attemptedWallet = false;

    const pollStatus = async () => {
      try {
        const token = await getAccessTokenSilently({ authorizationParams: { scope: 'openid profile email' } });
        const res = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });
        const { next_step } = res.data || {};
        if (next_step === 'done') {
          navigate('/dashboard');
        } else if (next_step === 'create_wallet') {
          if (!attemptedWallet) {
            attemptedWallet = true;
            try { await api.post('/user/create-wallet', {}, { headers: { Authorization: `Bearer ${token}` } }); } catch(e) {}
          }
        }
      } catch (e) {
        // ignore and keep polling
      }
    };

    if (activeStep === 2) {
      pollStatus();
      intervalId = setInterval(pollStatus, 3000);
    }

    return () => { if (intervalId) clearInterval(intervalId); };
  }, [activeStep, getAccessTokenSilently, navigate]);

  // Utility to determine if submit should be enabled (all fields complete + ToS accepted)
  const isTosAccepted = Boolean(signedAgreementId);
  const isFormComplete = (() => {
    const requiredFields = [
      'first_name',
      'last_name',
      'birth_date',
      'street_line_1',
      'city',
      'subdivision',
      'postal_code',
      'country',
      'id_type',
      'id_number'
    ];
    if (selectedRegion === 'US') requiredFields.push('ssn');

    const allTextPresent = requiredFields.every((field) => {
      const value = formData[field];
      return typeof value === 'string' ? value.trim().length > 0 : Boolean(value);
    });

    const imagesPresent = Boolean(formData.id_image_front) && (
      formData.id_type !== 'drivers_license' || Boolean(formData.id_image_back)
    );

    const ssnValid = selectedRegion !== 'US'
      ? true
      : (formData.ssn ? formData.ssn.replace(/\D/g, '').length === 9 : false);

    return allTextPresent && imagesPresent && ssnValid && isTosAccepted;
  })();

  // Show loading state while Auth0 loads
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }
  
  // Render region selection step
  const renderRegionSelection = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
          Select Your Region
        </Typography>
        <Typography variant="body2" sx={{ mb: 3, color: 'rgba(255,255,255,0.7)' }}>
          We'll collect the appropriate verification information based on your region
        </Typography>
        <FormControl fullWidth>
          <InputLabel>Region</InputLabel>
          <Select
            value={selectedRegion}
            onChange={handleRegionChange}
            label="Region"
            sx={{ 
              color: 'white',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: 'rgba(255,255,255,0.1)',
              },
            }}
          >
            {regions.map((region) => (
              <MenuItem key={region.code} value={region.code}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {region.name}
                  {!region.available && (
                    <Chip label="Coming Soon" size="small" color="default" />
                  )}
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );
  
  // Render KYC form
  const renderKYCForm = () => (
    <>
      <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
        Personal Information & Identity Verification
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: 'rgba(255,255,255,0.7)' }}>
        Please provide accurate information as it appears on your government-issued ID
      </Typography>
      
      <Grid container spacing={3}>
        {/* Personal Information */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
            Personal Details
          </Typography>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="First Name"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            error={!!errors.first_name}
            helperText={errors.first_name}
            required
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Last Name"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            error={!!errors.last_name}
            helperText={errors.last_name}
            required
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Date of Birth"
            name="birth_date"
            type="date"
            value={formData.birth_date}
            onChange={handleChange}
            error={!!errors.birth_date}
            helperText={errors.birth_date}
            required
            InputLabelProps={{ 
              style: { color: 'rgba(255,255,255,0.7)' },
              shrink: true 
            }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        {/* Address Section */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" sx={{ mb: 2, mt: 2, fontWeight: 600 }}>
            Residential Address
          </Typography>
        </Grid>
        
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Street Address"
            name="street_line_1"
            value={formData.street_line_1}
            onChange={handleChange}
            error={!!errors.street_line_1}
            helperText={errors.street_line_1 || 'Start typing to use address autocomplete'}
            required
            inputRef={addressRef}
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ 
              style: { color: '#fff' },
              endAdornment: googleMapsLoaded && (
                <InputAdornment position="end">
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                    🌍
                  </Typography>
                </InputAdornment>
              )
            }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="City"
            name="city"
            value={formData.city}
            onChange={handleChange}
            error={!!errors.city}
            helperText={errors.city}
            required
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={selectedRegion === 'US' ? 'State' : 'State/Province'}
            name="subdivision"
            value={formData.subdivision}
            onChange={handleChange}
            error={!!errors.subdivision}
            helperText={errors.subdivision}
            required
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={selectedRegion === 'US' ? 'ZIP Code' : 'Postal Code'}
            name="postal_code"
            value={formData.postal_code}
            onChange={handleChange}
            error={!!errors.postal_code}
            helperText={errors.postal_code}
            required
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Country"
            name="country"
            value={formData.country}
            onChange={handleChange}
            error={!!errors.country}
            helperText={errors.country}
            required
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        {/* Identity Verification */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" sx={{ mb: 2, mt: 2, fontWeight: 600 }}>
            Identity Verification
          </Typography>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth error={!!errors.id_type}>
            <InputLabel sx={{ color: 'rgba(255,255,255,0.7)' }}>ID Type</InputLabel>
            <Select
              name="id_type"
              value={formData.id_type}
              onChange={handleChange}
              required
              label="ID Type"
              sx={{ 
                color: 'white',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              {ID_TYPES.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
            {errors.id_type && <FormHelperText>{errors.id_type}</FormHelperText>}
          </FormControl>
        </Grid>

        {selectedRegion === 'US' && (
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Social Security Number"
              name="ssn"
              value={formData.ssn}
              onChange={handleChange}
              error={!!errors.ssn}
              helperText={errors.ssn || 'Format: XXX-XX-XXXX'}
              required
              placeholder="XXX-XX-XXXX"
              InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
              InputProps={{ style: { color: '#fff' } }}
              sx={{ 
                '& .MuiOutlinedInput-root': {
                  '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                  '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                }
              }}
            />
          </Grid>
        )}
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="ID Number"
            name="id_number"
            value={formData.id_number}
            onChange={handleChange}
            error={!!errors.id_number}
            helperText={errors.id_number}
            required
            InputLabelProps={{ style: { color: 'rgba(255,255,255,0.7)' } }}
            InputProps={{ style: { color: '#fff' } }}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
              }
            }}
          />
        </Grid>
        
        {/* File Uploads */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" sx={{ mb: 2, mt: 2, fontWeight: 600 }}>
            Document Images
          </Typography>
          <Typography variant="body2" sx={{ mb: 2, color: 'rgba(255,255,255,0.7)' }}>
            {formData.id_type === 'drivers_license' 
              ? 'Please upload clear photos of both the front and back of your driver\'s license'
              : 'Please upload a clear photo of your ID document'
            }
          </Typography>
        </Grid>
        
        <Grid item xs={12} md={formData.id_type === 'drivers_license' ? 6 : 12}>
          <Box>
            <Typography sx={{ mb: 1, color: 'rgba(255,255,255,0.9)' }}>
              ID Front Image *
            </Typography>
            <Button
              variant="outlined"
              component="label"
              fullWidth
              sx={{ 
                height: '56px',
                borderColor: errors.id_image_front ? 'error.main' : 'rgba(255,255,255,0.1)',
                color: 'white',
                justifyContent: 'flex-start'
              }}
            >
              {formData.id_image_front ? `📷 ${formData.id_image_front.name}` : '📷 Upload Front Image'}
              <input
                type="file"
                name="id_image_front"
                onChange={handleFileChange}
                hidden
                accept="image/*"
                required
              />
            </Button>
            {errors.id_image_front && (
              <FormHelperText error>{errors.id_image_front}</FormHelperText>
            )}
          </Box>
        </Grid>
        
        {formData.id_type === 'drivers_license' && (
          <Grid item xs={12} md={6}>
            <Box>
              <Typography sx={{ mb: 1, color: 'rgba(255,255,255,0.9)' }}>
                ID Back Image *
              </Typography>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                sx={{ 
                  height: '56px',
                  borderColor: errors.id_image_back ? 'error.main' : 'rgba(255,255,255,0.1)',
                  color: 'white',
                  justifyContent: 'flex-start'
                }}
              >
                {formData.id_image_back ? `📷 ${formData.id_image_back.name}` : '📷 Upload Back Image'}
                <input
                  type="file"
                  name="id_image_back"
                  onChange={handleFileChange}
                  hidden
                  accept="image/*"
                  required
                />
              </Button>
              {errors.id_image_back && (
                <FormHelperText error>{errors.id_image_back}</FormHelperText>
              )}
            </Box>
          </Grid>
        )}
      </Grid>
    </>
  );
  
  // Render success step
  const renderSuccess = () => (
    <Box sx={{ textAlign: 'center' }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        ✅ Verification Submitted Successfully!
      </Typography>
      <Typography variant="body1" sx={{ mb: 3, color: 'rgba(255,255,255,0.7)' }}>
        Your identity verification has been submitted. You'll be redirected to your dashboard shortly.
      </Typography>
      <CircularProgress sx={{ mt: 2 }} />
    </Box>
  );
  
  return (
    <>
      <AnimatedBackground />
      <Box sx={{ backgroundColor: 'transparent', color: '#fff', minHeight: '100vh', py: 8 }}>
        <Container maxWidth="md">
          <Typography variant="h3" sx={{ mb: 3, textAlign: 'center', fontWeight: 700 }}>
            Identity Verification
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 4, textAlign: 'center', color: 'rgba(255,255,255,0.7)' }}>
            Secure verification powered by Bridge. Your information is encrypted and protected.
          </Typography>
          
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            <Step>
              <StepLabel>Select Region</StepLabel>
            </Step>
            <Step>
              <StepLabel>Provide Information</StepLabel>
            </Step>
            <Step>
              <StepLabel>Complete</StepLabel>
            </Step>
          </Stepper>
          
          {submitError && (
            <Alert severity="error" sx={{ mb: 4 }}>
              {submitError}
            </Alert>
          )}
          
          <Paper
            component={activeStep === 1 ? "form" : "div"}
            onSubmit={activeStep === 1 ? handleSubmit : undefined}
            sx={{ 
              backgroundColor: 'rgba(30, 30, 30, 0.4)',
              p: { xs: 3, md: 5 },
              borderRadius: 2,
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}
          >
            {activeStep === 0 && renderRegionSelection()}
            {activeStep === 1 && renderKYCForm()}
            {activeStep === 2 && (
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6">Verification Submitted</Typography>
                <Typography variant="body2" sx={{ mt: 1, color: 'rgba(255,255,255,0.7)' }}>
                  We’re finalizing your account. This can take up to a minute. You’ll be redirected automatically.
                </Typography>
                <CircularProgress sx={{ mt: 3 }} />
              </Box>
            )}
            
            {activeStep === 1 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
                  By proceeding you acknowledge our Terms of Service.
                </Typography>
                <Button variant="text" onClick={handleGenerateTos} sx={{ color: '#90caf9' }}>
                  View and Accept Terms of Service
                </Button>
                {signedAgreementId ? (
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'rgba(255,255,255,0.7)' }}>
                    Terms accepted. Agreement ID: {signedAgreementId}
                  </Typography>
                ) : (
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'error.main' }}>
                    You must view and accept the Terms of Service to continue.
                  </Typography>
                )}
              </Box>
            )}

            {activeStep === 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                <Button 
                  variant="outlined"
                  onClick={handleBackToRegion}
                  sx={{ 
                    color: 'white',
                    borderColor: 'rgba(255,255,255,0.3)'
                  }}
                >
                  Back
                </Button>
                <Button 
                  type="submit"
                  variant="contained"
                  disabled={isSubmitting || !isFormComplete}
                  sx={{ 
                    bgcolor: isSubmitting || !isFormComplete ? 'action.disabledBackground' : 'primary.main',
                    color: isSubmitting || !isFormComplete ? 'action.disabled' : undefined,
                    '&:hover': {
                      bgcolor: isSubmitting || !isFormComplete ? 'action.disabledBackground' : 'primary.dark',
                    }
                  }}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Verification'}
                </Button>
              </Box>
            )}
          </Paper>
        </Container>
      </Box>
      
      <Snackbar 
        open={submitSuccess} 
        autoHideDuration={6000} 
        onClose={() => setSubmitSuccess(false)}
      >
        <Alert severity="success">
          Identity verification submitted successfully!
        </Alert>
      </Snackbar>
    </>
  );
};

export default KYCVerification; 