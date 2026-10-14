import { Button } from '../../atoms/button/Button';
import { Paragraph } from '../../atoms/text/Paragraph';

export const PrimaryButton = ({
  children,
  onClick,
  icon: IconComponent,
  disabled = false,
  className = '',
  loading = false,
  type = 'button',
  ...props
}) => {
  return (
    <Button
      variant="default"
      onClick={onClick}
      icon={IconComponent}
      disabled={disabled || loading}
      type={type}
      className={`bg-bg-button hover:bg-text-primary
                 text-text-primary hover:text-white
                 px-6 py-3 rounded-4xl
                 transition-all duration-200
                 disabled:opacity-50 disabled:cursor-not-allowed
                 ${className}`}
      {...props}
    >
      {loading ? (
        <div className="flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
          <Paragraph variant="bold" className="text-base">
            Procesando...
          </Paragraph>
        </div>
      ) : (
        <Paragraph variant="bold" className="text-base">
          {children}
        </Paragraph>
      )}
    </Button>
  );
};
