import { Button } from '../../atoms/button/Button';
import { Paragraph } from '../../atoms/text/Paragraph';

export const SignUpButton = ({ onClick }) => {
  return (
    <Button
      variant="default"
      onClick={onClick}
      className=" w-full px-4 py-2.5 h-6 sm:h-8  sm:py-4"
    >
      <Paragraph variant="bold">Sign Up</Paragraph>
    </Button>
  );
};
