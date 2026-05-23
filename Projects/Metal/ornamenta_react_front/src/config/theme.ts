/**
 * Configuration de colores y tema de la aplicacion
 * Colores de marca: Naranja oscuro y azul aguamarina/verde agua
 */

// Colores de marca
export const brandColors = {
  // Naranja oscuro (primario)
  orange: {
    50: '#fef9f5',
    100: '#fef0e6',
    200: '#fde0d1',
    300: '#fac9a8',
    400: '#f6a675',
    500: '#f39c12', // Main brand color
    600: '#e67e22', // Darker
    700: '#d35400', // Darkest
    800: '#ba5018',
    900: '#8e3d14',
    DEFAULT: '#f39c12',
    dark: '#e67e22',
    darker: '#d35400',
  },

  // Azul aguamarina/Verde agua (secundario)
  teal: {
    50: '#f0fcfc',
    100: '#ccf7f7',
    200: '#9ff0f0',
    300: '#5de6e6',
    400: '#22d9d9',
    500: '#16a085', // Main brand color
    600: '#1abc9c', // Bright
    700: '#148f77',
    800: '#137863',
    900: '#0f5d4e',
    DEFAULT: '#1abc9c',
    bright: '#16a085',
    dark: '#148f77',
  },
};

// Estados (semaforos) - se mantienen para UX
export const statusColors = {
  success: {
    bg: '#d4edda',
    border: '#c3e6cb',
    text: '#155724',
    icon: '#28a745',
  },
  error: {
    bg: '#f8d7da',
    border: '#f5c6cb',
    text: '#721c24',
    icon: '#dc3545',
  },
  warning: {
    bg: '#fff3cd',
    border: '#ffeaa7',
    text: '#856404',
    icon: '#ffc107',
  },
  info: {
    bg: '#f3e8ff',
    border: '#e9d5ff',
    text: '#6b21a8',
    icon: '#8b5cf6',
  },
};

// Colores de accion para botones
interface ButtonColorConfig {
  bg: string;
  text: string;
  hover: string;
  disabled: string;
  border?: string;
  icon?: string;
  gradient?: string;
}

export const buttonColors = {
  primary: {
    bg: brandColors.orange[600], // #e67e22
    hover: brandColors.orange[700], // #d35400
    text: '#ffffff',
    disabled: brandColors.orange[300],
    gradient: 'linear-gradient(135deg, #e67e22 0%, #d35400 100%)',
  },
  secondary: {
    bg: brandColors.teal[600], // #1abc9c
    hover: brandColors.teal[500], // #16a085
    text: '#ffffff',
    disabled: brandColors.teal[300],
    gradient: 'linear-gradient(135deg, #1abc9c 0%, #16a085 100%)',
  },
  neutral: {
    bg: '#34495e',
    hover: '#2c3e50',
    text: '#ffffff',
    disabled: '#95a5a6',
  },
  success: {
    bg: '#28a745',
    hover: '#218838',
    text: '#ffffff',
    disabled: '#9dd9ac',
    border: statusColors.success.border,
    icon: statusColors.success.icon,
    gradient: 'linear-gradient(135deg, #28a745 0%, #218838 100%)',
  },
  danger: {
    bg: '#dc3545',
    hover: '#c82333',
    text: '#ffffff',
    disabled: '#f1aeb5',
    border: statusColors.error.border,
    icon: statusColors.error.icon,
    gradient: 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)',
  },
  warning: {
    bg: '#ffc107',
    hover: '#e0a800',
    text: '#212529',
    disabled: '#ffe69c',
    border: statusColors.warning.border,
    icon: statusColors.warning.icon,
    gradient: 'linear-gradient(135deg, #ffc107 0%, #e0a800 100%)',
  },
} satisfies Record<string, ButtonColorConfig>;

// Configuration de variantes de botones
export const buttonVariants = {
  solid: (color: keyof typeof buttonColors) => ({
    backgroundColor: buttonColors[color].bg,
    color: buttonColors[color].text,
    border: 'none',
    '&:hover': {
      backgroundColor: buttonColors[color].hover,
    },
    '&:disabled': {
      backgroundColor: buttonColors[color].disabled,
      opacity: 0.5,
      cursor: 'not-allowed',
    },
  }),
  outlined: (color: keyof typeof buttonColors) => ({
    backgroundColor: 'transparent',
    color: buttonColors[color].bg,
    border: `2px solid ${buttonColors[color].bg}`,
    '&:hover': {
      backgroundColor: `${buttonColors[color].bg}15`,
    },
  }),
  flat: (color: keyof typeof buttonColors) => ({
    backgroundColor: `${buttonColors[color].bg}20`,
    color: buttonColors[color].bg,
    border: 'none',
    '&:hover': {
      backgroundColor: `${buttonColors[color].bg}30`,
    },
  }),
};

// Configuration para HeroUI
export const herouiTheme = {
  colors: {
    primary: {
      ...brandColors.orange,
    },
    secondary: {
      ...brandColors.teal,
    },
  },
};

// Utilities para usar en componentes
export const getButtonStyle = (
  variant: 'solid' | 'outlined' | 'flat' = 'solid',
  color: keyof typeof buttonColors = 'primary'
) => {
  return buttonVariants[variant](color);
};

export const getStatusStyle = (status: keyof typeof statusColors) => {
  return statusColors[status];
};
