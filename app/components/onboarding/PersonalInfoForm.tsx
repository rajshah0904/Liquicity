import React, { useState } from 'react';
import { TextField, Button, DatePicker, Select } from '../ui';

interface PersonalInfoFormProps {
  onSubmit: (data: PersonalInfo) => void;
  initialData?: Partial<PersonalInfo>;
}

export interface PersonalInfo {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  nationality: string;
  taxId: string;
}

const PersonalInfoForm: React.FC<PersonalInfoFormProps> = ({ onSubmit, initialData = {} }) => {
  const [formData, setFormData] = useState<PersonalInfo>({
    firstName: initialData.firstName || '',
    lastName: initialData.lastName || '',
    email: initialData.email || '',
    phone: initialData.phone || '',
    dateOfBirth: initialData.dateOfBirth || '',
    nationality: initialData.nationality || '',
    taxId: initialData.taxId || '',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof PersonalInfo, string>>>({});
  
  const handleChange = (key: keyof PersonalInfo, value: string) => {
    setFormData({
      ...formData,
      [key]: value
    });
    
    // Clear error when field is changed
    if (errors[key]) {
      setErrors({
        ...errors,
        [key]: undefined
      });
    }
  };
  
  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof PersonalInfo, string>> = {};
    
    if (!formData.firstName) {
      newErrors.firstName = 'First name is required';
    }
    
    if (!formData.lastName) {
      newErrors.lastName = 'Last name is required';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = 'Email format is invalid';
    }
    
    if (!formData.phone) {
      newErrors.phone = 'Phone number is required';
    }
    
    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required';
    }
    
    if (!formData.nationality) {
      newErrors.nationality = 'Nationality is required';
    }
    
    if (!formData.taxId) {
      newErrors.taxId = 'Tax ID / SSN is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <TextField
          label="First Name"
          value={formData.firstName}
          onChange={(e) => handleChange('firstName', e.target.value)}
          error={errors.firstName}
          required
        />
        
        <TextField
          label="Last Name"
          value={formData.lastName}
          onChange={(e) => handleChange('lastName', e.target.value)}
          error={errors.lastName}
          required
        />
      </div>
      
      <TextField
        label="Email"
        type="email"
        value={formData.email}
        onChange={(e) => handleChange('email', e.target.value)}
        error={errors.email}
        className="mb-4"
        required
      />
      
      <TextField
        label="Phone Number"
        type="tel"
        value={formData.phone}
        onChange={(e) => handleChange('phone', e.target.value)}
        error={errors.phone}
        className="mb-4"
        required
      />
      
      <DatePicker
        label="Date of Birth"
        value={formData.dateOfBirth}
        onChange={(date) => handleChange('dateOfBirth', date)}
        error={errors.dateOfBirth}
        className="mb-4"
        required
        maxDate={new Date()}
      />
      
      <Select
        label="Nationality"
        value={formData.nationality}
        onChange={(e) => handleChange('nationality', e.target.value)}
        error={errors.nationality}
        className="mb-4"
        required
      >
        <option value="">Select nationality</option>
        <option value="US">United States</option>
        <option value="CA">Canada</option>
        <option value="MX">Mexico</option>
        <option value="GB">United Kingdom</option>
        <option value="FR">France</option>
        <option value="DE">Germany</option>
        <option value="AU">Australia</option>
        <option value="NG">Nigeria</option>
        {/* Add more countries as needed */}
      </Select>
      
      <TextField
        label="Tax ID / SSN"
        value={formData.taxId}
        onChange={(e) => handleChange('taxId', e.target.value)}
        error={errors.taxId}
        className="mb-4"
        required
      />
      
      <Button type="submit" variant="primary" className="w-full">
        Continue
      </Button>
    </form>
  );
};

export default PersonalInfoForm; 