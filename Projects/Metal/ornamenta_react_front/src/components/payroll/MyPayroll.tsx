import React, { useState, useEffect, useCallback } from 'react';
import { DollarSign, Calendar, FileText, TrendingUp, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { payrollService } from '@/services/payrollService';
import { useAuth } from '@hooks/useAuth';
import {
  Payroll,
  StatePayroll,
  formatMoney,
  getStateLabel,
  getContractTypeLabel
} from '@/types/payroll';
import { PayrollHistory } from '@/types/payroll_history';
import { ServiceProvisionTasksModal } from './ServiceProvisionTasksModal';

export const MyPayroll: React.FC = () => {
  const { user } = useAuth();
  const [payroll, setPayroll] = useState<Payroll | null>(null);
  const [history, setHistory] = useState<PayrollHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<'overview' | 'history'>('overview');
  const [userIdentification, setUserIdentification] = useState<string | null>(null);
  const [showTasksModal, setShowTasksModal] = useState(false);

  // Obtener el identification_number del user actual
  const fetchUserIdentification = useCallback(async () => {
    if (!user) {
      setError('No hay user autenticado');
      return null;
    }

    try {
      const token = await user.getIdToken();
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        const identification = userData.identification_number || userData.id;
        setUserIdentification(identification);
        return identification;
      } else {
        throw new Error('No se pudo obtener la information del user');
      }
    } catch (err) {
      console.error('Error obteniendo identificacion del user:', err);
      setError('Error al obtener la information del user');
      return null;
    }
  }, [user]);

  const loadPayrollData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Obtener el identification_number del user
      let identification = userIdentification;
      if (!identification) {
        identification = await fetchUserIdentification();
        if (!identification) {
          setError('No se pudo obtener tu identificacion de user');
          return;
        }
      }

      console.log('Buscando payroll para identification_number:', identification);

      // Obtener todas las payrolls y filtrar por el user actual
      const allPayrolls = await payrollService.getPayrolls();
      const userPayroll = allPayrolls.find(
        p => p.identification_number === identification
      );

      if (!userPayroll) {
        setError('No se encontro information de payroll para tu user.');
        setIsLoading(false);
        return;
      }

      console.log('Payroll encontrada:', userPayroll);
      setPayroll(userPayroll);

      // Cargar historial usando el payroll_id
      try {
        const historyData = await payrollService.getPayrollHistory(userPayroll.payroll_id);
        console.log('Historial cargado:', historyData);
        setHistory(historyData);
      } catch (histError) {
        console.warn('No se pudo cargar el historial:', histError);
        // No mostrar error si no hay historial, solo dejarlo vacio
        setHistory([]);
      }
    } catch (err) {
      console.error('Error cargando datos de payroll:', err);
      setError(err instanceof Error ? err.message : 'Error al cargar los datos de payroll');
    } finally {
      setIsLoading(false);
    }
  }, [userIdentification, fetchUserIdentification]);

  useEffect(() => {
    loadPayrollData();
  }, [loadPayrollData]);

  const formatDate = (dateString: string, checkToday: boolean = false): string => {
    try {
      const date = new Date(dateString);
      
      // Si se debe verificar si es hoy y la payroll esta activa
      if (checkToday && payroll?.state === StatePayroll.ACTIVE) {
        const today = new Date();
        const isSameDay = 
          date.getFullYear() === today.getFullYear() &&
          date.getMonth() === today.getMonth() &&
          date.getDate() === today.getDate();
        
        if (isSameDay) {
          return 'Hoy';
        }
      }
      
      return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const getStateIcon = (state: StatePayroll) => {
    switch (state) {
      case StatePayroll.ACTIVE:
        return <Clock className="w-5 h-5 text-warning-500" />;
      case StatePayroll.LIQUIDATED:
        return <AlertCircle className="w-5 h-5 text-warning-500" />;
      case StatePayroll.PAID:
        return <CheckCircle className="w-5 h-5 text-success-500" />;
      case StatePayroll.CANCELLED:
        return <AlertCircle className="w-5 h-5 text-danger-500" />;
      default:
        return <Clock className="w-5 h-5 text-default-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded-xl">
        <p className="font-medium">Error</p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    );
  }

  if (!payroll) {
    return (
      <div className="bg-warning-50 border border-warning-200 text-warning-700 px-4 py-3 rounded-xl">
        <p className="font-medium">Sin information</p>
        <p className="text-sm mt-1">No se encontro information de payroll para tu user.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Tabs de navegacion */}
      <div className="border-b border-divider">
        <nav className="-mb-px flex gap-1">
          <button
            onClick={() => setActiveSection('overview')}
            className={`py-3 px-4 border-b-2 font-medium text-sm transition-colors ${
              activeSection === 'overview'
                ? 'border-primary text-primary'
                : 'border-transparent text-default-500 hover:text-default-700 hover:border-default-300'
            }`}
          >
            Resumen
          </button>
          <button
            onClick={() => setActiveSection('history')}
            className={`py-3 px-4 border-b-2 font-medium text-sm transition-colors ${
              activeSection === 'history'
                ? 'border-primary text-primary'
                : 'border-transparent text-default-500 hover:text-default-700 hover:border-default-300'
            }`}
          >
            Historial
          </button>
        </nav>
      </div>

      {activeSection === 'overview' && (
        <div className="space-y-4 md:space-y-6">
          {/* Informacion General */}
          <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6">
            <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">Informacion General</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  {getStateIcon(payroll.state)}
                  <p className="text-sm text-default-500">Estado</p>
                </div>
                <p className="font-semibold text-foreground text-lg">{getStateLabel(payroll.state)}</p>
              </div>
              
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-5 h-5 text-default-400" />
                  <p className="text-sm text-default-500">Tipo de Contract</p>
                </div>
                <p className="font-semibold text-foreground text-lg">{getContractTypeLabel(payroll.contract_type)}</p>
              </div>
            </div>
          </div>

          {/* Informacion Salarial */}
          <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6">
            <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">Informacion Salarial</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-4 border-b border-divider">
                <div>
                  <p className="text-sm text-default-500">Salario Base</p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    {payroll.base_salary_formatted || formatMoney(payroll.base_salary)}
                  </p>
                </div>
                <div className="p-2 bg-primary/10 rounded-xl">
                  <DollarSign className="w-7 h-7 text-primary" />
                </div>
              </div>

              {payroll.current_period_salary !== undefined && (
                <>
                  <div className="flex justify-between items-center pb-4 border-b border-divider">
                    <div>
                      <p className="text-sm text-default-500">Salario Periodo Actual</p>
                      <p className="text-xl md:text-2xl font-bold text-success-600">
                        {payroll.current_period_salary_formatted || 
                         formatMoney({ amount: payroll.current_period_salary, currency: 'COP' })}
                      </p>
                    </div>
                    <div className="p-2 bg-success-50 rounded-xl">
                      <TrendingUp className="w-7 h-7 text-success-500" />
                    </div>
                  </div>

                  {payroll.current_period_start_date && (
                    <div className="flex justify-between items-center">
                      <div className="flex-1">
                        <p className="text-sm text-default-500 mb-2">Periodo Actual</p>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-5 h-5 text-default-400" />
                          <p className="font-medium text-foreground">
                            {formatDate(payroll.current_period_start_date)} - {' '}
                            {payroll.current_period_end_date 
                              ? formatDate(payroll.current_period_end_date, true)
                              : 'Presente'}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Boton para ver detalle de tasks */}
              {payroll.is_service_provision && (
                <div className="pt-3 border-t border-divider">
                  <button
                    onClick={() => setShowTasksModal(true)}
                    className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity font-semibold shadow-md flex items-center justify-center gap-2"
                  >
                    <FileText className="w-5 h-5" />
                    Ver Detalle de Tasks Realizadas
                  </button>
                  <p className="text-xs text-default-400 text-center mt-2">
                    Consulta las tasks que justifican tu pago
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeSection === 'history' && (
        <div className="bg-content1 border border-divider rounded-xl shadow-sm p-4 md:p-6">
          <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">Historial de Pagos</h3>
          {history.length === 0 ? (
            <p className="text-default-400 text-center py-8">
              No hay historial de pagos disponible
            </p>
          ) : (
            <div className="space-y-3">
              {history.map((item, index) => (
                <div key={`${item.init_date}-${index}`} className="border-l-4 border-primary pl-4 py-2">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="font-medium text-foreground">
                        {formatDate(item.init_date)} - {formatDate(item.end_date)}
                      </p>
                      <p className="text-sm text-default-500 mt-1">
                        Valor: {formatMoney({ amount: item.works_value_amount, currency: 'COP' })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Modal de tasks de prestacion de servicios */}
      {showTasksModal && payroll && (
        <ServiceProvisionTasksModal
          payroll={payroll}
          isOpen={showTasksModal}
          onClose={() => setShowTasksModal(false)}
        />
      )}
    </div>
  );
};
