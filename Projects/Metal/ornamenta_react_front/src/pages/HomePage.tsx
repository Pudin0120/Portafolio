import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "../assets/Logo.png";
import {
  Package,
  Users,
  DollarSign,
  ClipboardCheck,
  TrendingUp,
  Shield,
  Hammer,
  FileText,
  CheckCircle2,
} from "lucide-react";
import { Card, CardBody, Skeleton } from "@heroui/react";
import { apiClient } from "../services/apiClient";
import { employeeService } from "../services/employeeService";
import { payrollService } from "../services/payrollService";
import { workService } from "../services/workService";
import { taskService } from "../services/taskService";
import { ProductsResponse } from "../types/products";
import { StatePayroll } from "../types/payroll";

interface RecentActivity {
  id: string;
  type:
    | "work_created"
    | "quote_created"
    | "task_assigned"
    | "payroll_created"
    | "payroll_state_changed"
    | "employee_state_changed";
  title: string;
  description: string;
  time: string;
  date: Date;
  icon: React.ReactNode;
  color: string;
}

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  // Estados para datos reales
  const [totalProducts, setTotalProducts] = useState<number | null>(null);
  const [empleadosActives, setEmpleadosActives] = useState<number | null>(null);
  const [nominasActivas, setPayrollsActivas] = useState<number | null>(null);
  const [trabajosPendings, setWorksPendings] = useState<number | null>(
    null,
  );
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  // Estado para actividades recientes
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>(
    [],
  );
  const [isLoadingActivities, setIsLoadingActivities] = useState(true);

  const quickActions = [
    {
      title: "Products",
      description: "Gestiona products y materials del sistema",
      icon: <Package className="w-10 h-10" />,
      iconColor: "text-primary",
      titleColor: "text-primary",
      link: "/products",
    },
    {
      title: "Gestion de Empleados",
      description: "Administra empleados, gerentes y supervisores",
      icon: <Users className="w-10 h-10" />,
      iconColor: "text-secondary",
      titleColor: "text-secondary",
      link: "/employees",
    },
    {
      title: "Payrolls",
      description: "Control de payrolls y pagos",
      icon: <DollarSign className="w-10 h-10" />,
      iconColor: "text-warning",
      titleColor: "text-warning",
      link: "/payrolls",
    },
    {
      title: "Works",
      description: "Gestion de works y proyectos",
      icon: <Hammer className="w-10 h-10" />,
      iconColor: "text-success",
      titleColor: "text-success",
      link: "/works",
    },
  ];

  // Cargar datos reales al montar el componente
  useEffect(() => {
    const loadStats = async () => {
      setIsLoadingStats(true);

      // Cargar total de products
      try {
        const productsData: ProductsResponse =
          await apiClient.get("/products/");
        if (productsData && typeof productsData.total === "number") {
          setTotalProducts(productsData.total);
        }
      } catch (error) {
        console.warn("Error al cargar total de products:", error);
      }

      // Cargar empleados activos
      try {
        const employees = await employeeService.getEmployees();
        const activos = employees.filter(
          (emp) => emp.state === "A" || emp.state === "ACTIVE",
        );
        setEmpleadosActives(activos.length);
      } catch (error) {
        console.warn("Error al cargar empleados activos:", error);
      }

      // Cargar payrolls activas
      try {
        const summary = await payrollService.getPayrollSummary();
        if (
          summary &&
          summary.by_state &&
          summary.by_state[StatePayroll.ACTIVE] !== undefined
        ) {
          setPayrollsActivas(Number(summary.by_state[StatePayroll.ACTIVE]));
        }
      } catch (error) {
        console.warn("Error al cargar payrolls activas:", error);
      }

      // Cargar works pendientes
      try {
        const draftWorks = await workService.getWorksByState("DRAFT");
        setWorksPendings(draftWorks?.works?.length || 0);
      } catch (error) {
        console.warn("Error al cargar works pendientes:", error);
      }

      setIsLoadingStats(false);
    };

    loadStats();
  }, []);

  // Function helper para formatear tiempo relativo
  const formatRelativeTime = useCallback((dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

      if (diffInSeconds < 60) {
        return "Hace unos segundos";
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `Hace ${minutes} ${minutes === 1 ? "minuto" : "minutos"}`;
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `Hace ${hours} ${hours === 1 ? "hora" : "horas"}`;
      } else if (diffInSeconds < 604800) {
        const days = Math.floor(diffInSeconds / 86400);
        return `Hace ${days} ${days === 1 ? "dia" : "dias"}`;
      } else {
        return date.toLocaleDateString("es-CO", {
          day: "numeric",
          month: "short",
        });
      }
    } catch (error) {
      return "Fecha desconocida";
    }
  }, []);

  // Cargar actividades recientes
  useEffect(() => {
    const loadRecentActivities = async () => {
      setIsLoadingActivities(true);
      const activities: RecentActivity[] = [];

      try {
        // 1. Obtener works recientes (creados)
        const allWorks = await workService.getWorks();
        if (allWorks?.works && allWorks.works.length > 0) {
          const recentWorks = allWorks.works.slice(0, 5);
          recentWorks.forEach((work) => {
            activities.push({
              id: `work-${work.work_id}`,
              type: "work_created",
              title: "Work created",
              description:
                work.work_name || `Work #${work.work_id.slice(0, 8)}`,
              time: formatRelativeTime(
                work.start_date || new Date().toISOString(),
              ),
              date: new Date(work.start_date || new Date()),
              icon: <Hammer className="w-5 h-5" />,
              color: "text-primary bg-primary/10",
            });
          });
        }

        // 2. Obtener cotizaciones creadas (works en estado QUOTED)
        const quotedWorks = await workService.getWorksByState("QUOTED");
        if (quotedWorks?.works && quotedWorks.works.length > 0) {
          const recentQuotes = quotedWorks.works.slice(0, 3);
          recentQuotes.forEach((work) => {
            activities.push({
              id: `quote-${work.work_id}`,
              type: "quote_created",
              title: "Quotation created",
              description:
                work.work_name || `Quotation #${work.work_id.slice(0, 8)}`,
              time: formatRelativeTime(
                work.start_date || new Date().toISOString(),
              ),
              date: new Date(work.start_date || new Date()),
              icon: <FileText className="w-5 h-5" />,
              color: "text-secondary bg-secondary/10",
            });
          });
        }

        // 3. Obtener payrolls creadas recientemente
        const allPayrolls = await payrollService.getPayrolls();
        if (allPayrolls && allPayrolls.length > 0) {
          const recentPayrolls = allPayrolls.slice(0, 5);
          recentPayrolls.forEach((payroll) => {
            const employeeName = payroll.identification_number
              ? `Payroll for employee ${payroll.identification_number}`
              : `Payroll #${payroll.payroll_id.slice(0, 8)}`;

            activities.push({
              id: `payroll-created-${payroll.payroll_id}`,
              type: "payroll_created",
              title: "Payroll created",
              description: employeeName,
              time: formatRelativeTime(
                payroll.start_date || new Date().toISOString(),
              ),
              date: new Date(payroll.start_date || new Date()),
              icon: <DollarSign className="w-5 h-5" />,
              color: "text-success bg-success/10",
            });
          });
        }

        // 4. Obtener tasks asignadas desde works en progreso
        const inProgressWorks =
          await workService.getWorksByState("IN_PROGRESS");
        if (inProgressWorks?.works && inProgressWorks.works.length > 0) {
          for (const work of inProgressWorks.works.slice(0, 3)) {
            try {
              const workTasks = await taskService.getTasksByWorkId(
                work.work_id,
              );
              if (workTasks?.tasks && workTasks.tasks.length > 0) {
                workTasks.tasks
                  .filter(
                    (task) =>
                      (task as any).is_assigned ||
                      (task as any).assigned_user_id,
                  )
                  .slice(0, 2)
                  .forEach((task) => {
                    activities.push({
                      id: `task-${task.task_id}`,
                      type: "task_assigned",
                      title: "Task assigned",
                      description:
                        task.task_name || `Task #${task.task_id.slice(0, 8)}`,
                      time: formatRelativeTime(
                        task.created_at ||
                          task.updated_at ||
                          new Date().toISOString(),
                      ),
                      date: new Date(
                        task.created_at || task.updated_at || new Date(),
                      ),
                      icon: <CheckCircle2 className="w-5 h-5" />,
                      color: "text-warning bg-warning/10",
                    });
                  });
              }
            } catch (error) {
              console.warn(
                `Error al cargar tasks del work ${work.work_id}:`,
                error,
              );
            }
          }
        }

        // 5. Obtener payrolls con cambios de estado (usando _domain_events)
        if (allPayrolls && allPayrolls.length > 0) {
          const payrollsWithEvents = allPayrolls
            .filter((p) => p._domain_events && p._domain_events.length > 0)
            .slice(0, 3);

          payrollsWithEvents.forEach((payroll) => {
            const latestEvent =
              payroll._domain_events?.[payroll._domain_events.length - 1];
            if (latestEvent) {
              activities.push({
                id: `payroll-state-${payroll.payroll_id}`,
                type: "payroll_state_changed",
                title: "Estado de payroll cambiado",
                description: `Payroll #${payroll.payroll_id.slice(0, 8)} - Status: ${payroll.state}`,
                time: formatRelativeTime(latestEvent.occurred_at.toString()),
                date: new Date(latestEvent.occurred_at),
                icon: <DollarSign className="w-5 h-5" />,
                color: "text-success bg-success/10",
              });
            }
          });
        }

        activities.sort((a, b) => b.date.getTime() - a.date.getTime());
        setRecentActivities(activities.slice(0, 5));
      } catch (error) {
        console.warn("Error al cargar actividades recientes:", error);
        setRecentActivities([]);
      } finally {
        setIsLoadingActivities(false);
      }
    };

    loadRecentActivities();
  }, [formatRelativeTime]);

  const stats = [
    {
      id: "total-products",
      label: "Total Products",
      value: totalProducts !== null ? totalProducts.toLocaleString() : "0",
      icon: <Package className="w-8 h-8" />,
      change: "+12%",
      trend: "up",
      iconColor: "text-primary",
      valueColor: "text-primary",
      bgColor: "bg-primary/10",
    },
    {
      id: "empleados-activos",
      label: "Empleados Actives",
      value: empleadosActives !== null ? empleadosActives.toString() : "0",
      icon: <Users className="w-8 h-8" />,
      change: "+3",
      trend: "up",
      iconColor: "text-secondary",
      valueColor: "text-secondary",
      bgColor: "bg-secondary/10",
    },
    {
      id: "payrolls-activas",
      label: "Payrolls Activas",
      value: nominasActivas !== null ? nominasActivas.toString() : "0",
      icon: <DollarSign className="w-8 h-8" />,
      change: "+5%",
      trend: "up",
      iconColor: "text-warning",
      valueColor: "text-warning",
      bgColor: "bg-warning/10",
    },
    {
      id: "works-pendientes",
      label: "Works Pendings",
      value: trabajosPendings !== null ? trabajosPendings.toString() : "0",
      icon: <ClipboardCheck className="w-8 h-8" />,
      change: "+2%",
      trend: "up",
      iconColor: "text-success",
      valueColor: "text-success",
      bgColor: "bg-success/10",
    },
  ];

  return (
    <div className="p-4 md:p-6 space-y-8 animate-in fade-in duration-500 min-h-[calc(100vh-140px)] flex flex-col">
      {/* Hero Section - Redisenada sin scrolls y mas compacta */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 to-primary-800 p-8 md:p-12 shadow-2xl flex-shrink-0">
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-4 text-center md:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md border border-white/30 text-white text-xs font-bold tracking-wider uppercase">
              <Shield size={14} />
              Acceso Gerencial
            </div>
            <h1 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
              Sistema de Gestion <br />
              <span className="text-primary-100">Serviperfiles A&C</span>
            </h1>
            <p className="text-primary-50/80 text-lg md:text-xl max-w-xl font-medium">
              Taller de Ornamentacion y Carpinteria Metalica.
            </p>
          </div>

          <div className="hidden lg:block relative">
            <div className="absolute inset-0 bg-white/10 blur-3xl rounded-full"></div>
            <div className="relative z-10 w-48 h-48 rounded-full bg-white flex items-center justify-center shadow-2xl p-3">
              <img src={Logo} alt="Logo" className="w-full h-auto" />
            </div>
          </div>
        </div>

        {/* Ornamentos de fondo controlados para evitar scroll */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-64 h-64 bg-primary-400/10 rounded-full blur-3xl"></div>
      </section>

      {/* Stats Grid - Tarjetas mas "Premium" */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 flex-shrink-0">
        {stats.map((stat) => (
          <Card
            key={stat.id}
            className="border-none bg-content1/50 backdrop-blur-md shadow-sm hover:shadow-xl transition-all duration-400 hover:-translate-y-1"
          >
            <CardBody className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div
                  className={`p-3 rounded-2xl ${stat.bgColor} ${stat.iconColor} shadow-inner`}
                >
                  {stat.icon}
                </div>
                <div className="flex items-center gap-1 text-[10px] font-black px-2 py-1 rounded-lg bg-success/10 text-success uppercase tracking-wider">
                  <TrendingUp size={12} />
                  {stat.change}
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-bold text-default-400 uppercase tracking-widest">
                  {stat.label}
                </p>
                <p
                  className={`text-4xl font-black tracking-tighter ${stat.valueColor}`}
                >
                  {stat.value}
                </p>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-grow">
        {/* Quick Actions - Ocupa 2/3 en desktop */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-black text-foreground uppercase tracking-tighter">
              Accesos Directos
            </h2>
            <div className="h-[2px] flex-1 bg-divider"></div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {quickActions.map((action) => (
              <Card
                key={action.title}
                isPressable
                onPress={() => navigate(action.link)}
                className="group border-none bg-content1 shadow-sm hover:bg-primary hover:text-primary-foreground transition-all duration-300"
              >
                <CardBody className="flex flex-row items-center gap-5 p-5">
                  <div
                    className={`p-3 rounded-xl bg-default-100 group-hover:bg-white/20 transition-colors ${action.iconColor} group-hover:text-white`}
                  >
                    {action.icon}
                  </div>
                  <div>
                    <h3 className="font-bold text-lg leading-none mb-1 group-hover:text-white">
                      {action.title}
                    </h3>
                    <p className="text-xs text-default-500 group-hover:text-white/80 line-clamp-1">
                      {action.description}
                    </p>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        </div>

        {/* Recent Activity - Ocupa 1/3 en desktop */}
        <div className="space-y-6 h-full flex flex-col">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-black text-foreground uppercase tracking-tighter">
              Actividad
            </h2>
            <div className="h-[2px] flex-1 bg-divider"></div>
          </div>

          <Card className="border-none bg-content1 shadow-sm overflow-hidden flex-grow">
            <CardBody className="p-0">
              {isLoadingActivities ? (
                <div className="p-4 space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex gap-3">
                      <Skeleton className="w-10 h-10 rounded-xl" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="w-1/2 h-3 rounded-lg" />
                        <Skeleton className="w-full h-2 rounded-lg" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : recentActivities.length > 0 ? (
                <div className="divide-y divide-divider/50">
                  {recentActivities.map((activity) => (
                    <div
                      key={activity.id}
                      className="flex items-center gap-4 p-4 hover:bg-default-50 transition-colors group cursor-default"
                    >
                      <div
                        className={`p-2 rounded-lg ${activity.color} group-hover:scale-110 transition-transform`}
                      >
                        {activity.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-baseline gap-2">
                          <p className="text-sm font-bold text-foreground truncate uppercase tracking-tight">
                            {activity.title}
                          </p>
                          <span className="text-[10px] font-medium text-default-400 whitespace-nowrap">
                            {activity.time}
                          </span>
                        </div>
                        <p className="text-xs text-default-500 truncate">
                          {activity.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center text-default-400">
                  <p className="text-sm font-medium">
                    Sin movimientos recientes
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Footer info visible sin scroll excesivo */}
      <div className="pt-4 mt-auto border-t border-divider flex justify-center flex-shrink-0">
        <p className="text-default-400 text-sm">
          (c) {new Date().getFullYear()} Serviperfiles A & C - Todos los derechos
          reservados
        </p>
      </div>
    </div>
  );
};

export default HomePage;
