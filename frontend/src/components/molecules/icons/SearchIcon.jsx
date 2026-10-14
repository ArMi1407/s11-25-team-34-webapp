import { Button } from '../../atoms/button/Button';
import { FiSearch } from 'react-icons/fi';

export const SearchIcon = ({ onToggle }) => {
  return (
    <Button
      icon={FiSearch}
      iconClassName="text-text-primary group-hover:text-white"
      onClick={onToggle}
      variant="ghost"
      className="group p-2"
    />
  );
};
