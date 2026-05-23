// src/hooks/useEmployeeMetadata.ts
import { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/services/apiClient";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import {
  getEmployeeMetadata,
  setEmployeeMetadata,
  clearEmployeeMetadata,
  type Role,
  type DocumentType,
  type EmployeeMetadata,
} from "@/services/indexedDb/employeeMetadataDb";

/**
 * Hook to fetch and cache employee metadata (roles and document types).
 * - When online: fetch from `/employees/metadata`, store in IndexedDB,
 *   and return the fresh data.
 * - When offline: return cached data from IndexedDB if available.
 * - Provides a `refresh` function to force a network reload.
 */
export const useEmployeeMetadata = () => {
  const isOnline = useOnlineStatus();
  const [metadata, setMetadata] = useState<EmployeeMetadata | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const loadMetadata = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      if (isOnline && (!metadata || forceRefresh)) {
        // Fetch from backend
        const fresh = await apiClient.get<EmployeeMetadata>("/employees/metadata");
        await setEmployeeMetadata(fresh);
        setMetadata(fresh);
      } else {
        // Offline or cached fallback
        const cached = await getEmployeeMetadata();
        if (cached) {
          setMetadata(cached);
        } else if (isOnline) {
          // No cache but online - fetch anyway
          const fresh = await apiClient.get<EmployeeMetadata>("/employees/metadata");
          await setEmployeeMetadata(fresh);
          setMetadata(fresh);
        } else {
          // Offline with no cache
          setMetadata(null);
        }
      }
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, [isOnline, metadata]);

  // Initial load
  useEffect(() => {
    loadMetadata();
    // Listen to online status changes to attempt refetch when back online
    if (isOnline) {
      loadMetadata();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOnline]);

  const refresh = useCallback(() => loadMetadata(true), [loadMetadata]);

  return {
    roles: metadata?.roles ?? [],
    documentTypes: metadata?.document_types ?? [],
    loading,
    error,
    refresh,
    clearCache: clearEmployeeMetadata,
  };
};
