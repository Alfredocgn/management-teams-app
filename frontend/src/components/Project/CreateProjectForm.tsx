import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Input } from '../common/Input/Input';

interface CreateProjectFormProps {
  onSubmit: (values: { title: string; description: string }) => Promise<void>;
}

const validationSchema = Yup.object({
  title: Yup.string().required('Required'),
  description: Yup.string().required('Required'),
});

export const CreateProjectForm = ({ onSubmit }: CreateProjectFormProps) => {
  const formik = useFormik({
    initialValues: {
      title: '',
      description: '',
    },
    validationSchema,
    onSubmit: async (values, { resetForm }) => {
      await onSubmit(values);
      resetForm();
    },
  });

  return (
    <div className="bg-white shadow sm:rounded-lg mb-6 p-6">
      <h2 className="text-lg font-medium mb-4">Create New Project</h2>
      <form onSubmit={formik.handleSubmit} className="space-y-4">
        <Input
          label="Title"
          name="title"
          type="text"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          value={formik.values.title}
          error={formik.errors.title}
          touched={formik.touched.title}
        />
        
        <Input
          label="Description"
          name="description"
          type="text"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          value={formik.values.description}
          error={formik.errors.description}
          touched={formik.touched.description}
        />

        <button
          type="submit"
          disabled={formik.isSubmitting}
          className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          {formik.isSubmitting ? 'Creating...' : 'Create Project'}
        </button>
      </form>
    </div>
  );
};