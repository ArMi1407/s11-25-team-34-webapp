import { Button } from '../../atoms/button/Button';
import { IoHomeSharp } from 'react-icons/io5';

export const HomeIcon = ({ onToggle }) => {
  return (
    <Button
      icon={IoHomeSharp}
      iconClassName="text-text-primary group-hover:text-white"
      onClick={onToggle}
      variant="ghost"
      className="group p-2"
    />
  );
};
