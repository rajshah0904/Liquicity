import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DatePicker } from "@/components/ui/date-picker";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadButton } from "@/components/ui/upload-button";

interface IdentityVerificationFormProps {
  onSubmit: (data: any) => void;
  onBack: () => void;
}

const IdentityVerificationForm = ({ onSubmit, onBack }: IdentityVerificationFormProps) => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    dateOfBirth: null as Date | null,
    nationality: "",
    idType: "passport",
    idNumber: "",
    frontIdImage: null as File | null,
    backIdImage: null as File | null,
    selfieImage: null as File | null,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Clear the error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Clear the error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleDateChange = (date: Date | null) => {
    setFormData((prev) => ({ ...prev, dateOfBirth: date }));
    
    // Clear the error for dateOfBirth
    if (errors.dateOfBirth) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors.dateOfBirth;
        return newErrors;
      });
    }
  };

  const handleFileUpload = (name: string, file: File | null) => {
    setFormData((prev) => ({ ...prev, [name]: file }));
    
    // Clear the error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = "Last name is required";
    }

    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = "Date of birth is required";
    } else {
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <Card className="w-full max-w-3xl mx-auto">
      <CardHeader>
        <CardTitle>Verify Your Identity</CardTitle>
        <CardDescription>
          We need to verify your identity to comply with financial regulations.
          All information is encrypted and stored securely.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                className={errors.firstName ? "border-red-500" : ""}
              />
              {errors.firstName && (
                <p className="text-red-500 text-sm mt-1">{errors.firstName}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Input
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                className={errors.lastName ? "border-red-500" : ""}
              />
              {errors.lastName && (
                <p className="text-red-500 text-sm mt-1">{errors.lastName}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="dateOfBirth">Date of Birth</Label>
              <DatePicker
                id="dateOfBirth"
                selected={formData.dateOfBirth}
                onSelect={handleDateChange}
                className={errors.dateOfBirth ? "border-red-500" : ""}
              />
              {errors.dateOfBirth && (
                <p className="text-red-500 text-sm mt-1">{errors.dateOfBirth}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="nationality">Nationality</Label>
              <Select
                value={formData.nationality}
                onValueChange={(value) => handleSelectChange("nationality", value)}
              >
                <SelectTrigger id="nationality" className={errors.nationality ? "border-red-500" : ""}>
                  <SelectValue placeholder="Select nationality" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="us">United States</SelectItem>
                  <SelectItem value="ca">Canada</SelectItem>
                  <SelectItem value="uk">United Kingdom</SelectItem>
                  <SelectItem value="au">Australia</SelectItem>
                  <SelectItem value="de">Germany</SelectItem>
                  <SelectItem value="fr">France</SelectItem>
                  <SelectItem value="jp">Japan</SelectItem>
                  <SelectItem value="sg">Singapore</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
              {errors.nationality && (
                <p className="text-red-500 text-sm mt-1">{errors.nationality}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="idType">ID Type</Label>
              <Select
                value={formData.idType}
                onValueChange={(value) => handleSelectChange("idType", value)}
              >
                <SelectTrigger id="idType">
                  <SelectValue placeholder="Select ID type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="passport">Passport</SelectItem>
                  <SelectItem value="drivers_license">Driver's License</SelectItem>
                  <SelectItem value="national_id">National ID Card</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="idNumber">ID Number</Label>
              <Input
                id="idNumber"
                name="idNumber"
                value={formData.idNumber}
                onChange={handleChange}
                className={errors.idNumber ? "border-red-500" : ""}
              />
              {errors.idNumber && (
                <p className="text-red-500 text-sm mt-1">{errors.idNumber}</p>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium">Upload ID Documents</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="frontIdImage">Front Side of ID</Label>
                <UploadButton
                  accept="image/*"
                  onChange={(file) => handleFileUpload("frontIdImage", file)}
                  className={errors.frontIdImage ? "border-red-500" : ""}
                />
                {formData.frontIdImage && (
                  <p className="text-sm text-green-600">
                    Uploaded: {formData.frontIdImage.name}
                  </p>
                )}
                {errors.frontIdImage && (
                  <p className="text-red-500 text-sm mt-1">{errors.frontIdImage}</p>
                )}
              </div>
              
              {formData.idType !== "passport" && (
                <div className="space-y-2">
                  <Label htmlFor="backIdImage">Back Side of ID</Label>
                  <UploadButton
                    accept="image/*"
                    onChange={(file) => handleFileUpload("backIdImage", file)}
                    className={errors.backIdImage ? "border-red-500" : ""}
                  />
                  {formData.backIdImage && (
                    <p className="text-sm text-green-600">
                      Uploaded: {formData.backIdImage.name}
                    </p>
                  )}
                  {errors.backIdImage && (
                    <p className="text-red-500 text-sm mt-1">{errors.backIdImage}</p>
                  )}
                </div>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="selfieImage">Selfie With ID</Label>
              <UploadButton
                accept="image/*"
                onChange={(file) => handleFileUpload("selfieImage", file)}
                className={errors.selfieImage ? "border-red-500" : ""}
              />
              {formData.selfieImage && (
                <p className="text-sm text-green-600">
                  Uploaded: {formData.selfieImage.name}
                </p>
              )}
              {errors.selfieImage && (
                <p className="text-red-500 text-sm mt-1">{errors.selfieImage}</p>
              )}
            </div>
          </div>

          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={onBack}>
              Back
            </Button>
            <Button type="submit">Continue</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default IdentityVerificationForm; 