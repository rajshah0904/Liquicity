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
  { code: 'EU', name: 'European Union', region: 'eu', available: true },
  { code: 'MX', name: 'Mexico', region: 'mexico', available: true },
  { code: 'BR', name: 'Brazil', region: 'brazil', available: true },
  { code: 'CO', name: 'Colombia', region: 'colombia', available: true },
  { code: 'PE', name: 'Peru', region: 'peru', available: true },
  { code: 'AR', name: 'Argentina', region: 'argentina', available: true },
];

// ID Types for Bridge API
const ID_TYPES = [
  { value: 'drivers_license', label: 'Driver\'s License' },
  { value: 'passport', label: 'Passport' }
];

// International regions (no longer requiring separate verification)
const INTERNATIONAL_REGIONS = ['mexico', 'brazil', 'colombia', 'peru', 'argentina'];

// Regional form configurations - Updated with exact verification requirements
const getFormConfig = (region) => {
  const configs = {
    us: {
      nationalIdLabel: 'Social Security Number',
      nationalIdHint: 'Format: XXX-XX-XXXX',
      nationalIdField: 'ssn',
      bankFieldHint: 'Routing/Account',

      documents: ['Government ID', 'Proof of Address'],
      details: 'Bridge KYC: Identity verification with government-issued ID and address confirmation'
    },
    eu: {
      nationalIdLabel: 'National ID',
      nationalIdHint: 'Government-issued ID (passport, national ID, or driver\'s license)',
      nationalIdField: 'national_id',
      bankFieldHint: 'IBAN',

      documents: ['EU Government ID', 'Proof of Address', 'SEPA Bank Details'],
      details: 'Bridge KYC: EU-compliant identity verification with SEPA endorsements'
    },
    mexico: {
      nationalIdLabel: 'National ID',
      nationalIdHint: 'CURP, RFC, or Mexican government ID',
      nationalIdField: 'national_id',
      bankFieldHint: 'CLABE',

      documents: ['Mexican Government ID', 'Proof of Address', 'SPEI Bank Details'],
      details: 'Bridge KYC: Mexican identity verification with SPEI payment rail support'
    },
    brazil: {
      nationalIdLabel: 'CPF',
      nationalIdHint: 'Brazilian CPF number',
      nationalIdField: 'national_id',
      bankFieldHint: 'PIX key',

      documents: ['Brazilian Government ID', 'CPF', 'Proof of Address', 'PIX Details'],
      details: 'Bridge KYC: Brazilian identity verification with PIX payment rail support'
    },
    colombia: {
      nationalIdLabel: 'Cédula',
      nationalIdHint: 'Cédula de Ciudadanía (CC) or NIT',
      nationalIdField: 'national_id',
      bankFieldHint: 'Colombian bank details',

      documents: ['Colombian Government ID', 'Cédula', 'Proof of Address'],
      details: 'Bridge KYC: Colombian identity verification with local transfer support'
    },
    peru: {
      nationalIdLabel: 'DNI',
      nationalIdHint: 'DNI or Carné de Extranjería (CE)',
      nationalIdField: 'national_id',
      bankFieldHint: 'Peruvian bank details',

      documents: ['Peruvian Government ID', 'DNI/CE', 'Proof of Address'],
      details: 'Bridge KYC: Peruvian identity verification with local transfer support'
    },
    argentina: {
      nationalIdLabel: 'DNI',
      nationalIdHint: 'Documento Nacional de Identidad',
      nationalIdField: 'national_id',
      bankFieldHint: 'CBU or alias',

      documents: ['Argentine Government ID', 'DNI', 'Proof of Address', 'Bank Details'],
      details: 'Bridge KYC: Argentine identity verification with local transfer support'
    },
  };
  
  return configs[region] || configs.us;
};

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
    national_id: '', // for international users
    id_type: '',
    id_number: '',
    id_image_front: null,
    id_image_back: null,
    
    // Region-specific fields
    bank_details: '', // IBAN, CLABE, PIX key, CBU, etc.
    tax_id: '', // CPF, CURP, RFC, etc.
    proof_of_address: null, // Utility bill, bank statement, etc.
    additional_documents: null, // Any additional required documents
    
    // International region additional fields
    phone: '', // Phone number for international
    employment_status: '', // Employment status for international
    expected_monthly_payments: '', // Expected monthly payment volume
    acting_as_intermediary: 'no', // Acting as intermediary (default no)
    most_recent_occupation: '', // Occupation code
    account_purpose: '', // Account purpose
    account_purpose_other: '', // Other account purpose if needed
    source_of_funds: '' // Source of funds
  });
  
  // TOS acceptance state
  const [bridgeTosAccepted, setBridgeTosAccepted] = useState(false);
  
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
      // Determine country restriction based on selected region
      let countryRestriction = undefined;
      if (selectedRegion === 'us') countryRestriction = { country: 'us' };
      else if (selectedRegion === 'mexico') countryRestriction = { country: 'mx' };
      else if (selectedRegion === 'brazil') countryRestriction = { country: 'br' };
      else if (selectedRegion === 'colombia') countryRestriction = { country: 'co' };
      else if (selectedRegion === 'peru') countryRestriction = { country: 'pe' };
      else if (selectedRegion === 'argentina') countryRestriction = { country: 'ar' };
      else if (selectedRegion === 'eu') {
        // For EU, allow multiple European countries
        countryRestriction = { country: ['at', 'be', 'bg', 'hr', 'cy', 'cz', 'dk', 'ee', 'fi', 'fr', 'de', 'gr', 'hu', 'ie', 'it', 'lv', 'lt', 'lu', 'mt', 'nl', 'pl', 'pt', 'ro', 'sk', 'si', 'es', 'se'] };
      }
      
      autocompleteRef.current = new window.google.maps.places.Autocomplete(
        addressRef.current,
        {
          types: ['address'],
          componentRestrictions: countryRestriction
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
    
    // Check if region is available for KYC
    const region = regions.find(r => r.code === regionCode);
    if (!region?.available) {
      console.log(`KYC: Region '${regionCode}' not yet available - redirecting to coming soon`);
      navigate(`/coming-soon?country=${regionCode}&region=${region?.region}`);
      return;
    }
    
    // Set the selected region to the region name (not code) for form config
    setSelectedRegion(region.region);
    
    // Set country based on region
    if (regionCode === 'US') {
      setFormData(prev => ({ ...prev, country: 'USA' }));
    } else if (regionCode === 'EU') {
      setFormData(prev => ({ ...prev, country: 'EU' }));
    } else {
      setFormData(prev => ({ ...prev, country: regionCode }));
    }
    
    console.log(`KYC: Region '${region.region}' selected locally (not saved until KYC complete)`);
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
      
      // Add region-specific data for international KYC
      customerData.region = selectedRegion.toLowerCase();
      customerData.bank_details = formData.bank_details;
      customerData.tax_id = formData.tax_id;
      
      // Add document uploads
      if (formData.proof_of_address) {
        const proofBase64 = await fileToBase64(formData.proof_of_address);
        customerData.proof_of_address = proofBase64;
      }
      
      if (formData.additional_documents) {
        const additionalBase64 = await fileToBase64(formData.additional_documents);
        customerData.additional_documents = additionalBase64;
      }

      if (signedAgreementId) {
        customerData.signed_agreement_id = signedAgreementId;
      }
      
      console.log('Submitting international KYC data to backend...');
      
              // Submit to our backend (which will handle Bridge API calls)
      const response = await api.post(
        '/kyc/v2/submit-info',  // Use new international endpoint
        customerData,
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );
      
      console.log('KYC submission response:', response.data);
      
      // Show processing time information
      const responseData = response.data;
      let processingMessage = `KYC submitted successfully!`;
      
      processingMessage = `KYC submitted successfully for ${selectedRegion.toUpperCase()}!\n` +
        `Expected processing time: 1-2 business days via Bridge API.`;
      
      // Store processing info for display
      setSubmitSuccess(true);
      setActiveStep(2);
      sessionStorage.setItem('kycProcessingInfo', JSON.stringify({
        message: processingMessage,
        region: responseData.region || selectedRegion,
        processing_time: '1-2 business days'
      }));
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
    
    // Add region-specific national ID field
    const config = getFormConfig(selectedRegion);
    if (config.nationalIdField) {
      requiredFields.push(config.nationalIdField);
    }
    
    // Add region-specific required fields
    if (config.bankFieldHint) {
      requiredFields.push('bank_details');
    }
    if (selectedRegion === 'brazil' || selectedRegion === 'mexico') {
      requiredFields.push('tax_id');
    }

    const allTextPresent = requiredFields.every((field) => {
      const value = formData[field];
      return typeof value === 'string' ? value.trim().length > 0 : Boolean(value);
    });

    const imagesPresent = Boolean(formData.id_image_front) && (
      formData.id_type !== 'drivers_license' || Boolean(formData.id_image_back)
    );
    
    // Check required document uploads
    const requiredDocsPresent = Boolean(formData.proof_of_address) && (
      !(selectedRegion === 'eu' || selectedRegion === 'brazil') || Boolean(formData.additional_documents)
    );

    // Validate national ID based on region
    let nationalIdValid = true;
    if (selectedRegion === 'us' && formData.ssn) {
      nationalIdValid = formData.ssn.replace(/\D/g, '').length === 9;
    } else if (selectedRegion !== 'us' && formData.national_id) {
      nationalIdValid = formData.national_id.trim().length > 0;
    }

    // Check TOS acceptance - Bridge required for all
    const allTosAccepted = bridgeTosAccepted;

    return allTextPresent && imagesPresent && requiredDocsPresent && nationalIdValid && allTosAccepted;
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
      <Typography variant="body2" sx={{ mb: 2, color: 'rgba(255,255,255,0.7)' }}>
        Please provide accurate information as it appears on your government-issued ID
      </Typography>
      
      {/* Verification Requirements Info */}
      <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.1)' }}>
        <Typography variant="subtitle2" sx={{ mb: 1, color: '#90caf9', fontWeight: 600 }}>
          Required for {getFormConfig(selectedRegion).details?.split(':')[0] || 'Verification'}
        </Typography>
        <Typography variant="body2" sx={{ mb: 1, color: 'rgba(255,255,255,0.8)' }}>
          {getFormConfig(selectedRegion).details?.split(':')[1] || 'Identity verification required'}
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {getFormConfig(selectedRegion).documents?.map((doc, index) => (
            <Chip 
              key={index} 
              label={doc} 
              size="small" 
              sx={{ 
                backgroundColor: 'rgba(144, 202, 249, 0.1)', 
                color: '#90caf9',
                border: '1px solid rgba(144, 202, 249, 0.3)'
              }} 
            />
          ))}
        </Box>
      </Box>
      
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

        {/* National ID field - adapts based on region */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={getFormConfig(selectedRegion).nationalIdLabel}
            name={getFormConfig(selectedRegion).nationalIdField}
            value={formData[getFormConfig(selectedRegion).nationalIdField]}
            onChange={handleChange}
            error={!!errors[getFormConfig(selectedRegion).nationalIdField]}
            helperText={errors[getFormConfig(selectedRegion).nationalIdField] || getFormConfig(selectedRegion).nationalIdHint}
            required
            placeholder={selectedRegion === 'us' ? 'XXX-XX-XXXX' : getFormConfig(selectedRegion).nationalIdHint}
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
        
        {/* Region-Specific Additional Fields */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" sx={{ mb: 2, mt: 3, fontWeight: 600 }}>
            Additional Regional Requirements
          </Typography>
        </Grid>
        
        {/* Bank Details Field - Required for most regions */}
        {getFormConfig(selectedRegion).bankFieldHint && (
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={`Bank Details (${getFormConfig(selectedRegion).bankFieldHint})`}
              name="bank_details"
              value={formData.bank_details}
              onChange={handleChange}
              error={!!errors.bank_details}
              helperText={errors.bank_details || `Please provide your ${getFormConfig(selectedRegion).bankFieldHint} for payments`}
              required
              placeholder={
                selectedRegion === 'eu' ? 'DE89 3704 0044 0532 0130 00' :
                selectedRegion === 'mexico' ? '646180157000000004' :
                selectedRegion === 'brazil' ? 'your-pix-key@email.com' :
                selectedRegion === 'argentina' ? '0000003100010000000001' :
                'Your bank account details'
              }
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
        
        {/* Tax ID / Additional ID Field for specific regions */}
        {(selectedRegion === 'brazil' || selectedRegion === 'mexico') && (
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={selectedRegion === 'brazil' ? 'CPF Number' : 'CURP/RFC'}
              name="tax_id"
              value={formData.tax_id || ''}
              onChange={handleChange}
              error={!!errors.tax_id}
              helperText={
                errors.tax_id || 
                (selectedRegion === 'brazil' ? 'Brazilian CPF number (11 digits)' : 'Mexican CURP or RFC number')
              }
              required
              placeholder={selectedRegion === 'brazil' ? '000.000.000-00' : 'CURP18DIGITS000 or RFC12DIGITS000'}
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
        
        {/* Proof of Address Upload */}
        <Grid item xs={12} md={6}>
          <Box>
            <Typography sx={{ mb: 1, color: 'rgba(255,255,255,0.9)' }}>
              Proof of Address *
            </Typography>
            <Typography variant="caption" sx={{ display: 'block', mb: 1, color: 'rgba(255,255,255,0.6)' }}>
              Utility bill, bank statement, or government document (dated within last 3 months)
            </Typography>
            <Button
              variant="outlined"
              component="label"
              fullWidth
              sx={{ 
                height: '56px',
                borderColor: errors.proof_of_address ? 'error.main' : 'rgba(255,255,255,0.1)',
                color: 'white',
                justifyContent: 'flex-start'
              }}
            >
              {formData.proof_of_address ? `📄 ${formData.proof_of_address.name}` : '📄 Upload Proof of Address'}
              <input
                type="file"
                name="proof_of_address"
                onChange={handleFileChange}
                hidden
                accept="image/*,.pdf"
                required
              />
            </Button>
            {errors.proof_of_address && (
              <FormHelperText error>{errors.proof_of_address}</FormHelperText>
            )}
          </Box>
        </Grid>
        
        {/* Additional Documents for specific regions */}
        {(selectedRegion === 'eu' || selectedRegion === 'brazil') && (
          <Grid item xs={12} md={6}>
            <Box>
              <Typography sx={{ mb: 1, color: 'rgba(255,255,255,0.9)' }}>
                {selectedRegion === 'eu' ? 'SEPA Authorization *' : 'Additional Brazilian Documents *'}
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', mb: 1, color: 'rgba(255,255,255,0.6)' }}>
                {selectedRegion === 'eu' 
                  ? 'SEPA direct debit mandate or bank authorization letter'
                  : 'Additional Brazilian identity or residency documents'
                }
              </Typography>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                sx={{ 
                  height: '56px',
                  borderColor: errors.additional_documents ? 'error.main' : 'rgba(255,255,255,0.1)',
                  color: 'white',
                  justifyContent: 'flex-start'
                }}
              >
                {formData.additional_documents ? `📎 ${formData.additional_documents.name}` : '📎 Upload Additional Documents'}
                <input
                  type="file"
                  name="additional_documents"
                  onChange={handleFileChange}
                  hidden
                  accept="image/*,.pdf"
                  required
                />
              </Button>
              {errors.additional_documents && (
                <FormHelperText error>{errors.additional_documents}</FormHelperText>
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
            {activeStep === 2 && (() => {
              const processingInfo = JSON.parse(sessionStorage.getItem('kycProcessingInfo') || '{}');
              
              return (
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ color: '#00ff88', mb: 3 }}>
                    ✅ Verification Submitted Successfully!
                  </Typography>
                  
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="h6" sx={{ color: '#ffffff', mb: 2 }}>
                      KYC Processing for {processingInfo.region?.toUpperCase() || selectedRegion.toUpperCase()}
                    </Typography>
                    <Box sx={{ 
                      background: 'rgba(255,255,255,0.1)', 
                      borderRadius: 2, 
                      p: 3, 
                      mb: 2,
                      textAlign: 'center',
                      maxWidth: 500,
                      mx: 'auto'
                    }}>
                      <Typography variant="subtitle1" sx={{ color: '#00ff88', mb: 1 }}>
                        🌉 Bridge API
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 1 }}>
                        Global compliance and identity verification
                      </Typography>
                      <Typography variant="h6" sx={{ color: '#00ff88', mb: 2 }}>
                        ⏱️ Expected processing time: {processingInfo.processing_time || '1-2 business days'}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', mb: 2 }}>
                    📧 You'll receive email notifications when your verification is complete.
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 3 }}>
                    Redirecting to dashboard...
                  </Typography>
                  <CircularProgress sx={{ color: '#00ff88' }} />
                </Box>
              );
            })()}
            
            {activeStep === 1 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 2 }}>
                  Terms of Service Acceptance
                </Typography>
                
                {/* Bridge TOS - Required for all regions */}
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <input
                      type="checkbox"
                      id="bridge-tos"
                      checked={bridgeTosAccepted}
                      onChange={(e) => setBridgeTosAccepted(e.target.checked)}
                      style={{ marginRight: 8 }}
                    />
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      I accept the{' '}
                      <Button 
                        variant="text" 
                        onClick={handleGenerateTos} 
                        sx={{ color: '#90caf9', textTransform: 'none', p: 0, minWidth: 'auto' }}
                      >
                        Bridge Terms of Service
                      </Button>
                    </Typography>
                  </Box>
                  {signedAgreementId && (
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', ml: 3 }}>
                      ✓ Terms accepted. Agreement ID: {signedAgreementId}
                    </Typography>
                  )}
                </Box>
                

                
                {!bridgeTosAccepted && (
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'error.main' }}>
                    You must accept the Bridge Terms of Service to continue.
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