import React, { useLayoutEffect, useState } from "react";
import { ThemeContext } from "./theme-context";

const DEFAULT_PRIMARY = "#e67e22";
const DEFAULT_SECONDARY = "#1abc9c";

const clamp = (value: number, min: number, max: number) =>
  Math.min(max, Math.max(min, value));

const normalizeHex = (hex: string) => {
  const sanitized = hex.trim().replace("#", "");
  const expanded =
    sanitized.length === 3
      ? sanitized
          .split("")
          .map((character) => character + character)
          .join("")
      : sanitized;

  return `#${expanded.slice(0, 6).padEnd(6, "0")}`.toLowerCase();
};

const hexToRgb = (hex: string) => {
  const normalizedHex = normalizeHex(hex).slice(1);

  return {
    r: parseInt(normalizedHex.slice(0, 2), 16),
    g: parseInt(normalizedHex.slice(2, 4), 16),
    b: parseInt(normalizedHex.slice(4, 6), 16),
  };
};

const rgbToHex = (r: number, g: number, b: number) =>
  `#${[r, g, b]
    .map((channel) => clamp(Math.round(channel), 0, 255).toString(16).padStart(2, "0"))
    .join("")}`;

const adjustColor = (hex: string, amount: number) => {
  const { r, g, b } = hexToRgb(hex);

  return rgbToHex(r + amount, g + amount, b + amount);
};

const getContrastColor = (hex: string) => {
  const { r, g, b } = hexToRgb(hex);
  const yiq = (r * 299 + g * 587 + b * 114) / 1000;

  return yiq >= 160 ? "#000000" : "#ffffff";
};

const hexToRgbChannels = (hex: string) => {
  const { r, g, b } = hexToRgb(hex);

  return `${r} ${g} ${b}`;
};

const hexToHslChannels = (hex: string) => {
  const { r, g, b } = hexToRgb(hex);
  const red = r / 255;
  const green = g / 255;
  const blue = b / 255;
  const max = Math.max(red, green, blue);
  const min = Math.min(red, green, blue);
  const lightness = (max + min) / 2;
  const delta = max - min;
  let hue = 0;
  let saturation = 0;

  if (delta !== 0) {
    saturation = delta / (1 - Math.abs(2 * lightness - 1));

    switch (max) {
      case red:
        hue = ((green - blue) / delta) % 6;
        break;
      case green:
        hue = (blue - red) / delta + 2;
        break;
      default:
        hue = (red - green) / delta + 4;
        break;
    }
  }

  return `${Math.round((((hue * 60 + 360) % 360) + Number.EPSILON) * 10) / 10} ${
    Math.round((Math.min(saturation * 100, 100) + Number.EPSILON) * 10) / 10
  }% ${Math.round((Math.min(lightness * 100, 100) + Number.EPSILON) * 10) / 10}%`;
};

const getHarmonicSecondary = (hex: string) => {
  const { r, g, b } = hexToRgb(hex);
  const red = r / 255;
  const green = g / 255;
  const blue = b / 255;
  const max = Math.max(red, green, blue);
  const min = Math.min(red, green, blue);
  const lightness = (max + min) / 2;
  let hue = 0;
  let saturation = 0;

  if (max !== min) {
    const delta = max - min;
    saturation = lightness > 0.5 ? delta / (2 - max - min) : delta / (max + min);

    switch (max) {
      case red:
        hue = (green - blue) / delta + (green < blue ? 6 : 0);
        break;
      case green:
        hue = (blue - red) / delta + 2;
        break;
      default:
        hue = (red - green) / delta + 4;
        break;
    }

    hue /= 6;
  }

  const rotatedHue = (hue + 0.08) % 1;
  const hueToRgb = (p: number, q: number, t: number) => {
    let adjusted = t;

    if (adjusted < 0) adjusted += 1;
    if (adjusted > 1) adjusted -= 1;
    if (adjusted < 1 / 6) return p + (q - p) * 6 * adjusted;
    if (adjusted < 1 / 2) return q;
    if (adjusted < 2 / 3) return p + (q - p) * (2 / 3 - adjusted) * 6;

    return p;
  };

  const q =
    lightness < 0.5
      ? lightness * (1 + saturation)
      : lightness + saturation - lightness * saturation;
  const p = 2 * lightness - q;

  return rgbToHex(
    hueToRgb(p, q, rotatedHue + 1 / 3) * 255,
    hueToRgb(p, q, rotatedHue) * 255,
    hueToRgb(p, q, rotatedHue - 1 / 3) * 255,
  );
};

const setColorToken = (
  root: HTMLElement,
  token: string,
  color: string,
  options?: { herouiToken?: string },
) => {
  const normalizedColor = normalizeHex(color);

  root.style.setProperty(`--${token}`, normalizedColor);
  root.style.setProperty(`--${token}-rgb`, hexToRgbChannels(normalizedColor));
  root.style.setProperty(
    `--heroui-${options?.herouiToken ?? token}`,
    hexToHslChannels(normalizedColor),
  );
};

const getSemanticSurfaceTokens = (isDarkMode: boolean) => {
  if (isDarkMode) {
    return {
      background: "#09090b",
      foreground: "#f4f4f5",
      "surface-1": "#111113",
      "surface-2": "#18181b",
      "surface-3": "#232326",
      "surface-4": "#2f2f33",
      "surface-elevated": "#141416",
      "surface-foreground": "#f8fafc",
      "surface-muted": "#a1a1aa",
      "surface-border": "#27272a",
      "surface-hover": "#1f1f23",
      "secondary-surface": "#111113",
      "secondary-surface-muted": "#18181b",
      "secondary-surface-strong": "#232326",
      "secondary-border": "#27272a",
      "table-header": "#1a1a1d",
      "table-row-hover": "#1f1f23",
      "sidebar-background": "#0f0f10",
      "sidebar-border": "#232326",
      "sidebar-foreground": "#ffffff",
      "sidebar-muted": "#d4d4d8",
      "sidebar-hover": "#1a1a1d",
      "field-background": "#111113",
      "field-foreground": "#f4f4f5",
      "field-placeholder": "#71717a",
      "field-border": "#27272a",
    };
  }

  return {
    background: "#fafafa",
    foreground: "#17212b",
    "surface-1": "#ffffff",
    "surface-2": "#f4f7f8",
    "surface-3": "#e9eff1",
    "surface-4": "#d9e4e7",
    "surface-elevated": "#ffffff",
    "surface-foreground": "#17212b",
    "surface-muted": "#52606d",
    "surface-border": "#d8e1eb",
    "surface-hover": "#eef3f5",
    "secondary-surface": "#ffffff",
    "secondary-surface-muted": "#f4f7f8",
    "secondary-surface-strong": "#e9eff1",
    "secondary-border": "#d8e1eb",
    "table-header": "#e9eff1",
    "table-row-hover": "#eef3f5",
    "sidebar-background": "#2c3e50",
    "sidebar-border": "#405468",
    "sidebar-foreground": "#ffffff",
    "sidebar-muted": "#dbe4ed",
    "sidebar-hover": "#34495e",
    "field-background": "#ffffff",
    "field-foreground": "#17212b",
    "field-placeholder": "#64748b",
    "field-border": "#d8e1eb",
  };
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [primaryColor, setPrimaryColor] = useState(
    () => localStorage.getItem("theme-primary-color") || DEFAULT_PRIMARY,
  );
  const [secondaryColor, setSecondaryColor] = useState(
    () => localStorage.getItem("theme-secondary-color") || DEFAULT_SECONDARY,
  );
  const [isDarkMode, setIsDarkMode] = useState(
    () => localStorage.getItem("theme-mode") === "dark",
  );

  useLayoutEffect(() => {
    const root = document.documentElement;
    const body = document.body;

    root.classList.toggle("dark", isDarkMode);
    root.setAttribute("data-theme", isDarkMode ? "dark" : "light");
    root.style.colorScheme = isDarkMode ? "dark" : "light";
    body.classList.remove("dark");
    body.removeAttribute("data-theme");

    const applyPalette = (baseColor: string, prefix: string) => {
      const normalizedBaseColor = normalizeHex(baseColor);
      const palette = {
        50: adjustColor(normalizedBaseColor, 200),
        100: adjustColor(normalizedBaseColor, 150),
        200: adjustColor(normalizedBaseColor, 100),
        300: adjustColor(normalizedBaseColor, 50),
        400: adjustColor(normalizedBaseColor, 25),
        500: normalizedBaseColor,
        600: normalizedBaseColor,
        700: adjustColor(normalizedBaseColor, -30),
        800: adjustColor(normalizedBaseColor, -60),
        900: adjustColor(normalizedBaseColor, -90),
      };
      const contrastColor = getContrastColor(normalizedBaseColor);

      Object.entries(palette).forEach(([shade, color]) => {
        root.style.setProperty(`--${prefix}-${shade}`, color);
        root.style.setProperty(`--${prefix}-${shade}-rgb`, hexToRgbChannels(color));
        root.style.setProperty(`--heroui-${prefix}-${shade}`, hexToHslChannels(color));

        if (prefix === "primary") {
          root.style.setProperty(`--brand-orange-${shade}`, color);
          root.style.setProperty(`--tw-primary-${shade}`, color);
        } else if (prefix === "secondary") {
          root.style.setProperty(`--brand-teal-${shade}`, color);
          root.style.setProperty(`--tw-secondary-${shade}`, color);
        }
      });

      root.style.setProperty(`--${prefix}`, normalizedBaseColor);
      root.style.setProperty(
        `--${prefix}-rgb`,
        hexToRgbChannels(normalizedBaseColor),
      );
      root.style.setProperty(`--heroui-${prefix}`, hexToHslChannels(normalizedBaseColor));
      root.style.setProperty(`--${prefix}-foreground`, contrastColor);
      root.style.setProperty(
        `--${prefix}-foreground-rgb`,
        hexToRgbChannels(contrastColor),
      );
      root.style.setProperty(
        `--heroui-${prefix}-foreground`,
        hexToHslChannels(contrastColor),
      );
    };

    applyPalette(primaryColor, "primary");
    applyPalette(secondaryColor, "secondary");

    const semanticSurfaceTokens = getSemanticSurfaceTokens(isDarkMode);
    Object.entries(semanticSurfaceTokens).forEach(([token, value]) => {
      setColorToken(root, token, value);
    });

    root.style.setProperty("--heroui-focus", hexToHslChannels(primaryColor));
    root.style.setProperty(
      "--heroui-content1",
      hexToHslChannels(semanticSurfaceTokens["surface-1"]),
    );
    root.style.setProperty(
      "--heroui-content1-foreground",
      hexToHslChannels(semanticSurfaceTokens["surface-foreground"]),
    );
    root.style.setProperty(
      "--heroui-content2",
      hexToHslChannels(semanticSurfaceTokens["surface-2"]),
    );
    root.style.setProperty(
      "--heroui-content2-foreground",
      hexToHslChannels(semanticSurfaceTokens["surface-foreground"]),
    );
    root.style.setProperty(
      "--heroui-content3",
      hexToHslChannels(semanticSurfaceTokens["surface-3"]),
    );
    root.style.setProperty(
      "--heroui-content3-foreground",
      hexToHslChannels(semanticSurfaceTokens["surface-foreground"]),
    );
    root.style.setProperty(
      "--heroui-content4",
      hexToHslChannels(semanticSurfaceTokens["surface-4"]),
    );
    root.style.setProperty(
      "--heroui-content4-foreground",
      hexToHslChannels(semanticSurfaceTokens["surface-foreground"]),
    );
    root.style.setProperty(
      "--heroui-background",
      hexToHslChannels(semanticSurfaceTokens.background),
    );
    root.style.setProperty(
      "--heroui-foreground",
      hexToHslChannels(semanticSurfaceTokens.foreground),
    );
    root.style.setProperty(
      "--heroui-divider",
      hexToHslChannels(semanticSurfaceTokens["surface-border"]),
    );
    root.style.setProperty(
      "--heroui-field-background",
      hexToHslChannels(semanticSurfaceTokens["field-background"]),
    );
    root.style.setProperty(
      "--heroui-field-foreground",
      hexToHslChannels(semanticSurfaceTokens["field-foreground"]),
    );
    root.style.setProperty(
      "--heroui-field-placeholder",
      hexToHslChannels(semanticSurfaceTokens["field-placeholder"]),
    );
    root.style.setProperty(
      "--heroui-field-border",
      hexToHslChannels(semanticSurfaceTokens["field-border"]),
    );

    localStorage.setItem("theme-primary-color", normalizeHex(primaryColor));
    localStorage.setItem("theme-secondary-color", normalizeHex(secondaryColor));
    localStorage.setItem("theme-mode", isDarkMode ? "dark" : "light");
  }, [isDarkMode, primaryColor, secondaryColor]);

  const toggleDarkMode = () => setIsDarkMode((previousValue) => !previousValue);

  const updatePrimaryColor = (color: string) => {
    setPrimaryColor(normalizeHex(color));
  };

  const updateSecondaryColor = (color: string) => {
    setSecondaryColor(normalizeHex(color));
  };

  const suggestSecondaryColor = () => {
    setSecondaryColor(getHarmonicSecondary(primaryColor));
  };

  const resetToDefault = () => {
    setPrimaryColor(DEFAULT_PRIMARY);
    setSecondaryColor(DEFAULT_SECONDARY);
    setIsDarkMode(false);
  };

  return (
    <ThemeContext.Provider
      value={{
        colors: { primary: primaryColor, secondary: secondaryColor },
        isDarkMode,
        toggleDarkMode,
        updatePrimaryColor,
        updateSecondaryColor,
        suggestSecondaryColor,
        resetToDefault,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};
