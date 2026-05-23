import { useState, useEffect } from "react";

/**
 * Hook para debounce de valores.
 * Util para evitar requests innecesarios al servidor mientras el user escribe.
 *
 * @param value - Valor a hacer debounce
 * @param delay - Delay en milisegundos (default: 500ms)
 * @returns El valor debounceado
 *
 * @example
 * const [searchQuery, setSearchQuery] = useState("");
 * const debouncedQuery = useDebounce(searchQuery, 500);
 *
 * useEffect(() => {
 *   // Solo se ejecuta 500ms despues de que el user deje de escribir
 *   fetchData(debouncedQuery);
 * }, [debouncedQuery]);
 */
export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Setear un timeout para actualizar el valor debounceado
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Cleanup: cancel el timeout si el valor cambia antes de que se cumpla el delay
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
