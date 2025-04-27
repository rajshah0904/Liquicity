import * as React from "react";
import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Select } from "../ui/select";
import { DatePicker } from "../ui/date-picker";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { UploadButton } from "../ui/upload-button";

interface KYCLiteFormProps {
  onSubmit: (data: KYCData) => void;
  onBack?: () => void;
}

// Define all possible fields across different jurisdictions
interface KYCData {
  // Core identity fields (universal)
  fullName: string;
  dateOfBirth: Date | null;
  phoneNumber: string;
  email: string;
  
  // Residential address
  residentialAddress: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  
  // Government ID information
  idType: "ssn" | "passport" | "driversLicense" | "nationalId" | "bvn" | "ine";
  idNumber: string;
  idExpiryDate: Date | null;
  
  // Document uploads
  photoIdFront: File | null;
  photoIdBack: File | null;
  selfie: File | null;
  proofOfAddress: File | null;
  
  // Nigeria-specific (BVN)
  bvnNumber?: string;
  
  // Admin review fields
  ofacScreened: boolean;
  pepScreened: boolean;
  reviewerNotes: string;
  reviewDate: Date | null;
  reviewerName: string;
  approvalStatus: "pending" | "approved" | "rejected";
}

// Configuration for different countries and their KYC requirements
const countryConfig: Record<string, {
  name: string,
  currencySymbol: string,
  txCap: string,
  monthlyCap: string,
  requiredFields: string[],
  optionalFields: string[],
  idTypes: {value: string, label: string}[],
  notes: string
}> = {
  "US": {
    name: "United States",
    currencySymbol: "$",
    txCap: "1,000 USD",
    monthlyCap: "5,000 USD",
    requiredFields: ["fullName", "dateOfBirth", "residentialAddress", "idType", "idNumber", "photoIdFront", "selfie"],
    optionalFields: ["proofOfAddress", "phoneNumber", "email"],
    idTypes: [
      {value: "ssn", label: "Social Security Number"},
      {value: "passport", label: "Passport"},
      {value: "driversLicense", label: "Driver's License"}
    ],
    notes: "OFAC screening required. Records kept 5 years. CTR for $10K+ transactions."
  },
  "CA": {
    name: "Canada",
    currencySymbol: "CA$",
    txCap: "1,000 CAD",
    monthlyCap: "5,000 CAD",
    requiredFields: ["fullName", "dateOfBirth", "residentialAddress", "idType", "idNumber", "photoIdFront"],
    optionalFields: ["selfie", "proofOfAddress", "phoneNumber", "email"],
    idTypes: [
      {value: "passport", label: "Passport"},
      {value: "driversLicense", label: "Driver's License"},
      {value: "nationalId", label: "National ID"}
    ],
    notes: "FINTRAC reporting at CAD 10,000+. PEP screening recommended."
  },
  "MX": {
    name: "Mexico",
    currencySymbol: "MXN$",
    txCap: "10,000 MXN",
    monthlyCap: "30,000 MXN",
    requiredFields: ["fullName", "dateOfBirth", "residentialAddress", "idType", "idNumber", "photoIdFront", "proofOfAddress"],
    optionalFields: ["selfie", "phoneNumber", "email"],
    idTypes: [
      {value: "passport", label: "Passport"},
      {value: "ine", label: "INE Voter ID"},
      {value: "nationalId", label: "National ID"}
    ],
    notes: "Report transactions ≥ MXN 1,000,000. UIF sanctions screening required."
  },
  "NG": {
    name: "Nigeria",
    currencySymbol: "₦",
    txCap: "10,000 NGN",
    monthlyCap: "50,000 NGN",
    requiredFields: ["fullName", "phoneNumber"],
    optionalFields: ["email", "residentialAddress", "proofOfAddress", "bvnNumber", "photoIdFront", "selfie"],
    idTypes: [
      {value: "bvn", label: "Bank Verification Number (BVN)"},
      {value: "nationalId", label: "National ID"},
      {value: "passport", label: "Passport"}
    ],
    notes: "Tier 1 KYC (₦50K/mo cap). Tier 2 adds address/utility bill (₦300K/mo)."
  },
  "EG": {
    name: "Egypt",
    currencySymbol: "E£",
    txCap: "10,000 EGP",
    monthlyCap: "50,000 EGP",
    requiredFields: ["fullName", "dateOfBirth", "residentialAddress", "idType", "idNumber", "photoIdFront"],
    optionalFields: ["selfie", "proofOfAddress", "phoneNumber", "email"],
    idTypes: [
      {value: "nationalId", label: "National ID"},
      {value: "passport", label: "Passport"}
    ],
    notes: "Report transactions ≥ EGP 100,000. Records kept 5 years."
  },
  "EU": {
    name: "European Union",
    currencySymbol: "€",
    txCap: "1,000 EUR",
    monthlyCap: "5,000 EUR",
    requiredFields: ["fullName", "dateOfBirth", "residentialAddress", "idType", "idNumber", "photoIdFront"],
    optionalFields: ["selfie", "proofOfAddress", "phoneNumber", "email"],
    idTypes: [
      {value: "nationalId", label: "National ID"},
      {value: "passport", label: "Passport"},
      {value: "driversLicense", label: "Driver's License"}
    ],
    notes: "EU AML Directives apply. €10K reporting threshold. GDPR compliance."
  }
};

export function KYCLiteForm({ onSubmit, onBack }: KYCLiteFormProps) {
  const [selectedCountry, setSelectedCountry] = useState<string>("US");
  const [formData, setFormData] = useState<KYCData>({
    fullName: "",
    dateOfBirth: null,
    phoneNumber: "",
    email: "",
    residentialAddress: {
      street: "",
      city: "",
      state: "",
      zipCode: "",
      country: "US",
    },
    idType: "ssn",
    idNumber: "",
    idExpiryDate: null,
    photoIdFront: null,
    photoIdBack: null,
    selfie: null,
    proofOfAddress: null,
    bvnNumber: "",
    ofacScreened: false,
    pepScreened: false,
    reviewerNotes: "",
    reviewDate: null,
    reviewerName: "",
    approvalStatus: "pending"
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Handle country change - updates the required fields and ID types
  const handleCountryChange = (country: string) => {
    setSelectedCountry(country);
    setFormData(prev => ({
      ...prev,
      residentialAddress: {
        ...prev.residentialAddress,
        country: country
      },
      // Set default ID type based on country
      idType: countryConfig[country].idTypes[0].value as any
    }));
  };

  const handleChange = (
    field: string, 
    value: string | Date | null | File | boolean
  ) => {
    setFormData((prev) => {
      if (field.includes(".")) {
        const [parent, child] = field.split(".");
        return {
          ...prev,
          [parent]: {
            ...prev[parent as keyof typeof prev] as Record<string, any>,
            [child]: value,
          },
        };
      }
      return {
        ...prev,
        [field]: value,
      };
    });

    // Clear error
    if (field in errors) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    const config = countryConfig[selectedCountry];
    
    // Validate required fields for the selected country
    config.requiredFields.forEach(field => {
      if (field === "residentialAddress") {
        // Check address fields
        if (!formData.residentialAddress.street.trim()) {
          newErrors["residentialAddress.street"] = "Street address is required";
        }
        if (!formData.residentialAddress.city.trim()) {
          newErrors["residentialAddress.city"] = "City is required";
        }
        if (!formData.residentialAddress.state.trim()) {
          newErrors["residentialAddress.state"] = "State/province is required";
        }
        if (!formData.residentialAddress.zipCode.trim()) {
          newErrors["residentialAddress.zipCode"] = "Postal/ZIP code is required";
        }
      } else if (field === "fullName" && !formData.fullName.trim()) {
        newErrors.fullName = "Full legal name is required";
      } else if (field === "dateOfBirth" && !formData.dateOfBirth) {
        newErrors.dateOfBirth = "Date of birth is required";
      } else if (field === "phoneNumber" && !formData.phoneNumber.trim()) {
        newErrors.phoneNumber = "Phone number is required";
      } else if (field === "email" && !formData.email.trim()) {
        newErrors.email = "Email address is required";
      } else if (field === "idNumber" && !formData.idNumber.trim()) {
        newErrors.idNumber = "ID number is required";
      } else if (field === "photoIdFront" && !formData.photoIdFront) {
        newErrors.photoIdFront = "Photo ID front is required";
      } else if (field === "photoIdBack" && !formData.photoIdBack && formData.idType !== "passport") {
        newErrors.photoIdBack = "Photo ID back is required";
      } else if (field === "selfie" && !formData.selfie) {
        newErrors.selfie = "Selfie is required";
      } else if (field === "proofOfAddress" && !formData.proofOfAddress) {
        newErrors.proofOfAddress = "Proof of address is required";
      } else if (field === "bvnNumber" && selectedCountry === "NG" && !formData.bvnNumber?.trim()) {
        newErrors.bvnNumber = "BVN is required for Nigerian accounts";
      }
    });

    // Additional validations
    if (formData.dateOfBirth) {
      // Check if user is at least 18 years old
      const eighteenYearsAgo = new Date();
      eighteenYearsAgo.setFullYear(eighteenYearsAgo.getFullYear() - 18);
      if (formData.dateOfBirth > eighteenYearsAgo) {
        newErrors.dateOfBirth = "You must be at least 18 years old";
      }
    }

    // Validate ID formats by country
    if (formData.idType === "ssn" && selectedCountry === "US" && 
        !/^\d{9}$|^\d{3}-\d{2}-\d{4}$/.test(formData.idNumber)) {
      newErrors.idNumber = "Please enter a valid SSN (9 digits or XXX-XX-XXXX format)";
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

  const config = countryConfig[selectedCountry];

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Identity Verification (KYC)</CardTitle>
        <CardDescription>
          To comply with financial regulations, we need to verify your identity.
          All information is encrypted and securely stored as required by law.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Country Selection */}
          <div className="space-y-2">
            <Label htmlFor="country_select">Country of Residence</Label>
            <Select
              id="country_select"
              value={selectedCountry}
              onChange={(e) => handleCountryChange(e.target.value)}
            >
              <option value="US">🇺🇸 United States</option>
              <option value="CA">🇨🇦 Canada</option>
              <option value="MX">🇲🇽 Mexico</option>
              <option value="NG">🇳🇬 Nigeria</option>
              <option value="EG">🇪🇬 Egypt</option>
              <option value="EU">🇪🇺 European Union</option>
            </Select>
          </div>

          {/* Personal Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Personal Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="fullName">Full Legal Name</Label>
              <Input
                id="fullName"
                value={formData.fullName}
                onChange={(e) => handleChange("fullName", e.target.value)}
                className={errors.fullName ? "border-red-500" : ""}
              />
              {errors.fullName && (
                <p className="text-red-500 text-sm">{errors.fullName}</p>
              )}
            </div>
            
            {/* Only show if required for country */}
            {(config.requiredFields.includes("dateOfBirth") || config.optionalFields.includes("dateOfBirth")) && (
              <div className="space-y-2">
                <Label htmlFor="dateOfBirth">
                  Date of Birth
                  {!config.requiredFields.includes("dateOfBirth") && <span className="text-gray-500 text-sm ml-1">(Optional)</span>}
                </Label>
                <DatePicker
                  id="dateOfBirth"
                  selected={formData.dateOfBirth}
                  onSelect={(date) => handleChange("dateOfBirth", date)}
                  className={errors.dateOfBirth ? "border-red-500" : ""}
                />
                {errors.dateOfBirth && (
                  <p className="text-red-500 text-sm">{errors.dateOfBirth}</p>
                )}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Phone Number - Required for Nigeria, optional for others */}
              <div className="space-y-2">
                <Label htmlFor="phoneNumber">
                  Phone Number
                  {!config.requiredFields.includes("phoneNumber") && <span className="text-gray-500 text-sm ml-1">(Optional)</span>}
                </Label>
                <Input
                  id="phoneNumber"
                  type="tel"
                  value={formData.phoneNumber}
                  onChange={(e) => handleChange("phoneNumber", e.target.value)}
                  className={errors.phoneNumber ? "border-red-500" : ""}
                />
                {errors.phoneNumber && (
                  <p className="text-red-500 text-sm">{errors.phoneNumber}</p>
                )}
              </div>
              
              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email">
                  Email Address
                  {!config.requiredFields.includes("email") && <span className="text-gray-500 text-sm ml-1">(Optional)</span>}
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange("email", e.target.value)}
                  className={errors.email ? "border-red-500" : ""}
                />
                {errors.email && (
                  <p className="text-red-500 text-sm">{errors.email}</p>
                )}
              </div>
            </div>
          </div>

          {/* Residential Address - Skip for Nigeria Tier 1 */}
          {(config.requiredFields.includes("residentialAddress") || config.optionalFields.includes("residentialAddress")) && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">
                Residential Address
                {!config.requiredFields.includes("residentialAddress") && <span className="text-gray-500 text-sm ml-1">(Optional for {config.name})</span>}
              </h3>
              
              <div className="space-y-2">
                <Label htmlFor="street">Street Address</Label>
                <Input
                  id="street"
                  value={formData.residentialAddress.street}
                  onChange={(e) => handleChange("residentialAddress.street", e.target.value)}
                  className={errors["residentialAddress.street"] ? "border-red-500" : ""}
                />
                {errors["residentialAddress.street"] && (
                  <p className="text-red-500 text-sm">{errors["residentialAddress.street"]}</p>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={formData.residentialAddress.city}
                    onChange={(e) => handleChange("residentialAddress.city", e.target.value)}
                    className={errors["residentialAddress.city"] ? "border-red-500" : ""}
                  />
                  {errors["residentialAddress.city"] && (
                    <p className="text-red-500 text-sm">{errors["residentialAddress.city"]}</p>
                  )}
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="state">State/Province</Label>
                  <Input
                    id="state"
                    value={formData.residentialAddress.state}
                    onChange={(e) => handleChange("residentialAddress.state", e.target.value)}
                    className={errors["residentialAddress.state"] ? "border-red-500" : ""}
                  />
                  {errors["residentialAddress.state"] && (
                    <p className="text-red-500 text-sm">{errors["residentialAddress.state"]}</p>
                  )}
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="zipCode">Postal/ZIP Code</Label>
                <Input
                  id="zipCode"
                  value={formData.residentialAddress.zipCode}
                  onChange={(e) => handleChange("residentialAddress.zipCode", e.target.value)}
                  className={errors["residentialAddress.zipCode"] ? "border-red-500" : ""}
                />
                {errors["residentialAddress.zipCode"] && (
                  <p className="text-red-500 text-sm">{errors["residentialAddress.zipCode"]}</p>
                )}
              </div>
            </div>
          )}

          {/* Government ID - Nigeria BVN or regular ID types */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Government ID</h3>
            
            {selectedCountry === "NG" && (
              <div className="space-y-2">
                <Label htmlFor="bvnNumber">
                  Bank Verification Number (BVN)
                  {!config.requiredFields.includes("bvnNumber") && <span className="text-gray-500 text-sm ml-1">(Optional for Tier 1)</span>}
                </Label>
                <Input
                  id="bvnNumber"
                  value={formData.bvnNumber || ""}
                  onChange={(e) => handleChange("bvnNumber", e.target.value)}
                  className={errors.bvnNumber ? "border-red-500" : ""}
                  placeholder="11-digit BVN number"
                />
                {errors.bvnNumber && (
                  <p className="text-red-500 text-sm">{errors.bvnNumber}</p>
                )}
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="idType">ID Type</Label>
                <Select
                  id="idType"
                  value={formData.idType}
                  onChange={(e) => handleChange("idType", e.target.value)}
                >
                  {config.idTypes.map(idType => (
                    <option key={idType.value} value={idType.value}>{idType.label}</option>
                  ))}
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="idNumber">ID Number</Label>
                <Input
                  id="idNumber"
                  value={formData.idNumber}
                  onChange={(e) => handleChange("idNumber", e.target.value)}
                  className={errors.idNumber ? "border-red-500" : ""}
                  placeholder={formData.idType === "ssn" ? "XXX-XX-XXXX" : ""}
                />
                {errors.idNumber && (
                  <p className="text-red-500 text-sm">{errors.idNumber}</p>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="idExpiryDate">ID Expiration Date</Label>
              <DatePicker
                id="idExpiryDate"
                selected={formData.idExpiryDate}
                onSelect={(date) => handleChange("idExpiryDate", date)}
              />
            </div>
          </div>

          {/* Photo Verification */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Photo Verification</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(config.requiredFields.includes("photoIdFront") || config.optionalFields.includes("photoIdFront")) && (
                <div className="space-y-2">
                  <Label htmlFor="photoIdFront">
                    Photo ID Front
                    {!config.requiredFields.includes("photoIdFront") && <span className="text-gray-500 text-sm ml-1">(Optional)</span>}
                  </Label>
                  <UploadButton
                    accept="image/*"
                    onChange={(file) => handleChange("photoIdFront", file)}
                    className={errors.photoIdFront ? "border-red-500" : ""}
                  />
                  {errors.photoIdFront && (
                    <p className="text-red-500 text-sm">{errors.photoIdFront}</p>
                  )}
                </div>
              )}
              
              {(formData.idType !== "passport" && (config.requiredFields.includes("photoIdBack") || config.optionalFields.includes("photoIdBack"))) && (
                <div className="space-y-2">
                  <Label htmlFor="photoIdBack">
                    Photo ID Back
                    {!config.requiredFields.includes("photoIdBack") && <span className="text-gray-500 text-sm ml-1">(Optional)</span>}
                  </Label>
                  <UploadButton
                    accept="image/*"
                    onChange={(file) => handleChange("photoIdBack", file)}
                    className={errors.photoIdBack ? "border-red-500" : ""}
                  />
                  {errors.photoIdBack && (
                    <p className="text-red-500 text-sm">{errors.photoIdBack}</p>
                  )}
                </div>
              )}
            </div>
            
            {(config.requiredFields.includes("selfie") || config.optionalFields.includes("selfie")) && (
              <div className="space-y-2">
                <Label htmlFor="selfie">
                  Selfie with ID
                  {!config.requiredFields.includes("selfie") && <span className="text-gray-500 text-sm ml-1">(Optional)</span>}
                </Label>
                <UploadButton
                  accept="image/*"
                  onChange={(file) => handleChange("selfie", file)}
                  className={errors.selfie ? "border-red-500" : ""}
                />
                <p className="text-xs text-gray-500">
                  Please take a photo of yourself holding your ID next to your face.
                </p>
                {errors.selfie && (
                  <p className="text-red-500 text-sm">{errors.selfie}</p>
                )}
              </div>
            )}
            
            {(config.requiredFields.includes("proofOfAddress") || config.optionalFields.includes("proofOfAddress")) && (
              <div className="space-y-2">
                <Label htmlFor="proofOfAddress">
                  Proof of Address
                  {!config.requiredFields.includes("proofOfAddress") && <span className="text-gray-500 text-sm ml-1">(Optional)</span>}
                </Label>
                <UploadButton
                  accept="image/*,.pdf"
                  onChange={(file) => handleChange("proofOfAddress", file)}
                  className={errors.proofOfAddress ? "border-red-500" : ""}
                />
                <p className="text-xs text-gray-500">
                  Upload a utility bill, bank statement, or government letter dated within the last 3 months.
                </p>
                {errors.proofOfAddress && (
                  <p className="text-red-500 text-sm">{errors.proofOfAddress}</p>
                )}
              </div>
            )}
          </div>

          {/* For admin use - not displayed to end users */}
          {process.env.NODE_ENV === "development" && (
            <div className="space-y-4 bg-gray-100 p-4 rounded-md">
              <h3 className="text-lg font-medium">Admin Review (Internal Only)</h3>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <input
                    id="ofacScreened"
                    type="checkbox"
                    checked={formData.ofacScreened}
                    onChange={(e) => handleChange("ofacScreened", e.target.checked)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  <Label htmlFor="ofacScreened" className="ml-2">
                    OFAC/Sanctions Checked
                  </Label>
                </div>
                
                <div className="flex items-center">
                  <input
                    id="pepScreened"
                    type="checkbox"
                    checked={formData.pepScreened}
                    onChange={(e) => handleChange("pepScreened", e.target.checked)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                  />
                  <Label htmlFor="pepScreened" className="ml-2">
                    PEP Screening Completed
                  </Label>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="reviewerName">Reviewer Name</Label>
                  <Input
                    id="reviewerName"
                    value={formData.reviewerName}
                    onChange={(e) => handleChange("reviewerName", e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="reviewDate">Review Date</Label>
                  <DatePicker
                    id="reviewDate"
                    selected={formData.reviewDate}
                    onSelect={(date) => handleChange("reviewDate", date)}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="approvalStatus">Approval Status</Label>
                <Select
                  id="approvalStatus"
                  value={formData.approvalStatus}
                  onChange={(e) => handleChange("approvalStatus", e.target.value)}
                >
                  <option value="pending">Pending Review</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="reviewerNotes">Reviewer Notes</Label>
                <textarea
                  id="reviewerNotes"
                  value={formData.reviewerNotes}
                  onChange={(e) => handleChange("reviewerNotes", e.target.value)}
                  className="w-full p-2 border rounded-md"
                  rows={3}
                />
              </div>
            </div>
          )}

          {/* Transaction Caps Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4 text-sm text-blue-800">
            <h4 className="font-medium mb-1">Transaction Limits for {config.name}</h4>
            <p>For security reasons, the following limits apply to your account:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>Maximum single transaction: {config.currencySymbol}{config.txCap}</li>
              <li>Maximum monthly transaction volume: {config.currencySymbol}{config.monthlyCap}</li>
              {selectedCountry === "NG" && (
                <li>Tier 1 accounts limited to ₦50,000/month (~$65 USD)</li>
              )}
              {selectedCountry === "US" && (
                <li>Travel Rule applies for on-chain transfers over $3,000</li>
              )}
            </ul>
            <p className="mt-2 text-xs italic">{config.notes}</p>
          </div>

          {/* Submit Button */}
          <div className="flex justify-between pt-4">
            {onBack && (
              <button 
                type="button" 
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background border border-input hover:bg-accent hover:text-accent-foreground h-10 py-2 px-4"
                onClick={onBack}
              >
                Back
              </button>
            )}
            <button 
              type="submit"
              className={`inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-primary text-primary-foreground hover:bg-primary/90 h-10 py-2 px-4 ${!onBack ? "w-full" : ""}`}
            >
              Submit KYC Information
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

export default KYCLiteForm; 