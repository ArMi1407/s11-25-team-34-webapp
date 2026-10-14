// components/atoms/Link.jsx
import { Link as RouterLink } from 'react-router-dom';

export const Link = ({
  to,
  children,
  className = '',
  variant = 'default',
  ...props
}) => {
  const baseStyles = 'transition-colors duration-200';

  const variants = {
    default: 'text-text-primary hover:text-text-secondary',
    secondary: 'text-primary hover:text-primary-hover',
  };

  return (
    <RouterLink
      to={to}
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </RouterLink>
  );
};
