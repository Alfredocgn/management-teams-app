import { taskApi } from "../../services/api";
import { CreateTaskFormProps, User } from "../../types/models";
import { Input } from "../common/Input/Input";
import * as Yup from 'yup';
import { useFormik } from 'formik';

export const CreateTaskForm = ({ projectId, onSubmit, members }: CreateTaskFormProps) => {
  const formik = useFormik({
    initialValues: {
      title: '',
      description: '',
      due_date: '',
      assignee_id: '',
      status: 'pending'
    },
    validationSchema: Yup.object({
      title: Yup.string().required('Required'),
      description: Yup.string().required('Required'),
      due_date: Yup.date().nullable(),
      assignee_id: Yup.string().nullable(),
      status: Yup.string().oneOf(['pending', 'in_progress', 'completed']).default('pending'),
    }),
    onSubmit: async (values) => {
      try {
        const taskData = {
          ...values,
          assignee_id: values.assignee_id || null,
          due_date: values.due_date ? new Date(values.due_date).toISOString() : null,
        };
        await taskApi.createTask(projectId, taskData);
        onSubmit();
      } catch (error) {
        console.error('Failed to create task:', error);
      }
    },
  });

  return (
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

      <Input
        label="Due Date"
        name="due_date"
        type="date"
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        value={formik.values.due_date}
        error={formik.errors.due_date}
        touched={formik.touched.due_date}
      />

      <div>
        <label htmlFor="assignee_id" className="block text-sm font-medium text-gray-700">
          Assignee
        </label>
        <select
          id="assignee_id"
          name="assignee_id"
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          value={formik.values.assignee_id}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="">Select an assignee</option>
          {members.map((member: User) => (
            <option key={member.id} value={member.id}>
              {member.first_name} {member.last_name}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={formik.isSubmitting}
        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700"
      >
        {formik.isSubmitting ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
};