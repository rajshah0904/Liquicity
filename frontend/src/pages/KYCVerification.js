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
import api, { authAPI } from '../utils/api';

// Define KYC requirements for different countries
const countryKycRequirements = {
  US: {
    name: 'United States',
    fields: [
      { name: 'fullName', label: 'Full Legal Name', type: 'text', required: true },
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
      { name: 'idType', label: 'Identification Type', type: 'select', required: true, 
        options: [
          { value: 'ssn', label: 'Social Security Number (SSN)' },
          { value: 'drivers_license', label: 'Driver\'s License' },
          { value: 'passport', label: 'US Passport' },
          { value: 'state_id', label: 'State ID Card' }
        ]
      },
      { name: 'idNumber', label: 'ID Number', type: 'text', required: true },
      { name: 'idState', label: 'Issuing State', type: 'select', required: false, 
        dependsOn: { field: 'idType', values: ['drivers_license', 'state_id'] },
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
      { name: 'idExpiryDate', label: 'ID Expiry Date', type: 'date', required: false,
        dependsOn: { field: 'idType', values: ['drivers_license', 'state_id', 'passport'] }
      }
    ],
    description: 'Per FinCEN CIP Rule (31 C.F.R. § 1020.220)'
  },
  CA: {
    name: 'Canada',
    fields: [
      { name: 'fullName', label: 'Full Legal Name', type: 'text', required: true },
      { name: 'dateOfBirth', label: 'Date of Birth', type: 'date', required: true },
      { name: 'streetAddress', label: 'Street Address', type: 'text', required: true },
      { name: 'city', label: 'City', type: 'text', required: true },
      { name: 'province', label: 'Province', type: 'select', required: true, 
        options: [
          { value: 'AB', label: 'Alberta' },
          { value: 'BC', label: 'British Columbia' },
          { value: 'MB', label: 'Manitoba' },
          { value: 'NB', label: 'New Brunswick' },
          { value: 'NL', label: 'Newfoundland and Labrador' },
          { value: 'NS', label: 'Nova Scotia' },
          { value: 'NT', label: 'Northwest Territories' },
          { value: 'NU', label: 'Nunavut' },
          { value: 'ON', label: 'Ontario' },
          { value: 'PE', label: 'Prince Edward Island' },
          { value: 'QC', label: 'Quebec' },
          { value: 'SK', label: 'Saskatchewan' },
          { value: 'YT', label: 'Yukon' }
        ]
      },
      { name: 'postalCode', label: 'Postal Code', type: 'text', required: true },
      { name: 'idType', label: 'Government-issued ID Type', type: 'select', required: true, 
        options: [
  { value: 'passport', label: 'Passport' },
  { value: 'drivers_license', label: 'Driver\'s License' },
        ]
      },
      { name: 'idNumber', label: 'ID Number', type: 'text', required: true },
      { name: 'idIssuingProvince', label: 'Issuing Province', type: 'text', required: true },
      { name: 'idExpiryDate', label: 'ID Expiry Date', type: 'date', required: true },
    ],
    description: 'Per FINTRAC\'s PCMLTFA guidance for Money Services Businesses'
  },
  NG: {
    name: 'Nigeria',
    fields: [
      { name: 'fullName', label: 'Full Legal Name', type: 'text', required: true },
      { name: 'dateOfBirth', label: 'Date of Birth', type: 'date', required: true },
      { name: 'gender', label: 'Gender', type: 'select', required: true,
        options: [
          { value: 'male', label: 'Male' },
          { value: 'female', label: 'Female' },
          { value: 'other', label: 'Other' }
        ]
      },
      { name: 'nationality', label: 'Nationality', type: 'text', required: true },
      { name: 'streetAddress', label: 'Street Address', type: 'text', required: true },
      { name: 'city', label: 'City', type: 'text', required: true },
      { name: 'state', label: 'State', type: 'select', required: true, 
        options: [
          { value: 'AB', label: 'Abia' },
          { value: 'AD', label: 'Adamawa' },
          { value: 'AK', label: 'Akwa Ibom' },
          { value: 'AN', label: 'Anambra' },
          { value: 'BA', label: 'Bauchi' },
          { value: 'BY', label: 'Bayelsa' },
          { value: 'BE', label: 'Benue' },
          { value: 'BO', label: 'Borno' },
          { value: 'CR', label: 'Cross River' },
          { value: 'DE', label: 'Delta' },
          { value: 'EB', label: 'Ebonyi' },
          { value: 'ED', label: 'Edo' },
          { value: 'EK', label: 'Ekiti' },
          { value: 'EN', label: 'Enugu' },
          { value: 'FC', label: 'Federal Capital Territory' },
          { value: 'GO', label: 'Gombe' },
          { value: 'IM', label: 'Imo' },
          { value: 'JI', label: 'Jigawa' },
          { value: 'KD', label: 'Kaduna' },
          { value: 'KN', label: 'Kano' },
          { value: 'KT', label: 'Katsina' },
          { value: 'KB', label: 'Kebbi' },
          { value: 'KG', label: 'Kogi' },
          { value: 'KW', label: 'Kwara' },
          { value: 'LA', label: 'Lagos' },
          { value: 'NA', label: 'Nasarawa' },
          { value: 'NI', label: 'Niger' },
          { value: 'OG', label: 'Ogun' },
          { value: 'ON', label: 'Ondo' },
          { value: 'OS', label: 'Osun' },
          { value: 'OY', label: 'Oyo' },
          { value: 'PL', label: 'Plateau' },
          { value: 'RI', label: 'Rivers' },
          { value: 'SO', label: 'Sokoto' },
          { value: 'TA', label: 'Taraba' },
          { value: 'YO', label: 'Yobe' },
          { value: 'ZA', label: 'Zamfara' }
        ]
      },
      { name: 'postalCode', label: 'Postal Code', type: 'text', required: true },
      { name: 'phoneNumber', label: 'Telephone Number', type: 'text', required: true },
      { name: 'bvn', label: 'Bank Verification Number (BVN)', type: 'text', required: true },
      { name: 'photo', label: 'Passport-size Photograph', type: 'file', required: true },
    ],
    description: 'Under the CBN\'s tiered KYC framework, Tier 1 ("KYC Lite")'
  },
  MX: {
    name: 'Mexico',
    fields: [
      { name: 'fullName', label: 'Full Legal Name', type: 'text', required: true },
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
      { name: 'rfc', label: 'Taxpayer Registration Code (RFC)', type: 'text', required: true },
      { name: 'phoneNumber', label: 'Telephone Number', type: 'text', required: true },
      { name: 'email', label: 'Email Address', type: 'email', required: true },
    ],
    description: 'According to CNBV and AML law (LFPIORPI)'
  },
  EU: {
    name: 'European Union',
    fields: [
      { name: 'fullName', label: 'Full Legal Name', type: 'text', required: true },
      { name: 'placeOfBirth', label: 'Place of Birth', type: 'text', required: true },
      { name: 'dateOfBirth', label: 'Date of Birth', type: 'date', required: true },
      { name: 'streetAddress', label: 'Street Address', type: 'text', required: true },
      { name: 'city', label: 'City', type: 'text', required: true },
      { name: 'region', label: 'Region/Province', type: 'text', required: true },
      { name: 'postalCode', label: 'Postal Code', type: 'text', required: true },
      { name: 'countryOfResidence', label: 'Country of Residence', type: 'select', required: true,
        options: [
          { value: 'AT', label: 'Austria' },
          { value: 'BE', label: 'Belgium' },
          { value: 'BG', label: 'Bulgaria' },
          { value: 'HR', label: 'Croatia' },
          { value: 'CY', label: 'Cyprus' },
          { value: 'CZ', label: 'Czech Republic' },
          { value: 'DK', label: 'Denmark' },
          { value: 'EE', label: 'Estonia' },
          { value: 'FI', label: 'Finland' },
          { value: 'FR', label: 'France' },
          { value: 'DE', label: 'Germany' },
          { value: 'GR', label: 'Greece' },
          { value: 'HU', label: 'Hungary' },
          { value: 'IE', label: 'Ireland' },
          { value: 'IT', label: 'Italy' },
          { value: 'LV', label: 'Latvia' },
          { value: 'LT', label: 'Lithuania' },
          { value: 'LU', label: 'Luxembourg' },
          { value: 'MT', label: 'Malta' },
          { value: 'NL', label: 'Netherlands' },
          { value: 'PL', label: 'Poland' },
          { value: 'PT', label: 'Portugal' },
          { value: 'RO', label: 'Romania' },
          { value: 'SK', label: 'Slovakia' },
          { value: 'SI', label: 'Slovenia' },
          { value: 'ES', label: 'Spain' },
          { value: 'SE', label: 'Sweden' }
        ]
      },
      { name: 'nationality', label: 'Nationality', type: 'text', required: true },
      { name: 'idNumber', label: 'Identity Document Number', type: 'text', required: true },
      { name: 'personalIdNumber', label: 'Personal Identification Number (if applicable)', type: 'text', required: false },
    ],
    description: 'Under EU AML/CFT rules (Directive (EU) 2015/849 and delegations)'
  }
};

// Countries for dropdown selection
const countries = [
  { code: 'US', name: 'United States' },
  { code: 'CA', name: 'Canada' },
  { code: 'NG', name: 'Nigeria' },
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
          initialData.fullName = user.name || '';
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
      const fieldsToCheck = ['idState', 'idExpiryDate'];
      const updatedErrors = { ...errors };
      
      fieldsToCheck.forEach(field => {
        if (updatedErrors[field]) {
          delete updatedErrors[field];
        }
      });
      
      setErrors(updatedErrors);
    }
  }, [selectedCountry, formData.idType]);
  
  // Register user in our backend as soon as Auth0 is ready
  useEffect(() => {
    const registerUser = async () => {
      try {
        // Set longer timeout for the registration request
        const token = await getAccessTokenSilently();
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        console.log('Registering user with Auth0 token...');
        
        // Create a payload with user information from Auth0
        const userData = {
          email: user.email,
          name: user.name,
          given_name: user.given_name || user.name.split(' ')[0],
          family_name: user.family_name || user.name.split(' ').slice(1).join(' '),
          auth0_id: user.sub,
          picture: user.picture,
          // Include empty strings for required fields
          taxId: "",
          nationality: "",
          dateOfBirth: "",
          country: ""
        };
        
        // Add timeout option for registration API call
        const { data } = await authAPI.register(userData, { 
          timeout: 15000 // 15 second timeout
        });
        
        console.log('User registered successfully:', data);
        setDbUserId(data.id);
      } catch (err) {
        console.error('Error registering user:', err);
        
        // If registration fails, still allow user to proceed with KYC
        // We'll create their account when they submit KYC data
        if (err.code === 'ERR_BAD_RESPONSE' || err.code === 'ERR_NETWORK') {
          console.log('Using fallback registration flow - will register on KYC submit');
        }
      }
    };
    
    // Only try to register if the user is authenticated with Auth0
    if (isAuthenticated && user) {
      registerUser();
    }
  }, [isAuthenticated, getAccessTokenSilently, user]);
  
  // Handle country selection change
  const handleCountryChange = (e) => {
    setSelectedCountry(e.target.value);
    setActiveStep(1);
  };
  
  // Handle form field changes
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
      if (formData.idType === 'ssn' && formData.idNumber) {
        const ssnRegex = /^\d{3}-\d{2}-\d{4}$/;
        if (!ssnRegex.test(formData.idNumber)) {
          newErrors.idNumber = 'Enter a valid SSN (XXX-XX-XXXX)';
        }
      } else if ((formData.idType === 'drivers_license' || formData.idType === 'state_id') && !formData.idState) {
        newErrors.idState = 'Issuing state is required for this ID type';
      } else if ((formData.idType === 'drivers_license' || formData.idType === 'state_id' || formData.idType === 'passport') && !formData.idExpiryDate) {
        newErrors.idExpiryDate = 'Expiry date is required for this ID type';
      }
    }
    
    // Nigeria-specific validations for passport photo
    if (selectedCountry === 'NG' && !formData.photo) {
      newErrors.photo = 'Passport-size photograph is required for Nigeria KYC';
    }
    
    if (formData.phoneNumber) {
    const phoneRegex = /^\+?[0-9]{10,15}$/;
      if (!phoneRegex.test(formData.phoneNumber.replace(/\s+/g, ''))) {
      newErrors.phoneNumber = 'Enter a valid phone number';
      }
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
      if (formData.fullName) {
        const nameParts = formData.fullName.trim().split(' ');
        const firstName = nameParts[0];
        const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : '';
        submitData.append('first_name', firstName);
        submitData.append('last_name', lastName);
      }
      
      // Add country information
      submitData.append('country', countryKycRequirements[selectedCountry].name);
      submitData.append('country_code', selectedCountry);
      
      // Append all form fields, converting camelCase keys to snake_case
      Object.entries(formData).forEach(([key, value]) => {
        // React form uses camelCase, FastAPI expects snake_case
        const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
        submitData.append(snakeKey, value);
      });
      
      // Add testing flag
      submitData.append('skip_verification', 'true');
      
      console.log('Submitting KYC data to backend...');
      
      // Submit KYC data to backend
      const response = await api.post(
        '/user/kyc/submit',
        submitData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      console.log('KYC submission response:', response.data);
      setSubmitSuccess(true);
      
      // For testing: Instead of waiting for verification, redirect to dashboard immediately
      setTimeout(() => navigate('/dashboard'), 1000);
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
            To comply with financial regulations and ensure your security, we need to verify your identity before you can use Liquicity.
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
                  
                  {selectedCountry === 'NG' && (
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mt: 1 }}>
                      <strong>Note for Nigeria:</strong> CBN regulations require a passport-size photograph for KYC verification.
                      Your photo will be processed securely and in accordance with data protection laws.
                    </Typography>
                  )}
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                  <Button 
                    variant="outlined"
                    onClick={() => setActiveStep(0)}
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