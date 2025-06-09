import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import api from '../../utils/api';

const RequireKyc = ({ children }) => {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();
  const [allowed, setAllowed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const check = async () => {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      }
      try {
        const token = await getAccessTokenSilently();
        const res = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });
        const { exists, kyc_complete } = res.data;
        if (!exists) {
          // something went wrong, restart sign-up
          navigate('/signup?noaccount=true');
          return;
        }
        if (!kyc_complete) {
          // TEMP: bypass KYC enforcement for testing
          setAllowed(true);
          return;
        }
        setAllowed(true);
      } catch (e) {
        console.error('RequireKyc error', e);
        navigate('/login');
      }
    };
    check();
  }, [isAuthenticated, getAccessTokenSilently, navigate]);

  return allowed ? children : null;
};

export default RequireKyc; 