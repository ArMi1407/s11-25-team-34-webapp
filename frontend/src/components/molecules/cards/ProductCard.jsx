import { Image } from '../../atoms/image/Image';
import { CardButton } from '../buttons/CardButton';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';
import { EcoBadge } from '../../atoms/badge/EcoBadge';

export const ProductCard = ({
  imageSrc,
  name,
  price,
  ecoBadge,
  onAddToCart,
  productId,
}) => {
  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(productId); // Pasar el ID del producto
    }
  };
  return (
    <div className=" bg-bg-card rounded-lg shadow-md overflow-hidden flex flex-col">
      <Image
        src={imageSrc}
        alt={name}
        className="w-full aspect-square object-cover mb-3"
      />
      <div className="p-4">
        <Title className="mb-4 text-base text-text-primary" variant="subtitle">
          {name}
        </Title>
        <div className="flex flex-col mb-8 gap-2">
          <Paragraph className="text-text-primary">${price}</Paragraph>
          <EcoBadge>{ecoBadge}</EcoBadge>
        </div>

        <CardButton onClick={handleAddToCart} />
      </div>
    </div>
  );
};
