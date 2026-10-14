import { Input } from '../../atoms/input/Input';

export const FirstNameInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input
        variant={variant}
        type="text"
        placeholder="First name"
        {...props}
      />
    </div>
  );
};
