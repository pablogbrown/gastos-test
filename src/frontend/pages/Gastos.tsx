import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormGroup from "@mui/material/FormGroup";
import InputLabel from "@mui/material/InputLabel";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { Miembro } from "../api/casasClient";
import {
  Categoria,
  Gasto,
  actualizarEstadoGasto,
  crearCategoria,
  esApiError,
  listarCategorias,
  listarGastos,
  registrarGasto,
} from "../api/gastosClient";
import { crearSuscripcion } from "../api/suscripcionesClient";

export interface GastosProps {
  casaId: string;
  miembros: Miembro[];
}

/** "Tipo de gasto" (spec `gastos-suscripcion-mensual`): Único (default) /
 * En cuotas (spec `gastos-en-cuotas`, sin cambios de comportamiento) /
 * Suscripción mensual — mutuamente excluyente con el campo Cuotas:
 * elegir "Suscripción mensual" oculta/ignora ese campo y hace que el
 * envío llame a `crearSuscripcion` en vez de `registrarGasto`. */
type TipoGasto = "unico" | "cuotas" | "suscripcion";

/** Spec `gastos-multi-moneda`: moneda de un gasto o suscripción. */
type Moneda = "ARS" | "USD";

/** Spec `gastos-estado-pago`: estado de pago de un gasto. */
type Estado = "pagado" | "a_pagar";

/** Pantalla "Gastos" (REQ-001, REQ-002, REQ-003, REQ-008): formulario de
 * alta de un gasto y su historial. "Todos los miembros" viene
 * preseleccionado (REQ-003); el historial no filtra por `activo` — la
 * API ya incluye gastos de miembros desactivados (REQ-008/TC-010).
 * Spec `usuarios-auth`: el actor se resuelve del JWT en el backend — ya
 * no recibe `usuarioId` como prop. */
export function Gastos({ casaId, miembros }: GastosProps) {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [gastos, setGastos] = useState<Gasto[]>([]);
  const [descripcion, setDescripcion] = useState("");
  const [importe, setImporte] = useState("");
  const [fecha, setFecha] = useState("");
  const [categoriaId, setCategoriaId] = useState("");
  const [cuotas, setCuotas] = useState("");
  const [tipoGasto, setTipoGasto] = useState<TipoGasto>("unico");
  const [moneda, setMoneda] = useState<Moneda>("ARS");
  const [estado, setEstado] = useState<Estado>("pagado");
  const [nuevaCategoria, setNuevaCategoria] = useState("");
  const [todosLosMiembros, setTodosLosMiembros] = useState(true);
  const [seleccionados, setSeleccionados] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  // Spec `gastos-vista-mensual` (REQ-002): mes preseleccionado = mes
  // actual, mismo componente y criterio que el selector de `Balance.tsx`.
  const [mes, setMes] = useState<string>(() => new Date().toISOString().slice(0, 7));

  const cargar = useCallback(async () => {
    try {
      const [listaCategorias, historial] = await Promise.all([
        listarCategorias(casaId),
        listarGastos(casaId, mes),
      ]);
      setCategorias(listaCategorias);
      setGastos(historial);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar los gastos.");
    }
  }, [casaId, mes]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleCrearCategoria(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await crearCategoria(casaId, nuevaCategoria);
      setNuevaCategoria("");
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo crear la categoría.");
    }
  }

  async function handleRegistrarGasto(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      // Spec `gastos-multi-moneda`: nunca se fuerza "ARS" explícito en el
      // body — el backend ya lo asume por default (mismo patrón
      // vacío->undefined que `cuotas`).
      const monedaEnviada = moneda === "ARS" ? undefined : moneda;
      // Spec `gastos-estado-pago`: mismo criterio que `moneda` -- nunca
      // se fuerza "pagado" explícito en el body cuando queda en el
      // default.
      const estadoEnviado = estado === "pagado" ? undefined : estado;
      if (tipoGasto === "suscripcion") {
        // Spec `gastos-suscripcion-mensual`, TC-007: el modo "Suscripción
        // mensual" llama a `crearSuscripcion`, nunca a `registrarGasto` —
        // sin cuotas ni selección de participantes (siempre "todos los
        // miembros", igual que `crear_suscripcion` ya hace del lado del
        // servicio).
        await crearSuscripcion(casaId, {
          descripcion,
          importe,
          categoriaId,
          moneda: monedaEnviada,
        });
      } else {
        await registrarGasto(casaId, {
          descripcion,
          importe,
          fecha,
          categoriaId,
          participantes: todosLosMiembros ? undefined : seleccionados,
          cuotas: cuotas === "" ? undefined : Number(cuotas),
          moneda: monedaEnviada,
          estado: estadoEnviado,
        });
      }
      setDescripcion("");
      setImporte("");
      setFecha("");
      setCategoriaId("");
      setCuotas("");
      setTipoGasto("unico");
      setMoneda("ARS");
      setEstado("pagado");
      setTodosLosMiembros(true);
      setSeleccionados([]);
      await cargar();
    } catch (err) {
      setError(
        esApiError(err)
          ? err.detail
          : tipoGasto === "suscripcion"
            ? "No se pudo crear la suscripción."
            : "No se pudo registrar el gasto."
      );
    }
  }

  /** Spec `gastos-estado-pago`, TC-010: alterna el estado del gasto
   * clickeado al contrario del actual y refresca el listado. */
  async function handleToggleEstado(gasto: Gasto) {
    setError(null);
    try {
      const nuevoEstado: Estado = gasto.estado === "pagado" ? "a_pagar" : "pagado";
      await actualizarEstadoGasto(casaId, gasto.id, nuevoEstado);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo actualizar el estado del gasto.");
    }
  }

  function toggleParticipante(miembroId: string) {
    setSeleccionados((actuales) =>
      actuales.includes(miembroId)
        ? actuales.filter((id) => id !== miembroId)
        : [...actuales, miembroId]
    );
  }

  function nombreCategoria(id: string): string {
    return categorias.find((categoria) => categoria.id === id)?.nombre ?? id;
  }

  /** Spec `gastos-multi-moneda`: prefijo `US$` para un gasto en dólares,
   * `$` (comportamiento actual) en cualquier otro caso. */
  function importeConPrefijo(gasto: Gasto): string {
    return `${gasto.moneda === "USD" ? "US$" : "$"}${gasto.importe}`;
  }

  return (
    <Box component="section" aria-label="Gastos" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 2 }}>
        <Typography variant="h5" component="h2">
          Gastos
        </Typography>

        <TextField
          id="mes-gastos"
          label="Mes"
          type="month"
          value={mes}
          onChange={(event) => setMes(event.target.value)}
          size="small"
          slotProps={{ inputLabel: { shrink: true } }}
        />
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleCrearCategoria}
          aria-label="Nueva categoría"
          sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "flex-start" }}
        >
          <TextField
            id="nueva-categoria"
            label="Nueva categoría"
            value={nuevaCategoria}
            onChange={(event) => setNuevaCategoria(event.target.value)}
            size="small"
          />
          <Button type="submit" variant="outlined">
            Crear categoría
          </Button>
        </Box>
      </Paper>

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleRegistrarGasto}
          aria-label="Nuevo gasto"
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
            <TextField
              id="descripcion-gasto"
              label="Descripción"
              value={descripcion}
              onChange={(event) => setDescripcion(event.target.value)}
              size="small"
            />

            <TextField
              id="importe-gasto"
              label="Importe"
              type="number"
              value={importe}
              onChange={(event) => setImporte(event.target.value)}
              size="small"
            />

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel htmlFor="moneda-gasto" shrink>
                Moneda
              </InputLabel>
              <Select
                native
                id="moneda-gasto"
                label="Moneda"
                value={moneda}
                onChange={(event) => setMoneda(event.target.value as Moneda)}
              >
                <option value="ARS">ARS</option>
                <option value="USD">USD</option>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 140 }}>
              <InputLabel htmlFor="estado-gasto" shrink>
                Estado
              </InputLabel>
              <Select
                native
                id="estado-gasto"
                label="Estado"
                value={estado}
                onChange={(event) => setEstado(event.target.value as Estado)}
              >
                <option value="pagado">Pagado</option>
                <option value="a_pagar">A pagar</option>
              </Select>
            </FormControl>

            <TextField
              id="fecha-gasto"
              label="Fecha"
              type="date"
              value={fecha}
              onChange={(event) => setFecha(event.target.value)}
              size="small"
              slotProps={{ inputLabel: { shrink: true } }}
            />

            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel htmlFor="categoria-gasto" shrink>
                Categoría
              </InputLabel>
              <Select
                native
                id="categoria-gasto"
                label="Categoría"
                value={categoriaId}
                onChange={(event) => setCategoriaId(event.target.value)}
              >
                <option value="">Seleccionar categoría</option>
                {categorias.map((categoria) => (
                  <option key={categoria.id} value={categoria.id}>
                    {categoria.nombre}
                  </option>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel htmlFor="tipo-gasto" shrink>
                Tipo de gasto
              </InputLabel>
              <Select
                native
                id="tipo-gasto"
                label="Tipo de gasto"
                value={tipoGasto}
                onChange={(event) => setTipoGasto(event.target.value as TipoGasto)}
              >
                <option value="unico">Único</option>
                <option value="cuotas">En cuotas</option>
                <option value="suscripcion">Suscripción mensual</option>
              </Select>
            </FormControl>

            {tipoGasto !== "suscripcion" && (
              <TextField
                id="cuotas-gasto"
                label="Cuotas (opcional)"
                type="number"
                value={cuotas}
                onChange={(event) => setCuotas(event.target.value)}
                size="small"
              />
            )}
          </Box>

          {tipoGasto === "suscripcion" && (
            <Typography variant="body2" color="text.secondary">
              Se va a generar un gasto de este mes en adelante, todos los meses, hasta que
              canceles la suscripción — repartido entre todos los miembros.
            </Typography>
          )}

          {tipoGasto !== "suscripcion" && Number(cuotas) >= 2 && (
            <Typography variant="body2" color="text.secondary">
              Se van a crear {Number(cuotas)} gastos, uno por mes.
            </Typography>
          )}

          {tipoGasto !== "suscripcion" && (
            <FormGroup>
              <FormControlLabel
                control={
                  <Checkbox
                    id="todos-los-miembros"
                    checked={todosLosMiembros}
                    onChange={(event) => setTodosLosMiembros(event.target.checked)}
                  />
                }
                label="Todos los miembros"
              />
            </FormGroup>
          )}

          {tipoGasto !== "suscripcion" && !todosLosMiembros && (
            <FormGroup aria-label="Participantes">
              {miembros.map((miembro) => (
                <FormControlLabel
                  key={miembro.id}
                  control={
                    <Checkbox
                      checked={seleccionados.includes(miembro.id)}
                      onChange={() => toggleParticipante(miembro.id)}
                    />
                  }
                  label={miembro.nombre}
                />
              ))}
            </FormGroup>
          )}

          <Box>
            <Button type="submit" variant="contained">
              Registrar gasto
            </Button>
          </Box>
        </Box>
      </Paper>

      <TableContainer component={Paper} variant="outlined">
        <Table aria-label="Historial de gastos" sx={{ minWidth: 320 }}>
          <TableHead>
            <TableRow>
              <TableCell>Fecha</TableCell>
              <TableCell>Descripción</TableCell>
              <TableCell>Importe</TableCell>
              <TableCell>Categoría</TableCell>
              <TableCell>Estado</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {gastos.map((gasto) => (
              <TableRow key={gasto.id}>
                <TableCell>{gasto.fecha}</TableCell>
                <TableCell>{gasto.descripcion}</TableCell>
                <TableCell>{importeConPrefijo(gasto)}</TableCell>
                <TableCell>{nombreCategoria(gasto.categoria_id)}</TableCell>
                <TableCell>
                  <Chip
                    label={gasto.estado === "pagado" ? "Pagado" : "A pagar"}
                    color={gasto.estado === "pagado" ? "success" : "warning"}
                    size="small"
                    onClick={() => void handleToggleEstado(gasto)}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
