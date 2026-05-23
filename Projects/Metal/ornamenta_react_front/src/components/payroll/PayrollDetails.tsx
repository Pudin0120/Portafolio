import React from "react";
import {
  Payroll,
  formatMoney,
  getStateLabel,
  getStateColor,
  getContractTypeLabel,
} from "../../types/payroll";
import { CenteredModal } from "../common/CenteredModal";
import { ModalHeader, ModalBody, ModalFooter, Button } from "@heroui/react";

interface PayrollDetailsProps {
  payroll: Payroll;
  onClose: () => void;
  onEdit: (payroll: Payroll) => void;
  employeeName?: string;
}

export const PayrollDetails: React.FC<PayrollDetailsProps> = ({
  payroll,
  onClose,
  onEdit,
  employeeName = "Empleado desconocido",
}) => {
  const totalPayroll =
    payroll.current_period_salary || payroll.base_salary.amount;

  return (
    <CenteredModal
      isOpen={true}
      onOpenChange={(open: boolean) => !open && onClose()}
      size="2xl"
      scrollBehavior="inside"
    >
      {() => (
        <>
          <ModalHeader className="flex flex-col gap-1">
            <h2 className="text-2xl font-bold text-default-800">
              Detalles de Payroll #{payroll.payroll_id.slice(0, 8)}
            </h2>
          </ModalHeader>

          <ModalBody className="gap-6 py-4">
            <div className="space-y-6">
              {/* Informacion General */}
              <div className="bg-default-50 p-4 rounded-lg border border-divider">
                <h3 className="text-lg font-semibold text-default-800 mb-4">
                  Informacion General
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-default-600">ID de Payroll</p>
                    <p className="font-medium text-default-900">
                      {payroll.payroll_id}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-default-600">Empleado</p>
                    <p className="font-medium text-default-900">
                      {employeeName}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-default-600">Tipo de Contract</p>
                    <p className="font-medium text-default-900">
                      {getContractTypeLabel(payroll.contract_type)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-default-600">Estado Actual</p>
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStateColor(payroll.state)}`}
                    >
                      {getStateLabel(payroll.state)}
                    </span>
                  </div>
                  {payroll.current_period_start_date && (
                    <div className="md:col-span-2">
                      <p className="text-sm text-default-600">Periodo Actual</p>
                      <p className="font-medium text-default-900">
                        {new Date(
                          payroll.current_period_start_date,
                        ).toLocaleDateString("es-CO")}{" "}
                        -{" "}
                        {payroll.current_period_end_date
                          ? new Date(
                              payroll.current_period_end_date,
                            ).toLocaleDateString("es-CO")
                          : "Presente"}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Informacion Financiera */}
              <div className="bg-default-50 p-4 rounded-lg border border-divider">
                <h3 className="text-lg font-semibold text-default-800 mb-4">
                  Informacion Financiera
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-default-600">Salario Base:</span>
                    <span className="font-semibold text-default-900">
                      {payroll.base_salary_formatted ||
                        formatMoney(payroll.base_salary)}
                    </span>
                  </div>
                  {payroll.current_period_salary !== undefined && (
                    <div className="flex justify-between items-center">
                      <span className="text-default-600">
                        Salario Periodo Actual:
                      </span>
                      <span className="font-semibold text-default-900">
                        {payroll.current_period_salary_formatted ||
                          formatMoney({
                            amount: payroll.current_period_salary,
                            currency: "COP",
                          })}
                      </span>
                    </div>
                  )}
                  <div className="border-t border-divider pt-2">
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-semibold text-default-800">
                        Total Payroll:
                      </span>
                      <span className="text-xl font-bold text-success-600">
                        {payroll.current_period_salary_formatted ||
                          formatMoney({
                            amount: totalPayroll,
                            currency: "COP",
                          })}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Eventos de Dominio */}
              {payroll._domain_events && payroll._domain_events.length > 0 && (
                <div className="bg-default-50 p-4 rounded-lg border border-divider">
                  <h3 className="text-lg font-semibold text-default-800 mb-4">
                    Historial de Cambios ({payroll._domain_events.length})
                  </h3>
                  <div className="space-y-3">
                    {payroll._domain_events.map((event, index) => (
                      <div
                        key={`${event.event_id}-${index}`}
                        className="border-l-4 border-primary pl-4"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium text-default-800">
                              {event.event_id.slice(0, 8)}...
                            </p>
                            <p className="text-sm text-default-600">
                              {new Date(event.occurred_at).toLocaleString(
                                "es-CO",
                              )}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </ModalBody>

          <ModalFooter className="border-t border-divider">
            <Button
              variant="flat"
              color="default"
              onPress={onClose}
              className="font-medium"
            >
              Cerrar
            </Button>
            <Button
              color="primary"
              variant="solid"
              onPress={() => onEdit(payroll)}
              className="font-semibold"
            >
              Edit Payroll
            </Button>
          </ModalFooter>
        </>
      )}
    </CenteredModal>
  );
};
