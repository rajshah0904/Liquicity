import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import api from '../../utils/api';

const RequireKyc = ({ children }) => {
  const { isAuthenticated, getAccessTokenSilently, user } = useAuth0();
  const [allowed, setAllowed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const check = async () => {
      if (!isAuthenticated) {
        navigate('/login');
        return;
      }
      try {
        const token = await getAccessTokenSilently({
          authorizationParams: {
            scope: 'openid profile email'
          }
        });
        const res = await api.get('/user/check', { headers: { Authorization: `Bearer ${token}` } });
        const { exists, next_step } = res.data;
        if (!exists) {
          // Auto-register if we can, then send to KYC
          try {
            if (user?.email) {
              await api.post('/onboard/register', { email: user.email }, { headers: { Authorization: `Bearer ${token}` } });
              localStorage.setItem('isNewSignup', 'true');
              navigate('/kyc-verification');
              return;
            }
          } catch (regErr) {
            if (regErr?.response?.status === 409) {
              navigate('/kyc-verification');
              return;
            }
          }
          navigate('/signup?noaccount=true');
          return;
        }
        if (next_step !== 'done') {
          // Allow KYC page to load
          navigate('/kyc-verification');
          return;
        }
        setAllowed(true);
      } catch (e) {
        console.error('RequireKyc error', e);
        navigate('/login');
      }
    };
    check();
  }, [isAuthenticated, getAccessTokenSilently, navigate, user]);

  return allowed ? children : null;
};

export default RequireKyc; 