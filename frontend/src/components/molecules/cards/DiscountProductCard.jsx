import { Image } from '../../atoms/image/Image';
import { CardButton } from '../buttons/CardButton';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';
import { EcoBadge } from '../../atoms/badge/EcoBadge';

export const DiscountProductCard = ({
  imageSrc,
  name,
  price,
  discountedPrice,
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
          <div className="flex flex-col">
            <Paragraph className="text-text-secondary text-xs line-through">
              ${price}
            </Paragraph>
            <div className="flex gap-2 items-center">
              <Paragraph className="text-text-primary">
                ${discountedPrice}
              </Paragraph>
              <Paragraph className="text-text-discount text-xs">
                19% OFF
              </Paragraph>
            </div>
          </div>
          <EcoBadge>{ecoBadge}</EcoBadge>
        </div>

        <CardButton onClick={handleAddToCart} />
      </div>
    </div>
  );
};
