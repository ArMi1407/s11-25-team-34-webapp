export const NavItem = ({ icon, text, href }) => {
  return (
    <a href={href} className="flex items-center gap-2">
      <Icon name={icon} size={20} />
      <Text variant="nav">{text}</Text>
    </a>
  );
};
