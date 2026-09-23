import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import Checkbox from "@mui/material/Checkbox";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Select from "@mui/material/Select";
import Switch from "@mui/material/Switch";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, KeyboardEvent, useCallback, useEffect, useState } from "react";

import {
  ItemMantenimiento,
  NuevoMaterial,
  actualizarMaterial,
  completarItem,
  crearItem,
  esApiError,
  listarItems,
} from "../api/mantenimientoClient";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

export interface MantenimientoProps {
  casaId: string;
}

/** Enfoca el primer campo del formulario "Nuevo ítem" ya renderizado
 * (spec `pantallas-financieras`, REQ-003): el formulario nunca estuvo
 * oculto, "abrirlo" desde `PageHeader`/`EmptyState` es llevarle el foco. */
function enfocarFormularioAlta() {
  document.getElementById("nombre-item")?.focus();
}

const PERIODICIDADES = ["semanal", "mensual", "trimestral", "semestral", "anual"] as const;

/** Pantalla "Mantenimiento" (spec `mantenimiento-casa`, REQ-001 a
 * REQ-004): alta de ítems de mantenimiento de la casa (con materiales
 * opcionales), listado con acción de completar, y por ítem su checklist
 * de materiales. Toggle Recurrente + selector Periodicidad, mismo patrón
 * que `Tareas.tsx` usa para Recurrente/Frecuencia. */
export function Mantenimiento({ casaId }: MantenimientoProps) {
  const [items, setItems] = useState<ItemMantenimiento[]>([]);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [fechaEstimada, setFechaEstimada] = useState("");
  const [recurrente, setRecurrente] = useState(false);
  const [periodicidad, setPeriodicidad] = useState<string>(PERIODICIDADES[0]);
  const [materiales, setMateriales] = useState<NuevoMaterial[]>([]);
  const [nombreMaterial, setNombreMaterial] = useState("");
  const [cantidadMaterial, setCantidadMaterial] = useState("1");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      setItems(await listarItems(casaId));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar el mantenimiento.");
    } finally {
      setCargando(false);
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  function agregarMaterialALista() {
    if (!nombreMaterial.trim()) return;
    setMateriales((actuales) => [
      ...actuales,
      { nombre: nombreMaterial.trim(), cantidad: Number(cantidadMaterial) || 1 },
    ]);
    setNombreMaterial("");
    setCantidadMaterial("1");
  }

  function quitarMaterialDeLista(index: number) {
    setMateriales((actuales) => actuales.filter((_, i) => i !== index));
  }

  // Reportado en vivo: sin esto, Enter en el campo de material dispara el
  // submit nativo del <form> (handleCrear) en vez de agregar el material a
  // la lista pendiente — el ítem se crea sin materiales, sin ningún error,
  // perdiendo silenciosamente lo que el usuario acababa de tipear.
  function handleKeyDownMaterial(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      agregarMaterialALista();
    }
  }

  async function handleCrear(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await crearItem(casaId, {
        nombre,
        descripcion: descripcion || undefined,
        fechaEstimada: fechaEstimada || undefined,
        recurrente,
        periodicidad: recurrente ? periodicidad : undefined,
        materiales: materiales.length > 0 ? materiales : undefined,
      });
      setNombre("");
      setDescripcion("");
      setFechaEstimada("");
      setRecurrente(false);
      setMateriales([]);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo crear el ítem de mantenimiento.");
    }
  }

  async function handleCompletar(itemId: string) {
    setError(null);
    try {
      await completarItem(casaId, itemId);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo completar el ítem.");
    }
  }

  async function handleToggleMaterial(itemId: string, materialId: string, conseguido: boolean) {
    setError(null);
    try {
      await actualizarMaterial(casaId, itemId, materialId, conseguido);
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo actualizar el material.");
    }
  }

  return (
    <Box
      component="section"
      aria-label="Mantenimiento"
      sx={{ display: "flex", flexDirection: "column", gap: 3 }}
    >
      <PageHeader
        title="Mantenimiento"
        action={{ label: "Nuevo ítem", onClick: enfocarFormularioAlta }}
      />

      {error && <Alert severity="error">{error}</Alert>}

      <Card variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleCrear}
          aria-label="Nuevo ítem"
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
            <TextField
              id="nombre-item"
              label="Nombre"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              size="small"
            />

            <TextField
              id="descripcion-item"
              label="Descripción"
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              size="small"
            />

            <TextField
              id="fecha-item"
              label={recurrente ? "Fecha estimada (obligatoria si es recurrente)" : "Fecha estimada"}
              type="date"
              value={fechaEstimada}
              onChange={(e) => setFechaEstimada(e.target.value)}
              size="small"
              slotProps={{ inputLabel: { shrink: true } }}
            />
          </Box>

          <FormControlLabel
            control={
              <Switch
                id="recurrente-item"
                checked={recurrente}
                onChange={(e) => setRecurrente(e.target.checked)}
              />
            }
            label="Recurrente"
          />

          {recurrente && (
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel htmlFor="periodicidad-item" shrink>
                Periodicidad
              </InputLabel>
              <Select
                native
                id="periodicidad-item"
                label="Periodicidad"
                value={periodicidad}
                onChange={(e) => setPeriodicidad(e.target.value)}
              >
                {PERIODICIDADES.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </Select>
            </FormControl>
          )}

          <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            <Typography variant="subtitle2">Materiales</Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
              <TextField
                id="nombre-material"
                label="Material"
                value={nombreMaterial}
                onChange={(e) => setNombreMaterial(e.target.value)}
                onKeyDown={handleKeyDownMaterial}
                size="small"
              />
              <TextField
                id="cantidad-material"
                label="Cantidad"
                type="number"
                value={cantidadMaterial}
                onChange={(e) => setCantidadMaterial(e.target.value)}
                onKeyDown={handleKeyDownMaterial}
                size="small"
                sx={{ width: 120 }}
              />
              <IconButton
                aria-label="Agregar material"
                onClick={agregarMaterialALista}
                type="button"
                size="small"
              >
                <AddIcon />
              </IconButton>
            </Box>
            {materiales.length > 0 && (
              <List dense aria-label="Materiales a agregar">
                {materiales.map((material, index) => (
                  <ListItem
                    key={`${material.nombre}-${index}`}
                    disableGutters
                    secondaryAction={
                      <IconButton
                        aria-label={`Quitar ${material.nombre}`}
                        onClick={() => quitarMaterialDeLista(index)}
                        size="small"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemText primary={`${material.nombre} (${material.cantidad})`} />
                  </ListItem>
                ))}
              </List>
            )}
          </Box>

          <Box>
            <Button type="submit" variant="contained">
              Crear ítem
            </Button>
          </Box>
        </Box>
      </Card>

      {cargando ? (
        <Typography>Cargando mantenimiento...</Typography>
      ) : items.length === 0 ? (
        <EmptyState
          message="Todavía no hay ítems de mantenimiento cargados."
          action={{ label: "Agregar el primero", onClick: enfocarFormularioAlta }}
        />
      ) : (
        <TableContainer component={Card} variant="outlined">
          <Table aria-label="Listado de mantenimiento" sx={{ minWidth: 320 }}>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Fecha estimada</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Materiales</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.nombre}</TableCell>
                  <TableCell>{item.fecha_estimada ?? "—"}</TableCell>
                  <TableCell>
                    <Chip
                      label={item.estado}
                      color={item.estado === "completado" ? "success" : "warning"}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {item.materiales.length === 0 ? (
                      "—"
                    ) : (
                      <List dense aria-label={`Materiales de ${item.nombre}`}>
                        {item.materiales.map((material) => (
                          <ListItem key={material.id} disableGutters>
                            <FormControlLabel
                              control={
                                <Checkbox
                                  checked={material.conseguido}
                                  onChange={(e) =>
                                    handleToggleMaterial(item.id, material.id, e.target.checked)
                                  }
                                />
                              }
                              label={`${material.nombre} (${material.cantidad})`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </TableCell>
                  <TableCell>
                    {item.estado !== "completado" && (
                      <Button
                        type="button"
                        size="small"
                        onClick={() => handleCompletar(item.id)}
                      >
                        Completar
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
