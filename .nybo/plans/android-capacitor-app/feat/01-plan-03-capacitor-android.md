# T3 — Proyecto Android + Capacitor

## Scope
- `package.json`: agregar `@capacitor/core`, `@capacitor/android`
  (`dependencies`), `@capacitor/cli` (`devDependencies`). `npm install`.
- `capacitor.config.ts` (raíz del repo) — shape exacto en
  `00-overview.md` § T3 (appId `com.taskia.app`, appName `taskia`,
  `webDir: "dist"`, `android.allowMixedContent: true`, bloque `server`
  comentado para el modo live-reload).
- `npm run build` (genera `dist/` — precondición de `npx cap add`, que
  falla si `webDir` no existe todavía).
- `npx cap add android` — genera `android/`.
- Network security config: crear
  `android/app/src/main/res/xml/network_security_config.xml`
  permitiendo cleartext (`<base-config cleartextTrafficPermitted="true">`),
  y referenciarlo desde `android/app/src/main/AndroidManifest.xml` vía
  `android:networkSecurityConfig="@xml/network_security_config"` en la
  etiqueta `<application>`.
- `.gitignore`: agregar las entradas de `00-overview.md` § T3
  (`android/app/build/`, `android/.gradle/`, `android/local.properties`,
  `android/app/release/`, `*.keystore`, `*.jks`).
- `npx cap sync android` — confirma que la config se propaga
  correctamente al proyecto nativo.

## Dependencies
Ninguna en código (independiente de T1/T2), pero conceptualmente se
apoya en T1 (la app instalada necesita `VITE_API_BASE_URL` seteada al
buildear para poder hablar con un backend real) — documentar esa
relación en el paso de build de T4, no bloquear T3 en T1 en el código.

## Done When
- TC-005/TC-006 pasan.
- `git status` después de `npx cap add android` + `npx cap sync
  android` no muestra ningún artifact de build (`android/app/build/`,
  etc.) como untracked — el `.gitignore` los cubre correctamente.
- Este entorno NO tiene Android SDK/Gradle/Android Studio — no se
  intenta compilar el APK acá (`./gradlew assembleDebug` fallaría sin
  el SDK); esa verificación es manual, parte de T4.

## Verifiability
INTEGRATION (estructural, sin SDK) — nuevo
`tests/integration/infra/capacitor_config.test.py` (dominio `infra`,
mismo criterio que otros chequeos de configuración de entorno en ese
dominio) que confirma: `capacitor.config.ts` existe y tiene
`webDir: "dist"`/el `appId` esperado; `android/app/src/main/
AndroidManifest.xml` referencia el network security config;
`android/app/src/main/res/xml/network_security_config.xml` permite
cleartext. No requiere el SDK — son chequeos de contenido de archivo.
