import { Button } from '../../atoms/button/Button';
import { Paragraph } from '../../atoms/text/Paragraph';
import { IoTrashOutline } from 'react-icons/io5'; // O usa tu propio ícono

export const DeleteButton = ({
  onClick,
  label = 'Remove',
  showLabel = false,
  className = '',
  ...props
}) => {
  return (
    <Button
      variant="ghost"
      onClick={onClick}
      className={`text-red-500 hover:text-white hover:bg-red-500 active:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-300 ${className}`}
      aria-label={showLabel ? undefined : 'Remove item'}
      {...props}
    >
      <IoTrashOutline className="w-5 h-5 sm:w-6 sm:h-6" />
      {showLabel && (
        <Paragraph variant="bold" className="ml-2 text-sm sm:text-base">
          {label}
        </Paragraph>
      )}
    </Button>
  );
};
