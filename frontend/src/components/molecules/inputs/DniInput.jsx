import { Input } from '../../atoms/input/Input';

export const DniInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input
        variant={variant}
        type="text"
        placeholder="DNI of 8 digits"
        {...props}
      />
    </div>
  );
};
