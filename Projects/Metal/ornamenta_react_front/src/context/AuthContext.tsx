import React, { createContext } from "react";
import type { AuthContextType } from "@shared/auth";
import { usePersistentAuth } from "@hooks/usePersistentAuth";


export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const authValue = usePersistentAuth();

  return <AuthContext.Provider value={authValue}>{children}</AuthContext.Provider>;
};
