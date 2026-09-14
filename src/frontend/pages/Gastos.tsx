import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
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
  crearCategoria,
  esApiError,
  listarCategorias,
  listarGastos,
  registrarGasto,
} from "../api/gastosClient";

export interface GastosProps {
  casaId: string;
  miembros: Miembro[];
}

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
  const [nuevaCategoria, setNuevaCategoria] = useState("");
  const [todosLosMiembros, setTodosLosMiembros] = useState(true);
  const [seleccionados, setSeleccionados] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      const [listaCategorias, historial] = await Promise.all([
        listarCategorias(casaId),
        listarGastos(casaId),
      ]);
      setCategorias(listaCategorias);
      setGastos(historial);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar los gastos.");
    }
  }, [casaId]);

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
      await registrarGasto(casaId, {
        descripcion,
        importe,
        fecha,
        categoriaId,
        participantes: todosLosMiembros ? undefined : seleccionados,
      });
      setDescripcion("");
      setImporte("");
      setFecha("");
      setCategoriaId("");
      setTodosLosMiembros(true);
      setSeleccionados([]);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo registrar el gasto.");
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

  return (
    <Box component="section" aria-label="Gastos" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <Typography variant="h5" component="h2">
        Gastos
      </Typography>

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
          </Box>

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

          {!todosLosMiembros && (
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
            </TableRow>
          </TableHead>
          <TableBody>
            {gastos.map((gasto) => (
              <TableRow key={gasto.id}>
                <TableCell>{gasto.fecha}</TableCell>
                <TableCell>{gasto.descripcion}</TableCell>
                <TableCell>{gasto.importe}</TableCell>
                <TableCell>{nombreCategoria(gasto.categoria_id)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
