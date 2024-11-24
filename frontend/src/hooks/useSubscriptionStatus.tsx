import { useState, useEffect } from 'react';
import { userApi } from '../services/api';

export const useSubscriptionStatus = () => {
  const [status, setStatus] = useState<'active' | 'expired' | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await userApi.getSubscriptionStatus();
        setStatus(response.status);
      } catch (error) {
        setStatus('expired');
        console.log(error)
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  return { isSubscribed: status === 'active', loading };
};