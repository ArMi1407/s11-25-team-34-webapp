import { Input } from '../../atoms/input/Input';

export const ConfirmPasswordInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';
  return (
    <div className="w-full">
      <Input
        variant={variant}
        type="password"
        placeholder="Confirm Password"
        {...props}
      />
    </div>
  );
};
