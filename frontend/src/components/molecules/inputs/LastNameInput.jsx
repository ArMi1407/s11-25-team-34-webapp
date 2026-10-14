import { Input } from '../../atoms/input/Input';

export const LastNameInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input variant={variant} type="text" placeholder="Last name" {...props} />
    </div>
  );
};
