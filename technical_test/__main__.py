"""
Orquestador de scripts de análisis de datos.

Permite ejecutar todos los análisis disponibles o seleccionar específicamente cuáles ejecutar.

Uso:
    python -m technical_test                    # Ejecuta todos los análisis
    python -m technical_test --select 1,5       # Ejecuta análisis 01 y 05
    python -m technical_test --list             # Lista análisis disponibles
    python -m technical_test --interactive      # Modo interactivo (menú)
"""

import os
import sys
import importlib
import argparse
from pathlib import Path

# Análisis disponibles con descripción
ANALYSIS_SCRIPTS = {
    "01": {
        "module": "technical_test.answers.01_top_products",
        "name": "Top Productos y Categorías",
        "description": "Análisis de las categorías y productos más vendidos por ingresos y volumen",
    },
    "02": {
        "module": "technical_test.answers.02_customer_pain_points",
        "name": "Puntos de Dolor del Cliente",
        "description": "Identificación de productos problémáticos y categorías con peor rating",
    },
    "03": {
        "module": "technical_test.answers.03_customer_segmentation",
        "name": "Segmentación de Clientes RFM",
        "description": "Análisis RFM con KMeans para identificar clientes fieles, en riesgo, inactivos y nuevos",
    },
    "05": {
        "module": "technical_test.answers.05_store_location",
        "name": "Ubicación Óptima de Tienda",
        "description": "Análisis de ciudades, densidad de clientes y ubicación óptima en São Paulo con mapa interactivo",
    },
    "06": {
        "module": "technical_test.answers.06_knowledge_base",
        "name": "Base de Conocimiento de Productos",
        "description": "Base de conocimiento simulada con descripciones atractivas y precios reales de los 3 productos top",
    },
    "07": {
        "module": "technical_test.answers.07_prompts",
        "name": "System Prompts Hiper-Personalizados",
        "description": "Genera 3 System Prompts para LLM con datos reales del dataset: cliente joven digital, mayor conservador con queja, y VIP corporativo",
    },
}


def print_header():
    """Imprime encabezado del orquestador."""
    print("\n" + "=" * 80)
    print("  ORQUESTADOR DE ANÁLISIS DE DATOS - PRUEBA TÉCNICA PROTECCIÓN".center(80))
    print("=" * 80 + "\n")


def print_available_scripts():
    """Lista todos los análisis disponibles."""
    print("📊 ANÁLISIS DISPONIBLES:\n")
    for code, info in sorted(ANALYSIS_SCRIPTS.items()):
        print(f"  [{code}] {info['name']}")
        print(f"       {info['description']}\n")


def execute_script(script_code):
    """Ejecuta un script de análisis específico."""
    if script_code not in ANALYSIS_SCRIPTS:
        print(f"  ❌ Código '{script_code}' no válido", file=sys.stderr)
        return False

    info = ANALYSIS_SCRIPTS[script_code]
    print(f"\n{'─' * 80}")
    print(f"  Ejecutando [{script_code}] {info['name']}...")
    print(f"{'─' * 80}\n")

    try:
        module = importlib.import_module(info["module"])
        print(f"\n✓ [{script_code}] {info['name']} completado exitosamente\n")
        return True
    except Exception as e:
        print(f"\n❌ Error ejecutando [{script_code}]: {str(e)}\n", file=sys.stderr)
        return False


def interactive_mode():
    """Modo interactivo con menú."""
    print_available_scripts()

    print("OPCIONES:")
    print("  [a] Ejecutar TODOS los análisis")
    print("  [s] Seleccionar análisis específicos")
    print("  [q] Salir\n")

    choice = input("Selecciona una opción (a/s/q): ").strip().lower()

    if choice == "a":
        scripts_to_run = sorted(ANALYSIS_SCRIPTS.keys())
    elif choice == "s":
        print("\nIngresa los códigos separados por comas (ej: 01,05):")
        selection = input("Códigos: ").strip()
        scripts_to_run = [s.strip() for s in selection.split(",")]
    elif choice == "q":
        print("Saliendo...")
        return False
    else:
        print("Opción no válida")
        return False

    # Ejecutar scripts seleccionados
    results = {}
    for script_code in scripts_to_run:
        results[script_code] = execute_script(script_code)

    # Resumen
    print("\n" + "=" * 80)
    print("  RESUMEN".center(80))
    print("=" * 80)
    total = len(results)
    successful = sum(1 for v in results.values() if v)
    print(f"\n  Total: {total} | Exitosos: {successful} | Errores: {total - successful}\n")

    return True


def main():
    """Función principal del orquestador."""
    parser = argparse.ArgumentParser(
        description="Orquestador de análisis de datos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python -m technical_test              # Ejecuta todos (por defecto)
  python -m technical_test --list       # Lista análisis disponibles
  python -m technical_test --select 1,5 # Ejecuta análisis 01 y 05
  python -m technical_test --interactive # Modo menú interactivo
        """,
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista todos los análisis disponibles",
    )
    parser.add_argument(
        "--select",
        type=str,
        help="Códigos de análisis a ejecutar, separados por comas (ej: 01,05)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Modo interactivo con menú",
    )

    args = parser.parse_args()

    print_header()

    # Mostrar lista
    if args.list:
        print_available_scripts()
        return

    # Modo interactivo
    if args.interactive:
        interactive_mode()
        return

    # Obtener scripts a ejecutar
    if args.select:
        scripts_to_run = [s.strip() for s in args.select.split(",")]
    else:
        # Por defecto: ejecutar todos
        scripts_to_run = sorted(ANALYSIS_SCRIPTS.keys())

    # Ejecutar scripts
    results = {}
    for script_code in scripts_to_run:
        results[script_code] = execute_script(script_code)

    # Resumen final
    print("\n" + "=" * 80)
    print("  RESUMEN FINAL".center(80))
    print("=" * 80)
    total = len(results)
    successful = sum(1 for v in results.values() if v)
    failed = total - successful

    print(f"\n  Total ejecutados: {total}")
    print(f"  ✓ Exitosos: {successful}")
    if failed > 0:
        print(f"  ❌ Errores: {failed}")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
