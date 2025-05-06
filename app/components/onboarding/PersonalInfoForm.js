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
const PersonalInfoForm = ({ onSubmit, initialData = {} }) => {
    const [formData, setFormData] = (0, react_1.useState)({
        firstName: initialData.firstName || '',
        lastName: initialData.lastName || '',
        email: initialData.email || '',
        phone: initialData.phone || '',
        dateOfBirth: initialData.dateOfBirth || '',
        nationality: initialData.nationality || '',
        taxId: initialData.taxId || '',
    });
    const [errors, setErrors] = (0, react_1.useState)({});
    const handleChange = (key, value) => {
        setFormData(Object.assign(Object.assign({}, formData), { [key]: value }));
        // Clear error when field is changed
        if (errors[key]) {
            setErrors(Object.assign(Object.assign({}, errors), { [key]: undefined }));
        }
    };
    const validateForm = () => {
        const newErrors = {};
        if (!formData.firstName) {
            newErrors.firstName = 'First name is required';
        }
        if (!formData.lastName) {
            newErrors.lastName = 'Last name is required';
        }
        if (!formData.email) {
            newErrors.email = 'Email is required';
        }
        else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
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
    const handleSubmit = (e) => {
        e.preventDefault();
        if (validateForm()) {
            onSubmit(formData);
        }
    };
    return (<form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ui_1.TextField label="First Name" value={formData.firstName} onChange={(e) => handleChange('firstName', e.target.value)} error={errors.firstName} required/>
        
        <ui_1.TextField label="Last Name" value={formData.lastName} onChange={(e) => handleChange('lastName', e.target.value)} error={errors.lastName} required/>
      </div>
      
      <ui_1.TextField label="Email" type="email" value={formData.email} onChange={(e) => handleChange('email', e.target.value)} error={errors.email} className="mb-4" required/>
      
      <ui_1.TextField label="Phone Number" type="tel" value={formData.phone} onChange={(e) => handleChange('phone', e.target.value)} error={errors.phone} className="mb-4" required/>
      
      <ui_1.DatePicker label="Date of Birth" value={formData.dateOfBirth} onChange={(date) => handleChange('dateOfBirth', date)} error={errors.dateOfBirth} className="mb-4" required maxDate={new Date()}/>
      
      <ui_1.Select label="Nationality" value={formData.nationality} onChange={(e) => handleChange('nationality', e.target.value)} error={errors.nationality} className="mb-4" required>
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
      </ui_1.Select>
      
      <ui_1.TextField label="Tax ID / SSN" value={formData.taxId} onChange={(e) => handleChange('taxId', e.target.value)} error={errors.taxId} className="mb-4" required/>
      
      <ui_1.Button type="submit" variant="primary" className="w-full">
        Continue
      </ui_1.Button>
    </form>);
};
exports.default = PersonalInfoForm;
