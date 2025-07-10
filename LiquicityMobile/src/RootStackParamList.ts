export type RootStackParamList = {
  Home: undefined;
  TermsOfService: undefined;
  KYCStart: { signed_agreement_id?: string };
  KYCStatusScreen: undefined;
  KYCUploadID: { customerId: string };
  MainTabs: undefined;
  // Add other screens as needed
};
