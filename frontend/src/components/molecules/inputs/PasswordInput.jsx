import { Input } from '../../atoms/input/Input';

export const PasswordInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input
        variant={variant}
        type="password"
        placeholder="Password"
        {...props}
      />
    </div>
  );
};
