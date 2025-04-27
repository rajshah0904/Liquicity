import { NextResponse } from 'next/server';
import { kycService } from '@/app/services/kyc-service';
import { db } from '@/app/lib/db';

export async function POST(request: Request) {
  try {
    const data = await request.json();
    const { userId, personalInfo, identity, address } = data;

    // Validate required data
    if (!userId || !personalInfo || !identity || !address) {
      return NextResponse.json(
        { error: 'Missing required verification data' },
        { status: 400 }
      );
    }

    // Check if user exists
    const user = await db.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Store verification data
    await db.kycVerification.create({
      data: {
        userId,
        status: 'pending',
        personalInfo,
        identityInfo: identity,
        addressInfo: address,
        submittedAt: new Date()
      }
    });

    // Submit to external KYC provider
    const verificationResult = await kycService.submitVerification({
      userId,
      firstName: personalInfo.firstName,
      lastName: personalInfo.lastName,
      email: personalInfo.email,
      dateOfBirth: personalInfo.dateOfBirth,
      nationality: personalInfo.nationality,
      taxId: personalInfo.taxId,
      identityDocument: identity.documentType,
      identityNumber: identity.documentNumber,
      identityImage: identity.documentImage,
      addressLine1: address.line1,
      addressLine2: address.line2,
      city: address.city,
      state: address.state,
      postalCode: address.postalCode,
      country: address.country,
      addressProofImage: address.proofImage
    });

    // Update user KYC status based on provider response
    let kycStatus = 'pending';
    
    if (verificationResult.requiresManualReview) {
      kycStatus = 'pending';
    } else if (verificationResult.approved) {
      kycStatus = 'approved';
    } else {
      kycStatus = 'rejected';
    }

    await db.user.update({
      where: { id: userId },
      data: {
        kycStatus,
        kycVerifiedAt: kycStatus === 'approved' ? new Date() : null,
        kycLevel: verificationResult.verificationLevel || 1
      }
    });

    // Update verification record with provider reference
    await db.kycVerification.update({
      where: { userId },
      data: {
        providerReferenceId: verificationResult.referenceId,
        status: kycStatus,
        notes: verificationResult.notes,
        updatedAt: new Date()
      }
    });

    return NextResponse.json({ 
      status: kycStatus,
      requiresManualReview: verificationResult.requiresManualReview,
      message: verificationResult.message || 'Verification submitted successfully'
    });
  } catch (error) {
    console.error('KYC verification error:', error);
    return NextResponse.json(
      { error: 'Failed to process verification request' },
      { status: 500 }
    );
  }
} 