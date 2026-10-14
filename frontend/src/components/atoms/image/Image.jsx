export const Image = ({ src, alt = '', className = '' }) => {
  const baseStyles = 'w-full object-cover select-none';
  return (
    <img
      src={src}
      alt={alt}
      className={`${baseStyles} ${className}`}
      draggable={false}
      loading="lazy"
    />
  );
};
