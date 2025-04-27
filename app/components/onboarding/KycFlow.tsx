import React, { useState } from 'react';
import { Progress, Button, Alert, Card } from '../ui';
import PersonalInfoForm from './PersonalInfoForm';
import IdentityVerificationForm from './IdentityVerificationForm';
import AddressVerificationForm from './AddressVerificationForm';
import SuccessScreen from './SuccessScreen';

export type KycStatus = 'unverified' | 'pending' | 'approved' | 'rejected';

interface KycFlowProps {
  userId: string;
  onComplete: (status: KycStatus) => void;
  initialStep?: number;
}

const KycFlow: React.FC<KycFlowProps> = ({ 
  userId, 
  onComplete,
  initialStep = 0 
}) => {
  const [currentStep, setCurrentStep] = useState(initialStep);
  const [error, setError] = useState<string | null>(null);
  const [kycData, setKycData] = useState({
    personalInfo: {},
    identity: {},
    address: {}
  });
  
  const steps = [
    { title: 'Personal Information', component: PersonalInfoForm },
    { title: 'Identity Verification', component: IdentityVerificationForm },
    { title: 'Address Verification', component: AddressVerificationForm },
    { title: 'Complete', component: SuccessScreen }
  ];
  
  const CurrentStepComponent = steps[currentStep].component;
  
  const handleNext = async (stepData: any) => {
    try {
      setError(null);
      
      // Update the KYC data with the current step's data
      const updatedKycData = {
        ...kycData,
        [Object.keys(kycData)[currentStep]]: stepData
      };
      
      setKycData(updatedKycData);
      
      // If this is the final data collection step, submit all data
      if (currentStep === steps.length - 2) {
        // Submit KYC data to backend
        const response = await fetch('/api/users/kyc', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            userId,
            ...updatedKycData
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to submit verification data');
        }
        
        const result = await response.json();
        onComplete(result.status);
      }
      
      // Move to next step
      setCurrentStep(currentStep + 1);
    } catch (err: any) {
      setError(err.message || 'An error occurred during verification');
    }
  };
  
  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };
  
  const progressPercentage = (currentStep / (steps.length - 1)) * 100;
  
  return (
    <Card className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Account Verification</h2>
      <Progress value={progressPercentage} className="mb-6" />
      
      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}
      
      <CurrentStepComponent 
        onSubmit={handleNext}
        initialData={kycData[Object.keys(kycData)[currentStep]]}
      />
      
      <div className="flex justify-between mt-6">
        {currentStep > 0 && currentStep < steps.length - 1 && (
          <Button variant="outline" onClick={handleBack}>
            Back
          </Button>
        )}
        {currentStep === steps.length - 1 && (
          <Button variant="primary" onClick={() => window.location.href = '/dashboard'}>
            Go to Dashboard
          </Button>
        )}
      </div>
    </Card>
  );
};

export default KycFlow; 