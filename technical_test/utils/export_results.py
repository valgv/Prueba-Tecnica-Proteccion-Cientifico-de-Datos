"""Módulo para exportar resultados de consultas SQL a archivos CSV, JSON e imágenes.

Proporciona funciones para guardar DataFrames en archivos CSV,
diccionarios/listas en JSON,
y gráficos de matplotlib en archivos de imagen,
con manejo automático de directorios.
"""

from pathlib import Path
from typing import Optional, Union, Any
import json
import pandas as pd
import matplotlib.pyplot as plt


def save_to_csv(
    dataframe: pd.DataFrame,
    file: str = "resultado.csv",
    folder: str = "default",
    results_path: Optional[Union[str, Path]] = None
) -> Path:
    """
    Guarda un DataFrame en un archivo CSV.
    
    Crea automáticamente los directorios si no existen.
    
    Args:
        dataframe: DataFrame de pandas a guardar.
        file: Nombre del archivo CSV. Default: "resultado.csv"
        folder: Subcarpeta dentro de results/. Default: "default"
        results_path: Ruta base de la carpeta results/. 
                     Si es None, busca results/ en el directorio padre del proyecto.
    
    Returns:
        Path: Ruta completa del archivo guardado.
    
    Raises:
        ValueError: Si el nombre del archivo no tiene extensión .csv
        IOError: Si hay problemas al guardar el archivo.
    
    Ejemplo:
        from src.export_results import save_to_csv
        from src.database import Database
        
        db = Database()
        resultado = db.query("SELECT * FROM customers_dataset LIMIT 5")
        
        # Guarda en results/answer_01/top_clientes.csv
        ruta = save_to_csv(resultado, file="top_clientes.csv", folder="answer_01")
        print(f"Guardado en: {ruta}")
        
        # Guarda en results/default/datos.csv
        ruta = save_to_csv(resultado)
        print(f"Guardado en: {ruta}")
    """
    
    # Validar que el archivo tenga extensión .csv
    if not file.endswith(".csv"):
        raise ValueError(f"El nombre del archivo debe terminar en '.csv', recibido: {file}")
    
    # Determinar la ruta base de results/
    if results_path is None:
        # Buscar results/ en el directorio padre del proyecto
        current_dir = Path(__file__).parent.parent.parent
        results_path = current_dir / "results"
    else:
        results_path = Path(results_path)
    
    # Construir la ruta completa: results/folder/file
    full_path = results_path / folder / file
    
    # Crear los directorios si no existen
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar el DataFrame en CSV
    try:
        dataframe.to_csv(full_path, index=False, encoding='utf-8')
        print(f"✓ Archivo guardado en: {full_path}")
        return full_path
    
    except Exception as e:
        raise IOError(f"Error al guardar el archivo: {str(e)}")


def save_multiple_results(
    results: dict,
    results_path: Optional[Union[str, Path]] = None
) -> dict:
    """
    Guarda múltiples DataFrames en archivos CSV.
    
    Args:
        results: Diccionario donde:
                - key: carpeta (ej: "answer_01")
                - value: diccionario con {nombre_archivo: dataframe}
        
        results_path: Ruta base de results/. Si es None, busca en el padre.
    
    Returns:
        Diccionario con las rutas guardadas.
    
    Ejemplo:
        db = Database()
        
        resultados = {
            "analisis_01": {
                "clientes.csv": db.query("SELECT * FROM customers_dataset LIMIT 10"),
                "ordenes.csv": db.query("SELECT * FROM orders_dataset LIMIT 10")
            },
            "analisis_02": {
                "vendedores.csv": db.query("SELECT * FROM sellers_dataset LIMIT 10")
            }
        }
        
        rutas = save_multiple_results(resultados)
        for carpeta, archivos in rutas.items():
            print(f"Carpeta {carpeta}:")
            for archivo, ruta in archivos.items():
                print(f"  - {archivo}: {ruta}")
    """
    
    guardados = {}
    
    for folder, files_dict in results.items():
        guardados[folder] = {}
        
        for filename, dataframe in files_dict.items():
            ruta = save_to_csv(
                dataframe=dataframe,
                file=filename,
                folder=folder,
                results_path=results_path
            )
            guardados[folder][filename] = ruta
    
    return guardados


def save_to_json(
    data: Any,
    file: str = "resultado.json",
    folder: str = "default",
    results_path: Optional[Union[str, Path]] = None,
    indent: int = 2
) -> Path:
    """
    Guarda un diccionario o lista en un archivo JSON.
    
    Crea automáticamente los directorios si no existen.
    
    Args:
        data: Diccionario, lista o cualquier objeto serializable a JSON.
        file: Nombre del archivo JSON. Default: "resultado.json"
        folder: Subcarpeta dentro de results/. Default: "default"
        results_path: Ruta base de la carpeta results/. 
                     Si es None, busca results/ en el directorio padre del proyecto.
        indent: Espacios de indentación en el JSON. Default: 2
    
    Returns:
        Path: Ruta completa del archivo guardado.
    
    Raises:
        ValueError: Si el nombre del archivo no tiene extensión .json
        IOError: Si hay problemas al guardar el archivo.
    
    Ejemplo:
        from technical_test.utils.export_results import save_to_json
        
        # Guardar un diccionario
        datos = {
            "nombre": "Juan",
            "edad": 30,
            "hobbies": ["lectura", "cine", "viajes"]
        }
        
        ruta = save_to_json(datos, file="persona.json", folder="answer_06")
        print(f"Guardado en: {ruta}")
        
        # Guardar una lista
        lista_datos = [
            {"id": 1, "nombre": "Item 1"},
            {"id": 2, "nombre": "Item 2"}
        ]
        
        ruta = save_to_json(lista_datos, file="items.json", folder="answer_06")
        print(f"Guardado en: {ruta}")
    """
    
    # Validar que el archivo tenga extensión .json
    if not file.endswith(".json"):
        raise ValueError(f"El nombre del archivo debe terminar en '.json', recibido: {file}")
    
    # Determinar la ruta base de results/
    if results_path is None:
        # Buscar results/ en el directorio padre del proyecto
        current_dir = Path(__file__).parent.parent.parent
        results_path = current_dir / "results"
    else:
        results_path = Path(results_path)
    
    # Construir la ruta completa: results/folder/file
    full_path = results_path / folder / file
    
    # Crear los directorios si no existen
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar el JSON
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"✓ Archivo JSON guardado en: {full_path}")
        return full_path
    
    except Exception as e:
        raise IOError(f"Error al guardar el archivo JSON: {str(e)}")


def save_plot(
    figure,
    file: str = "grafico.png",
    folder: str = "default",
    results_path: Optional[Union[str, Path]] = None,
    dpi: int = 300,
    bbox_inches: str = "tight",
    format: Optional[str] = None
) -> Path:
    """
    Guarda un gráfico de matplotlib en un archivo de imagen.
    
    Crea automáticamente los directorios si no existen.
    
    Args:
        figure: Objeto Figure de matplotlib.
        file: Nombre del archivo de imagen. Default: "grafico.png"
        folder: Subcarpeta dentro de results/. Default: "default"
        results_path: Ruta base de la carpeta results/. 
                     Si es None, busca results/ en el directorio padre del proyecto.
        dpi: Resolución en puntos por pulgada. Default: 300
        bbox_inches: Control de márgenes. Default: "tight"
        format: Formato de imagen ('png', 'jpg', 'pdf', 'svg'). 
               Si es None, se deduce de la extensión del archivo.
    
    Returns:
        Path: Ruta completa del archivo guardado.
    
    Raises:
        ValueError: Si el nombre del archivo no tiene extensión de imagen válida.
        IOError: Si hay problemas al guardar el archivo.
    
    Ejemplo:
        import matplotlib.pyplot as plt
        from technical_test.utils.export_results import save_plot
        
        # Crear un gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title('Mi Gráfico')
        
        # Guardar en results/graficos/mi_grafico.png
        ruta = save_plot(fig, file="mi_grafico.png", folder="graficos")
        print(f"Gráfico guardado en: {ruta}")
        
        # Guardar en alta resolución como PDF
        ruta = save_plot(fig, file="mi_grafico.pdf", folder="graficos", dpi=300, format="pdf")
    """
    
    # Extensiones de imagen válidas
    valid_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.svg', '.gif', '.tiff'}
    file_extension = Path(file).suffix.lower()
    
    if file_extension not in valid_extensions:
        raise ValueError(
            f"Extensión de archivo inválida: {file_extension}. "
            f"Extensiones válidas: {', '.join(valid_extensions)}"
        )
    
    # Determinar la ruta base de results/
    if results_path is None:
        # Buscar results/ en el directorio padre del proyecto
        current_dir = Path(__file__).parent.parent.parent
        results_path = current_dir / "results"
    else:
        results_path = Path(results_path)
    
    # Construir la ruta completa: results/folder/file
    full_path = results_path / folder / file
    
    # Crear los directorios si no existen
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar el gráfico
    try:
        figure.savefig(
            full_path,
            dpi=dpi,
            bbox_inches=bbox_inches,
            format=format
        )
        print(f"✓ Gráfico guardado en: {full_path}")
        return full_path
    
    except Exception as e:
        raise IOError(f"Error al guardar el gráfico: {str(e)}")


def save_multiple_plots(
    plots: dict,
    results_path: Optional[Union[str, Path]] = None,
    dpi: int = 300,
    bbox_inches: str = "tight"
) -> dict:
    """
    Guarda múltiples gráficos de matplotlib en archivos de imagen.
    
    Args:
        plots: Diccionario donde:
               - key: carpeta (ej: "graficos_01")
               - value: diccionario con {nombre_archivo: figure de matplotlib}
        
        results_path: Ruta base de results/. Si es None, busca en el padre.
        dpi: Resolución en puntos por pulgada. Default: 300
        bbox_inches: Control de márgenes. Default: "tight"
    
    Returns:
        Diccionario con las rutas guardadas.
    
    Ejemplo:
        import matplotlib.pyplot as plt
        from technical_test.utils.export_results import save_multiple_plots
        
        # Crear gráficos
        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [1, 2, 3])
        
        fig2, ax2 = plt.subplots()
        ax2.bar([1, 2, 3], [1, 4, 2])
        
        graficos = {
            "analisis_01": {
                "linea.png": fig1,
                "barras.png": fig2
            },
            "analisis_02": {
                "scatter.png": fig1
            }
        }
        
        rutas = save_multiple_plots(graficos)
        for carpeta, archivos in rutas.items():
            print(f"Carpeta {carpeta}:")
            for archivo, ruta in archivos.items():
                print(f"  - {archivo}: {ruta}")
    """
    
    guardados = {}
    
    for folder, files_dict in plots.items():
        guardados[folder] = {}
        
        for filename, figure in files_dict.items():
            ruta = save_plot(
                figure=figure,
                file=filename,
                folder=folder,
                results_path=results_path,
                dpi=dpi,
                bbox_inches=bbox_inches
            )
            guardados[folder][filename] = ruta
    
    return guardados


if __name__ == "__main__":
    # Script de ejemplo
    print("=" * 60)
    print("Módulo de exportación de resultados")
    print("=" * 60)
    
    # Crear un DataFrame de ejemplo
    data = {
        'id': [1, 2, 3, 4, 5],
        'nombre': ['Ana', 'Bob', 'Carlos', 'Diana', 'Eduardo'],
        'edad': [25, 30, 35, 28, 32]
    }
    df_ejemplo = pd.DataFrame(data)
    
    print("\nDataFrame de ejemplo:")
    print(df_ejemplo)
    
    # Guardar en un archivo
    print("\n" + "=" * 60)
    print("Guardando en archivo CSV...")
    print("=" * 60)
    
    ruta = save_to_csv(
        dataframe=df_ejemplo,
        file="personas.csv",
        folder="test_export"
    )
    
    print(f"\nArchivo guardado en: {ruta}")
    print(f"Archivo existe: {ruta.exists()}")
    
    # Ejemplo con gráficos
    print("\n" + "=" * 60)
    print("Guardando gráficos...")
    print("=" * 60)
    
    # Crear un gráfico de líneas
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(df_ejemplo['id'], df_ejemplo['edad'], marker='o', linewidth=2, markersize=8)
    ax1.set_xlabel('ID')
    ax1.set_ylabel('Edad')
    ax1.set_title('Edad por ID')
    ax1.grid(True, alpha=0.3)
    
    # Guardar el gráfico
    ruta_grafico = save_plot(
        fig1,
        file="edad_por_id.png",
        folder="test_export"
    )
    print(f"Gráfico guardado en: {ruta_grafico}")
    
    # Crear un gráfico de barras
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.bar(df_ejemplo['nombre'], df_ejemplo['edad'], color='skyblue', edgecolor='navy')
    ax2.set_xlabel('Nombre')
    ax2.set_ylabel('Edad')
    ax2.set_title('Edad por Persona')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Guardar múltiples gráficos
    graficos = {
        "test_export": {
            "edad_por_personas.png": fig2,
            "edad_por_id_hires.pdf": fig1
        }
    }
    
    rutas_graficos = save_multiple_plots(graficos, dpi=300)
    print("\nGráficos guardados:")
    for carpeta, archivos in rutas_graficos.items():
        print(f"  Carpeta '{carpeta}':")
        for archivo, ruta in archivos.items():
            print(f"    - {archivo}: {ruta}")
