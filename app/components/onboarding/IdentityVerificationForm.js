"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const button_1 = require("@/components/ui/button");
const input_1 = require("@/components/ui/input");
const label_1 = require("@/components/ui/label");
const select_1 = require("@/components/ui/select");
const date_picker_1 = require("@/components/ui/date-picker");
const card_1 = require("@/components/ui/card");
const upload_button_1 = require("@/components/ui/upload-button");
const IdentityVerificationForm = ({ onSubmit, onBack }) => {
    const [formData, setFormData] = (0, react_1.useState)({
        firstName: "",
        lastName: "",
        dateOfBirth: null,
        nationality: "",
        idType: "passport",
        idNumber: "",
        frontIdImage: null,
        backIdImage: null,
        selfieImage: null,
    });
    const [errors, setErrors] = (0, react_1.useState)({});
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => (Object.assign(Object.assign({}, prev), { [name]: value })));
        // Clear the error for this field when user starts typing
        if (errors[name]) {
            setErrors((prev) => {
                const newErrors = Object.assign({}, prev);
                delete newErrors[name];
                return newErrors;
            });
        }
    };
    const handleSelectChange = (name, value) => {
        setFormData((prev) => (Object.assign(Object.assign({}, prev), { [name]: value })));
        // Clear the error for this field
        if (errors[name]) {
            setErrors((prev) => {
                const newErrors = Object.assign({}, prev);
                delete newErrors[name];
                return newErrors;
            });
        }
    };
    const handleDateChange = (date) => {
        setFormData((prev) => (Object.assign(Object.assign({}, prev), { dateOfBirth: date })));
        // Clear the error for dateOfBirth
        if (errors.dateOfBirth) {
            setErrors((prev) => {
                const newErrors = Object.assign({}, prev);
                delete newErrors.dateOfBirth;
                return newErrors;
            });
        }
    };
    const handleFileUpload = (name, file) => {
        setFormData((prev) => (Object.assign(Object.assign({}, prev), { [name]: file })));
        // Clear the error for this field
        if (errors[name]) {
            setErrors((prev) => {
                const newErrors = Object.assign({}, prev);
                delete newErrors[name];
                return newErrors;
            });
        }
    };
    const validateForm = () => {
        const newErrors = {};
        if (!formData.firstName.trim()) {
            newErrors.firstName = "First name is required";
        }
        if (!formData.lastName.trim()) {
            newErrors.lastName = "Last name is required";
        }
        if (!formData.dateOfBirth) {
            newErrors.dateOfBirth = "Date of birth is required";
        }
        else {
            // Check if user is at least 18 years old
            const eighteenYearsAgo = new Date();
            eighteenYearsAgo.setFullYear(eighteenYearsAgo.getFullYear() - 18);
            if (formData.dateOfBirth > eighteenYearsAgo) {
                newErrors.dateOfBirth = "You must be at least 18 years old";
            }
        }
        if (!formData.nationality) {
            newErrors.nationality = "Nationality is required";
        }
        if (!formData.idNumber.trim()) {
            newErrors.idNumber = "ID number is required";
        }
        if (!formData.frontIdImage) {
            newErrors.frontIdImage = "Front side of ID is required";
        }
        if (formData.idType !== "passport" && !formData.backIdImage) {
            newErrors.backIdImage = "Back side of ID is required";
        }
        if (!formData.selfieImage) {
            newErrors.selfieImage = "Selfie is required";
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
    return (<card_1.Card className="w-full max-w-3xl mx-auto">
      <card_1.CardHeader>
        <card_1.CardTitle>Verify Your Identity</card_1.CardTitle>
        <card_1.CardDescription>
          We need to verify your identity to comply with financial regulations.
          All information is encrypted and stored securely.
        </card_1.CardDescription>
      </card_1.CardHeader>
      <card_1.CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label_1.Label htmlFor="firstName">First Name</label_1.Label>
              <input_1.Input id="firstName" name="firstName" value={formData.firstName} onChange={handleChange} className={errors.firstName ? "border-red-500" : ""}/>
              {errors.firstName && (<p className="text-red-500 text-sm mt-1">{errors.firstName}</p>)}
            </div>
            
            <div className="space-y-2">
              <label_1.Label htmlFor="lastName">Last Name</label_1.Label>
              <input_1.Input id="lastName" name="lastName" value={formData.lastName} onChange={handleChange} className={errors.lastName ? "border-red-500" : ""}/>
              {errors.lastName && (<p className="text-red-500 text-sm mt-1">{errors.lastName}</p>)}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label_1.Label htmlFor="dateOfBirth">Date of Birth</label_1.Label>
              <date_picker_1.DatePicker id="dateOfBirth" selected={formData.dateOfBirth} onSelect={handleDateChange} className={errors.dateOfBirth ? "border-red-500" : ""}/>
              {errors.dateOfBirth && (<p className="text-red-500 text-sm mt-1">{errors.dateOfBirth}</p>)}
            </div>
            
            <div className="space-y-2">
              <label_1.Label htmlFor="nationality">Nationality</label_1.Label>
              <select_1.Select value={formData.nationality} onValueChange={(value) => handleSelectChange("nationality", value)}>
                <select_1.SelectTrigger id="nationality" className={errors.nationality ? "border-red-500" : ""}>
                  <select_1.SelectValue placeholder="Select nationality"/>
                </select_1.SelectTrigger>
                <select_1.SelectContent>
                  <select_1.SelectItem value="us">United States</select_1.SelectItem>
                  <select_1.SelectItem value="ca">Canada</select_1.SelectItem>
                  <select_1.SelectItem value="uk">United Kingdom</select_1.SelectItem>
                  <select_1.SelectItem value="au">Australia</select_1.SelectItem>
                  <select_1.SelectItem value="de">Germany</select_1.SelectItem>
                  <select_1.SelectItem value="fr">France</select_1.SelectItem>
                  <select_1.SelectItem value="jp">Japan</select_1.SelectItem>
                  <select_1.SelectItem value="sg">Singapore</select_1.SelectItem>
                  <select_1.SelectItem value="other">Other</select_1.SelectItem>
                </select_1.SelectContent>
              </select_1.Select>
              {errors.nationality && (<p className="text-red-500 text-sm mt-1">{errors.nationality}</p>)}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label_1.Label htmlFor="idType">ID Type</label_1.Label>
              <select_1.Select value={formData.idType} onValueChange={(value) => handleSelectChange("idType", value)}>
                <select_1.SelectTrigger id="idType">
                  <select_1.SelectValue placeholder="Select ID type"/>
                </select_1.SelectTrigger>
                <select_1.SelectContent>
                  <select_1.SelectItem value="passport">Passport</select_1.SelectItem>
                  <select_1.SelectItem value="drivers_license">Driver's License</select_1.SelectItem>
                  <select_1.SelectItem value="national_id">National ID Card</select_1.SelectItem>
                </select_1.SelectContent>
              </select_1.Select>
            </div>
            
            <div className="space-y-2">
              <label_1.Label htmlFor="idNumber">ID Number</label_1.Label>
              <input_1.Input id="idNumber" name="idNumber" value={formData.idNumber} onChange={handleChange} className={errors.idNumber ? "border-red-500" : ""}/>
              {errors.idNumber && (<p className="text-red-500 text-sm mt-1">{errors.idNumber}</p>)}
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium">Upload ID Documents</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label_1.Label htmlFor="frontIdImage">Front Side of ID</label_1.Label>
                <upload_button_1.UploadButton accept="image/*" onChange={(file) => handleFileUpload("frontIdImage", file)} className={errors.frontIdImage ? "border-red-500" : ""}/>
                {formData.frontIdImage && (<p className="text-sm text-green-600">
                    Uploaded: {formData.frontIdImage.name}
                  </p>)}
                {errors.frontIdImage && (<p className="text-red-500 text-sm mt-1">{errors.frontIdImage}</p>)}
              </div>
              
              {formData.idType !== "passport" && (<div className="space-y-2">
                  <label_1.Label htmlFor="backIdImage">Back Side of ID</label_1.Label>
                  <upload_button_1.UploadButton accept="image/*" onChange={(file) => handleFileUpload("backIdImage", file)} className={errors.backIdImage ? "border-red-500" : ""}/>
                  {formData.backIdImage && (<p className="text-sm text-green-600">
                      Uploaded: {formData.backIdImage.name}
                    </p>)}
                  {errors.backIdImage && (<p className="text-red-500 text-sm mt-1">{errors.backIdImage}</p>)}
                </div>)}
            </div>

            <div className="space-y-2">
              <label_1.Label htmlFor="selfieImage">Selfie With ID</label_1.Label>
              <upload_button_1.UploadButton accept="image/*" onChange={(file) => handleFileUpload("selfieImage", file)} className={errors.selfieImage ? "border-red-500" : ""}/>
              {formData.selfieImage && (<p className="text-sm text-green-600">
                  Uploaded: {formData.selfieImage.name}
                </p>)}
              {errors.selfieImage && (<p className="text-red-500 text-sm mt-1">{errors.selfieImage}</p>)}
            </div>
          </div>

          <div className="flex justify-between pt-4">
            <button_1.Button type="button" variant="outline" onClick={onBack}>
              Back
            </button_1.Button>
            <button_1.Button type="submit">Continue</button_1.Button>
          </div>
        </form>
      </card_1.CardContent>
    </card_1.Card>);
};
exports.default = IdentityVerificationForm;
