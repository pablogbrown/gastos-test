import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Chip from "@mui/material/Chip";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { useCallback, useEffect, useState } from "react";

import { Rol } from "../api/casasClient";
import {
  Suscripcion,
  cancelarSuscripcion,
  esApiError,
  listarSuscripciones,
} from "../api/suscripcionesClient";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

export interface SuscripcionesProps {
  casaId: string;
  rolUsuarioActual: Rol;
}

/** Pantalla "Suscripciones" (REQ-005): lista las suscripciones de la
 * casa (activas e inactivas) y ofrece "Cancelar" solo para una activa —
 * y solo si el usuario actual es Administrador (defensa en profundidad,
 * mismo patrón que `Miembros.tsx`; la autorización real vive en la API).
 */
export function Suscripciones({ casaId, rolUsuarioActual }: SuscripcionesProps) {
  const [suscripciones, setSuscripciones] = useState<Suscripcion[]>([]);
  const [error, setError] = useState<string | null>(null);

  const puedeCancelar = rolUsuarioActual === "admin";

  const cargar = useCallback(async () => {
    try {
      const lista = await listarSuscripciones(casaId);
      setSuscripciones(lista);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar las suscripciones.");
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  /** Spec `gastos-multi-moneda`: prefijo `US$` para una suscripción en
   * dólares, `$` (comportamiento actual) en cualquier otro caso — mismo
   * criterio que `Gastos.tsx`. */
  function importeConPrefijo(suscripcion: Suscripcion): string {
    return `${suscripcion.moneda === "USD" ? "US$" : "$"}${suscripcion.importe}`;
  }

  async function handleCancelar(suscripcionId: string) {
    setError(null);
    try {
      await cancelarSuscripcion(casaId, suscripcionId);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cancelar la suscripción.");
    }
  }

  return (
    <Box
      component="section"
      aria-label="Suscripciones"
      sx={{ display: "flex", flexDirection: "column", gap: 3 }}
    >
      {/* Sin `action` (spec `pantallas-financieras`, T2, decisión
       * registrada en decisions.yaml): esta pantalla no tiene un flujo de
       * alta propio hoy — una suscripción se crea desde `Gastos.tsx`
       * (tipo de gasto "Suscripción mensual"). Inventar un formulario de
       * alta acá violaría REQ-004 (cero regresión funcional, restyle
       * puramente de presentación). */}
      <PageHeader title="Suscripciones" />

      {error && <Alert severity="error">{error}</Alert>}

      {suscripciones.length === 0 ? (
        <EmptyState message="Todavía no hay suscripciones para mostrar." />
      ) : (
      <TableContainer component={Card} variant="outlined">
        <Table aria-label="Listado de suscripciones" sx={{ minWidth: 320 }}>
          <TableHead>
            <TableRow>
              <TableCell>Descripción</TableCell>
              <TableCell>Importe</TableCell>
              <TableCell>Estado</TableCell>
              {puedeCancelar && <TableCell>Acciones</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {suscripciones.map((suscripcion) => (
              <TableRow key={suscripcion.id}>
                <TableCell>{suscripcion.descripcion}</TableCell>
                <TableCell>{importeConPrefijo(suscripcion)}</TableCell>
                <TableCell>
                  <Chip
                    label={suscripcion.activa ? "Activa" : "Inactiva"}
                    color={suscripcion.activa ? "success" : "default"}
                    size="small"
                  />
                </TableCell>
                {puedeCancelar && (
                  <TableCell>
                    {suscripcion.activa && (
                      <Button
                        type="button"
                        size="small"
                        color="error"
                        onClick={() => handleCancelar(suscripcion.id)}
                      >
                        Cancelar
                      </Button>
                    )}
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      )}
    </Box>
  );
}
