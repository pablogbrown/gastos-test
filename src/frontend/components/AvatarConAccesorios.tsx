import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import { useEffect, useState } from "react";

import { AvatarPersonaje, obtenerAvatarSeleccionado } from "../api/avatarClient";
import { AccesorioAvatar, listarAccesoriosEquipados } from "../api/tiendaClient";
import { AccesorioOverlayIcon } from "./AccesorioOverlayIcon";
import { LottieAvatar } from "./LottieAvatar";

export interface AvatarConAccesoriosProps {
  casaId: string;
  miembroId: string;
  nombre: string;
  size?: number;
}

/** Spec `perfil-avatar-ui`, REQ-001 (TC-001/TC-002/TC-003): avatar Lottie
 * del miembro con sus accesorios equipados superpuestos como overlay
 * simple (`position: absolute`, nunca integrados a la animación —
 * `personalizacion-avatares`, Decisiones ya tomadas), o el `Avatar` con
 * inicial de siempre como respaldo (TC-002) cuando el miembro no tiene
 * avatar seleccionado (dato preexistente a esta feature) — mismo
 * criterio "cero regresión" que el resto del proyecto. Compartido por
 * Miembros/Ranking (Constraints de la spec: ninguna de las 2 pantallas
 * duplica esta lógica condicional). No se muestra ningún estado de
 * carga propio: mientras resuelve, se ve el respaldo — evita el
 * parpadeo de reemplazar un ícono por otro más grande a mitad de carga
 * de la lista. */
export function AvatarConAccesorios({ casaId, miembroId, nombre, size = 40 }: AvatarConAccesoriosProps) {
  const [avatar, setAvatar] = useState<AvatarPersonaje | null>(null);
  const [equipados, setEquipados] = useState<AccesorioAvatar[]>([]);

  useEffect(() => {
    let vigente = true;
    setAvatar(null);
    setEquipados([]);

    async function cargar() {
      let seleccionado: AvatarPersonaje | null = null;
      try {
        seleccionado = await obtenerAvatarSeleccionado(casaId, miembroId);
      } catch {
        seleccionado = null;
      }
      if (!vigente) return;
      setAvatar(seleccionado);
      if (!seleccionado) return;

      try {
        const accesorios = await listarAccesoriosEquipados(casaId, miembroId);
        if (vigente) setEquipados(accesorios);
      } catch {
        // Sin accesorios equipados legibles: el avatar se muestra igual,
        // solo sin overlays — nunca rompe el render por este dato
        // secundario.
      }
    }

    void cargar();
    return () => {
      vigente = false;
    };
  }, [casaId, miembroId]);

  if (!avatar) {
    return (
      <Avatar aria-label={`Avatar de ${nombre}`}>{nombre.charAt(0).toUpperCase()}</Avatar>
    );
  }

  return (
    <Box
      aria-label={`Avatar de ${nombre}`}
      sx={{ position: "relative", width: size, height: size, flexShrink: 0 }}
    >
      <LottieAvatar src={avatar.lottie_url} />
      {equipados.map((accesorio) => (
        <Box key={accesorio.id} sx={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
          <AccesorioOverlayIcon
            src={accesorio.asset_overlay_url}
            alt={accesorio.nombre}
            size="100%"
          />
        </Box>
      ))}
    </Box>
  );
}
