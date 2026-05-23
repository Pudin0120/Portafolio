import React, { useMemo } from "react";
import { Package, Circle, DollarSign } from "lucide-react";
import { Button, Chip, Card, CardBody } from "@heroui/react";
import { formatPrice } from "@/utils";
import { Product } from "@/types/products";

const getNumericPrice = (price: Product["price"]): number => {
  const parsed =
    typeof price === "number" ? price : Number.parseFloat(price ?? "");
  return Number.isFinite(parsed) ? parsed : 0;
};

export type ComponentItem = {
  product_id: string;
  quantity: number;
};

type ComponentsListProps = {
  components: ComponentItem[];
  products: Product[];
  onRemoveComponent: (index: number) => void;
  showPrices?: boolean;
};

export const ComponentsList: React.FC<ComponentsListProps> = ({
  components,
  products,
  onRemoveComponent,
  showPrices = false,
}) => {
  const getProductDetails = (productId: string) => {
    const product = products.find((p) => p.id === productId);
    return product;
  };

  const calculateComponentPrice = (component: ComponentItem): number => {
    const product = getProductDetails(component.product_id);
    const price = getNumericPrice(product?.price);
    if (!price) return 0;

    return price * component.quantity;
  };

  const totalPrice = useMemo(() => {
    return components.reduce((sum, comp) => {
      return sum + calculateComponentPrice(comp);
    }, 0);
  }, [components, products]);

  const hasAnyPrice = useMemo(() => {
    return components.some((comp) => {
      const product = getProductDetails(comp.product_id);
      return getNumericPrice(product?.price) > 0;
    });
  }, [components, products]);

  if (components.length === 0) {
    return (
      <Card className="bg-default-50">
        <CardBody>
          <p className="text-center text-sm text-default-500">
            No hay componentes agregados. Agrega products para construir tu
            product compuesto.
          </p>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-foreground">
          Componentes agregados ({components.length}):
        </p>
        {showPrices && hasAnyPrice && totalPrice > 0 && (
          <Chip color="success" variant="solid" size="lg" className="font-bold">
            Total: ${formatPrice(totalPrice)} COP
          </Chip>
        )}
      </div>

      <div className="space-y-2">
        {components.map((comp, index) => {
          const product = getProductDetails(comp.product_id);
          const productPrice = getNumericPrice(product?.price);
          const componentPrice = calculateComponentPrice(comp);

          return (
            <Card key={index} className="bg-default-100">
              <CardBody className="p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex flex-1 items-center gap-3">
                    <Chip size="sm" color="primary" variant="flat">
                      x{comp.quantity}
                    </Chip>

                    <div className="flex-1">
                      <p className="font-medium text-foreground">
                        {product?.name || comp.product_id}
                      </p>
                      {product && (
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-2 text-xs text-default-500">
                            <span className="flex items-center gap-1">
                              {product.product_type === "simple" ? (
                                <Circle className="w-3 h-3" />
                              ) : (
                                <Package className="w-3 h-3" />
                              )}
                              {product.product_type === "simple"
                                ? "Simple"
                                : "Compuesto"}
                            </span>
                            {product.material_name && (
                              <>
                                <span></span>
                                <span className="flex items-center gap-1">
                                  <Package className="w-3 h-3" />{" "}
                                  {product.material_name}
                                </span>
                              </>
                            )}
                          </div>
                          {product.description && (
                            <p className="text-xs text-default-400 line-clamp-1">
                              {product.description}
                            </p>
                          )}
                        </div>
                      )}
                    </div>

                    {showPrices && product && productPrice > 0 && (
                      <div className="text-right">
                        <p className="text-sm font-semibold text-success">
                          ${formatPrice(componentPrice)}{" "}
                          {product.currency || "COP"}
                        </p>
                        {comp.quantity > 1 && (
                          <p className="text-xs text-default-500">
                            ${formatPrice(componentPrice / comp.quantity)} c/u
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  <Button
                    size="sm"
                    color="danger"
                    variant="flat"
                    onPress={() => onRemoveComponent(index)}
                  >
                    Delete
                  </Button>
                </div>
              </CardBody>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
