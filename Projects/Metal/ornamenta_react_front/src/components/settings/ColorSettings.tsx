import React from "react";
import { Button, Card, CardBody, Switch, Tooltip } from "@heroui/react";
import { Info, Moon, Palette, RefreshCcw, Sparkles, Sun } from "lucide-react";
import { useTheme } from "@hooks/useTheme";

interface ColorSettingsProps {
  title?: string;
  description?: string;
}

interface ColorPreset {
  label: string;
  value: string;
}

const PRIMARY_PRESETS = [
  { label: "Naranja", value: "#e67e22" },
  { label: "Azul", value: "#3b82f6" },
  { label: "Esmeralda", value: "#10b981" },
  { label: "Rosa", value: "#f43f5e" },
] as const satisfies readonly ColorPreset[];

const SECONDARY_PRESETS = [
  { label: "Teal", value: "#1abc9c" },
  { label: "Indigo", value: "#6366f1" },
  { label: "Violeta", value: "#8b5cf6" },
  { label: "Ambar", value: "#f59e0b" },
] as const satisfies readonly ColorPreset[];

export const ColorSettings: React.FC<ColorSettingsProps> = ({
  title = "Personalizacion de Marca",
  description = "Configura la identidad visual de tu plataforma",
}) => {
  const {
    colors,
    isDarkMode,
    toggleDarkMode,
    updatePrimaryColor,
    updateSecondaryColor,
    suggestSecondaryColor,
    resetToDefault,
  } = useTheme();

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 space-y-8 duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">{title}</h2>
          <p className="text-default-500">{description}</p>
        </div>
        <Button
          variant="flat"
          color="danger"
          startContent={<RefreshCcw size={18} />}
          onPress={resetToDefault}
          size="sm"
        >
          Restablecer
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <Card className="border border-surface-border bg-surface-1 shadow-sm">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={`rounded-lg p-2 ${
                    isDarkMode
                      ? "bg-primary/20 text-primary"
                      : "bg-surface-3 text-surface-muted"
                  }`}
                >
                  {isDarkMode ? <Moon size={24} /> : <Sun size={24} />}
                </div>
                <div>
                  <p className="font-semibold">Modo Oscuro</p>
                  <p className="text-xs text-surface-muted">
                    Cambiar apariencia del sistema
                  </p>
                </div>
              </div>
              <Switch
                isSelected={isDarkMode}
                onValueChange={toggleDarkMode}
                color="primary"
                size="lg"
              />
            </div>
          </CardBody>
        </Card>
      </div>

      <Card className="border border-surface-border bg-surface-elevated shadow-md">
        <CardBody className="p-8">
          <div className="space-y-10">
            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Palette className="text-primary" size={20} />
                  <h3 className="text-lg font-semibold">
                    Paleta Institucional
                  </h3>
                  <Tooltip content="Configura los colores que representan la identidad de tu empresa.">
                    <Info size={14} className="cursor-help text-surface-muted" />
                  </Tooltip>
                </div>
                <div className="hidden gap-4 sm:flex">
                  <div className="flex flex-col items-center gap-1">
                    <div
                      className="h-10 w-10 rounded-xl border-2 border-background shadow-md transition-transform hover:scale-105"
                      style={{ backgroundColor: colors.primary }}
                    />
                    <span className="text-[10px] font-bold uppercase text-surface-muted">
                      Primario
                    </span>
                  </div>
                  <div className="flex flex-col items-center gap-1">
                    <div
                      className="h-10 w-10 rounded-xl border-2 border-background shadow-md transition-transform hover:scale-105"
                      style={{ backgroundColor: colors.secondary }}
                    />
                    <span className="text-[10px] font-bold uppercase text-surface-muted">
                      Secundario
                    </span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-8 pt-4 md:grid-cols-2">
                <div className="space-y-4">
                  <p className="text-sm font-medium text-surface-foreground">
                    Color Primario
                  </p>
                  <div className="flex items-center gap-4">
                    <input
                      type="color"
                      value={colors.primary}
                      onChange={(event) => updatePrimaryColor(event.target.value)}
                      aria-label="Seleccionar color primario"
                      className="h-12 w-12 cursor-pointer rounded-lg border-2 border-surface-border bg-surface-2 p-1 transition-all hover:border-primary"
                    />
                    <div className="flex flex-wrap gap-2">
                      {PRIMARY_PRESETS.map((preset) => (
                        <button
                          type="button"
                          key={preset.value}
                          aria-label={`Usar ${preset.label} como color primario`}
                          onClick={() => updatePrimaryColor(preset.value)}
                          className={`h-8 w-8 rounded-full border-2 transition-transform hover:scale-110 ${
                            colors.primary === preset.value
                              ? "border-foreground"
                              : "border-transparent"
                          }`}
                          style={{ backgroundColor: preset.value }}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-surface-foreground">
                      Color Secundario
                    </p>
                    <Button
                      size="sm"
                      variant="light"
                      color="primary"
                      onPress={suggestSecondaryColor}
                      startContent={<Sparkles size={14} />}
                    >
                      Sugerir
                    </Button>
                  </div>
                  <div className="flex items-center gap-4">
                    <input
                      type="color"
                      value={colors.secondary}
                      onChange={(event) =>
                        updateSecondaryColor(event.target.value)
                      }
                      aria-label="Seleccionar color secundario"
                      className="h-12 w-12 cursor-pointer rounded-lg border-2 border-surface-border bg-surface-2 p-1 transition-all hover:border-secondary"
                    />
                    <div className="flex flex-wrap gap-2">
                      {SECONDARY_PRESETS.map((preset) => (
                        <button
                          type="button"
                          key={preset.value}
                          aria-label={`Usar ${preset.label} como color secundario`}
                          onClick={() => updateSecondaryColor(preset.value)}
                          className={`h-8 w-8 rounded-full border-2 transition-transform hover:scale-110 ${
                            colors.secondary === preset.value
                              ? "border-foreground"
                              : "border-transparent"
                          }`}
                          style={{ backgroundColor: preset.value }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </CardBody>
      </Card>

      <div className="flex gap-4 rounded-2xl border border-primary/10 bg-primary/5 p-6">
        <Info className="shrink-0 text-primary" />
        <p className="text-sm text-surface-muted">
          Los cambios se aplican en tiempo real en toda la plataforma. El
          sistema calcula automaticamente las variantes de color y el contraste
          ideal para asegurar la accesibilidad.
        </p>
      </div>
    </div>
  );
};
