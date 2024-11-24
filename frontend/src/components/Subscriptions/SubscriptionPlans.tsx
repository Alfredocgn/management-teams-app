import { useState, useEffect } from 'react';
import { subscriptionApi } from '../../services/api';


interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  price_id: string;
}

export const SubscriptionPlans = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await subscriptionApi.getProducts();
        setProducts(data);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load subscription plans');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const handleSubscribe = async (priceId: string) => {
    try {
      setLoading(true);
      const { url } = await subscriptionApi.createCheckoutSession(priceId);
      window.location.href = url;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initiate subscription');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">
            Choose your plan
          </h2>
          <p className="mt-4 text-xl text-gray-600">
            Select the perfect plan for your needs
          </p>
        </div>

        {error && (
          <div className="mt-8 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="mt-12 space-y-4 sm:mt-16 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-6 lg:max-w-4xl lg:mx-auto">
          {products.map((product) => (
            <div key={product.id} className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900">{product.name}</h3>
                <p className="mt-4">
                  <span className="text-4xl font-extrabold text-gray-900">${product.price}</span>
                  <span className="text-base font-medium text-gray-500">/month</span>
                </p>
                <p className="mt-6 text-gray-500">{product.description}</p>
              </div>
              <button
                onClick={() => handleSubscribe(product.price_id)}
                disabled={loading}
                className="mt-8 w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Subscribe Now'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};