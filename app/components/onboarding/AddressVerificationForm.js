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
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importStar(require("react"));
const ui_1 = require("../ui");
const AddressVerificationForm = ({ onSubmit, initialData = {} }) => {
    const [formData, setFormData] = (0, react_1.useState)({
        line1: initialData.line1 || '',
        line2: initialData.line2 || '',
        city: initialData.city || '',
        state: initialData.state || '',
        postalCode: initialData.postalCode || '',
        country: initialData.country || '',
        proofImage: initialData.proofImage || '',
    });
    const [errors, setErrors] = (0, react_1.useState)({});
    const handleChange = (key, value) => {
        setFormData(Object.assign(Object.assign({}, formData), { [key]: value }));
        // Clear error when field is changed
        if (errors[key]) {
            setErrors(Object.assign(Object.assign({}, errors), { [key]: undefined }));
        }
    };
    const handleFileUpload = (file) => {
        setFormData(Object.assign(Object.assign({}, formData), { proofImage: file }));
        if (errors.proofImage) {
            setErrors(Object.assign(Object.assign({}, errors), { proofImage: undefined }));
        }
    };
    const validateForm = () => {
        const newErrors = {};
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
    const handleSubmit = (e) => {
        e.preventDefault();
        if (validateForm()) {
            onSubmit(formData);
        }
    };
    return (<form onSubmit={handleSubmit}>
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Address Verification</h3>
        <p className="text-gray-500 text-sm mb-4">
          Please enter your current residential address and provide proof of address
        </p>
      </div>
      
      <ui_1.TextField label="Address Line 1" value={formData.line1} onChange={(e) => handleChange('line1', e.target.value)} error={errors.line1} className="mb-4" required placeholder="Street address, P.O. box, company name"/>
      
      <ui_1.TextField label="Address Line 2" value={formData.line2} onChange={(e) => handleChange('line2', e.target.value)} error={errors.line2} className="mb-4" placeholder="Apartment, suite, unit, building, floor, etc."/>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ui_1.TextField label="City" value={formData.city} onChange={(e) => handleChange('city', e.target.value)} error={errors.city} required/>
        
        <ui_1.TextField label="State/Province/Region" value={formData.state} onChange={(e) => handleChange('state', e.target.value)} error={errors.state} required/>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ui_1.TextField label="Postal Code" value={formData.postalCode} onChange={(e) => handleChange('postalCode', e.target.value)} error={errors.postalCode} required/>
        
        <ui_1.Select label="Country" value={formData.country} onChange={(e) => handleChange('country', e.target.value)} error={errors.country} required>
          <option value="">Select country</option>
          <option value="US">United States</option>
          <option value="CA">Canada</option>
          <option value="MX">Mexico</option>
          <option value="GB">United Kingdom</option>
          <option value="FR">France</option>
          <option value="DE">Germany</option>
          <option value="AU">Australia</option>
          <option value="NG">Nigeria</option>
        </ui_1.Select>
      </div>
      
      <ui_1.FileUpload label="Upload Proof of Address" accept="image/*,.pdf" onUpload={handleFileUpload} error={errors.proofImage} className="mb-6" required helpText="Please upload a utility bill, bank statement, or government letter dated within the last 3 months"/>
      
      <ui_1.Button type="submit" variant="primary" className="w-full">
        Continue
      </ui_1.Button>
    </form>);
};
exports.default = AddressVerificationForm;
