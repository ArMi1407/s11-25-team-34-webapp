// components/molecules/menus/HamburgerMenu.jsx
import { IoMenu } from 'react-icons/io5';
import { Button } from '../../atoms/button/Button';

export const HamburgerMenu = ({ onToggle }) => {
  return (
    <Button
      icon={IoMenu}
      iconClassName="text-text-primary group-hover:text-white"
      onClick={onToggle}
      variant="ghost"
      className="group p-2"
    />
  );
};
