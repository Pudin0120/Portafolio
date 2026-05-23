import React, { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  Calendar,
  CheckCircle,
  Clock,
  DollarSign,
  FileText,
  Landmark,
  TrendingUp,
} from "lucide-react";
import { payrollService } from "../services/payrollService";
import { useAuth } from "@hooks/useAuth";
import { ContractType, Payroll, StatePayroll } from "../types/payroll";
import { PayrollHistory } from "@/types/payroll_history";

interface Money {
  amount: number;
  currency: string;
}

interface CurrentUserResponse {
  identification_number?: string;
  id?: string;
}

interface OverviewCardProps {
  title: string;
  description: string;
  value: React.ReactNode;
  icon: React.ReactNode;
  iconClassName: string;
}

const OverviewCard: React.FC<OverviewCardProps> = ({
  title,
  description,
  value,
  icon,
  iconClassName,
}) => (
  <article className="rounded-3xl border border-divider bg-content1 p-4 shadow-sm transition-shadow hover:shadow-md md:p-6">
    <div className="mb-4 flex items-center gap-3">
      <div className={`rounded-2xl p-3 ${iconClassName}`}>{icon}</div>
      <div className="min-w-0">
        <h3 className="text-base font-semibold text-foreground md:text-lg">
          {title}
        </h3>
        <p className="text-sm text-default-500">{description}</p>
      </div>
    </div>
    <div className="min-w-0 break-words">{value}</div>
  </article>
);

const EmployeePayrollPage: React.FC = () => {
  const { user } = useAuth();
  const [payroll, setPayroll] = useState<Payroll | null>(null);
  const [history, setHistory] = useState<PayrollHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<"overview" | "history">(
    "overview",
  );
  const [userIdentification, setUserIdentification] = useState<string | null>(
    null,
  );

  const fetchUserIdentification = useCallback(async (): Promise<string | null> => {
    if (!user) {
      setError("No hay user autenticado.");
      return null;
    }

    try {
      const token = await user.getIdToken();
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("No se pudo obtener la information del user.");
      }

      const userData = (await response.json()) as CurrentUserResponse;
      const identification = userData.identification_number ?? userData.id;

      if (!identification) {
        throw new Error("Tu user no tiene una identificacion asociada.");
      }

      setUserIdentification(identification);
      return identification;
    } catch {
      setError("Error al obtener la information del user.");
      return null;
    }
  }, [user]);

  const loadPayrollData = useCallback(async () => {
    if (!user) {
      setError("Debes iniciar sesion para ver tu payroll.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const identification =
        userIdentification ?? (await fetchUserIdentification());

      if (!identification) {
        setPayroll(null);
        setHistory([]);
        return;
      }

      const allPayrolls = await payrollService.getPayrolls();
      const userPayroll = allPayrolls.find(
        (item) => item.identification_number === identification,
      );

      if (!userPayroll) {
        setPayroll(null);
        setHistory([]);
        setError("No se encontro information de payroll para tu user.");
        return;
      }

      setPayroll(userPayroll);

      try {
        const historyData = await payrollService.getPayrollHistory(
          userPayroll.payroll_id,
        );
        setHistory(historyData);
      } catch {
        setHistory([]);
      }
    } catch (err: unknown) {
      setPayroll(null);
      setHistory([]);
      setError(
        err instanceof Error
          ? err.message
          : "Error al cargar la information de payroll. Intenta nuevamente.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [fetchUserIdentification, user, userIdentification]);

  useEffect(() => {
    void loadPayrollData();
  }, [loadPayrollData]);

  const formatMoney = (money: Money): string =>
    new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: money.currency,
    }).format(money.amount);

  const formatDate = (dateString: string): string =>
    new Date(dateString).toLocaleDateString("es-CO", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });

  const getStateInfo = (state: StatePayroll) => {
    const states = {
      [StatePayroll.ACTIVE]: {
        label: "Activa",
        colorClassName:
          "bg-success-50 text-success-700 ring-1 ring-success-200/80",
        icon: <CheckCircle className="h-4 w-4" />,
      },
      [StatePayroll.CANCELLED]: {
        label: "Cancelada",
        colorClassName:
          "bg-danger-50 text-danger-700 ring-1 ring-danger-200/80",
        icon: <Clock className="h-4 w-4" />,
      },
      [StatePayroll.LIQUIDATED]: {
        label: "Liquidada",
        colorClassName:
          "bg-secondary-50 text-secondary-700 ring-1 ring-secondary-200/80",
        icon: <FileText className="h-4 w-4" />,
      },
      [StatePayroll.PAID]: {
        label: "Pagada",
        colorClassName:
          "bg-primary-50 text-primary-700 ring-1 ring-primary-200/80",
        icon: <CheckCircle className="h-4 w-4" />,
      },
    };

    return states[state] ?? states[StatePayroll.ACTIVE];
  };

  const getContractTypeLabel = (type: ContractType): string => {
    const types = {
      [ContractType.FIXED_TERM]: "Termino fijo",
      [ContractType.INDEFINITE_TERM]: "Termino indefinido",
      [ContractType.SERVICE_PROVISION]: "Prestacion de servicios",
    };

    return types[type] ?? "No especificado";
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-6xl p-4 md:p-6">
        <div className="flex min-h-[40dvh] flex-col items-center justify-center rounded-3xl border border-divider bg-content1 px-6 py-12 text-center shadow-sm">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
          <p className="text-lg font-semibold text-foreground">
            Cargando information de payroll...
          </p>
          <p className="mt-2 max-w-md text-sm text-default-500">
            Estamos preparando tu resumen salarial e historial de cambios.
          </p>
        </div>
      </div>
    );
  }

  if (error || !payroll) {
    return (
      <div className="mx-auto max-w-6xl p-4 md:p-6">
        <div className="overflow-hidden rounded-3xl border border-danger-200 bg-content1 shadow-sm">
          <div className="bg-gradient-to-r from-danger-500 to-danger-600 px-5 py-4 text-white md:px-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-6 w-6" />
              <h2 className="text-lg font-bold md:text-xl">
                No pudimos cargar tu payroll
              </h2>
            </div>
          </div>
          <div className="space-y-5 p-5 md:p-6">
            <p className="text-sm text-danger-700 md:text-base">
              {error ?? "No se pudo cargar la information."}
            </p>
            <button
              type="button"
              onClick={() => {
                void loadPayrollData();
              }}
              className="inline-flex w-full items-center justify-center rounded-2xl bg-danger px-5 py-3 text-sm font-semibold text-danger-foreground transition-opacity hover:opacity-90 sm:w-auto"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  const stateInfo = getStateInfo(payroll.state);
  const lastUpdateDate =
    payroll.current_period_end_date ??
    payroll.current_period_start_date ??
    payroll.end_date ??
    payroll.start_date;

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:space-y-8 md:p-6">
      <section className="overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 p-5 text-white shadow-2xl md:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex min-w-0 items-start gap-4">
            <div className="rounded-3xl bg-white/15 p-3 shadow-lg ring-1 ring-white/15 backdrop-blur md:p-4">
              <DollarSign className="h-8 w-8 md:h-10 md:w-10" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-white/70">
                Portal de empleado
              </p>
              <h1 className="mt-2 text-3xl font-black tracking-tight md:text-4xl">
                My Payroll
              </h1>
              <p className="mt-2 max-w-2xl text-sm text-white/80 md:text-base">
                Consulta tu salario, el estado de tu contract y el historial
                asociado a tu payroll desde un solo lugar.
              </p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:max-w-sm lg:flex-1">
            <div className="rounded-2xl bg-white/10 p-4 ring-1 ring-white/15 backdrop-blur">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-white/65">
                Estado
              </p>
              <div
                className={`mt-2 inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-semibold ${stateInfo.colorClassName}`}
              >
                {stateInfo.icon}
                {stateInfo.label}
              </div>
            </div>
            <div className="rounded-2xl bg-white/10 p-4 ring-1 ring-white/15 backdrop-blur">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-white/65">
                Contract
              </p>
              <p className="mt-2 text-sm font-semibold text-white">
                {getContractTypeLabel(payroll.contract_type)}
              </p>
            </div>
          </div>
        </div>
      </section>

      <div className="overflow-x-auto">
        <div className="inline-flex min-w-full gap-2 rounded-2xl border border-divider bg-content1 p-2 shadow-sm">
          <button
            type="button"
            onClick={() => setActiveSection("overview")}
            className={`inline-flex flex-1 items-center justify-center gap-2 whitespace-nowrap rounded-xl px-4 py-3 text-sm font-semibold transition-all ${
              activeSection === "overview"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-default-500 hover:bg-default-100 hover:text-foreground"
            }`}
          >
            <FileText className="h-4 w-4" />
            Informacion general
          </button>
          <button
            type="button"
            onClick={() => setActiveSection("history")}
            className={`inline-flex flex-1 items-center justify-center gap-2 whitespace-nowrap rounded-xl px-4 py-3 text-sm font-semibold transition-all ${
              activeSection === "history"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-default-500 hover:bg-default-100 hover:text-foreground"
            }`}
          >
            <TrendingUp className="h-4 w-4" />
            Historial ({history.length})
          </button>
        </div>
      </div>

      {activeSection === "overview" ? (
        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          <OverviewCard
            title="Salario base"
            description="Salario mensual bruto"
            icon={<DollarSign className="h-6 w-6 text-success-600" />}
            iconClassName="bg-success-50"
            value={
              <>
                <p className="text-3xl font-black tracking-tight text-foreground md:text-4xl">
                  {payroll.base_salary_formatted ?? formatMoney(payroll.base_salary)}
                </p>
                <p className="mt-2 text-sm text-default-500">
                  Valor configurado en tu payroll actual.
                </p>
              </>
            }
          />

          {payroll.current_period_salary !== undefined && (
            <OverviewCard
              title="Periodo actual"
              description="Monto correspondiente al periodo vigente"
              icon={<TrendingUp className="h-6 w-6 text-primary-600" />}
              iconClassName="bg-primary-50"
              value={
                <>
                  <p className="text-3xl font-black tracking-tight text-foreground md:text-4xl">
                    {payroll.current_period_salary_formatted ??
                      formatMoney({
                        amount: payroll.current_period_salary,
                        currency: "COP",
                      })}
                  </p>
                  {payroll.current_period_start_date && (
                    <p className="mt-2 text-sm text-default-500">
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
                  )}
                </>
              }
            />
          )}

          <OverviewCard
            title="Estado del contract"
            description="Situacion actual de tu vinculo laboral"
            icon={<CheckCircle className="h-6 w-6 text-secondary-600" />}
            iconClassName="bg-secondary-50"
            value={
              <div className="space-y-3">
                <span
                  className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold ${stateInfo.colorClassName}`}
                >
                  {stateInfo.icon}
                  {stateInfo.label}
                </span>
                <p className="text-sm text-default-500">
                  Tipo:{" "}
                  <span className="font-semibold text-foreground">
                    {getContractTypeLabel(payroll.contract_type)}
                  </span>
                </p>
              </div>
            }
          />

          <OverviewCard
            title="Inicio de contract"
            description="Fecha registrada en tu payroll"
            icon={<Calendar className="h-6 w-6 text-warning-600" />}
            iconClassName="bg-warning-50"
            value={
              <>
                <p className="text-2xl font-bold text-foreground md:text-3xl">
                  {formatDate(payroll.start_date)}
                </p>
                <p className="mt-2 text-sm text-default-500">
                  Inicio oficial de tu contract.
                </p>
              </>
            }
          />

          <OverviewCard
            title="Ultima actualizacion"
            description="Ultima fecha de referencia disponible"
            icon={<Clock className="h-6 w-6 text-primary-600" />}
            iconClassName="bg-primary-50"
            value={
              <>
                <p className="text-2xl font-bold text-foreground md:text-3xl">
                  {formatDate(lastUpdateDate)}
                </p>
                <p className="mt-2 text-sm text-default-500">
                  Tomada del periodo actual o de las fechas del contract.
                </p>
              </>
            }
          />

          <OverviewCard
            title="Identificacion"
            description="Document associated with payroll"
            icon={<Landmark className="h-6 w-6 text-secondary-600" />}
            iconClassName="bg-secondary-50"
            value={
              <>
                <p className="text-2xl font-bold text-foreground md:text-3xl">
                  {payroll.identification_number}
                </p>
                <p className="mt-2 text-sm text-default-500">
                  Se usa para vincular tu information laboral.
                </p>
              </>
            }
          />
        </section>
      ) : (
        <section className="rounded-3xl border border-divider bg-content1 p-4 shadow-sm md:p-6">
          <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-bold text-foreground md:text-2xl">
                Historial de cambios
              </h2>
              <p className="text-sm text-default-500">
                Periodos liquidados o registrados para esta payroll.
              </p>
            </div>
            <span className="inline-flex w-fit items-center rounded-full bg-default-100 px-3 py-1 text-xs font-semibold text-default-600">
              {history.length} registro(s)
            </span>
          </div>

          {history.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-divider bg-default-50 px-6 py-12 text-center">
              <FileText className="mx-auto mb-4 h-14 w-14 text-default-300" />
              <p className="text-base font-semibold text-foreground">
                Aun no hay cambios registrados
              </p>
              <p className="mt-2 text-sm text-default-500">
                Cuando exista historial para tu payroll, aparecera aqui.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((item) => (
                <article
                  key={item.history_id ?? `${item.payroll_id}-${item.init_date}`}
                  className="rounded-2xl border border-divider bg-default-50/60 p-4 transition-shadow hover:shadow-sm md:p-5"
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0 space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-primary-50 p-2 text-primary-600">
                          <TrendingUp className="h-5 w-5" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-default-500">
                            Periodo
                          </p>
                          <p className="text-base font-bold text-foreground">
                            {formatDate(item.init_date)} - {formatDate(item.end_date)}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <div className="rounded-xl border border-divider bg-content1 p-3">
                          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-default-400">
                            ID de seguridad
                          </p>
                          <p className="mt-1 break-all text-sm font-medium text-foreground">
                            {item.security_id}
                          </p>
                        </div>
                        <div className="rounded-xl border border-divider bg-content1 p-3">
                          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-default-400">
                            Payroll ID
                          </p>
                          <p className="mt-1 break-all text-sm font-medium text-foreground">
                            {item.payroll_id}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="rounded-2xl bg-success-50 p-4 ring-1 ring-success-200/70 lg:min-w-[220px]">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-success-700">
                        Valor de obras
                      </p>
                      <p className="mt-2 text-2xl font-black text-success-700">
                        {formatMoney({
                          amount: item.works_value_amount,
                          currency: "COP",
                        })}
                      </p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default EmployeePayrollPage;
