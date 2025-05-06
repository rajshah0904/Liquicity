"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importStar(require("react"));
const ui_1 = require("../ui");
const PersonalInfoForm_1 = __importDefault(require("./PersonalInfoForm"));
const IdentityVerificationForm_1 = __importDefault(require("./IdentityVerificationForm"));
const AddressVerificationForm_1 = __importDefault(require("./AddressVerificationForm"));
const SuccessScreen_1 = __importDefault(require("./SuccessScreen"));
const KycFlow = ({ userId, onComplete, initialStep = 0 }) => {
    const [currentStep, setCurrentStep] = (0, react_1.useState)(initialStep);
    const [error, setError] = (0, react_1.useState)(null);
    const [kycData, setKycData] = (0, react_1.useState)({
        personalInfo: {},
        identity: {},
        address: {}
    });
    const steps = [
        { title: 'Personal Information', component: PersonalInfoForm_1.default },
        { title: 'Identity Verification', component: IdentityVerificationForm_1.default },
        { title: 'Address Verification', component: AddressVerificationForm_1.default },
        { title: 'Complete', component: SuccessScreen_1.default }
    ];
    const CurrentStepComponent = steps[currentStep].component;
    const handleNext = (stepData) => __awaiter(void 0, void 0, void 0, function* () {
        try {
            setError(null);
            // Update the KYC data with the current step's data
            const updatedKycData = Object.assign(Object.assign({}, kycData), { [Object.keys(kycData)[currentStep]]: stepData });
            setKycData(updatedKycData);
            // If this is the final data collection step, submit all data
            if (currentStep === steps.length - 2) {
                // Submit KYC data to backend
                const response = yield fetch('/api/users/kyc', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(Object.assign({ userId }, updatedKycData))
                });
                if (!response.ok) {
                    throw new Error('Failed to submit verification data');
                }
                const result = yield response.json();
                onComplete(result.status);
            }
            // Move to next step
            setCurrentStep(currentStep + 1);
        }
        catch (err) {
            setError(err.message || 'An error occurred during verification');
        }
    });
    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };
    const progressPercentage = (currentStep / (steps.length - 1)) * 100;
    return (<ui_1.Card className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Account Verification</h2>
      <ui_1.Progress value={progressPercentage} className="mb-6"/>
      
      {error && (<ui_1.Alert variant="error" className="mb-4">
          {error}
        </ui_1.Alert>)}
      
      <CurrentStepComponent onSubmit={handleNext} initialData={kycData[Object.keys(kycData)[currentStep]]}/>
      
      <div className="flex justify-between mt-6">
        {currentStep > 0 && currentStep < steps.length - 1 && (<ui_1.Button variant="outline" onClick={handleBack}>
            Back
          </ui_1.Button>)}
        {currentStep === steps.length - 1 && (<ui_1.Button variant="primary" onClick={() => window.location.href = '/dashboard'}>
            Go to Dashboard
          </ui_1.Button>)}
      </div>
    </ui_1.Card>);
};
exports.default = KycFlow;
