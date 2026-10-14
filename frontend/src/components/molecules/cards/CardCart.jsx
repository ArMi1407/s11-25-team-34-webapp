// CardCart.jsx - VERSIÓN FINAL (no necesita cartItemId ni productId)
import { Image } from '../../atoms/image/Image';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';
import { EcoBadge } from '../../atoms/badge/EcoBadge';
import { QuantitySelector } from '../selectors/QuantitySelector';
import { DeleteButton } from '../buttons/DeleteButton';

export const CardCart = ({
  imageSrc,
  name,
  price,
  ecoBadge,
  quantity,
  onQuantityChange, // Esta función recibe solo la nueva cantidad
  onRemove, // Esta función no recibe parámetros
}) => {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-4 bg-bg-card rounded-lg shadow-md">
      {/* Imagen - Responsive */}
      <div className="w-full sm:w-24 md:w-32 lg:w-40 shrink-0">
        <Image
          src={imageSrc}
          alt={name}
          className="w-full aspect-square object-cover rounded-md"
        />
      </div>

      {/* Contenido */}
      <div className="flex-1 flex flex-col sm:flex-row sm:items-center gap-4 w-full">
        {/* Información del producto */}
        <div className="flex-1">
          <Title
            className="mb-2 text-base sm:text-lg text-text-primary"
            variant="subtitle"
          >
            {name}
          </Title>
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
            <Paragraph className="text-text-primary font-semibold">
              ${price}
            </Paragraph>
            <EcoBadge>{ecoBadge}</EcoBadge>
          </div>
        </div>

        {/* Controles */}
        <div className="flex items-center justify-between sm:justify-end gap-4 sm:gap-6">
          <QuantitySelector
            value={quantity}
            onChange={onQuantityChange} // Pasa solo la nueva cantidad
            min={1}
            max={99}
          />
          <DeleteButton onClick={onRemove} />
        </div>
      </div>
    </div>
  );
};
