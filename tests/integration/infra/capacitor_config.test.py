"""T3 (android-capacitor-app) — TC-005/TC-006: chequeos estructurales
(sin Android SDK/Gradle) de que el proyecto Android generado por
Capacitor tiene la configuracion esperada.

Este entorno no tiene Android SDK/Gradle/Android Studio instalados --
NO intenta compilar el APK (`./gradlew assembleDebug` fallaria sin el
SDK). Solo valida contenido de archivos ya generados/versionados por
`npx cap add android` + `npx cap sync android` (dominio `infra`, mismo
criterio que otros chequeos de configuracion de entorno en ese
dominio -- ver `.nybo/memory/domains/infra.md`).
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_tc005_capacitor_config_ts_tiene_appid_appname_y_webdir():
    config = (REPO_ROOT / "capacitor.config.ts").read_text(encoding="utf-8")

    assert 'appId: "com.taskia.app"' in config
    assert 'appName: "taskia"' in config
    assert 'webDir: "dist"' in config


def test_tc005_android_project_existe_y_referencia_capacitor():
    android_dir = REPO_ROOT / "android"
    assert android_dir.is_dir(), "npx cap add android no genero android/"
    assert (android_dir / "app").is_dir()
    assert (android_dir / "app" / "src" / "main" / "AndroidManifest.xml").is_file()


def test_tc006_network_security_config_permite_cleartext():
    nsc_path = (
        REPO_ROOT
        / "android"
        / "app"
        / "src"
        / "main"
        / "res"
        / "xml"
        / "network_security_config.xml"
    )
    assert nsc_path.is_file()

    contenido = nsc_path.read_text(encoding="utf-8")
    assert re.search(
        r'cleartextTrafficPermitted\s*=\s*"true"', contenido
    ), "network_security_config.xml no permite cleartext traffic"


def test_tc006_android_manifest_referencia_el_network_security_config():
    manifest_path = (
        REPO_ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
    )
    contenido = manifest_path.read_text(encoding="utf-8")

    assert 'android:networkSecurityConfig="@xml/network_security_config"' in contenido


def test_gitignore_cubre_los_artifacts_de_build_de_android():
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    entradas_esperadas = [
        "android/app/build/",
        "android/.gradle/",
        "android/local.properties",
        "android/app/release/",
        "*.keystore",
        "*.jks",
    ]
    for entrada in entradas_esperadas:
        assert entrada in gitignore, f"falta {entrada!r} en .gitignore"
