import { Button } from '../../atoms/button/Button';
import { Paragraph } from '../../atoms/text/Paragraph';
import { FiShoppingCart } from 'react-icons/fi';

export const CardButton = ({ onClick }) => {
  return (
    <Button
      variant="default"
      icon={FiShoppingCart}
      iconClassName="text-text-primary group-hover:text-white"
      onClick={onClick}
      className="group w-full px-4 h-11 gap-2 border border-text-primary"
    >
      <Paragraph variant="bold" className="text-base">
        Agregar al carrito
      </Paragraph>
    </Button>
  );
};
