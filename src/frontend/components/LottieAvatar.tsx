import { Lottie } from "lottie-react";

export interface LottieAvatarProps {
  src: string;
  loop?: boolean;
  className?: string;
}

/** Reproductor Lottie compartido (spec `avatares-economia`, REQ-005):
 * reproduce la animación de una raza a partir de su `lottie_url`
 * (URL o path de texto plano), sin conocer nada de la lógica de negocio
 * de avatares/créditos — puramente presentacional, mismo criterio ya
 * establecido para `PageHeader`/`StatCard`/`EmptyState`
 * (`rediseno-ux-ui/sistema-visual`). Nunca importa nada de
 * `src/frontend/api/*` (constraint de la spec).
 *
 * `lottie-react`'s `<Lottie src=.../>` acepta tanto una URL/path (la
 * fetchea y parsea sola) como un objeto de animación ya parseado —
 * cubre las dos formas que puede tener `AvatarPersonaje.lottie_url` sin
 * que este componente tenga que decidir entre fetch/import él mismo. */
export function LottieAvatar({ src, loop = true, className }: LottieAvatarProps) {
  return <Lottie src={src} loop={loop} autoplay className={className} />;
}
