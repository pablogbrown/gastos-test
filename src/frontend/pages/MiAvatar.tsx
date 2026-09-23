import LockIcon from "@mui/icons-material/Lock";
import PaidIcon from "@mui/icons-material/Paid";
import PetsIcon from "@mui/icons-material/Pets";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import {
  AvatarPersonaje,
  esApiError,
  listarAvataresCatalogo,
  listarAvataresDisponibles,
  obtenerAvatarSeleccionado,
  obtenerCreditos,
  seleccionarAvatar,
} from "../api/avatarClient";
import {
  AccesorioAvatar,
  comprarAccesorio,
  equiparAccesorio,
  listarAccesoriosEquipados,
  listarCatalogoAccesorios,
  listarInventario,
} from "../api/tiendaClient";
import { AccesorioOverlayIcon } from "../components/AccesorioOverlayIcon";
import { LottieAvatar } from "../components/LottieAvatar";
import { PageHeader } from "../components/PageHeader";
import { StatCard } from "../components/StatCard";

export interface MiAvatarProps {
  casaId: string;
  miembroId: string;
}

/** Pantalla "Mi Avatar" (spec `perfil-avatar-ui`, REQ-002): saldo de
 * créditos, razas desbloqueadas (seleccionables) y bloqueadas (con su
 * nivel requerido visible, TC-004), y la tienda de accesorios filtrada
 * por especie del avatar actual (comprar/equipar, TC-006). Elegir una
 * raza desbloqueada la aplica de inmediato (sin confirmación, TC-005) —
 * mismo criterio "sin fricción" del resto de la app. */
export function MiAvatar({ casaId, miembroId }: MiAvatarProps) {
  const [saldo, setSaldo] = useState(0);
  const [avatarActual, setAvatarActual] = useState<AvatarPersonaje | null>(null);
  const [disponibles, setDisponibles] = useState<AvatarPersonaje[]>([]);
  const [catalogoRazas, setCatalogoRazas] = useState<AvatarPersonaje[]>([]);
  const [catalogoAccesorios, setCatalogoAccesorios] = useState<AccesorioAvatar[]>([]);
  const [inventario, setInventario] = useState<AccesorioAvatar[]>([]);
  const [equipados, setEquipados] = useState<AccesorioAvatar[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accionEnCurso, setAccionEnCurso] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const [creditos, actual, disponiblesLista, catalogoLista, accesoriosLista, inventarioLista, equipadosLista] =
        await Promise.all([
          obtenerCreditos(casaId, miembroId),
          obtenerAvatarSeleccionado(casaId, miembroId),
          listarAvataresDisponibles(casaId, miembroId),
          listarAvataresCatalogo(casaId, miembroId),
          listarCatalogoAccesorios(casaId, miembroId),
          listarInventario(casaId, miembroId),
          listarAccesoriosEquipados(casaId, miembroId),
        ]);
      setSaldo(creditos.saldo);
      setAvatarActual(actual);
      setDisponibles(disponiblesLista);
      setCatalogoRazas(catalogoLista);
      setCatalogoAccesorios(accesoriosLista);
      setInventario(inventarioLista);
      setEquipados(equipadosLista);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar la pantalla de Mi Avatar.");
    } finally {
      setCargando(false);
    }
  }, [casaId, miembroId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleElegirRaza(avatarPersonajeId: string) {
    setError(null);
    setAccionEnCurso(avatarPersonajeId);
    try {
      const nuevo = await seleccionarAvatar(casaId, miembroId, avatarPersonajeId);
      setAvatarActual(nuevo);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo seleccionar esa raza.");
    } finally {
      setAccionEnCurso(null);
    }
  }

  async function handleComprar(accesorioId: string) {
    setError(null);
    setAccionEnCurso(accesorioId);
    try {
      const comprado = await comprarAccesorio(casaId, miembroId, accesorioId);
      setInventario((actual) => [...actual, comprado]);
      const creditos = await obtenerCreditos(casaId, miembroId);
      setSaldo(creditos.saldo);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo comprar ese accesorio.");
    } finally {
      setAccionEnCurso(null);
    }
  }

  async function handleEquipar(accesorioId: string) {
    setError(null);
    setAccionEnCurso(accesorioId);
    try {
      const equipado = await equiparAccesorio(casaId, miembroId, accesorioId);
      setEquipados((actual) => [...actual.filter((a) => a.slot !== equipado.slot), equipado]);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo equipar ese accesorio.");
    } finally {
      setAccionEnCurso(null);
    }
  }

  const idsDisponibles = new Set(disponibles.map((raza) => raza.id));
  const bloqueadas = catalogoRazas.filter((raza) => !idsDisponibles.has(raza.id));
  const idsComprados = new Set(inventario.map((accesorio) => accesorio.id));
  const idsEquipados = new Set(equipados.map((accesorio) => accesorio.id));
  // Un accesorio ya comprado se muestra una sola vez (desde el
  // inventario, con controles de equipar) — nunca duplicado si además
  // sigue apareciendo en el catálogo de compra (`tienda_service.
  // listar_catalogo_accesorios` no lo excluye, ver docstring).
  const accesoriosParaComprar = catalogoAccesorios.filter((accesorio) => !idsComprados.has(accesorio.id));

  if (cargando) {
    return (
      <Box sx={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 1 }}>
        <CircularProgress size={20} />
        <Typography>Cargando Mi Avatar...</Typography>
      </Box>
    );
  }

  return (
    <Box component="section" aria-label="Mi Avatar" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <PageHeader title="Mi Avatar" subtitle="Elegí tu raza y personalizala con accesorios" />

      {error && <Alert severity="error">{error}</Alert>}

      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, alignItems: "center" }}>
        <StatCard icon={<PaidIcon />} label="Créditos disponibles" value={String(saldo)} />
        {avatarActual && (
          <Box sx={{ width: 64, height: 64 }}>
            <LottieAvatar src={avatarActual.lottie_url} />
          </Box>
        )}
      </Box>

      <Box>
        <Typography variant="h6" component="h3" sx={{ mb: 1.5 }}>
          Razas
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1.5 }}>
          {disponibles.map((raza) => {
            const esActual = avatarActual?.id === raza.id;
            return (
              <Card
                key={raza.id}
                variant="outlined"
                role="button"
                aria-label={`Elegir raza ${raza.raza}`}
                onClick={() => !esActual && handleElegirRaza(raza.id)}
                sx={{
                  cursor: esActual ? "default" : "pointer",
                  borderColor: esActual ? "primary.main" : undefined,
                  borderWidth: esActual ? 2 : 1,
                  width: 140,
                }}
              >
                <CardContent sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 1 }}>
                  <Box sx={{ width: 56, height: 56 }}>
                    <LottieAvatar src={raza.lottie_url} loop={false} />
                  </Box>
                  <Typography variant="body2">{raza.raza}</Typography>
                  {esActual ? (
                    <Chip label="Activa" size="small" color="primary" />
                  ) : (
                    accionEnCurso === raza.id && <CircularProgress size={16} />
                  )}
                </CardContent>
              </Card>
            );
          })}
          {bloqueadas.map((raza) => (
            <Card key={raza.id} variant="outlined" sx={{ width: 140, opacity: 0.6 }}>
              <CardContent sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 1 }}>
                <LockIcon fontSize="small" color="disabled" />
                <Typography variant="body2">{raza.raza}</Typography>
                <Chip label={`Nivel ${raza.nivel_requerido}`} size="small" variant="outlined" />
              </CardContent>
            </Card>
          ))}
        </Box>
      </Box>

      <Box>
        <Typography variant="h6" component="h3" sx={{ mb: 1.5 }}>
          Tienda de accesorios
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1.5 }}>
          {inventario.map((accesorio) => {
            const yaEquipado = idsEquipados.has(accesorio.id);
            return (
              <Card key={accesorio.id} variant="outlined" sx={{ width: 160 }}>
                <CardContent sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
                  <AccesorioOverlayIcon
                    src={accesorio.asset_overlay_url}
                    alt={accesorio.nombre}
                    size={40}
                    sx={{ alignSelf: "center" }}
                  />
                  <Typography variant="body2">{accesorio.nombre}</Typography>
                  <Chip label={accesorio.slot} size="small" variant="outlined" sx={{ alignSelf: "flex-start" }} />
                </CardContent>
                <CardActions>
                  {yaEquipado ? (
                    <Chip label="Equipado" size="small" color="success" />
                  ) : (
                    <Button
                      size="small"
                      onClick={() => handleEquipar(accesorio.id)}
                      disabled={accionEnCurso === accesorio.id}
                    >
                      Equipar
                    </Button>
                  )}
                </CardActions>
              </Card>
            );
          })}
          {accesoriosParaComprar.map((accesorio) => {
            // El saldo insuficiente lo rechaza el backend (402, spec
            // `tienda-accesorios` Contracts) — nunca se duplica esa
            // validación acá deshabilitando el botón: mismo criterio ya
            // establecido para el rechazo de nivel en razas (403), sin
            // gate del lado del cliente.
            const alcanza = saldo >= accesorio.precio_creditos;
            return (
              <Card key={accesorio.id} variant="outlined" sx={{ width: 160, opacity: alcanza ? 1 : 0.7 }}>
                <CardContent sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
                  <AccesorioOverlayIcon
                    src={accesorio.asset_overlay_url}
                    alt={accesorio.nombre}
                    size={40}
                    sx={{ alignSelf: "center" }}
                  />
                  <Typography variant="body2">{accesorio.nombre}</Typography>
                  <Chip label={`${accesorio.precio_creditos} créditos`} size="small" variant="outlined" />
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<PetsIcon fontSize="small" />}
                    onClick={() => handleComprar(accesorio.id)}
                    disabled={accionEnCurso === accesorio.id}
                  >
                    Comprar
                  </Button>
                </CardActions>
              </Card>
            );
          })}
        </Box>
      </Box>
    </Box>
  );
}
