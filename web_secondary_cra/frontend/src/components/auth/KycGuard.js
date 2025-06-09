import { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';

const KycGuard = ({ children }) => {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
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
          if (localStorage.getItem('isNewSignup') === 'true') {
            // Allow through; KYC page will handle registration
          } else {
            // user not registered and not in signup flow
            navigate('/signup?noaccount=true');
            return;
          }
        }
        if (kyc_complete) {
          // already completed KYC; send to dashboard
          navigate('/dashboard');
          return;
        }
        setAllowed(true);
      } catch (e) {
        console.error('KycGuard error', e);
        navigate('/login');
      }
    };
    check();
  }, [isAuthenticated, getAccessTokenSilently, navigate]);

  return allowed ? children : null;
};

export default KycGuard; 