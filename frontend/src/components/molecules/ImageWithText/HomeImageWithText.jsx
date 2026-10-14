// components/molecules/ImageWithText/ImageWithText.jsx
import { Image } from '../../atoms/image/Image';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';

export const HomeImageWithText = ({
  imageSrc,
  alt = '',
  title = '',
  description = '',
  subDescription = '',
  className = '',
  textPosition = 'center',
  //   overlayOpacity = 50,
  titleVariant = 'title',
}) => {
  // Mapeo de posiciones a clases de Tailwind
  const positionClasses = {
    'top-left': 'items-start justify-start text-left',
    'top-center': 'items-start justify-center text-center',
    'top-right': 'items-start justify-end text-right',
    'center-left': 'items-center justify-start text-left',
    center: 'items-center justify-center text-center',
    'center-right': 'items-center justify-end text-right',
    'bottom-left': 'items-end justify-start text-left',
    'bottom-center': 'items-end justify-center text-center',
    'bottom-right': 'items-end justify-end text-right',
  };

  // Si textPosition no es válido, usar 'center' por defecto
  const selectedPosition =
    positionClasses[textPosition] || positionClasses.center;

  return (
    <div className={`relative w-full h-auto md:h-40 lg:h-100 ${className}`}>
      {/* Imagen de fondo usando tu átomo Image */}
      <Image
        src={imageSrc}
        alt={alt}
        className="hidden md:flex absolute inset-0"
      />

      {/* Overlay para mejor legibilidad del texto */}
      {/* <div
        className="absolute inset-0 bg-black"
        style={{ opacity: `${overlayOpacity}%` }}
      /> */}

      {/* Contenedor de texto */}
      <div
        className={`relative md:absolute inset-0 flex md:block  p-2 sm:p-4 lg:p-8 ${selectedPosition}`}
      >
        <div className="max-w-2xl z-10">
          {title && (
            <Title
              variant={titleVariant}
              className="text-primary mb-2 sm:mb-3 lg:mb-4 lg:leading-25 text-2xl sm:text-3xl md:text-5xl lg:text-7xl"
            >
              {title}
            </Title>
          )}
          <div className="flex flex-col space-y md:space-y-2">
            {description && (
              <Paragraph
                variant="semibold"
                className="text-text-secondary text-base md:text-xl"
              >
                {description}
              </Paragraph>
            )}
            {subDescription && (
              <Paragraph
                variant="bold"
                className="text-primary mt-2 text-base md:text-lg"
              >
                {subDescription}
              </Paragraph>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
