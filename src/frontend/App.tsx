import Box from "@mui/material/Box";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import { useCallback, useEffect, useState } from "react";

import {
  cerrarSesion,
  obtenerToken,
  obtenerUsuarioIdActual,
  suscribirseACierreSesion,
} from "./api/authClient";
import { AppNav, Pantalla } from "./AppNav";
import { Casa, Miembro, Rol, listarMiembros } from "./api/casasClient";
import { Balance } from "./pages/Balance";
import { Gastos } from "./pages/Gastos";
import { HistorialActividad } from "./pages/HistorialActividad";
import { InicioCasa } from "./pages/InicioCasa";
import { Login } from "./pages/Login";
import { Miembros } from "./pages/Miembros";
import { Ranking } from "./pages/Ranking";
import { Registro } from "./pages/Registro";
import { SelectorCasas } from "./pages/SelectorCasas";
import { Tareas } from "./pages/Tareas";

type VistaSinSesion = "login" | "registro";

/** Gate de 3 estados (spec `usuarios-auth`, T3): sin JWT → `Login`/
 * `Registro`; con JWT y sin casa elegida → `SelectorCasas`; con JWT y
 * casa elegida → el shell existente de `ui-modernization` (sin cambios
 * en su navegación interna). Reemplaza el `usuarioIdDeSesion()` al azar
 * que generaba esta app en cada carga — la identidad ahora viene de un
 * login real (REQ-001 a REQ-005). */
export function App() {
  const theme = useTheme();
  const esDesktop = useMediaQuery(theme.breakpoints.up("sm"));

  const [token, setToken] = useState<string | null>(obtenerToken);
  const [vistaSinSesion, setVistaSinSesion] = useState<VistaSinSesion>("login");
  const [casaActual, setCasaActual] = useState<Casa | null>(null);
  const [pantalla, setPantalla] = useState<Pantalla>("inicio");
  const [miembros, setMiembros] = useState<Miembro[]>([]);

  useEffect(
    () =>
      suscribirseACierreSesion(() => {
        setToken(null);
        setCasaActual(null);
      }),
    []
  );

  const cargarMiembros = useCallback(async () => {
    if (!casaActual) return;
    setMiembros(await listarMiembros(casaActual.id));
  }, [casaActual]);

  useEffect(() => {
    void cargarMiembros();
  }, [cargarMiembros]);

  function handleCerrarSesion() {
    cerrarSesion();
  }

  if (!token) {
    return vistaSinSesion === "login" ? (
      <Login
        onLoginExitoso={() => setToken(obtenerToken())}
        onIrARegistro={() => setVistaSinSesion("registro")}
      />
    ) : (
      <Registro
        onRegistroExitoso={() => setVistaSinSesion("login")}
        onIrALogin={() => setVistaSinSesion("login")}
      />
    );
  }

  if (!casaActual) {
    return <SelectorCasas onCasaElegida={setCasaActual} />;
  }

  const usuarioIdActual = obtenerUsuarioIdActual();
  const miMiembro = miembros.find((m) => m.usuario_id === usuarioIdActual);
  /** Spec `resolver-rol-usuario-en-casa` (REQ-002): nunca `"admin"` por
   * default — mientras `miembros` carga o ante cualquier estado
   * inconsistente donde mi propia fila todavía no aparece, el rol
   * resuelto es el más restrictivo. */
  const rolUsuarioActual: Rol = miMiembro?.rol ?? "member";

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        bgcolor: "background.default",
      }}
    >
      <AppNav pantalla={pantalla} onChange={setPantalla} onCerrarSesion={handleCerrarSesion} />

      <Box
        component="main"
        sx={{
          flex: 1,
          p: { xs: 2, sm: 3 },
          pb: esDesktop ? 3 : 9,
          maxWidth: "100%",
          overflowX: "hidden",
        }}
      >
        {pantalla === "inicio" && <InicioCasa casaId={casaActual.id} miembros={miembros} />}
        {pantalla === "miembros" && (
          <Miembros casaId={casaActual.id} rolUsuarioActual={rolUsuarioActual} />
        )}
        {pantalla === "gastos" && <Gastos casaId={casaActual.id} miembros={miembros} />}
        {pantalla === "balance" && <Balance casaId={casaActual.id} />}
        {pantalla === "tareas" && (
          <Tareas
            casaId={casaActual.id}
            miembroIdActual={miMiembro?.id ?? ""}
            rolUsuarioActual={rolUsuarioActual}
          />
        )}
        {pantalla === "ranking" && <Ranking casaId={casaActual.id} miembros={miembros} />}
        {pantalla === "actividad" && <HistorialActividad casaId={casaActual.id} />}
      </Box>
    </Box>
  );
}
