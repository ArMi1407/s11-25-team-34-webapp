import { Button } from '../../atoms/button/Button';
import { Paragraph } from '../../atoms/text/Paragraph';

export const NextButton = ({ onClick }) => {
  return (
    <Button
      variant="secondary"
      onClick={onClick}
      className=" w-full px-4 h-6 sm:h-8 py-2.5 sm:py-4"
    >
      <Paragraph variant="bold">Next Step</Paragraph>
    </Button>
  );
};
