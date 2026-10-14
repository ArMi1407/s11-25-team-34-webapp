import { Button } from '../../atoms/button/Button';
import { Paragraph } from '../../atoms/text/Paragraph';
import { FiMinus } from 'react-icons/fi';
import { FaPlus } from 'react-icons/fa6';

export const QuantitySelector = ({
  value = 1,
  onChange,
  min = 1,
  max = 99,
  className = '',
}) => {
  const handleDecrease = () => {
    if (value > min) {
      onChange(value - 1);
    }
  };

  const handleIncrease = () => {
    if (value < max) {
      onChange(value + 1);
    }
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Botón disminuir */}
      <Button
        variant="ghost"
        onClick={handleDecrease}
        disabled={value <= min}
        className="w-8 h-8 sm:w-10 sm:h-10 rounded-full p-0 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Decrease quantity"
      >
        <FiMinus className="w-4 h-4 sm:w-5 sm:h-5" />
      </Button>

      {/* Cantidad */}
      <div className="min-w-10 text-center">
        <Paragraph variant="bold" className="text-base sm:text-lg">
          {value}
        </Paragraph>
      </div>

      {/* Botón aumentar */}
      <Button
        variant="ghost"
        onClick={handleIncrease}
        disabled={value >= max}
        className="w-8 h-8 sm:w-10 sm:h-10 rounded-full p-0 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Increase quantity"
      >
        <FaPlus className="w-4 h-4 sm:w-5 sm:h-5" />
      </Button>
    </div>
  );
};
