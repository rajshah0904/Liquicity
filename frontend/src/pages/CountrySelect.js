import React, { useEffect, useState } from 'react';
import { Container, Box, FormControl, InputLabel, Select, MenuItem, Button, Typography, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import api from '../utils/api';

const CountrySelect = () => {
  const navigate = useNavigate();
  const { getAccessTokenSilently } = useAuth0();
  const [countries, setCountries] = useState([]);
  const [country, setCountry] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCountries = async () => {
      try {
        const res = await api.get('/user/countries');
        setCountries(res.data);
      } catch (e) {
        console.error('Failed to load countries', e);
      }
    };
    fetchCountries();
  }, []);

  const handleSubmit = async () => {
    if (!country) return;
    try {
      setLoading(true);
      const token = await getAccessTokenSilently();
      await api.post('/user/country', { country }, { headers: { Authorization: `Bearer ${token}` } });
      const tos = localStorage.getItem('tos_url');
      const cb = encodeURIComponent(`${window.location.origin}/tos-callback`);
      if (tos) {
        window.location.href = `${tos}&redirect_uri=${cb}`;
      } else {
        navigate('/signup');
      }
    } catch (e) {
      console.error('Failed to set country', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 10 }}>
      <Typography variant="h5" gutterBottom>Select your Country</Typography>
      {countries.length === 0 ? <CircularProgress /> : (
        <>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel id="country-label">Country</InputLabel>
            <Select
              labelId="country-label"
              value={country}
              label="Country"
              onChange={(e) => setCountry(e.target.value)}
            >
              {countries.map((c) => (
                <MenuItem key={c} value={c}>{c}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="contained" sx={{ mt: 3 }} disabled={!country || loading} onClick={handleSubmit}>
            {loading ? <CircularProgress size={24} /> : 'Next'}
          </Button>
        </>
      )}
    </Container>
  );
};

export default CountrySelect; 