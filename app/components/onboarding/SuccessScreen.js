"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importDefault(require("react"));
const lucide_react_1 = require("lucide-react");
const SuccessScreen = ({ onSubmit, status = 'pending' }) => {
    const getStatusContent = () => {
        switch (status) {
            case 'approved':
                return {
                    icon: <lucide_react_1.Check size={48} className="text-green-500 mx-auto mb-4"/>,
                    title: 'Verification Complete',
                    message: 'Your identity has been successfully verified. You now have full access to all features.'
                };
            case 'rejected':
                return {
                    icon: <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-red-500 text-2xl font-bold">!</span>
          </div>,
                    title: 'Verification Declined',
                    message: 'Unfortunately, we could not verify your identity with the provided information. Please contact our support team for assistance.'
                };
            case 'pending':
            default:
                return {
                    icon: <lucide_react_1.Clock size={48} className="text-blue-500 mx-auto mb-4"/>,
                    title: 'Verification in Progress',
                    message: 'Your information has been submitted and is currently being reviewed. This usually takes 1-2 business days.'
                };
        }
    };
    const content = getStatusContent();
    return (<div className="text-center py-8">
      {content.icon}
      
      <h3 className="text-xl font-bold mb-2">{content.title}</h3>
      
      <p className="text-gray-600 mb-8">
        {content.message}
      </p>
      
      {status === 'pending' && (<div className="bg-blue-50 rounded-lg p-4 mb-6 text-sm text-blue-700">
          <p className="font-medium mb-1">What happens next?</p>
          <ul className="list-disc list-inside">
            <li className="mb-1">We'll review your documents and information</li>
            <li className="mb-1">You'll receive an email with the verification result</li>
            <li>You can check your verification status in your account settings</li>
          </ul>
        </div>)}
      
      {status === 'rejected' && (<div className="bg-red-50 rounded-lg p-4 mb-6 text-sm text-red-700">
          <p className="font-medium mb-1">Common reasons for rejection:</p>
          <ul className="list-disc list-inside">
            <li className="mb-1">Document was unclear or partially visible</li>
            <li className="mb-1">Information mismatch between documents</li>
            <li className="mb-1">Expired identification document</li>
            <li>Document appears to be altered or fraudulent</li>
          </ul>
        </div>)}
      
      <div className="mt-6">
        <button onClick={onSubmit} className="bg-primary text-white px-6 py-2 rounded-md font-medium hover:bg-primary-dark transition-colors">
          {status === 'approved' ? 'Continue to Dashboard' :
            status === 'rejected' ? 'Contact Support' :
                'Continue to Dashboard'}
        </button>
      </div>
    </div>);
};
exports.default = SuccessScreen;
