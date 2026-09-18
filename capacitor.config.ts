import type { CapacitorConfig } from "@capacitor/cli";

// T3 (android-capacitor-app): empaqueta el build de produccion existente
// (`npm run build` -> `dist/`) como app Android via Capacitor, sin crear
// un segundo frontend. Ver docs/android.md para el flujo completo de
// build/instalacion.
const config: CapacitorConfig = {
  appId: "com.taskia.app",
  appName: "taskia",
  webDir: "dist",
  android: {
    // Backend local/LAN sin TLS durante desarrollo — sin esto, Android
    // 9+ bloquea el trafico HTTP plano por default. Ver tambien
    // android/app/src/main/res/xml/network_security_config.xml, que
    // cubre el caso (una app que arranca en capacitor:// y llama a un
    // backend http:// plano) que allowMixedContent por si solo no cubre.
    allowMixedContent: true,
  },
  // Modo live-reload (opcional, comentado por default): descomentar y
  // apuntar a la IP de LAN del servidor de Vite (`npm run dev -- --host`)
  // para iterar sin recompilar el APK en cada cambio. Ver docs/android.md.
  // server: { url: "http://<ip-de-lan>:5173", cleartext: true },
};

export default config;
