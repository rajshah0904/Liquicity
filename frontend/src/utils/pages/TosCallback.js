import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import api from '../utils/api';

const TosCallback = () => {
  const navigate = useNavigate();
  const { getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    const handle = async () => {
      const params = new URLSearchParams(window.location.search);
      const signedId = params.get('signed_agreement_id');
      if (!signedId) {
        // malformed redirect – go back to signup
        navigate('/signup?tosfail=true');
        return;
      }
      try {
        const token = await getAccessTokenSilently();
        const res = await api.post('/onboard/tos/accepted', { signed_agreement_id: signedId }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        // Redirect straight to KYC link if provided
        if (res.data.kyc_url) {
          window.location.href = res.data.kyc_url;
        } else {
          navigate('/kyc-verification');
        }
      } catch (e) {
        console.error('TOS callback error', e);
        navigate('/signup?tosfail=true');
      }
    };
    handle();
  }, [getAccessTokenSilently, navigate]);

  return null;
};

export default TosCallback; 