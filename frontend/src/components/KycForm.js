import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import axios from 'axios';

const KycForm = () => {
  const { getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    country: '',
    country_code: '',
    id_type: 'passport',
    id_number: '',
    document_type: 'passport'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Get the Auth0 token
      const token = await getAccessTokenSilently();

      // Submit to existing KYC endpoint
      const response = await axios.post(
        `/kyc/submit`, 
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.status === 200 || response.status === 201) {
        // Successful KYC submission
        navigate('/dashboard');
      } else {
        alert('KYC submission failed. Please try again.');
      }
    } catch (error) {
      console.error('KYC submission error:', error);
      alert('Error submitting KYC information. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="kyc-form-container">
      <h2>Complete Your Identity Verification</h2>
      <p>Please provide your personal information to verify your identity</p>
      
      <form onSubmit={handleSubmit} className="kyc-form">
        <div className="form-group">
          <label htmlFor="first_name">First Name</label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="last_name">Last Name</label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="date_of_birth">Date of Birth</label>
          <input
            type="date"
            id="date_of_birth"
            name="date_of_birth"
            value={formData.date_of_birth}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="country">Country</label>
          <input
            type="text"
            id="country"
            name="country"
            value={formData.country}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="country_code">Country Code</label>
          <input
            type="text"
            id="country_code"
            name="country_code"
            value={formData.country_code}
            onChange={handleChange}
            required
            placeholder="e.g. US, GB, JP"
          />
        </div>

        <div className="form-group">
          <label htmlFor="id_type">ID Type</label>
          <select
            id="id_type"
            name="id_type"
            value={formData.id_type}
            onChange={handleChange}
            required
          >
            <option value="passport">Passport</option>
            <option value="drivers_license">Driver's License</option>
            <option value="national_id">National ID</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="id_number">ID Number</label>
          <input
            type="text"
            id="id_number"
            name="id_number"
            value={formData.id_number}
            onChange={handleChange}
            required
          />
        </div>

        <button 
          type="submit" 
          className="kyc-submit-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Submit KYC Information'}
        </button>
      </form>
    </div>
  );
};

export default KycForm; 