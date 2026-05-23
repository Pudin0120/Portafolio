import React, { useState } from "react";
import {
  Button,
  Tooltip,
  ModalContent,
  ModalHeader,
  ModalBody,
  Chip,
} from "@heroui/react";
import { HelpCircle, CheckCircle, AlertCircle } from "lucide-react";
import { CenteredModal } from "./common/CenteredModal";

interface HelpContent {
  title: string;
  description: string;
  steps?: { step: string; description: string }[];
  tips?: string[];
  warnings?: string[];
}

interface HelpTooltipProps {
  content: HelpContent;
  placement?: "top" | "bottom" | "left" | "right";
  size?: "sm" | "md" | "lg";
}

/**
 * Componente de ayuda discreto y profesional
 * Muestra un icono pequeno de "?" que al hacer click abre un modal con information de ayuda
 */
export const HelpTooltip: React.FC<HelpTooltipProps> = ({
  content,
  placement = "top",
  size = "sm",
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = () => setIsOpen(true);

  // No usamos Tooltip, solo el boton discreto
  return (
    <>
      <Tooltip content="Ayuda" placement={placement}>
        <Button
          isIconOnly
          size={size}
          variant="light"
          color="default"
          onPress={handleOpen}
          className="opacity-60 hover:opacity-100 transition-opacity"
        >
          <HelpCircle className="w-4 h-4" />
        </Button>
      </Tooltip>

      <CenteredModal
        isOpen={isOpen}
        onOpenChange={setIsOpen}
        size="2xl"
        scrollBehavior="inside"
      >
        {() => (
          <>
            <ModalHeader className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
                <HelpCircle className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold">{content.title}</h2>
                <p className="text-sm text-default-500 mt-1">
                  {content.description}
                </p>
              </div>
            </ModalHeader>

            <ModalBody className="pt-4 pb-6">
              {/* Pasos si existen */}
              {content.steps && content.steps.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-default-700 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-success" />
                    Pasos a seguir
                  </h3>
                  <ol className="space-y-3">
                    {content.steps.map((item, index) => (
                      <li
                        key={`step-${item.step.replace(/\s+/g, "-").toLowerCase()}-${index}`}
                        className="flex gap-3"
                      >
                        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-white text-sm font-semibold flex items-center justify-center">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-default-900">
                            {item.step}
                          </p>
                          <p className="text-sm text-default-600 mt-1">
                            {item.description}
                          </p>
                        </div>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Tips si existen */}
              {content.tips && content.tips.length > 0 && (
                <div className="mt-6 space-y-3">
                  <h3 className="text-sm font-semibold text-default-700 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-warning" />
                    Consejos utiles
                  </h3>
                  <ul className="space-y-2">
                    {content.tips.map((tip, index) => (
                      <li
                        key={`tip-${tip.slice(0, 20).replace(/\s+/g, "-")}-${index}`}
                        className="flex gap-2 items-start"
                      >
                        <div className="flex-shrink-0 w-1 h-1 rounded-full bg-warning mt-2" />
                        <p className="text-sm text-default-600">{tip}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Advertencias si existen */}
              {content.warnings && content.warnings.length > 0 && (
                <div className="mt-6 space-y-3">
                  <h3 className="text-sm font-semibold text-default-700 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-danger" />
                    Importante
                  </h3>
                  <div className="space-y-2">
                    {content.warnings.map((warning, index) => (
                      <Chip
                        key={`warning-${warning.slice(0, 20).replace(/\s+/g, "-")}-${index}`}
                        variant="flat"
                        color="danger"
                        className="w-full justify-start h-auto py-1"
                      >
                        <span className="text-sm whitespace-normal">
                          {warning}
                        </span>
                      </Chip>
                    ))}
                  </div>
                </div>
              )}
            </ModalBody>
          </>
        )}
      </CenteredModal>
    </>
  );
};

// Contenido de ayuda predefinido para diferentes contextos
export const helpContent = {
  materials: {
    title: "Gestion de Materials",
    description: "Aprende a create, edit y gestionar materials en el sistema",
    steps: [
      {
        step: "Selecciona el tipo de material",
        description:
          "Elige el tipo segun la categoria (Acero, Aluminio, Liquidos, etc.)",
      },
      {
        step: "Completa la description",
        description: "Describe el material de manera clara y especifica",
      },
      {
        step: "Establece el price",
        description: "Ingresa el price en la moneda correspondiente",
      },
      {
        step: "Define las properties",
        description:
          "Segun el tipo, configura las properties de measurement (espesor, dimensiones, etc.)",
      },
    ],
    tips: [
      "Los materials se utilizan para create products",
      "El price debe estar en formato numerico valid",
      "Las properties varian segun el tipo de material",
      "Puedes edit o delete materials existentes",
    ],
    warnings: [
      "Delete un material puede afectar products que lo usan",
      "Verifica que el price sea correcto antes de save",
    ],
  },

  materialsList: {
    title: "Lista de Materials",
    description: "Gestiona todos tus materials desde esta vista",
    steps: [
      {
        step: "Search materials",
        description:
          "Usa la barra de busqueda para filtrar por nombre, description o tipo",
      },
      {
        step: "Ver detalles",
        description: "Haz clic en un material para ver toda su information",
      },
      {
        step: "Edit o delete",
        description:
          "Usa los botones de acciones para modificar o delete materials",
      },
    ],
    tips: [
      "La busqueda es en tiempo real",
      "Puedes ver precios y properties de cada material",
      "Usa los filtros para organizar mejor tus materials",
    ],
  },

  products: {
    title: "Gestion de Products",
    description: "Crea y gestiona products simples y compuestos",
    steps: [
      {
        step: "Elige el tipo de product",
        description: "Simple: un material base. Compuesto: varios componentes",
      },
      {
        step: "Product Simple",
        description: "Selecciona un material y define dimensiones/properties",
      },
      {
        step: "Product Compuesto",
        description:
          "Agrega multiples componentes con sus cantidades y ordenes",
      },
      {
        step: "Completa la information",
        description: "Nombre, description y cualquier detalle adicional",
      },
    ],
    tips: [
      "Los products simples son mas rapidos de create",
      "Los products compuestos permiten mayor flexibilidad",
      "El orden de los componentes importa en products compuestos",
      "Puedes definir multiples properties por product",
    ],
    warnings: [
      "Un product compuesto requiere al menos dos componentes",
      "La quantity y orden de los componentes afectan el price final",
    ],
  },

  simpleProduct: {
    title: "Product Simple",
    description: "Crea un product con un solo material base",
    steps: [
      {
        step: "Selecciona el material",
        description: "Elige de la lista de materials disponibles",
      },
      {
        step: "Define las dimensiones",
        description: "Completa las properties segun el tipo de material",
      },
      {
        step: "Configura el product",
        description: "Nombre, description y cualquier detalle adicional",
      },
    ],
    tips: [
      "El material debe estar creado previamente",
      "Las properties son especificas del tipo de material",
      "Puedes agregar multiples dimensiones",
    ],
  },

  compositeProduct: {
    title: "Product Compuesto",
    description: "Crea products con multiples componentes",
    steps: [
      {
        step: "Agrega componentes",
        description: "Selecciona products existentes como componentes",
      },
      {
        step: "Establece cantidades",
        description: "Define cuanto de cada componente se requiere",
      },
      {
        step: "Define el orden",
        description: "El orden de los componentes es importante",
      },
      {
        step: "Completa la information",
        description: "Nombre y description del product compuesto",
      },
    ],
    tips: [
      "Puedes usar products simples o compuestos como componentes",
      "La quantity debe ser un number positivo",
      "El orden afecta como se procesan los componentes",
      "Un product compuesto puede tener multiples niveles",
    ],
  },

  quotations: {
    title: "Create Quotation",
    description:
      "Crea una nueva quotation para tus clients. El estado es Borrador hasta que la finalices.",
    steps: [
      {
        step: "Selecciona un client",
        description: "Busca el client existente o crea uno nuevo",
      },
      {
        step: "Crea o selecciona un work",
        description: "Define el work asociado a la quotation",
      },
      {
        step: "Agrega products",
        description:
          "Selecciona los products que formaran parte de la quotation",
      },
      {
        step: "Revisa y finaliza",
        description:
          'Verifica los datos y cambia el estado a "Finalizada" cuando este lista',
      },
    ],
    tips: [
      'Las cotizaciones comienzan en estado "Borrador"',
      "Puedes edit una quotation mientras este en Borrador",
      "Una vez finalizada, la quotation estara lista para presentar al client",
      "Guarda regularmente para no perder cambios",
    ],
    warnings: ["Los cambios en Borrador se guardan automaticamente"],
  },

  payroll: {
    title: "Gestion de Payrolls",
    description:
      "Administra las payrolls de los empleados y consulta tu information salarial",
    steps: [
      {
        step: "Gestion de Payrolls (Solo Gerente)",
        description:
          "Crea, edita y gestiona las payrolls de todos los empleados",
      },
      {
        step: "My Payroll",
        description:
          "Consulta tu information salarial, periodo actual y historial de pagos",
      },
      {
        step: "Estados de Payroll",
        description:
          "Las payrolls pueden estar Activas, Liquidadas, Pagadas o Canceladas",
      },
    ],
    tips: [
      "El periodo actual muestra el rango de fechas del salario actual",
      "Puedes ver tu historial completo de pagos",
      "Solo el gerente puede create y modificar payrolls",
      "Todos los empleados pueden ver su propia information",
    ],
    warnings: [
      "Los cambios en las payrolls son registrados en el historial",
      "Verifica que la information sea correcta antes de aprobar pagos",
    ],
  },
};
