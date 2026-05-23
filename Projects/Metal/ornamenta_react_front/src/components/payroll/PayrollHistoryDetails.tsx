import React from 'react';
import { PayrollHistory, formatMoney, createMoney } from '../../types/payroll_history';

interface PayrollHistoryDetailsProps {
    payrollHistory: PayrollHistory;
    employeeName: string;
    onClose: () => void;
    onEdit?: () => void;
}

export const PayrollHistoryDetails: React.FC<PayrollHistoryDetailsProps> = ({
    payrollHistory,
    employeeName,
    onClose,
    onEdit,
}) => {
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('es-CO', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const totalAmount = payrollHistory.works_value_amount;

    return (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
            <div className="bg-content1 border border-divider rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-4 md:p-6">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h2 className="text-xl md:text-2xl font-bold text-foreground">Detalles de Payroll</h2>
                            <p className="text-default-500 mt-1">{employeeName}</p>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-default-400 hover:text-default-600 transition-colors"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div>
                            <h3 className="text-lg font-semibold text-foreground mb-4">Informacion del Empleado</h3>
                            <div className="space-y-3">
                                <div>
                                    <p className="text-sm font-medium text-default-500">Nombre</p>
                                    <p className="text-foreground">{employeeName}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-default-500">Identificacion</p>
                                    <p className="text-foreground">{payrollHistory.identification_number}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-default-500">ID Seguridad Social</p>
                                    <p className="text-foreground">{payrollHistory.security_id}</p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h3 className="text-lg font-semibold text-foreground mb-4">Periodo</h3>
                            <div className="space-y-3">
                                <div>
                                    <p className="text-sm font-medium text-default-500">Fecha de Inicio</p>
                                    <p className="text-foreground">{formatDate(payrollHistory.init_date)}</p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-default-500">Fecha de Fin</p>
                                    <p className="text-foreground">{formatDate(payrollHistory.end_date)}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-default-50 border border-divider p-4 md:p-6 rounded-xl">
                        <h3 className="text-lg font-semibold text-foreground mb-4">Valores</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-default-500">Valor de works:</span>
                                <span className="font-medium text-foreground">{formatMoney(createMoney(payrollHistory.works_value_amount))}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-default-500">Mano de obra:</span>
                                <span className="font-medium text-foreground">{formatMoney(createMoney(0, 'COP'))}</span>
                            </div>
                            <div className="flex justify-between border-t border-divider pt-3">
                                <span className="text-foreground font-semibold">Total:</span>
                                <span className="font-bold text-xl text-success-600">
                                    {formatMoney(createMoney(totalAmount))}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col-reverse sm:flex-row justify-end gap-3 mt-6">
                        {onEdit && (
                            <button
                                onClick={onEdit}
                                className="px-4 py-2 text-primary bg-primary/10 rounded-xl hover:bg-primary/20 transition-colors font-medium"
                            >
                                Edit
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-default-600 bg-default-100 rounded-xl hover:bg-default-200 transition-colors font-medium"
                        >
                            Cerrar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};