import React, { useState } from "react";
import { Eye, EyeOff, XCircle, CheckCircle, Moon, Sun } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@hooks/useAuth";
import { useTheme } from "@hooks/useTheme";
import Logo from "../assets/Logo.png";
import { Button, Input, Card, CardBody } from "@heroui/react";
import "@pages/LoginPage.css";

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [showResetPassword, setShowResetPassword] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const { login, resetPassword } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const navigate = useNavigate();
  const loginInputClassNames = {
    base: "login-auth-input text-foreground",
    label: "font-semibold text-foreground/80",
    inputWrapper:
      "h-12 border border-divider bg-content1/90 shadow-sm transition-colors focus-within:!border-primary focus-within:!ring-0 dark:bg-content2/80",
    innerWrapper: "!shadow-none",
    input:
      "!border-0 !outline-none !shadow-none !ring-0 text-foreground placeholder:text-default-400 focus:!border-0 focus:!outline-none focus:!shadow-none focus:!ring-0 focus-visible:!border-0 focus-visible:!outline-none focus-visible:!shadow-none focus-visible:!ring-0",
  } as const;

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      const normalizedMsg = msg.toLowerCase();

      let friendlyMessage = "Ocurrio un error inesperado. Intenta nuevamente.";

      if (
        normalizedMsg.includes("network") ||
        normalizedMsg.includes("auth/network-request-failed") ||
        normalizedMsg.includes("sin conexion")
      ) {
        friendlyMessage = "Error de conexion. Si ya tenias sesion, podes seguir en modo offline.";
      } else if (normalizedMsg.includes("invalid-email")) {
        friendlyMessage = "El email no es valid.";
      } else if (normalizedMsg.includes("user-not-found")) {
        friendlyMessage = "User not found. Verifica tus datos.";
      } else if (normalizedMsg.includes("wrong-password")) {
        friendlyMessage = "Password incorrecta.";
      } else if (normalizedMsg.includes("too-many-requests")) {
        friendlyMessage =
          "Demasiados intentos fallidos. Espera un momento e intentalo de nuevo.";
      }

      setError(friendlyMessage);
      console.error("Firebase error:", msg);
    }
  };

  const handleResetPassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    if (!email) {
      setError("Please, ingresa tu email");
      return;
    }

    try {
      await resetPassword(email);
      setMessage(
        "Se ha enviado un email para restablecer tu password. Revisa tu bandeja de entrada.",
      );
      setShowResetPassword(false);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      const normalizedMsg = msg.toLowerCase();

      let friendlyMessage =
        "Ocurrio un error al enviar el email. Intenta nuevamente.";

      if (
        normalizedMsg.includes("network") ||
        normalizedMsg.includes("auth/network-request-failed")
      ) {
        friendlyMessage = "Error de conexion. Verifica tu internet.";
      } else if (normalizedMsg.includes("user-not-found")) {
        friendlyMessage = "No existe una cuenta con ese email.";
      } else if (normalizedMsg.includes("invalid-email")) {
        friendlyMessage = "El email no es valid.";
      } else if (normalizedMsg.includes("too-many-requests")) {
        friendlyMessage =
          "Demasiadas solicitudes. Espera unos minutos e intentalo nuevamente.";
      }

      setError(friendlyMessage);
      console.error("Firebase error:", msg);
    }
  };

  return (
    <div className="min-h-screen bg-slate-600 dark:bg-slate-900 flex flex-col items-center justify-center p-5 font-sans text-foreground transition-colors duration-300">
      {/* Theme Toggle Button */}
      <div className="fixed top-5 right-5">
        <Button
          isIconOnly
          variant="flat"
          className="bg-white/10 backdrop-blur-md text-white border border-white/20"
          onPress={toggleDarkMode}
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </Button>
      </div>

      {/* Logo Section */}
      <div className="mb-10 text-center animate-in fade-in zoom-in duration-700">
        <div className="w-[150px] h-[150px] bg-white rounded-full flex items-center justify-center mx-auto mb-5 border-4 border-primary shadow-2xl overflow-hidden transform hover:scale-105 transition-transform">
          <img
            src={Logo}
            alt="Logo Serviperfiles"
            className="w-4/5 h-4/5 object-contain"
          />
        </div>
        <h1 className="text-3xl font-bold text-white mb-1 tracking-wider uppercase">
          SERVIPERFILES
        </h1>
        <p className="text-xl font-bold text-primary tracking-[4px]">A&C</p>
      </div>

      {/* Form Card */}
      <Card className="w-full max-w-[400px] border border-divider bg-content1/95 shadow-2xl backdrop-blur-sm text-foreground">
        <CardBody className="p-10">
          {error && (
            <div className="bg-danger/10 text-danger p-3 rounded-xl mb-5 text-sm flex items-center justify-center gap-2 border border-danger/20 animate-in fade-in slide-in-from-top-2">
              <XCircle className="w-5 h-5" />
              <span className="font-medium">{error}</span>
            </div>
          )}

          {message && (
            <div className="bg-success/10 text-success p-3 rounded-xl mb-5 text-sm flex items-center justify-center gap-2 border border-success/20 animate-in fade-in slide-in-from-top-2">
              <CheckCircle className="w-5 h-5" />
              <span className="font-medium">{message}</span>
            </div>
          )}

          {!showResetPassword ? (
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">
              <Input
                type="email"
                label="User"
                labelPlacement="outside"
                placeholder="Ingresa tu user"
                variant="bordered"
                value={email}
                onValueChange={setEmail}
                isRequired
                disableAnimation={true}
                classNames={loginInputClassNames}
              />

              <Input
                type={showPassword ? "text" : "password"}
                label="Password"
                labelPlacement="outside"
                placeholder="Ingresa tu password"
                variant="bordered"
                value={password}
                onValueChange={setPassword}
                isRequired
                disableAnimation={true}
                classNames={loginInputClassNames}
                endContent={
                  <button
                    className="focus:outline-none focus-visible:outline-none"
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="text-default-400" />
                    ) : (
                      <Eye className="text-default-400" />
                    )}
                  </button>
                }
              />

              <div className="flex flex-col gap-3 mt-2">
                <Button
                  type="submit"
                  color="primary"
                  className="font-bold h-12 text-lg shadow-lg shadow-primary/30"
                >
                  Ingresar
                </Button>

                <button
                  type="button"
                  onClick={() => setShowResetPassword(true)}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium transition-colors p-2"
                >
                  Olvidaste tu password?
                </button>
              </div>
            </form>
          ) : (
            <form
              onSubmit={handleResetPassword}
              className="flex flex-col gap-6"
            >
              <div className="text-center">
                <h3 className="text-xl font-bold text-default-800 mb-2">
                  Restablecer Password
                </h3>
                <p className="text-default-500 text-sm">
                  Ingresa tu email para recibir las instrucciones
                </p>
              </div>

              <Input
                type="email"
                label="Email"
                labelPlacement="outside"
                placeholder="Ingresa tu email"
                variant="bordered"
                value={email}
                onValueChange={setEmail}
                isRequired
                classNames={{
                  label: "font-semibold text-foreground/80",
                  inputWrapper:
                    "h-12 border border-divider bg-content1/90 shadow-sm dark:bg-content2/80",
                  input: "text-foreground placeholder:text-default-400",
                }}
              />

              <div className="flex flex-col gap-3 mt-2">
                <Button
                  type="submit"
                  color="primary"
                  className="font-bold h-12"
                >
                  Enviar instrucciones
                </Button>

                <Button
                  type="button"
                  variant="flat"
                  onPress={() => setShowResetPassword(false)}
                  className="font-semibold"
                >
                  Volver al login
                </Button>
              </div>
            </form>
          )}
        </CardBody>
      </Card>

      {/* Decorative indicator */}
      <div className="fixed bottom-5 left-1/2 -translate-x-1/2 w-10 h-1 bg-white/30 rounded-full" />
    </div>
  );
};
