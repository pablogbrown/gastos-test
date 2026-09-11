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
  usuarioId: string;
  miembros: Miembro[];
}

/** Pantalla "Gastos" (REQ-001, REQ-002, REQ-003, REQ-008): formulario de
 * alta de un gasto y su historial. "Todos los miembros" viene
 * preseleccionado (REQ-003); el historial no filtra por `activo` — la
 * API ya incluye gastos de miembros desactivados (REQ-008/TC-010). */
export function Gastos({ casaId, usuarioId, miembros }: GastosProps) {
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
        listarCategorias(casaId, usuarioId),
        listarGastos(casaId, usuarioId),
      ]);
      setCategorias(listaCategorias);
      setGastos(historial);
    } catch (err) {
      setError(esApiError(err) ? err.detail : "No se pudo cargar los gastos.");
    }
  }, [casaId, usuarioId]);

  useEffect(() => {
    void cargar();
  }, [cargar]);

  async function handleCrearCategoria(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await crearCategoria(casaId, nuevaCategoria, usuarioId);
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
      await registrarGasto(
        casaId,
        {
          descripcion,
          importe,
          fecha,
          categoriaId,
          participantes: todosLosMiembros ? undefined : seleccionados,
        },
        usuarioId
      );
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
    <section aria-label="Gastos">
      {error && <p role="alert">{error}</p>}

      <form onSubmit={handleCrearCategoria} aria-label="Nueva categoría">
        <label htmlFor="nueva-categoria">Nueva categoría</label>
        <input
          id="nueva-categoria"
          value={nuevaCategoria}
          onChange={(event) => setNuevaCategoria(event.target.value)}
        />
        <button type="submit">Crear categoría</button>
      </form>

      <form onSubmit={handleRegistrarGasto} aria-label="Nuevo gasto">
        <label htmlFor="descripcion-gasto">Descripción</label>
        <input
          id="descripcion-gasto"
          value={descripcion}
          onChange={(event) => setDescripcion(event.target.value)}
        />

        <label htmlFor="importe-gasto">Importe</label>
        <input
          id="importe-gasto"
          type="number"
          value={importe}
          onChange={(event) => setImporte(event.target.value)}
        />

        <label htmlFor="fecha-gasto">Fecha</label>
        <input
          id="fecha-gasto"
          type="date"
          value={fecha}
          onChange={(event) => setFecha(event.target.value)}
        />

        <label htmlFor="categoria-gasto">Categoría</label>
        <select
          id="categoria-gasto"
          value={categoriaId}
          onChange={(event) => setCategoriaId(event.target.value)}
        >
          <option value="">Seleccionar categoría</option>
          {categorias.map((categoria) => (
            <option key={categoria.id} value={categoria.id}>
              {categoria.nombre}
            </option>
          ))}
        </select>

        <label htmlFor="todos-los-miembros">
          <input
            id="todos-los-miembros"
            type="checkbox"
            checked={todosLosMiembros}
            onChange={(event) => setTodosLosMiembros(event.target.checked)}
          />
          Todos los miembros
        </label>

        {!todosLosMiembros && (
          <fieldset aria-label="Participantes">
            {miembros.map((miembro) => (
              <label key={miembro.id}>
                <input
                  type="checkbox"
                  checked={seleccionados.includes(miembro.id)}
                  onChange={() => toggleParticipante(miembro.id)}
                />
                {miembro.nombre}
              </label>
            ))}
          </fieldset>
        )}

        <button type="submit">Registrar gasto</button>
      </form>

      <table aria-label="Historial de gastos">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Descripción</th>
            <th>Importe</th>
            <th>Categoría</th>
          </tr>
        </thead>
        <tbody>
          {gastos.map((gasto) => (
            <tr key={gasto.id}>
              <td>{gasto.fecha}</td>
              <td>{gasto.descripcion}</td>
              <td>{gasto.importe}</td>
              <td>{nombreCategoria(gasto.categoria_id)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
