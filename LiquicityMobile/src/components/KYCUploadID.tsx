import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Alert, ActivityIndicator } from 'react-native';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { useRoute, useNavigation } from '@react-navigation/native';
import { bridgeRequest } from '../lib/bridgeClient';

const KYCUploadID: React.FC = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const { customerId } = route.params as { customerId: string };
  
  const [frontImage, setFrontImage] = useState<string | null>(null);
  const [backImage, setBackImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async (side: 'front' | 'back') => {
    const result = await launchImageLibrary({ mediaType: 'photo', includeBase64: true });
    if (result.assets && result.assets.length > 0) {
      const base64 = result.assets[0].base64;
      if (base64) {
        if (side === 'front') setFrontImage(`data:image/jpg;base64,${base64}`);
        else setBackImage(`data:image/jpg;base64,${base64}`);
      }
    }
  };

  const takePhoto = async (side: 'front' | 'back') => {
    const result = await launchCamera({ mediaType: 'photo', includeBase64: true });
    if (result.assets && result.assets.length > 0) {
      const base64 = result.assets[0].base64;
      if (base64) {
        if (side === 'front') setFrontImage(`data:image/jpg;base64,${base64}`);
        else setBackImage(`data:image/jpg;base64,${base64}`);
      }
    }
  };

  const handleSubmit = async () => {
    if (!frontImage || !backImage) {
      Alert.alert('Error', 'Please upload both front and back images.');
      return;
    }
    setLoading(true);
    try {
      // Upload front image
      await bridgeRequest('POST', '/documents', {
        customer_id: customerId,
        purposes: ['government_id'],
        side: 'front',
        file: frontImage,
      });
      // Upload back image
      await bridgeRequest('POST', '/documents', {
        customer_id: customerId,
        purposes: ['government_id'],
        side: 'back',
        file: backImage,
      });
      Alert.alert('Success', 'ID images uploaded!');
      // Optionally navigate to next step
      // navigation.navigate('NextKYCStep', { customerId });
    } catch (e: any) {
      Alert.alert('Error', e?.message || String(e));
    }
    setLoading(false);
  };

  return (
    <View style={[styles.container, { paddingTop: 48 }]}>
      <Text style={[styles.title, { marginTop: 16 }]}>Upload US Government ID</Text>
      <Text style={styles.subtitle}>Please upload clear images of the front and back of your government-issued photo ID.</Text>
      <View style={styles.imageRow}>
        <View style={styles.imageCol}>
          <Text>Front</Text>
          {frontImage ? (
            <Image source={{ uri: frontImage }} style={styles.imagePreview} />
          ) : (
            <View style={styles.imagePlaceholder}><Text>No Image</Text></View>
          )}
          <TouchableOpacity style={styles.button} onPress={() => pickImage('front')}><Text>Upload Front</Text></TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={() => takePhoto('front')}><Text>Take Photo</Text></TouchableOpacity>
        </View>
        <View style={styles.imageCol}>
          <Text>Back</Text>
          {backImage ? (
            <Image source={{ uri: backImage }} style={styles.imagePreview} />
          ) : (
            <View style={styles.imagePlaceholder}><Text>No Image</Text></View>
          )}
          <TouchableOpacity style={styles.button} onPress={() => pickImage('back')}><Text>Upload Back</Text></TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={() => takePhoto('back')}><Text>Take Photo</Text></TouchableOpacity>
        </View>
      </View>
      <TouchableOpacity
        style={[styles.submitButton, (!frontImage || !backImage) && { backgroundColor: '#ccc' }]}
        onPress={handleSubmit}
        disabled={!frontImage || !backImage || loading}
      >
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.submitText}>Submit</Text>}
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: '#fff' },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 8 },
  subtitle: { fontSize: 15, color: '#555', marginBottom: 16 },
  imageRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 24 },
  imageCol: { alignItems: 'center', flex: 1 },
  imagePreview: { width: 120, height: 80, borderRadius: 8, marginBottom: 8, borderWidth: 1, borderColor: '#ccc' },
  imagePlaceholder: { width: 120, height: 80, borderRadius: 8, backgroundColor: '#eee', alignItems: 'center', justifyContent: 'center', marginBottom: 8 },
  button: { backgroundColor: '#e0e0e0', padding: 8, borderRadius: 6, marginBottom: 6 },
  submitButton: { backgroundColor: '#007AFF', padding: 14, borderRadius: 8, alignItems: 'center' },
  submitText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
});

export default KYCUploadID; 