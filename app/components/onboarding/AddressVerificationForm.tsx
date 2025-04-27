import React, { useState } from 'react';
import { TextField, Button, Select, FileUpload } from '../ui';

interface AddressVerificationFormProps {
  onSubmit: (data: AddressInfo) => void;
  initialData?: Partial<AddressInfo>;
}

export interface AddressInfo {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  proofImage: string;
}

const AddressVerificationForm: React.FC<AddressVerificationFormProps> = ({ 
  onSubmit, 
  initialData = {} 
}) => {
  const [formData, setFormData] = useState<AddressInfo>({
    line1: initialData.line1 || '',
    line2: initialData.line2 || '',
    city: initialData.city || '',
    state: initialData.state || '',
    postalCode: initialData.postalCode || '',
    country: initialData.country || '',
    proofImage: initialData.proofImage || '',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof AddressInfo, string>>>({});
  
  const handleChange = (key: keyof AddressInfo, value: string) => {
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
  
  const handleFileUpload = (file: string) => {
    setFormData({
      ...formData,
      proofImage: file
    });
    
    if (errors.proofImage) {
      setErrors({
        ...errors,
        proofImage: undefined
      });
    }
  };
  
  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof AddressInfo, string>> = {};
    
    if (!formData.line1) {
      newErrors.line1 = 'Address line 1 is required';
    }
    
    if (!formData.city) {
      newErrors.city = 'City is required';
    }
    
    if (!formData.state) {
      newErrors.state = 'State/Province/Region is required';
    }
    
    if (!formData.postalCode) {
      newErrors.postalCode = 'Postal code is required';
    }
    
    if (!formData.country) {
      newErrors.country = 'Country is required';
    }
    
    if (!formData.proofImage) {
      newErrors.proofImage = 'Proof of address is required';
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
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Address Verification</h3>
        <p className="text-gray-500 text-sm mb-4">
          Please enter your current residential address and provide proof of address
        </p>
      </div>
      
      <TextField
        label="Address Line 1"
        value={formData.line1}
        onChange={(e) => handleChange('line1', e.target.value)}
        error={errors.line1}
        className="mb-4"
        required
        placeholder="Street address, P.O. box, company name"
      />
      
      <TextField
        label="Address Line 2"
        value={formData.line2}
        onChange={(e) => handleChange('line2', e.target.value)}
        error={errors.line2}
        className="mb-4"
        placeholder="Apartment, suite, unit, building, floor, etc."
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <TextField
          label="City"
          value={formData.city}
          onChange={(e) => handleChange('city', e.target.value)}
          error={errors.city}
          required
        />
        
        <TextField
          label="State/Province/Region"
          value={formData.state}
          onChange={(e) => handleChange('state', e.target.value)}
          error={errors.state}
          required
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <TextField
          label="Postal Code"
          value={formData.postalCode}
          onChange={(e) => handleChange('postalCode', e.target.value)}
          error={errors.postalCode}
          required
        />
        
        <Select
          label="Country"
          value={formData.country}
          onChange={(e) => handleChange('country', e.target.value)}
          error={errors.country}
          required
        >
          <option value="">Select country</option>
          <option value="US">United States</option>
          <option value="CA">Canada</option>
          <option value="MX">Mexico</option>
          <option value="GB">United Kingdom</option>
          <option value="FR">France</option>
          <option value="DE">Germany</option>
          <option value="AU">Australia</option>
          <option value="NG">Nigeria</option>
        </Select>
      </div>
      
      <FileUpload
        label="Upload Proof of Address"
        accept="image/*,.pdf"
        onUpload={handleFileUpload}
        error={errors.proofImage}
        className="mb-6"
        required
        helpText="Please upload a utility bill, bank statement, or government letter dated within the last 3 months"
      />
      
      <Button type="submit" variant="primary" className="w-full">
        Continue
      </Button>
    </form>
  );
};

export default AddressVerificationForm; 