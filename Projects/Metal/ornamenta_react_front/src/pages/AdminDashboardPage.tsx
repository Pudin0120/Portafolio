import React, { useEffect, useState, useCallback, useMemo } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Users, User as UserIcon, Palette } from "lucide-react";
import {
  Button,
  Card,
  Input,
  Select,
  SelectItem,
  Spinner,
} from "@heroui/react";
import { useAuth } from "@hooks/useAuth";
import { UserService, type UserProfile } from "@services/userService";
import { getErrorMessage } from "@utils/errorHandling";
import type { IUserData } from "@shared/user";
import {
  validateEmail,
  validatePhone,
  validateRequiredFields,
  validateDocumentByType,
} from "@utils/validation";
import { ProfilePage } from "@pages/ProfilePage";
import { ColorSettings } from "@components/settings/ColorSettings";
import { DashboardLayout } from "@components/DashboardLayout";
import type { MenuItem } from "@components/SidebarMenu";
import type { BreadcrumbItem } from "@components/Breadcrumbs";

interface GerenteFormData {
  identification_number: string;
  document_type: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  password: string;
}

export const AdminDashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const activeTab = useMemo(() => {
    const pathname = location.pathname;
    if (pathname.includes("/about")) return "about";
    if (pathname.includes("/branding")) return "branding";
    return "gerentes";
  }, [location.pathname]);

  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [profileError, setProfileError] = useState("");

  const [formData, setFormData] = useState<GerenteFormData>({
    identification_number: "",
    document_type: "CC",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    password: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formMessage, setFormMessage] = useState("");
  const [formError, setFormError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const fetchUserProfile = useCallback(async () => {
    if (!user) return;
    try {
      const profileData = await UserService.getUserProfile();
      setUserProfile(profileData);
    } catch (err) {
      setProfileError("Error al cargar el perfil: " + getErrorMessage(err));
    } finally {
      setIsLoadingProfile(false);
    }
  }, [user]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchUserProfile();
  }, [fetchUserProfile]);

  const handleTabChange = (tab: string) => {
    switch (tab) {
      case "about":
        navigate("/about");
        break;
      case "branding":
        navigate("/branding");
        break;
      case "gerentes":
      default:
        navigate("/");
        break;
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (error) {
      console.error("Error al cerrar sesion:", error);
    }
  };

  const menuItems = useMemo(
    (): MenuItem[] => [
      {
        key: "gerentes",
        label: "Creation de Gerentes",
        icon: <Users className="w-5 h-5" />,
        active: activeTab === "gerentes",
      },
      {
        key: "branding",
        label: "Branding & Tema",
        icon: <Palette className="w-5 h-5" />,
        active: activeTab === "branding",
      },
      {
        key: "about",
        label: "Mi Perfil",
        icon: <UserIcon className="w-5 h-5" />,
        active: activeTab === "about",
      },
    ],
    [activeTab],
  );

  const breadcrumbItems = useMemo((): BreadcrumbItem[] => {
    const breadcrumbs: BreadcrumbItem[] = [
      { label: "Inicio", key: "home", active: false },
    ];
    if (activeTab === "gerentes") {
      breadcrumbs.push({
        label: "Gestion de Gerentes",
        key: "gerentes",
        active: true,
      });
    } else if (activeTab === "branding") {
      breadcrumbs.push({
        label: "Branding",
        key: "branding",
        active: true,
      });
    } else if (activeTab === "about") {
      breadcrumbs.push({ label: "Mi Perfil", key: "about", active: true });
    }
    return breadcrumbs;
  }, [activeTab]);

  const handleInputChange = (field: keyof GerenteFormData, value: string) => {
    let newValue = value;
    let error = "";

    switch (field) {
      case "identification_number":
        if (formData.document_type === "NI") {
          newValue = newValue.replace(/[^a-zA-Z0-9-]/g, "").slice(0, 12);
          if (!/^[a-zA-Z0-9-]*$/.test(newValue))
            error = "Solo se permiten letras, numbers y '-'.";
        } else {
          newValue = newValue.replace(/\D/g, "").slice(0, 12);
          if (!/^\d*$/.test(newValue)) error = "Solo se permiten numbers.";
        }
        break;
      case "phone":
        newValue = newValue.replace(/(?!^\+)\D/g, "").slice(0, 15);
        if (!/^\+?\d*$/.test(newValue)) {
          error = "Solo se permiten numbers y el prefijo '+' al inicio.";
        }
        if (newValue.startsWith("+") && !/^\+\d{0,12}$/.test(newValue)) {
          error = "Formato de telefono invalid.";
        }
        break;
      case "first_name":
      case "last_name":
        newValue = newValue
          .replace(/[^a-zA-ZaeiouAEIOUnN\s]/g, "")
          .slice(0, 50);
        if (!/^[a-zA-ZaeiouAEIOUnN\s]*$/.test(newValue))
          error = "Solo se permiten letras.";
        break;
      case "email":
        newValue = newValue.slice(0, 100);
        if (newValue && !validateEmail(newValue)) error = "Invalid email.";
        break;
      case "password":
        if (newValue.length < 6) error = "Minimo 6 caracteres.";
        break;
    }

    setFieldErrors((prev) => ({ ...prev, [field]: error }));
    setFormData((prev) => ({ ...prev, [field]: newValue }));
  };

  const resetForm = () => {
    setFormData({
      identification_number: "",
      document_type: "CC",
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      password: "",
    });
    setFormMessage("");
    setFormError("");
    setFieldErrors({});
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormMessage("");
    setFormError("");

    if (!user) {
      setFormError("Debes estar autenticado para create gerentes.");
      return;
    }

    const requiredFields = [
      "identification_number",
      "document_type",
      "first_name",
      "last_name",
      "email",
      "password",
    ];
    const validationError = validateRequiredFields(formData, requiredFields);
    if (validationError) {
      setFormError(validationError);
      return;
    }

    const docValidation = validateDocumentByType(
      formData.document_type,
      formData.identification_number.trim(),
    );
    if (!docValidation.valid) {
      setFormError(docValidation.error || "Number de document invalid.");
      return;
    }

    if (!validateEmail(formData.email.trim())) {
      setFormError("Please ingrese un email valid.");
      return;
    }

    if (formData.phone && !validatePhone(formData.phone.trim())) {
      setFormError("El number de telefono no es valid.");
      return;
    }

    if (formData.password.length < 6) {
      setFormError("La password debe tener al menos 6 caracteres.");
      return;
    }

    setIsSubmitting(true);
    try {
      const userData: IUserData = {
        ...formData,
        state: "A",
        firebase_uid: "",
        role: "MANAGER",
      };
      await UserService.createUserWithFirebase(userData);
      setFormMessage(
        `Gerente ${formData.first_name} ${formData.last_name} creado exitosamente.`,
      );
      setTimeout(() => resetForm(), 2500);
    } catch (err) {
      setFormError("Error al create el gerente: " + getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingProfile)
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner color="primary" size="lg" />
      </div>
    );

  if (profileError)
    return <div className="text-red-500 text-center mt-10">{profileError}</div>;

  const renderContent = () => {
    switch (activeTab) {
      case "gerentes":
        return (
          <div className="flex flex-col items-center min-h-screen bg-background p-6">
            <div className="w-full max-w-md">
              <h2 className="text-3xl font-bold text-foreground mb-2">
                Create Manager
              </h2>
              <p className="text-default-500 text-sm mt-4 leading-relaxed">
                Completa la information para registrar un nuevo gerente.
              </p>
            </div>

            <Card className="mt-6 w-full max-w-md p-6 rounded-2xl shadow-lg bg-content1">
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <Select
                  label="Document Type"
                  selectedKeys={[formData.document_type]}
                  onChange={(e: { target: { value: string } }) =>
                    handleInputChange("document_type", e.target.value)
                  }
                  disabled={isSubmitting}
                >
                  <SelectItem key="CC" textValue="Cedula de Ciudadania">
                    Cedula de Ciudadania
                  </SelectItem>
                  <SelectItem key="CE" textValue="Cedula de Extranjeria">
                    Cedula de Extranjeria
                  </SelectItem>
                  <SelectItem key="NI" textValue="NIT">
                    NIT
                  </SelectItem>
                </Select>

                <div>
                  <Input
                    label="Number de Identificacion"
                    value={formData.identification_number}
                    onChange={(e: { target: { value: string } }) =>
                      handleInputChange("identification_number", e.target.value)
                    }
                    disabled={isSubmitting}
                    required
                  />
                  {fieldErrors.identification_number && (
                    <p className="text-danger text-xs mt-1">
                      {fieldErrors.identification_number}
                    </p>
                  )}
                </div>

                <div>
                  <Input
                    label="Nombre"
                    value={formData.first_name}
                    onChange={(e: { target: { value: string } }) =>
                      handleInputChange("first_name", e.target.value)
                    }
                    disabled={isSubmitting}
                    required
                  />
                  {fieldErrors.first_name && (
                    <p className="text-danger text-xs mt-1">
                      {fieldErrors.first_name}
                    </p>
                  )}
                </div>

                <div>
                  <Input
                    label="Apellido"
                    value={formData.last_name}
                    onChange={(e: { target: { value: string } }) =>
                      handleInputChange("last_name", e.target.value)
                    }
                    disabled={isSubmitting}
                    required
                  />
                  {fieldErrors.last_name && (
                    <p className="text-danger text-xs mt-1">
                      {fieldErrors.last_name}
                    </p>
                  )}
                </div>

                <div>
                  <Input
                    label="Email"
                    type="email"
                    value={formData.email}
                    onChange={(e: { target: { value: string } }) =>
                      handleInputChange("email", e.target.value)
                    }
                    disabled={isSubmitting}
                    required
                  />
                  {fieldErrors.email && (
                    <p className="text-danger text-xs mt-1">
                      {fieldErrors.email}
                    </p>
                  )}
                </div>

                <div>
                  <Input
                    label="Telefono"
                    type="tel"
                    value={formData.phone}
                    onChange={(e: { target: { value: string } }) =>
                      handleInputChange("phone", e.target.value)
                    }
                    disabled={isSubmitting}
                  />
                  {fieldErrors.phone && (
                    <p className="text-danger text-xs mt-1">
                      {fieldErrors.phone}
                    </p>
                  )}
                </div>

                <div>
                  <Input
                    label="Password"
                    type="password"
                    value={formData.password}
                    onChange={(e: { target: { value: string } }) =>
                      handleInputChange("password", e.target.value)
                    }
                    disabled={isSubmitting}
                    required
                  />
                  {fieldErrors.password && (
                    <p className="text-danger text-xs mt-1">
                      {fieldErrors.password}
                    </p>
                  )}
                </div>

                <div className="text-sm bg-primary/10 border border-primary/20 rounded-xl p-3 text-primary text-center font-medium">
                  Rol asignado: <strong>Gerente</strong>
                </div>

                {formMessage && (
                  <div className="bg-success-100 text-success-800 p-3 rounded-xl text-center font-semibold">
                    {formMessage}
                  </div>
                )}
                {formError && (
                  <div className="bg-danger-100 text-danger-800 p-3 rounded-xl text-center font-semibold">
                    {formError}
                  </div>
                )}

                <Button
                  color="primary"
                  variant="solid"
                  type="submit"
                  isDisabled={isSubmitting}
                  className="rounded-xl font-semibold text-lg mt-2 text-primary-foreground"
                >
                  {isSubmitting ? "Creating..." : "Create Manager"}
                </Button>
              </form>
            </Card>
          </div>
        );
      case "branding":
        return (
          <div className="p-6">
            <ColorSettings />
          </div>
        );
      case "about":
        return <ProfilePage />;
      default:
        return null;
    }
  };

  return (
    <DashboardLayout
      menuItems={menuItems}
      breadcrumbItems={breadcrumbItems}
      onMenuItemClick={handleTabChange}
      onLogout={handleLogout}
      userProfile={userProfile}
      userEmail={user?.email || null}
      onMenuToggle={() => {}}
      onMenuStateChange={() => {}}
      onBreadcrumbClick={handleTabChange}
    >
      {renderContent()}
    </DashboardLayout>
  );
};
