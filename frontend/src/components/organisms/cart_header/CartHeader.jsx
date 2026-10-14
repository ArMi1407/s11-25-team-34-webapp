import { Brand } from '../../molecules/brand/Brand';
import { HamburgerMenu } from '../../molecules/menus/HamburgerMenu';
import { CartIcon } from '../../molecules/icons/CartIcon';
import { UserIcon } from '../../molecules/icons/UserIcon';
import { HomeIcon } from '../../molecules/icons/HomeIcon'; // Necesitarás crear este ícono
import { Link } from '../../atoms/link/Link';
import { Paragraph } from '../../atoms/text/Paragraph';
import { MdKeyboardArrowLeft } from 'react-icons/md'; // O usa tu propio ícono

export const CartHeader = () => {
  return (
    <header className="flex justify-between items-center py-4 md:py-6 px-4 sm:px-6 lg:px-8 h-20 bg-bg-body border-b border-gray-100">
      {/* Logo/Brand - Izquierda */}
      <div className="flex-1">
        <Brand />
      </div>

      {/* Título centrado - Solo en desktop */}
      <div className="hidden md:block flex-1 text-center">
        <Paragraph className="text-xl font-semibold text-text-primary">
          Mi Carrito
        </Paragraph>
      </div>

      {/* Navegación - Derecha */}
      <div className="flex-1 flex justify-end items-center gap-4 md:gap-6">
        {/* Enlace a Home - Solo móvil */}
        <Link to="/" className="md:hidden">
          <HomeIcon />
        </Link>

        {/* Enlace de regreso - Solo desktop */}
        <Link
          to="/"
          className="hidden md:flex items-center gap-2 hover:opacity-80"
        >
          <MdKeyboardArrowLeft className="w-5 h-5" />
          <Paragraph className="text-text-primary text-sm">
            Continuar comprando
          </Paragraph>
        </Link>

        {/* Iconos de navegación */}
        <div className="hidden sm:flex items-center gap-4">
          <Link to="/search">
            <Paragraph className="text-text-primary hover:text-primary transition-colors">
              Buscar
            </Paragraph>
          </Link>
          <Link to="/profile">
            <UserIcon />
          </Link>
          {/* Nota: No mostramos CartIcon aquí porque ya estamos en el carrito */}
        </div>

        {/* Menú hamburguesa para móvil */}
        <div className="sm:hidden">
          <HamburgerMenu />
        </div>
      </div>
    </header>
  );
};
