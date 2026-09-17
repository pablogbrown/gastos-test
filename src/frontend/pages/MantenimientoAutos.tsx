import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import InputLabel from "@mui/material/InputLabel";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
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

import { Auto, NuevoAuto, crearAuto, esApiError, listarAutos } from "../api/autosClient";
import {
  ItemMantenimiento,
  NuevoMaterial,
  actualizarMaterial,
  completarItem,
  crearItem,
  listarItems,
} from "../api/mantenimientoClient";

export interface MantenimientoAutosProps {
  casaId: string;
}

const PERIODICIDADES = ["semanal", "mensual", "trimestral", "semestral", "anual"] as const;

interface ItemsPorAutoState {
  [autoId: string]: ItemMantenimiento[];
}

/** Pantalla "Mantenimiento Autos" (spec `mantenimiento-autos`, REQ-001 a
 * REQ-003): alta de autos de la casa, y por cada auto registrado, su
 * propio formulario/checklist de ítems de mantenimiento — mismo shape de
 * UI que `Mantenimiento.tsx` (materiales, acción de completar),
 * parametrizado por `auto_id` y agrupado visualmente por auto. Duplicado
 * deliberado, no extraído a un componente compartido en esta spec (ver
 * `01-plan-04-frontend-autos.md`'s Design Rationale) — extraerlo es una
 * mejora futura opcional, no bloqueante para el alcance pedido. */
export function MantenimientoAutos({ casaId }: MantenimientoAutosProps) {
  const [autos, setAutos] = useState<Auto[]>([]);
  const [itemsPorAuto, setItemsPorAuto] = useState<ItemsPorAutoState>({});
  const [marca, setMarca] = useState("");
  const [modelo, setModelo] = useState("");
  const [patente, setPatente] = useState("");
  const [anio, setAnio] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      const listado = await listarAutos(casaId);
      setAutos(listado);
      const entradas = await Promise.all(
        listado.map(async (auto) => [auto.id, await listarItems(casaId, auto.id)] as const)
      );
      setItemsPorAuto(Object.fromEntries(entradas));
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar Mantenimiento Autos.");
    } finally {
      setCargando(false);
    }
  }, [casaId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleCrearAuto(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const nuevo: NuevoAuto = {
        marca,
        modelo,
        patente: patente || undefined,
        anio: anio ? Number(anio) : undefined,
      };
      await crearAuto(casaId, nuevo);
      setMarca("");
      setModelo("");
      setPatente("");
      setAnio("");
      await cargar();
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo registrar el auto.");
    }
  }

  return (
    <Box
      component="section"
      aria-label="Mantenimiento Autos"
      sx={{ display: "flex", flexDirection: "column", gap: 3 }}
    >
      <Typography variant="h5" component="h2">
        Mantenimiento Autos
      </Typography>

      {error && <Alert severity="error">{error}</Alert>}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleCrearAuto}
          aria-label="Nuevo auto"
          sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}
        >
          <TextField
            id="marca-auto"
            label="Marca"
            value={marca}
            onChange={(e) => setMarca(e.target.value)}
            size="small"
          />
          <TextField
            id="modelo-auto"
            label="Modelo"
            value={modelo}
            onChange={(e) => setModelo(e.target.value)}
            size="small"
          />
          <TextField
            id="patente-auto"
            label="Patente"
            value={patente}
            onChange={(e) => setPatente(e.target.value)}
            size="small"
          />
          <TextField
            id="anio-auto"
            label="Año"
            type="number"
            value={anio}
            onChange={(e) => setAnio(e.target.value)}
            size="small"
            sx={{ width: 120 }}
          />
          <Button type="submit" variant="contained">
            Registrar auto
          </Button>
        </Box>
      </Paper>

      {cargando ? (
        <Typography>Cargando Mantenimiento Autos...</Typography>
      ) : autos.length === 0 ? (
        <Typography color="text.secondary">Todavía no hay autos registrados.</Typography>
      ) : (
        autos.map((auto) => (
          <AutoConItems
            key={auto.id}
            casaId={casaId}
            auto={auto}
            items={itemsPorAuto[auto.id] ?? []}
            onCambio={cargar}
            onError={(detalle) => setError(detalle)}
          />
        ))
      )}
    </Box>
  );
}

interface AutoConItemsProps {
  casaId: string;
  auto: Auto;
  items: ItemMantenimiento[];
  onCambio: () => Promise<void>;
  onError: (detalle: string) => void;
}

/** Ítems de mantenimiento de un auto puntual (agrupados bajo su propia
 * sección, TC-006) — mismo formulario/checklist que `Mantenimiento.tsx`,
 * parametrizado por `auto.id` vía `crearItem(casaId, {..., autoId})`/
 * `listarItems(casaId, auto.id)`. */
function AutoConItems({ casaId, auto, items, onCambio, onError }: AutoConItemsProps) {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [fechaEstimada, setFechaEstimada] = useState("");
  const [recurrente, setRecurrente] = useState(false);
  const [periodicidad, setPeriodicidad] = useState<string>(PERIODICIDADES[0]);
  const [materiales, setMateriales] = useState<NuevoMaterial[]>([]);
  const [nombreMaterial, setNombreMaterial] = useState("");
  const [cantidadMaterial, setCantidadMaterial] = useState("1");

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

  // Reportado en vivo sobre Mantenimiento.tsx (mismo bug, re-implementación
  // independiente): sin esto, Enter en el campo de material dispara el
  // submit nativo del <form> en vez de agregar el material a la lista
  // pendiente — el ítem se crea sin materiales, sin ningún error.
  function handleKeyDownMaterial(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      agregarMaterialALista();
    }
  }

  async function handleCrear(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await crearItem(casaId, {
        nombre,
        descripcion: descripcion || undefined,
        fechaEstimada: fechaEstimada || undefined,
        recurrente,
        periodicidad: recurrente ? periodicidad : undefined,
        materiales: materiales.length > 0 ? materiales : undefined,
        autoId: auto.id,
      });
      setNombre("");
      setDescripcion("");
      setFechaEstimada("");
      setRecurrente(false);
      setMateriales([]);
      await onCambio();
    } catch (err) {
      onError(esApiError(err) ? err.detail : "No se pudo crear el ítem de mantenimiento.");
    }
  }

  async function handleCompletar(itemId: string) {
    try {
      await completarItem(casaId, itemId);
      await onCambio();
    } catch (err) {
      onError(esApiError(err) ? err.detail : "No se pudo completar el ítem.");
    }
  }

  async function handleToggleMaterial(itemId: string, materialId: string, conseguido: boolean) {
    try {
      await actualizarMaterial(casaId, itemId, materialId, conseguido);
      await onCambio();
    } catch (err) {
      onError(esApiError(err) ? err.detail : "No se pudo actualizar el material.");
    }
  }

  return (
    <Box
      component="section"
      aria-label={`Mantenimiento de ${auto.marca} ${auto.modelo}`}
      sx={{ display: "flex", flexDirection: "column", gap: 2 }}
    >
      <Typography variant="h6" component="h3">
        {auto.marca} {auto.modelo}
        {auto.patente ? ` — ${auto.patente}` : ""}
      </Typography>

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Box
          component="form"
          onSubmit={handleCrear}
          aria-label={`Nuevo ítem para ${auto.marca} ${auto.modelo}`}
          sx={{ display: "flex", flexDirection: "column", gap: 2 }}
        >
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
            <TextField
              id={`nombre-item-${auto.id}`}
              label="Nombre"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              size="small"
            />

            <TextField
              id={`descripcion-item-${auto.id}`}
              label="Descripción"
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              size="small"
            />

            <TextField
              id={`fecha-item-${auto.id}`}
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
                id={`recurrente-item-${auto.id}`}
                checked={recurrente}
                onChange={(e) => setRecurrente(e.target.checked)}
              />
            }
            label="Recurrente"
          />

          {recurrente && (
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel htmlFor={`periodicidad-item-${auto.id}`} shrink>
                Periodicidad
              </InputLabel>
              <Select
                native
                id={`periodicidad-item-${auto.id}`}
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
                id={`nombre-material-${auto.id}`}
                label="Material"
                value={nombreMaterial}
                onChange={(e) => setNombreMaterial(e.target.value)}
                onKeyDown={handleKeyDownMaterial}
                size="small"
              />
              <TextField
                id={`cantidad-material-${auto.id}`}
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
      </Paper>

      {items.length === 0 ? (
        <Typography color="text.secondary">
          Todavía no hay mantenimiento cargado para este auto.
        </Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table aria-label={`Listado de mantenimiento de ${auto.marca} ${auto.modelo}`} sx={{ minWidth: 320 }}>
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
