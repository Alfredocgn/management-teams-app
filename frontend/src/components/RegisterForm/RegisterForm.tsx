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
    .min(8, 'Must be at least 8 characters')
    .matches(/[A-Z]/, 'Must contain at least one uppercase letter')
    .matches(/[0-9]/, 'Must contain at least one number')
    .required('Required'),
  first_name: Yup.string().required('Required'),
  last_name: Yup.string().required('Required'),
});

export const RegisterForm = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  
  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await authApi.register(values);
        navigate('/login');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Registration failed');
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
      
      <Input
        label="First Name"
        name="first_name"
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        value={formik.values.first_name}
        error={formik.errors.first_name}
        touched={formik.touched.first_name}
      />
      
      <Input
        label="Last Name"
        name="last_name"
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        value={formik.values.last_name}
        error={formik.errors.last_name}
        touched={formik.touched.last_name}
      />

      <button
        type="submit"
        disabled={formik.isSubmitting}
        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
      >
        {formik.isSubmitting ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
};