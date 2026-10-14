// CartIcon.jsx - VERSIÓN MEJORADA
import { Button } from '../../atoms/button/Button';
import { LuShoppingCart } from 'react-icons/lu';
import { useCart } from '../../../contexts/CartContext'; // Import opcional

export const CartIcon = ({ onToggle, showCount = false }) => {
  const { cartCount } = useCart(); // Solo si showCount es true

  return (
    <div className="relative">
      <Button
        icon={LuShoppingCart}
        iconClassName="text-text-primary group-hover:text-white"
        onClick={onToggle}
        variant="ghost"
        className="group p-2"
      />
      {showCount && cartCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
          {cartCount > 99 ? '99+' : cartCount}
        </span>
      )}
    </div>
  );
};
