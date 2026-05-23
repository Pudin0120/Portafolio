/**
 * Arbol jerarquico recursivo para mostrar componentes
 * Soporta compuestos anidados con indentacion visual
 */

import React from "react";
import {
  Card,
  CardBody,
  Button,
  Chip,
  Image,
  Accordion,
  AccordionItem,
} from "@heroui/react";
import { Package, Circle, Trash2, Edit, ChevronRight } from "lucide-react";
import { CompositeComponentForm, CalculatedComponent } from "./types";
import { Product } from "@/types/products";
import { formatPrice } from "@/utils";

type ComponentsHierarchyTreeProps = {
  components: CompositeComponentForm[];
  products?: Product[]; // Para modo formulario (antes de simular)
  calculatedComponents?: CalculatedComponent[]; // Para modo preview (despues de simular)
  onRemoveComponent?: (index: number) => void;
  onEditComponent?: (index: number) => void;
  showActions?: boolean;
  showPrices?: boolean;
};

export const ComponentsHierarchyTree: React.FC<
  ComponentsHierarchyTreeProps
> = ({
  components,
  products: _products,
  calculatedComponents,
  onRemoveComponent,
  onEditComponent,
  showActions = true,
  showPrices = true,
}) => {
  if (components.length === 0) {
    return (
      <Card className="bg-default-50">
        <CardBody className="p-4">
          <p className="text-center text-sm text-default-500">
            No hay componentes agregados. Haz clic en "Agregar Componente" para
            comenzar.
          </p>
        </CardBody>
      </Card>
    );
  }

  // Renderizar un componente individual
  const renderComponent = (
    comp: CompositeComponentForm,
    index: number,
    calculated?: CalculatedComponent,
  ) => {
    const product = comp.product;
    const isComposite = product.product_type === "composite";

    return (
      <Card
        key={index}
        className="bg-default-100 border border-default-200 hover:border-primary/30 transition-all"
      >
        <CardBody className="p-4">
          <div className="flex items-start justify-between gap-3">
            {/* Info del product */}
            <div className="flex items-start gap-3 flex-1">
              {/* Imagen */}
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center overflow-hidden rounded-lg border border-surface-border bg-surface-elevated">
                <Package className="w-6 h-6 text-default-400" />
              </div>

              {/* Detalles */}
              <div className="flex-1 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <p className="font-bold text-foreground">{product.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Chip size="sm" color="primary" variant="flat">
                        {isComposite ? (
                          <div className="flex items-center gap-1">
                            <Package className="w-3 h-3" />
                            Compuesto
                          </div>
                        ) : (
                          <div className="flex items-center gap-1">
                            <Circle className="w-3 h-3" />
                            Simple
                          </div>
                        )}
                      </Chip>
                      {product.material_name && (
                        <Chip size="sm" variant="flat">
                          {product.material_name}
                        </Chip>
                      )}
                    </div>
                    {product.description && (
                      <p className="text-xs text-default-500 mt-1 line-clamp-2">
                        {product.description}
                      </p>
                    )}
                  </div>
                </div>

                {/* Reglas aplicadas */}
                <div className="flex flex-wrap gap-2 text-xs">
                  <div className="px-2 py-1 rounded-lg bg-primary/10 text-primary font-bold">
                    Quantity base: {comp.base_quantity}
                  </div>
                  <div className="px-2 py-1 rounded-lg bg-secondary/10 text-secondary font-bold">
                    Tipo:{" "}
                    {comp.relationship.quantity_type === "fixed"
                      ? "Fija"
                      : comp.relationship.quantity_type === "perimeter"
                        ? "Perimetro"
                        : "Area"}
                  </div>
                  {calculated && (
                    <div className="px-2 py-1 rounded-lg bg-success/10 text-success font-bold">
                      Calculado: {calculated.calculated_quantity.toFixed(2)}
                    </div>
                  )}
                </div>

                {/* Reglas dimensionales */}
                {(comp.relationship.width_rule ||
                  comp.relationship.height_rule ||
                  comp.relationship.depth_rule) && (
                  <div className="flex flex-wrap gap-1.5">
                    {comp.relationship.width_rule && (
                      <Chip size="sm" variant="bordered" color="default">
                        Ancho:{" "}
                        {comp.relationship.width_rule.reference_type ===
                        "parent"
                          ? ` ${comp.relationship.width_rule.parent_dimension}`
                          : `${comp.relationship.width_rule.fixed_value}mm`}
                      </Chip>
                    )}
                    {comp.relationship.height_rule && (
                      <Chip size="sm" variant="bordered" color="default">
                        Alto:{" "}
                        {comp.relationship.height_rule.reference_type ===
                        "parent"
                          ? ` ${comp.relationship.height_rule.parent_dimension}`
                          : `${comp.relationship.height_rule.fixed_value}mm`}
                      </Chip>
                    )}
                    {comp.relationship.depth_rule && (
                      <Chip size="sm" variant="bordered" color="default">
                        Profundidad:{" "}
                        {comp.relationship.depth_rule.reference_type ===
                        "parent"
                          ? ` ${comp.relationship.depth_rule.parent_dimension}`
                          : `${comp.relationship.depth_rule.fixed_value}mm`}
                      </Chip>
                    )}
                  </div>
                )}

                {/* Dimensiones calculadas */}
                {calculated &&
                  calculated.calculated_dimensions &&
                  Object.keys(calculated.calculated_dimensions).length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {Object.entries(calculated.calculated_dimensions).map(
                        ([key, value]) => (
                          <Chip
                            key={key}
                            size="sm"
                            variant="flat"
                            color="warning"
                          >
                            {key}: {value}mm
                          </Chip>
                        ),
                      )}
                    </div>
                  )}

                {/* Price */}
                {showPrices && calculated && (
                  <div className="flex items-center gap-4 mt-2 pt-2 border-t border-default-200">
                    <div>
                      <p className="text-[9px] font-bold uppercase text-default-400">
                        Costo
                      </p>
                      <p className="text-sm font-bold text-warning-600">
                        ${formatPrice(parseFloat(calculated.purchase_price))}
                      </p>
                    </div>
                    <div>
                      <p className="text-[9px] font-bold uppercase text-default-400">
                        Venta
                      </p>
                      <p className="text-sm font-bold text-success-600">
                        ${formatPrice(parseFloat(calculated.sale_price))}
                      </p>
                    </div>
                  </div>
                )}

                {/* Componentes anidados (recursivo) */}
                {isComposite &&
                  calculated &&
                  calculated.components &&
                  calculated.components.length > 0 && (
                    <Accordion variant="light" className="mt-2">
                      <AccordionItem
                        key="nested"
                        aria-label="Ver componentes internos"
                        title={
                          <div className="flex items-center gap-2 text-xs text-primary">
                            <ChevronRight className="w-3 h-3" />
                            <span className="font-bold">
                              Ver {calculated.components.length} componente(s)
                              interno(s)
                            </span>
                          </div>
                        }
                      >
                        <div className="pl-4 border-l-2 border-primary/20 space-y-2">
                          {calculated.components.map((nested, nestedIdx) => (
                            <div
                              key={`${nested.product_id}-${nestedIdx}`}
                              className="p-3 rounded-lg bg-default-50 border border-default-100"
                            >
                              <p className="text-sm font-bold">
                                {nested.product_name}
                              </p>
                              <div className="flex items-center gap-2 text-xs text-default-500 mt-1">
                                <span>
                                  Quantity: {nested.calculated_quantity}
                                </span>
                                {showPrices && (
                                  <>
                                    <span></span>
                                    <span className="text-success">
                                      $
                                      {formatPrice(
                                        parseFloat(nested.sale_price),
                                      )}
                                    </span>
                                  </>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </AccordionItem>
                    </Accordion>
                  )}
              </div>
            </div>

            {/* Acciones */}
            {showActions && (
              <div className="flex flex-col gap-2">
                {onEditComponent && (
                  <Button
                    size="sm"
                    variant="flat"
                    color="primary"
                    isIconOnly
                    onPress={() => onEditComponent(index)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                )}
                {onRemoveComponent && (
                  <Button
                    size="sm"
                    variant="flat"
                    color="danger"
                    isIconOnly
                    onPress={() => onRemoveComponent(index)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            )}
          </div>
        </CardBody>
      </Card>
    );
  };

  return (
    <div className="space-y-3">
      {components.map((comp, index) => {
        const calculated = calculatedComponents?.[index];
        return renderComponent(comp, index, calculated);
      })}
    </div>
  );
};
