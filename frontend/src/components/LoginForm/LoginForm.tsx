import { useFormik } from 'formik';
import * as Yup from 'yup';
import { authApi } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Input } from '../common/Input/Input';

const validationSchema = Yup.object({
  email: Yup.string()
    .email('Invalid email address')
    .required('Required'),
  password: Yup.string()
    .required('Required'),
});

export const LoginForm = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  
  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const response = await authApi.login(values.email, values.password);
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        navigate('/dashboard/projects');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || 'Login failed';
        setError(typeof errorMessage === 'string' ? errorMessage : 'Login failed');
      }
    },
  });

  return (
    <form onSubmit={formik.handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      <Input
        label="Email"
        name="email"
        type="email"
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        value={formik.values.email}
        error={formik.errors.email}
        touched={formik.touched.email}
      />
      
      <Input
        label="Password"
        name="password"
        type="password"
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        value={formik.values.password}
        error={formik.errors.password}
        touched={formik.touched.password}
      />

      <button
        type="submit"
        disabled={formik.isSubmitting}
        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
      >
        {formik.isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};