import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, Modal, FlatList, TextInput, Platform, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { createCustomer } from '../lib/bridgeClient';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Country list and alpha-2 to alpha-3 mapping
const countries = [
  { code: 'US', name: 'United States', alpha3: 'USA' },
  { code: 'CA', name: 'Canada', alpha3: 'CAN' },
  { code: 'MX', name: 'Mexico', alpha3: 'MEX' },
  { code: 'GB', name: 'United Kingdom', alpha3: 'GBR' },
  { code: 'DE', name: 'Germany', alpha3: 'DEU' },
  { code: 'FR', name: 'France', alpha3: 'FRA' },
  { code: 'IT', name: 'Italy', alpha3: 'ITA' },
  { code: 'ES', name: 'Spain', alpha3: 'ESP' },
  { code: 'NL', name: 'Netherlands', alpha3: 'NLD' },
  { code: 'BE', name: 'Belgium', alpha3: 'BEL' },
  { code: 'IE', name: 'Ireland', alpha3: 'IRL' },
  { code: 'PT', name: 'Portugal', alpha3: 'PRT' },
  { code: 'AT', name: 'Austria', alpha3: 'AUT' },
  { code: 'CH', name: 'Switzerland', alpha3: 'CHE' },
  { code: 'SE', name: 'Sweden', alpha3: 'SWE' },
  { code: 'NO', name: 'Norway', alpha3: 'NOR' },
  { code: 'DK', name: 'Denmark', alpha3: 'DNK' },
  { code: 'FI', name: 'Finland', alpha3: 'FIN' },
  { code: 'PL', name: 'Poland', alpha3: 'POL' },
  { code: 'CZ', name: 'Czech Republic', alpha3: 'CZE' },
  { code: 'SK', name: 'Slovakia', alpha3: 'SVK' },
  { code: 'HU', name: 'Hungary', alpha3: 'HUN' },
  { code: 'GR', name: 'Greece', alpha3: 'GRC' },
  { code: 'RO', name: 'Romania', alpha3: 'ROU' },
  { code: 'BG', name: 'Bulgaria', alpha3: 'BGR' },
  { code: 'HR', name: 'Croatia', alpha3: 'HRV' },
  { code: 'SI', name: 'Slovenia', alpha3: 'SVN' },
  { code: 'EE', name: 'Estonia', alpha3: 'EST' },
  { code: 'LV', name: 'Latvia', alpha3: 'LVA' },
  { code: 'LT', name: 'Lithuania', alpha3: 'LTU' },
  { code: 'LU', name: 'Luxembourg', alpha3: 'LUX' },
  { code: 'LI', name: 'Liechtenstein', alpha3: 'LIE' },
  { code: 'IS', name: 'Iceland', alpha3: 'ISL' },
  { code: 'TR', name: 'Turkey', alpha3: 'TUR' },
  { code: 'IL', name: 'Israel', alpha3: 'ISR' },
  { code: 'AE', name: 'United Arab Emirates', alpha3: 'ARE' },
  { code: 'SA', name: 'Saudi Arabia', alpha3: 'SAU' },
  { code: 'IN', name: 'India', alpha3: 'IND' },
  { code: 'SG', name: 'Singapore', alpha3: 'SGP' },
  { code: 'JP', name: 'Japan', alpha3: 'JPN' },
  { code: 'KR', name: 'South Korea', alpha3: 'KOR' },
  { code: 'AU', name: 'Australia', alpha3: 'AUS' },
  { code: 'NZ', name: 'New Zealand', alpha3: 'NZL' },
  { code: 'ZA', name: 'South Africa', alpha3: 'ZAF' },
  { code: 'NG', name: 'Nigeria', alpha3: 'NGA' },
  { code: 'KE', name: 'Kenya', alpha3: 'KEN' },
  { code: 'GH', name: 'Ghana', alpha3: 'GHA' },
  { code: 'EG', name: 'Egypt', alpha3: 'EGY' },
  { code: 'BR', name: 'Brazil', alpha3: 'BRA' },
  { code: 'AR', name: 'Argentina', alpha3: 'ARG' },
  { code: 'CL', name: 'Chile', alpha3: 'CHL' },
  { code: 'CO', name: 'Colombia', alpha3: 'COL' },
  { code: 'PE', name: 'Peru', alpha3: 'PER' },
  // ...add more as needed
];

const KYCStart = ({ navigation, route }: any) => {
  // Form state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [dobDay, setDobDay] = useState('');
  const [dobMonth, setDobMonth] = useState('');
  const [dobYear, setDobYear] = useState('');
  const [street, setStreet] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [ssn, setSSN] = useState('');

  const signedAgreementId = route?.params?.signed_agreement_id;

  const filteredCountries = countries.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  // Validation helper
  const validate = () => {
    if (!firstName.trim()) return 'First name is required.';
    if (!lastName.trim()) return 'Last name is required.';
    if (!email.trim()) return 'Email is required.';
    if (!ssn.trim()) return 'SSN is required.';
    if (!dobDay || !dobMonth || !dobYear) return 'Date of birth is required.';
    if (!/^[0-9]{3}-[0-9]{2}-[0-9]{4}$/.test(ssn.trim())) return 'SSN must be in the format XXX-XX-XXXX.';
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.trim())) return 'Email must be valid.';
    if (!/\d{4}/.test(dobYear) || !/\d{1,2}/.test(dobMonth) || !/\d{1,2}/.test(dobDay)) return 'Date of birth must be valid.';
    if (parseInt(dobMonth) < 1 || parseInt(dobMonth) > 12) return 'Month must be 1-12.';
    if (parseInt(dobDay) < 1 || parseInt(dobDay) > 31) return 'Day must be 1-31.';
    if (!street.trim()) return 'Street address is required.';
    if (!city.trim()) return 'City is required.';
    if (!postalCode.trim()) return 'Postal code is required.';
    if (!selectedCountry) return 'Country is required.';
    if (!signedAgreementId) return 'Missing signed_agreement_id.';
    return null;
  };

  const handleCountrySelect = (countryCode: string) => {
    setSelectedCountry(countryCode);
    setModalVisible(false);
    setSearch('');
  };

  const handleSubmit = async () => {
    const error = validate();
    if (error) {
      Alert.alert('Validation Error', error);
      return;
    }
    setLoading(true);
    try {
      const countryObj = countries.find(c => c.code === selectedCountry);
      const countryAlpha3 = countryObj ? countryObj.alpha3 : selectedCountry;
      const birthDate = `${dobYear}-${dobMonth.padStart(2, '0')}-${dobDay.padStart(2, '0')}`;
      const payload = {
        type: 'individual',
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        residential_address: {
          street_line_1: street.trim(),
          city: city.trim(),
          subdivision: state.trim() || undefined,
          postal_code: postalCode.trim(),
          country: countryAlpha3,
        },
        birth_date: birthDate,
        signed_agreement_id: signedAgreementId,
        identifying_information: [
          {
            type: 'ssn',
            issuing_country: 'usa',
            number: ssn.trim(),
          }
        ]
      };
      const resp = await createCustomer(payload);
      if (resp && resp.id) {
        await AsyncStorage.setItem('bridge_customer_id', resp.id);
        navigation.navigate('KYCUploadID', { customerId: resp.id });
      } else {
        Alert.alert('Error', 'Customer creation failed.');
      }
    } catch (e: any) {
      let errorMsg = e?.message || String(e);
      if (e?.response) {
        errorMsg = `Status: ${e.response.status}\n`;
        if (e.response.data) {
          if (typeof e.response.data === 'object') {
            errorMsg += JSON.stringify(e.response.data, null, 2);
          } else {
            errorMsg += e.response.data;
          }
        }
      }
      Alert.alert('Error', errorMsg);
    }
    setLoading(false);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={{ paddingBottom: 40 }} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>KYC Information</Text>
        <Text style={styles.subtitle}>Please enter your details as they appear on your government-issued ID.</Text>
        <TextInput
          style={styles.input}
          placeholder="First Name"
          placeholderTextColor="#aaa"
          value={firstName}
          onChangeText={setFirstName}
        />
        <TextInput
          style={styles.input}
          placeholder="Last Name"
          placeholderTextColor="#aaa"
          value={lastName}
          onChangeText={setLastName}
        />
        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#aaa"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="SSN (XXX-XX-XXXX)"
          placeholderTextColor="#aaa"
          value={ssn}
          onChangeText={setSSN}
          keyboardType="numbers-and-punctuation"
          autoCapitalize="none"
        />
        <View style={styles.dobRow}>
          <TextInput
            style={[styles.input, styles.dobInput]}
            placeholder="DD"
            placeholderTextColor="#aaa"
            value={dobDay}
            onChangeText={setDobDay}
            keyboardType="number-pad"
            maxLength={2}
          />
          <TextInput
            style={[styles.input, styles.dobInput]}
            placeholder="MM"
            placeholderTextColor="#aaa"
            value={dobMonth}
            onChangeText={setDobMonth}
            keyboardType="number-pad"
            maxLength={2}
          />
          <TextInput
            style={[styles.input, styles.dobInput]}
            placeholder="YYYY"
            placeholderTextColor="#aaa"
            value={dobYear}
            onChangeText={setDobYear}
            keyboardType="number-pad"
            maxLength={4}
          />
        </View>
        <TextInput
          style={styles.input}
          placeholder="Street Address"
          placeholderTextColor="#aaa"
          value={street}
          onChangeText={setStreet}
        />
        <TextInput
          style={styles.input}
          placeholder="City"
          placeholderTextColor="#aaa"
          value={city}
          onChangeText={setCity}
        />
        <TextInput
          style={styles.input}
          placeholder="State (optional)"
          placeholderTextColor="#aaa"
          value={state}
          onChangeText={setState}
        />
        <TextInput
          style={styles.input}
          placeholder="Postal Code"
          placeholderTextColor="#aaa"
          value={postalCode}
          onChangeText={setPostalCode}
        />
        <TouchableOpacity
          style={styles.dropdownButton}
          onPress={() => setModalVisible(true)}
          activeOpacity={0.8}
        >
          <Text style={selectedCountry ? styles.dropdownText : styles.dropdownPlaceholder}>
            {selectedCountry ? countries.find(c => c.code === selectedCountry)?.name : 'Select a country...'}
          </Text>
        </TouchableOpacity>
        <Modal
          visible={modalVisible}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <TextInput
                style={styles.searchInput}
                placeholder="Search country..."
                placeholderTextColor="#888"
                value={search}
                onChangeText={setSearch}
                autoFocus
              />
              <FlatList
                data={filteredCountries}
                keyExtractor={item => item.code}
                renderItem={({ item }) => (
                  <TouchableOpacity
                    style={styles.countryItem}
                    onPress={() => handleCountrySelect(item.code)}
                  >
                    <Text style={styles.countryText}>{item.name}</Text>
                  </TouchableOpacity>
                )}
                keyboardShouldPersistTaps="handled"
              />
            </View>
          </View>
        </Modal>
        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.submitButtonText}>Submit</Text>}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingHorizontal: 20,
    paddingTop: 40,
  },
  title: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 12,
    marginTop: 20,
  },
  subtitle: {
    color: '#aaa',
    fontSize: 14,
    marginBottom: 24,
  },
  input: {
    backgroundColor: '#222',
    color: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#fff',
    paddingVertical: 12,
    paddingHorizontal: 16,
    width: '100%',
    marginTop: 12,
    fontSize: 16,
  },
  dobRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 12,
  },
  dobInput: {
    flex: 1,
    marginRight: 8,
    marginTop: 0,
  },
  dropdownButton: {
    backgroundColor: '#18181b',
    borderRadius: 12,
    paddingVertical: 18,
    paddingHorizontal: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#333',
    marginTop: 12,
  },
  dropdownText: {
    color: '#fff',
    fontSize: 16,
  },
  dropdownPlaceholder: {
    color: '#888',
    fontSize: 16,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#111',
    borderRadius: 16,
    width: '90%',
    maxHeight: '70%',
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
  },
  searchInput: {
    backgroundColor: '#222',
    color: '#fff',
    borderRadius: 8,
    paddingVertical: Platform.OS === 'ios' ? 14 : 10,
    paddingHorizontal: 14,
    marginBottom: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  countryItem: {
    paddingVertical: 14,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  countryText: {
    color: '#fff',
    fontSize: 16,
  },
  submitButton: {
    backgroundColor: '#007AFF',
    borderRadius: 10,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 24,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default KYCStart; 