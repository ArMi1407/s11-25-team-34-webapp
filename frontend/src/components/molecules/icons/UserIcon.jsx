import { Button } from '../../atoms/button/Button';
import { FiUser } from 'react-icons/fi';

export const UserIcon = ({ onToggle }) => {
  return (
    <Button
      icon={FiUser}
      iconClassName="text-text-primary group-hover:text-white"
      onClick={onToggle}
      variant="ghost"
      className="group p-2"
    />
  );
};
