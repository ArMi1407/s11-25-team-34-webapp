import { Input } from '../../atoms/input/Input';

export const EmailInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input variant={variant} type="email" placeholder="Email" {...props} />
    </div>
  );
};
