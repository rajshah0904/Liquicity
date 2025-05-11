import React, { useState, useEffect } from 'react';
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
  Paper
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { AnimatedBackground } from '../components/ui/ModernUIComponents';
import api from '../utils/api';
import { kycAPI } from '../utils/api';

// Define KYC requirements for different countries
const countryKycRequirements = {
  US: {
    name: 'United States',
    fields: [
      { name: 'firstName', label: 'First Name', type: 'text', required: true },
      { name: 'lastName', label: 'Last Name', type: 'text', required: true },
      { name: 'dateOfBirth', label: 'Date of Birth', type: 'date', required: true },
      { name: 'streetAddress', label: 'Street Address', type: 'text', required: true },
      { name: 'city', label: 'City', type: 'text', required: true },
      { name: 'state', label: 'State', type: 'select', required: true, 
        options: [
          { value: 'AL', label: 'Alabama' },
          { value: 'AK', label: 'Alaska' },
          { value: 'AZ', label: 'Arizona' },
          { value: 'AR', label: 'Arkansas' },
          { value: 'CA', label: 'California' },
          { value: 'CO', label: 'Colorado' },
          { value: 'CT', label: 'Connecticut' },
          { value: 'DE', label: 'Delaware' },
          { value: 'FL', label: 'Florida' },
          { value: 'GA', label: 'Georgia' },
          { value: 'HI', label: 'Hawaii' },
          { value: 'ID', label: 'Idaho' },
          { value: 'IL', label: 'Illinois' },
          { value: 'IN', label: 'Indiana' },
          { value: 'IA', label: 'Iowa' },
          { value: 'KS', label: 'Kansas' },
          { value: 'KY', label: 'Kentucky' },
          { value: 'LA', label: 'Louisiana' },
          { value: 'ME', label: 'Maine' },
          { value: 'MD', label: 'Maryland' },
          { value: 'MA', label: 'Massachusetts' },
          { value: 'MI', label: 'Michigan' },
          { value: 'MN', label: 'Minnesota' },
          { value: 'MS', label: 'Mississippi' },
          { value: 'MO', label: 'Missouri' },
          { value: 'MT', label: 'Montana' },
          { value: 'NE', label: 'Nebraska' },
          { value: 'NV', label: 'Nevada' },
          { value: 'NH', label: 'New Hampshire' },
          { value: 'NJ', label: 'New Jersey' },
          { value: 'NM', label: 'New Mexico' },
          { value: 'NY', label: 'New York' },
          { value: 'NC', label: 'North Carolina' },
          { value: 'ND', label: 'North Dakota' },
          { value: 'OH', label: 'Ohio' },
          { value: 'OK', label: 'Oklahoma' },
          { value: 'OR', label: 'Oregon' },
          { value: 'PA', label: 'Pennsylvania' },
          { value: 'RI', label: 'Rhode Island' },
          { value: 'SC', label: 'South Carolina' },
          { value: 'SD', label: 'South Dakota' },
          { value: 'TN', label: 'Tennessee' },
          { value: 'TX', label: 'Texas' },
          { value: 'UT', label: 'Utah' },
          { value: 'VT', label: 'Vermont' },
          { value: 'VA', label: 'Virginia' },
          { value: 'WA', label: 'Washington' },
          { value: 'WV', label: 'West Virginia' },
          { value: 'WI', label: 'Wisconsin' },
          { value: 'WY', label: 'Wyoming' },
          { value: 'DC', label: 'District of Columbia' },
          { value: 'PR', label: 'Puerto Rico' },
        ]
      },
      { name: 'postalCode', label: 'ZIP Code', type: 'text', required: true },
      { name: 'idType', label: 'ID Type', type: 'select', required: true,
        options:[
          {value:'ssn',label:'Social Security Number'},
          {value:'drivers_license', label:'Driver License'},
          {value:'passport', label:'Passport'}
        ]
      },
      { name: 'idNumber', label: 'ID Number', type: 'text', required: true },
      { name: 'idImageFront', label: 'ID Image (Front)', type: 'file', required: false,
        dependsOn:{field:'idType', values:['drivers_license','passport']}
      },
      { name: 'idImageBack', label: 'ID Image (Back)', type: 'file', required: false,
        dependsOn:{field:'idType', values:['drivers_license']}
      },
    ],
    description: 'Per FinCEN CIP Rule (31 C.F.R. § 1020.220)'
  },
  MX: {
    name: 'Mexico',
    fields: [
      { name: 'firstName', label: 'First Name', type: 'text', required: true },
      { name: 'lastName', label: 'Last Name', type: 'text', required: true },
      { name: 'dateOfBirth', label: 'Date of Birth', type: 'date', required: true },
      { name: 'nationality', label: 'Nationality', type: 'text', required: true },
      { name: 'streetAddress', label: 'Street Address', type: 'text', required: true },
      { name: 'city', label: 'City', type: 'text', required: true },
      { name: 'state', label: 'State', type: 'select', required: true, 
        options: [
          { value: 'AGS', label: 'Aguascalientes' },
          { value: 'BC', label: 'Baja California' },
          { value: 'BCS', label: 'Baja California Sur' },
          { value: 'CAM', label: 'Campeche' },
          { value: 'CHIS', label: 'Chiapas' },
          { value: 'CHIH', label: 'Chihuahua' },
          { value: 'CDMX', label: 'Ciudad de México' },
          { value: 'COAH', label: 'Coahuila' },
          { value: 'COL', label: 'Colima' },
          { value: 'DGO', label: 'Durango' },
          { value: 'GTO', label: 'Guanajuato' },
          { value: 'GRO', label: 'Guerrero' },
          { value: 'HGO', label: 'Hidalgo' },
          { value: 'JAL', label: 'Jalisco' },
          { value: 'MEX', label: 'México' },
          { value: 'MICH', label: 'Michoacán' },
          { value: 'MOR', label: 'Morelos' },
          { value: 'NAY', label: 'Nayarit' },
          { value: 'NL', label: 'Nuevo León' },
          { value: 'OAX', label: 'Oaxaca' },
          { value: 'PUE', label: 'Puebla' },
          { value: 'QRO', label: 'Querétaro' },
          { value: 'QROO', label: 'Quintana Roo' },
          { value: 'SLP', label: 'San Luis Potosí' },
          { value: 'SIN', label: 'Sinaloa' },
          { value: 'SON', label: 'Sonora' },
          { value: 'TAB', label: 'Tabasco' },
          { value: 'TAMPS', label: 'Tamaulipas' },
          { value: 'TLAX', label: 'Tlaxcala' },
          { value: 'VER', label: 'Veracruz' },
          { value: 'YUC', label: 'Yucatán' },
          { value: 'ZAC', label: 'Zacatecas' }
        ]
      },
      { name: 'postalCode', label: 'Postal Code', type: 'text', required: true },
      { name: 'idType', label: 'ID Type', type: 'select', required: true,
        options:[
          {value:'consular_id', label:'Consular ID'},
          {value:'permanent_residency_id', label:'Residency Permit'},
          {value:'passport', label:'Passport'}
        ]
      },
      { name: 'idNumber', label: 'ID Number', type: 'text', required: true },
      { name: 'idImageFront', label: 'ID Image (Front)', type: 'file', required: true,
        dependsOn:{field:'idType', values:['consular_id','permanent_residency_id','passport']}
      },
      { name: 'idImageBack', label: 'ID Image (Back)', type: 'file', required: false },
      { name: 'rfc', label: 'Tax Identification Number (RFC)', type: 'text', required: true },
      { name: 'email', label: 'Email Address', type: 'email', required: true },
    ],
    description: 'According to CNBV and AML law (LFPIORPI)'
  },
  EU: {
    name: 'European Union',
    fields: [
      { name: 'firstName', label: 'First Name', type: 'text', required: true },
      { name: 'lastName', label: 'Last Name', type: 'text', required: true },
      { name: 'dateOfBirth', label: 'Date of Birth', type: 'date', required: true },
      { name: 'streetAddress', label: 'Street Address (Line 1)', type: 'text', required: true },
      { name: 'streetAddress2', label: 'Street Address (Line 2)', type: 'text', required: false },
      { name: 'city', label: 'City', type: 'text', required: true },
      { name: 'region', label: 'Subdivision (ISO-3166-2 code, e.g. MAN)', type: 'text', required: true },
      { name: 'postalCode', label: 'Postal Code', type: 'text', required: true },
      { name: 'countryOfResidence', label: 'Country of Residence', type: 'select', required: true,
        options: [
          { value: 'AT', label: 'Austria' },
          { value: 'BE', label: 'Belgium' },
          { value: 'BG', label: 'Bulgaria' },
          { value: 'HR', label: 'Croatia' },
          { value: 'CY', label: 'Cyprus' },
          { value: 'CZ', label: 'Czechia' },
          { value: 'DK', label: 'Denmark' },
          { value: 'EE', label: 'Estonia' },
          { value: 'FI', label: 'Finland' },
          { value: 'FR', label: 'France' },
          { value: 'DE', label: 'Germany' },
          { value: 'EL', label: 'Greece' },
          { value: 'HU', label: 'Hungary' },
          { value: 'IE', label: 'Ireland' },
          { value: 'IT', label: 'Italy' },
          { value: 'LV', label: 'Latvia' },
          { value: 'LI', label: 'Liechtenstein' },
          { value: 'LT', label: 'Lithuania' },
          { value: 'LU', label: 'Luxembourg' },
          { value: 'MT', label: 'Malta' },
          { value: 'NL', label: 'Netherlands' },
          { value: 'NO', label: 'Norway' },
          { value: 'PL', label: 'Poland' },
          { value: 'PT', label: 'Portugal' },
          { value: 'RO', label: 'Romania' },
          { value: 'SK', label: 'Slovakia' },
          { value: 'SI', label: 'Slovenia' },
          { value: 'ES', label: 'Spain' },
          { value: 'SE', label: 'Sweden' },
          { value: 'CH', label: 'Switzerland' },
          { value: 'GB', label: 'United Kingdom' }
        ]
      },
      { name: 'idType', label:'ID Type', type:'select', required:true,
        options:[
          {value:'drivers_license', label:'Driver License'},
          {value:'national_id', label:'National ID'},
          {value:'passport', label:'Passport'}
        ]
      },
      { name: 'idNumber', label: 'ID Number', type: 'text', required: true },
      { name: 'idImageFront', label: 'ID Image (Front)', type: 'file', required: true,
        dependsOn:{field:'idType', values:['drivers_license','national_id','passport']}
      },
      { name: 'idImageBack', label: 'ID Image (Back)', type: 'file', required: false,
        dependsOn:{field:'idType', values:['drivers_license']}
      },
      { name: 'proofOfAddress', label: 'Proof of Address Document', type: 'file', required: false },
      { name: 'personalIdNumber', label: 'Personal Identification Number (if applicable)', type: 'text', required: false },
    ],
    description: 'Under EU AML/CFT rules (Directive (EU) 2015/849 and delegations)'
  }
};

// Countries for dropdown selection
const countries = [
  { code: 'US', name: 'United States' },
  { code: 'MX', name: 'Mexico' },
  { code: 'EU', name: 'European Union' },
];

const KYCVerification = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading, getAccessTokenSilently } = useAuth0();
  const [dbUserId, setDbUserId] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [activeStep, setActiveStep] = useState(0);
  const [verificationStatus, setVerificationStatus] = useState(null);
  
  // Initialize form data when country is selected
  useEffect(() => {
    if (selectedCountry) {
      const countryConfig = countryKycRequirements[selectedCountry];
      if (countryConfig) {
        // Initialize form data for selected country
        const initialData = {};
        countryConfig.fields.forEach(field => {
          initialData[field.name] = '';
        });
        
        // Pre-populate with user data if available
        if (user) {
          const parts = user.name ? user.name.split(' ') : [''];
          initialData.firstName = parts[0];
          initialData.lastName = parts.slice(1).join(' ');
          initialData.email = user.email || '';
        }
        
        setFormData(initialData);
        setErrors({});
      }
    }
  }, [selectedCountry, user]);
  
  // Update required fields based on ID type for US
  useEffect(() => {
    if (selectedCountry === 'US' && formData.idType) {
      // Clear errors for conditional fields when ID type changes
      const fieldsToCheck = ['idIssuingState', 'idExpiryDate'];
      const updatedErrors = { ...errors };
      
      fieldsToCheck.forEach(field => {
        if (updatedErrors[field]) {
          delete updatedErrors[field];
        }
      });
      
      setErrors(updatedErrors);
    }
  }, [selectedCountry, formData.idType]);
  
  // If we already know user ID, check KYC status so we can skip the form when pending/approved
  useEffect(() => {
    const fetchKycStatus = async () => {
      if (!dbUserId) return;
      try {
        const { data } = await kycAPI.getKycStatus(dbUserId);
        setVerificationStatus(data.verification_status);

        if (data.verification_status === 'approved') {
          navigate('/dashboard');
        } else if (data.verification_status === 'pending') {
          setActiveStep(2); // show pending screen
        }
      } catch (err) {
        console.error('Failed to fetch KYC status', err);
      }
    };

    fetchKycStatus();
  }, [dbUserId, navigate]);
  
  // Handle country selection change
  const handleCountryChange = (e) => {
    setSelectedCountry(e.target.value);
    setActiveStep(1);
  };
  
  // Go back to country selection and clear previously entered data
  const handleBackToCountry = () => {
    setSelectedCountry('');
    setFormData({});
    setErrors({});
    setActiveStep(0);
  };
  
  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;

    // Auto-format SSN while typing for US users
    let newValue = value;
    if (selectedCountry === 'US' && formData.idType === 'ssn' && name === 'idNumber') {
      const digits = value.replace(/\D/g, '').slice(0, 9);
      if (digits.length > 5) {
        newValue = digits.replace(/^(\d{3})(\d{2})(\d+)/, '$1-$2-$3');
      } else if (digits.length > 3) {
        newValue = digits.replace(/^(\d{3})(\d+)/, '$1-$2');
      } else {
        newValue = digits;
      }
    }

    setFormData({
      ...formData,
      [name]: newValue
    });
    
    // Clear error when field is changed
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };
  
  // Handle file uploads
  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      setFormData({
        ...formData,
        [name]: files[0]
      });
      
      if (errors[name]) {
        setErrors({
          ...errors,
          [name]: ''
        });
      }
    }
  };
  
  // Validate the form based on selected country
  const validateForm = () => {
    const newErrors = {};
    const countryConfig = countryKycRequirements[selectedCountry];
    
    if (!countryConfig) {
      return false;
    }
    
    // Validate required fields
    countryConfig.fields.forEach(field => {
      // Check if the field should be validated based on dependencies
      if (field.dependsOn) {
        const dependentField = field.dependsOn.field;
        const allowedValues = field.dependsOn.values;
        
        // Skip validation if the dependency condition is not met
        if (!formData[dependentField] || !allowedValues.includes(formData[dependentField])) {
          return;
        }
      }
      
      if (field.required && !formData[field.name]) {
        newErrors[field.name] = `${field.label} is required`;
      }
    });
    
    // Special validations
    if (selectedCountry === 'US') {
      // Conditional validations based on ID type
      if (formData.idNumber) {
        const digits = formData.idNumber.replace(/\D/g, '');
        if (digits.length !== 9) {
          newErrors.idNumber = 'Enter a valid SSN (9 digits)';
        }
      }
    }
    
    // Image requirements based on idType
    if (formData.idType === 'drivers_license') {
      if (!formData.idImageFront) newErrors.idImageFront = 'Front image required';
      if (!formData.idImageBack) newErrors.idImageBack = 'Back image required';
    } else if (formData.idType && formData.idType !== 'ssn') {
      if (!formData.idImageFront) newErrors.idImageFront = 'Front image required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    setSubmitError('');
    
    try {
      // Create a new FormData object for file uploads
      const submitData = new FormData();
      
      // Process full name into first/last name for backend
      submitData.append('first_name', formData.firstName);
      submitData.append('last_name', formData.lastName);
      
      // Add country information
      submitData.append('kyc_country', selectedCountry);
      
      // Always include Auth0 email claim
      if (user && user.email) {
        submitData.append('email', user.email);
      }
      
      // Append all form fields, converting camelCase keys to snake_case
      Object.entries(formData).forEach(([key, value]) => {
        // Skip firstName and lastName as we've already processed them
        if (key === 'firstName' || key === 'lastName') return;
        
        // Map specific fields to their backend names
        const fieldMapping = {
          'dateOfBirth': 'date_of_birth',
          'streetAddress': 'street_address',
          'streetAddress2': 'street_address_2',
          'postalCode': 'postal_code',
          'idType': 'id_type',
          'idNumber': 'id_number',
          'region': 'state',
          'proofOfAddress': 'proof_of_address',
          'countryOfResidence': 'country_of_residence',
          'firstName': 'first_name',
          'lastName': 'last_name',
        };
        
        // Use mapped name if it exists, otherwise convert camelCase to snake_case
        const snakeKey = fieldMapping[key] || key.replace(/([A-Z])/g, '_$1').toLowerCase();
        submitData.append(snakeKey, value);
      });
      
      console.log('Submitting KYC data to backend...');
      
      // Submit KYC data to backend
      const response = await api.post(
        '/user/kyc/submit',
        submitData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      console.log('KYC submission response:', response.data);
      setSubmitSuccess(true);
      
      // Wait for 2 seconds to show success message before redirecting
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (error) {
      console.error('KYC submission error:', error);
      
      // Handle specific error cases
      if (error.response) {
        // The server responded with an error status
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
        // The request was made but no response was received
        if (error.code === 'ECONNABORTED') {
          setSubmitError('Request timed out. Please check your connection and try again.');
        } else {
          setSubmitError('Network error. Please check your connection and try again.');
        }
      } else {
        // Something else happened while setting up the request
        setSubmitError('Failed to submit verification. Please try again or contact support.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
  
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
  
  // Render form fields for selected country
  const renderFormFields = () => {
    if (!selectedCountry) return null;
    
    const countryConfig = countryKycRequirements[selectedCountry];
    if (!countryConfig) return null;
  
  return (
    <>
        <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
          {countryConfig.name} KYC Requirements
          </Typography>
          
        <Typography variant="body2" sx={{ mb: 3, color: 'rgba(255,255,255,0.7)' }}>
          {countryConfig.description}
          </Typography>
          
            <Grid container spacing={3}>
          {countryConfig.fields.map((field, index) => {
            // Check if the field should be displayed based on dependencies
            if (field.dependsOn) {
              const dependentField = field.dependsOn.field;
              const allowedValues = field.dependsOn.values;
              
              // Skip rendering if the dependency condition is not met
              if (!formData[dependentField] || !allowedValues.includes(formData[dependentField])) {
                return null;
              }
            }
            
            return (
              <Grid item xs={12} md={field.type === 'text' || field.type === 'email' ? 6 : 12} key={index}>
                {field.type === 'select' ? (
                  <FormControl fullWidth error={!!errors[field.name]}>
                    <InputLabel>{field.label}</InputLabel>
                    <Select
                      name={field.name}
                      value={formData[field.name] || ''}
                  onChange={handleChange}
                      required={field.required}
                      label={field.label}
                    >
                      {field.options.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                    {errors[field.name] && <FormHelperText>{errors[field.name]}</FormHelperText>}
                  </FormControl>
                ) : field.type === 'file' ? (
                  <Box>
                    <Typography sx={{ mb: 1 }}>{field.label}</Typography>
                    <Button
                  variant="outlined"
                      component="label"
                      fullWidth
                  sx={{ 
                        height: '56px',
                        borderColor: errors[field.name] ? 'error.main' : 'rgba(255,255,255,0.1)',
                        color: 'white'
                      }}
                    >
                      {formData[field.name] ? 'File selected' : 'Choose File'}
                      <input
                        type="file"
                        name={field.name}
                        onChange={handleFileChange}
                        hidden
                        required={field.required}
                      />
                    </Button>
                    {errors[field.name] && (
                      <FormHelperText error>{errors[field.name]}</FormHelperText>
                    )}
                  </Box>
                ) : (
                <TextField
                  fullWidth
                    label={field.label}
                    name={field.name}
                    type={field.type}
                    value={formData[field.name] || ''}
                  onChange={handleChange}
                    error={!!errors[field.name]}
                    helperText={errors[field.name]}
                    required={field.required}
                  InputLabelProps={{ 
                      style: { color: 'rgba(255,255,255,0.7)' },
                      shrink: field.type === 'date' ? true : undefined
                  }}
                  InputProps={{ style: { color: '#fff' } }}
                  sx={{ 
                    '& .MuiOutlinedInput-root': {
                      '& fieldset': {
                        borderColor: 'rgba(255,255,255,0.1)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255,255,255,0.2)',
                      },
                    }
                  }}
                />
                )}
              </Grid>
            );
          })}
        </Grid>
      </>
    );
  };
  
  // Render country selection step
  const renderCountrySelection = () => {
    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
            Select Your Country
          </Typography>
          <Typography variant="body2" sx={{ mb: 3, color: 'rgba(255,255,255,0.7)' }}>
            We'll show you the appropriate verification requirements based on your location
          </Typography>
          <FormControl fullWidth>
            <InputLabel>Country</InputLabel>
                  <Select
              value={selectedCountry}
              onChange={handleCountryChange}
                    label="Country"
                    sx={{ 
                color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255,255,255,0.1)',
                      },
                    }}
                  >
                    {countries.map((country) => (
                      <MenuItem key={country.code} value={country.code}>
                        {country.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
      </Grid>
    );
  };
  
  return (
    <>
      <AnimatedBackground />
      <Box sx={{ backgroundColor: 'transparent', color: '#fff', minHeight: '100vh', py: 8 }}>
        <Container maxWidth="md">
          <Typography variant="h3" sx={{ mb: 3, textAlign: 'center', fontWeight: 700 }}>
            Verify Your Identity
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 4, textAlign: 'center', color: 'rgba(255,255,255,0.7)' }}>
            To comply with financial regulations and ensure the security of our platform, 
            we require identity verification. Your information is encrypted and securely stored.
          </Typography>
          
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            <Step>
              <StepLabel>Select Country</StepLabel>
            </Step>
            <Step>
              <StepLabel>Provide Information</StepLabel>
            </Step>
            <Step>
              <StepLabel>Submission</StepLabel>
            </Step>
          </Stepper>
          
          {submitError && (
            <Alert severity="error" sx={{ mb: 4 }}>
              {submitError}
            </Alert>
          )}
          
          {submitSuccess && (
            <Alert severity="success" sx={{ mb: 4 }}>
              Your information has been submitted successfully!
            </Alert>
          )}
          
          <Paper
            component="form"
            onSubmit={handleSubmit}
                  sx={{ 
              backgroundColor: 'rgba(30, 30, 30, 0.4)',
              p: { xs: 3, md: 5 },
              borderRadius: 2,
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}
          >
            {activeStep === 0 && renderCountrySelection()}
            {activeStep === 1 && renderFormFields()}
            {activeStep === 2 && (
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6">
                  Verification Submitted
                </Typography>
                <Typography variant="body1" sx={{ mt: 2 }}>
                  Your information has been submitted for verification. We'll review it shortly.
                </Typography>
                <CircularProgress sx={{ mt: 4 }} />
              </Box>
            )}
            
            {activeStep === 1 && (
              <>
                <Box sx={{ mt: 4, backgroundColor: 'rgba(25, 118, 210, 0.1)', p: 2, borderRadius: 1 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    <strong>Verification Process:</strong> Your information will be verified through secure third-party services 
                    such as Socure, Persona, or Trulioo for ID verification and Plaid for bank account verification when applicable. 
                    We do not store sensitive document images or complete ID numbers in our database. All verification is done 
                    securely and in compliance with financial regulations.
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                  <Button 
                    variant="outlined"
                    onClick={handleBackToCountry}
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
                  disabled={isSubmitting}
                  sx={{ 
                      bgcolor: 'primary.main',
                      '&:hover': {
                        bgcolor: 'primary.dark',
                      }
                    }}
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Verification'}
                </Button>
          </Box>
              </>
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
          Your identity verification has been submitted successfully!
        </Alert>
      </Snackbar>
    </>
  );
};

export default KYCVerification; 