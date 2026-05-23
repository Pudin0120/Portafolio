import { createContext } from "react";

export interface ThemeColors {
  primary: string;
  secondary: string;
}

export interface ThemeContextType {
  colors: ThemeColors;
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  updatePrimaryColor: (color: string) => void;
  updateSecondaryColor: (color: string) => void;
  suggestSecondaryColor: () => void;
  resetToDefault: () => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(
  undefined,
);
