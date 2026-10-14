import { Button } from '../../atoms/button/Button';
import { Paragraph } from '../../atoms/text/Paragraph';

export const SignInButton = ({ onClick }) => {
  return (
    <Button
      variant="default"
      onClick={onClick}
      className=" w-full px-4 h-6 sm:h-8 py-2.5 sm:py-4"
    >
      <Paragraph variant="bold">Sign In</Paragraph>
    </Button>
  );
};
