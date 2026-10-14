import { CartHeader } from '../../organisms/cart_header/CartHeader';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';
import { PrimaryButton } from '../../molecules/buttons/PrimaryButton';

export const CartTemplate = ({
  children,
  cartItems,
  subtotal,
  tax = 0,
  shipping = 0,
  onCheckout,
  isLoading = false,
}) => {
  const total = subtotal + tax + shipping;

  return (
    <div className="min-h-screen bg-bg-body">
      <CartHeader />

      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Title
          className="text-text-primary mb-8 text-2xl sm:text-3xl md:text-4xl"
          variant="title"
        >
          Tu Carrito
        </Title>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Lista de productos */}
          <div className="flex-1">{children}</div>

          {/* Resumen del pedido */}
          <div className="lg:w-96 shrink-0">
            <div className="bg-bg-card rounded-lg shadow-md p-6 sticky top-8">
              <Title
                className="text-text-primary mb-6 text-xl"
                variant="subtitle"
              >
                Resumen del Pedido
              </Title>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between">
                  <Paragraph className="text-text-secondary">
                    Subtotal
                  </Paragraph>
                  <Paragraph className="text-text-primary font-semibold">
                    ${subtotal.toFixed(2)}
                  </Paragraph>
                </div>
                <div className="flex justify-between">
                  <Paragraph className="text-text-secondary">
                    Impuestos
                  </Paragraph>
                  <Paragraph className="text-text-primary">
                    ${tax.toFixed(2)}
                  </Paragraph>
                </div>
                <div className="flex justify-between">
                  <Paragraph className="text-text-secondary">Envío</Paragraph>
                  <Paragraph className="text-text-primary">
                    {shipping === 0 ? 'Gratis' : `$${shipping.toFixed(2)}`}
                  </Paragraph>
                </div>
                <div className="border-t pt-4 flex justify-between">
                  <Paragraph className="text-text-primary font-semibold text-lg">
                    Total
                  </Paragraph>
                  <Paragraph className="text-text-primary font-bold text-xl">
                    ${total.toFixed(2)}
                  </Paragraph>
                </div>
              </div>

              <PrimaryButton
                onClick={onCheckout}
                disabled={cartItems.length === 0 || isLoading}
                className="w-full"
              >
                {isLoading ? 'Procesando...' : 'Proceder al Pago'}
              </PrimaryButton>

              {cartItems.length > 0 && (
                <Paragraph className="text-center text-text-secondary text-sm mt-4">
                  {cartItems.length}{' '}
                  {cartItems.length === 1 ? 'producto' : 'productos'} en tu
                  carrito
                </Paragraph>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
