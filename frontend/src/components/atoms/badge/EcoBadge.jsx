export const EcoBadge = ({ children, className = '' }) => {
  const baseStyles =
    'inline-flex w-auto h-auto self-start items-center bg-bg-icons text-primary text-xs font-normal font-roboto px-2 py-0.5 rounded-full border border-primary';
  return <div className={`${baseStyles} ${className}`}>{children}</div>;
};
