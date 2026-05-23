import { Table, Hammer, Box, Droplets, Ruler } from "lucide-react";

export const STRATEGY_ICONS: Record<string, any> = {
  SHEET: Table,
  PROFILE: Hammer,
  LABOR: Hammer,
  SOLID: Box,
  LIQUID: Droplets,
  LINEAR: Ruler,
  UNIT: Box,
};

export const DEFAULT_ICON = Ruler;
