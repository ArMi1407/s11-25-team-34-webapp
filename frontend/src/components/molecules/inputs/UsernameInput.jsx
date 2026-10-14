import { Input } from '../../atoms/input/Input';

export const UsernameInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input variant={variant} type="text" placeholder="Username" {...props} />
    </div>
  );
};
