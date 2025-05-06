"use strict";
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
exports.kycService = void 0;
const axios_1 = __importDefault(require("axios"));
const uuid_1 = require("uuid");
class KycService {
    constructor() {
        this.apiKey = process.env.KYC_PROVIDER_API_KEY || '';
        this.apiUrl = process.env.KYC_PROVIDER_URL || 'https://api.kyc-provider.com';
        this.isTestMode = process.env.NODE_ENV !== 'production' || process.env.TESTING === '1';
        if (!this.apiKey && !this.isTestMode) {
            console.warn('KYC_PROVIDER_API_KEY not set. KYC service will only work in test mode.');
        }
    }
    submitVerification(request) {
        return __awaiter(this, void 0, void 0, function* () {
            // In test mode, return mock responses
            if (this.isTestMode) {
                return this.getMockVerificationResult(request);
            }
            try {
                // In production, make real API call to KYC provider
                const response = yield axios_1.default.post(`${this.apiUrl}/verifications`, {
                    apiKey: this.apiKey,
                    clientReference: request.userId,
                    personalInfo: {
                        firstName: request.firstName,
                        lastName: request.lastName,
                        email: request.email,
                        dateOfBirth: request.dateOfBirth,
                        nationality: request.nationality,
                        taxId: request.taxId
                    },
                    identity: {
                        documentType: request.identityDocument,
                        documentNumber: request.identityNumber,
                        documentImage: request.identityImage
                    },
                    address: {
                        line1: request.addressLine1,
                        line2: request.addressLine2,
                        city: request.city,
                        state: request.state,
                        postalCode: request.postalCode,
                        country: request.country,
                        proofImage: request.addressProofImage
                    }
                });
                return {
                    approved: response.data.status === 'approved',
                    requiresManualReview: response.data.status === 'review',
                    referenceId: response.data.referenceId,
                    verificationLevel: response.data.verificationLevel,
                    notes: response.data.notes,
                    message: response.data.message,
                    riskScore: response.data.riskScore
                };
            }
            catch (error) {
                console.error('KYC provider API error:', error);
                throw new Error('Failed to submit verification to KYC provider');
            }
        });
    }
    getVerificationStatus(referenceId) {
        return __awaiter(this, void 0, void 0, function* () {
            // In test mode, return mock status
            if (this.isTestMode) {
                return {
                    approved: true,
                    requiresManualReview: false,
                    referenceId,
                    verificationLevel: 2,
                    notes: 'Approved in test mode',
                    message: 'Verification approved'
                };
            }
            try {
                // In production, check status with KYC provider
                const response = yield axios_1.default.get(`${this.apiUrl}/verifications/${referenceId}`, {
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`
                    }
                });
                return {
                    approved: response.data.status === 'approved',
                    requiresManualReview: response.data.status === 'review',
                    referenceId: response.data.referenceId,
                    verificationLevel: response.data.verificationLevel,
                    notes: response.data.notes,
                    message: response.data.message,
                    riskScore: response.data.riskScore
                };
            }
            catch (error) {
                console.error('KYC provider status check error:', error);
                throw new Error('Failed to retrieve verification status from KYC provider');
            }
        });
    }
    getMockVerificationResult(request) {
        // For test mode, implement simple rules to simulate different verification outcomes
        const referenceId = `test_${(0, uuid_1.v4)()}`;
        // Simple risk-based logic: tax ID ending with "9999" triggers manual review
        const requiresManualReview = request.taxId.endsWith('9999');
        // Taxpayer ID ending with "0000" is rejected
        const isRejected = request.taxId.endsWith('0000');
        return {
            approved: !requiresManualReview && !isRejected,
            requiresManualReview,
            referenceId,
            verificationLevel: 2,
            notes: isRejected
                ? 'Rejected due to invalid taxpayer ID'
                : requiresManualReview
                    ? 'Manual review required'
                    : 'Automatically approved',
            message: isRejected
                ? 'Verification rejected'
                : requiresManualReview
                    ? 'Verification sent for manual review'
                    : 'Verification approved',
            riskScore: isRejected ? 85 : requiresManualReview ? 60 : 20
        };
    }
}
exports.kycService = new KycService();
