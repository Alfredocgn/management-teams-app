interface InputProps {
  label: string;
  name: string;
  type?: string;
  error?: string;
  touched?: boolean;
  placeholder?: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur: (e: React.FocusEvent<HTMLInputElement>) => void;
  value: string;
}

export const Input = ({ 
  label, 
  error, 
  touched,
  type = "text",
  ...props 
}: InputProps) => {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <input
        type={type}
        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 ${
          touched && error ? 'border-red-500' : 'border-gray-300'
        }`}
        {...props}
      />
      {touched && error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};