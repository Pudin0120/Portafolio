import React from "react";
import Logo from "../assets/Logo.png";
import { Shield } from "lucide-react";

export const EmployeeHomePage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-start min-h-[calc(100vh-140px)] bg-background p-4 md:p-6 space-y-12">
      {/* Hero Section similar to Manager but simpler */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-600 to-primary-800 p-8 md:p-12 shadow-2xl w-full max-w-5xl">
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8 text-center md:text-left">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md border border-white/30 text-white text-xs font-bold tracking-wider uppercase">
              <Shield size={14} />
              Portal de Empleados
            </div>
            <h1 className="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
              Bienvenido a <br />
              <span className="text-primary-100">Serviperfiles A&C</span>
            </h1>
            <p className="text-primary-50/80 text-lg md:text-xl max-w-xl font-medium">
              Sistema de gestion integral para servicios de carpinteria
              metalica.
            </p>
          </div>

          <div className="hidden lg:block relative">
            <div className="absolute inset-0 bg-white/10 blur-3xl rounded-full"></div>
            <div className="relative z-10 w-48 h-48 rounded-full bg-white flex items-center justify-center shadow-xl p-4">
              <img
                src={Logo}
                alt="Logo"
                className="w-full h-auto drop-shadow-sm"
              />
            </div>
          </div>
        </div>

        {/* Ornamentos de fondo */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-64 h-64 bg-primary-400/10 rounded-full blur-3xl"></div>
      </section>

      {/* Logo for mobile/tablet if hidden in hero */}
      <div className="lg:hidden flex justify-center">
        <div className="w-40 h-40 md:w-48 md:h-48 rounded-full bg-white flex items-center justify-center shadow-xl p-4 transform hover:scale-105 transition-transform duration-500 ease-in-out">
          <img
            src={Logo}
            alt="Logo de Serviperfiles A & C"
            className="w-full h-auto"
          />
        </div>
      </div>

      {/* Pie de pagina */}
      <p className="text-default-400 text-sm">
        (c) {new Date().getFullYear()} Serviperfiles A & C - Todos los derechos
        reservados
      </p>
    </div>
  );
};

export default EmployeeHomePage;
