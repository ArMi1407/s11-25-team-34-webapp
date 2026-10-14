import { Brand } from '../../molecules/brand/Brand';
import { HamburgerMenu } from '../../molecules/menus/HamburgerMenu';
import { CartIcon } from '../../molecules/icons/CartIcon';
import { UserIcon } from '../../molecules/icons/UserIcon';
import { SearchIcon } from '../../molecules/icons/SearchIcon';
import { Link } from '../../atoms/link/Link';
import { Paragraph } from '../../atoms/text/Paragraph';

export const HomeHeader = () => {
  return (
    <header className="md:bg-button flex justify-between items-center py-4 md:py-8 px-4 h-20 md:max-h-13">
      <Brand />

      <div className=" hidden md:flex md:gap-17">
        <Link to="/Skincare">
          <Paragraph className="text-xs md:text-xl text-text-primary">
            Skincare
          </Paragraph>
        </Link>
        <Link to="/mas-venidos">
          <Paragraph className="text-xs md:text-xl text-text-primary">
            Más venidos
          </Paragraph>
        </Link>
        <Link to="/mi-perfil">
          <Paragraph className="text-xs md:text-xl text-text-primary">
            Mi perfil
          </Paragraph>
        </Link>
      </div>

      <div className=" hidden sm:flex md:gap-4">
        <Link to="/clothes">
          <SearchIcon />
        </Link>
        <Link to="/cart">
          <CartIcon showCount={true} />
        </Link>
        <Link to="/profile">
          <UserIcon />
        </Link>
      </div>

      <div className="sm:hidden">
        <HamburgerMenu />
      </div>
    </header>
  );
};
