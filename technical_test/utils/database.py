"""
Módulo de acceso a base de datos SQL para los archivos CSV.

Este módulo proporciona una interfaz SQL para acceder a los archivos CSV
de la carpeta 'data' como si fueran tablas de una base de datos.

Utiliza pandasql para ejecutar consultas SQL sobre DataFrames de pandas.

Ejemplo de uso:
    from src.00_database import Database
    
    db = Database()
    
    # Ejecutar una consulta
    resultado = db.query('''
        SELECT customer_id, COUNT(*) as total_pedidos
        FROM orders_dataset
        GROUP BY customer_id
    ''')
    
    # Obtener resultados como DataFrame de pandas
    print(resultado)
    
    # Obtener resultados como lista de diccionarios
    registros = resultado.to_dict('records')
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, cast
import pandas as pd
import pandasql as pdsql


class Database:
    """
    Clase que proporciona acceso SQL a los archivos CSV.
    
    Cada archivo CSV en la carpeta 'data' se trata como una tabla.
    Las consultas SQL se ejecutan contra estos archivos usando pandasql.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Inicializa la base de datos y carga los archivos CSV.
        
        Args:
            data_path: Ruta a la carpeta con los archivos CSV.
                      Si no se especifica, busca la carpeta 'data' 
                      en el directorio padre del proyecto.
        """
        if data_path is None:
            # Obtener la ruta de la carpeta 'data' automáticamente
            current_dir = Path(__file__).parent.parent.parent
            self.data_path = current_dir / "data"
        else:
            self.data_path = Path(data_path)
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Carpeta de datos no encontrada: {self.data_path}")
        
        # Diccionario para almacenar los DataFrames
        self.tables: Dict[str, pd.DataFrame] = {}
        
        # Cargar las tablas desde los archivos CSV
        self._load_tables()
    
    def _load_tables(self) -> None:
        """Carga todos los archivos CSV como DataFrames."""
        csv_files = list(self.data_path.glob("*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No se encontraron archivos CSV en {self.data_path}")
        
        for csv_file in csv_files:
            table_name = csv_file.stem  # Nombre del archivo sin extensión
            self.tables[table_name] = pd.read_csv(csv_file)
            print(f"✓ Tabla '{table_name}' cargada ({len(self.tables[table_name])} filas)")
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL sobre los DataFrames.
        
        Args:
            sql: Consulta SQL a ejecutar.
        
        Returns:
            DataFrame de pandas con los resultados.
            
        Ejemplo:
            resultado = db.query("SELECT * FROM customers_dataset LIMIT 5")
        """
        try:
            # Ejecutar la consulta SQL usando pandasql
            result = pdsql.sqldf(sql, self.tables)
            return cast(pd.DataFrame, result)
        except Exception as e:
            raise Exception(f"Error en la consulta SQL: {str(e)}")
    
    def fetch_all(self, sql: str) -> List[Any]:
        """
        Ejecuta una consulta y devuelve todos los resultados como diccionarios.
        
        Args:
            sql: Consulta SQL a ejecutar.
        
        Returns:
            Lista de diccionarios con los resultados.
            
        Ejemplo:
            resultados = db.fetch_all("SELECT * FROM customers_dataset LIMIT 5")
        """
        resultado = self.query(sql)
        return resultado.to_dict('records')
    
    def fetch_one(self, sql: str) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta y devuelve el primer resultado.
        
        Args:
            sql: Consulta SQL a ejecutar.
        
        Returns:
            Primer registro como diccionario, o None si no hay resultados.
        """
        resultado = self.query(sql)
        if len(resultado) > 0:
            return cast(Dict[str, Any], resultado.iloc[0].to_dict())
        return None
    
    def to_dataframe(self, sql: str) -> pd.DataFrame:
        """
        Ejecuta una consulta y devuelve los resultados como DataFrame de pandas.
        
        Args:
            sql: Consulta SQL a ejecutar.
        
        Returns:
            DataFrame de pandas con los resultados.
            
        Ejemplo:
            df = db.to_dataframe("SELECT * FROM orders_dataset")
        """
        return self.query(sql)
    
    def get_tables(self) -> List[str]:
        """
        Obtiene la lista de todas las tablas disponibles.
        
        Returns:
            Lista con los nombres de las tablas.
        """
        return list(self.tables.keys())
    
    def describe_table(self, table_name: str) -> pd.DataFrame:
        """
        Obtiene la estructura (columnas y tipos) de una tabla.
        
        Args:
            table_name: Nombre de la tabla.
        
        Returns:
            DataFrame con información de las columnas.
            
        Ejemplo:
            estructura = db.describe_table("customers_dataset")
        """
        if table_name not in self.tables:
            raise ValueError(f"Tabla '{table_name}' no encontrada")
        
        df = self.tables[table_name]
        info = pd.DataFrame({
            'Column_Name': df.columns,
            'Data_Type': df.dtypes.astype(str),
            'Non_Null_Count': df.count(),
            'Null_Count': df.isnull().sum()
        })
        return info
    
    def get_table(self, table_name: str) -> pd.DataFrame:
        """
        Obtiene un DataFrame completo de una tabla.
        
        Args:
            table_name: Nombre de la tabla.
        
        Returns:
            DataFrame con todos los datos de la tabla.
            
        Ejemplo:
            df_customers = db.get_table("customers_dataset")
        """
        if table_name not in self.tables:
            raise ValueError(f"Tabla '{table_name}' no encontrada")
        return self.tables[table_name]
    
    def close(self) -> None:
        """Cierra la conexión (en este caso, limpia los DataFrames)."""
        self.tables.clear()
    
    def __enter__(self):
        """Soporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        self.close()


# Instancia global de la base de datos para uso conveniente
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """
    Obtiene la instancia global de la base de datos.
    Si no existe, la crea.
    
    Returns:
        Instancia de Database.
        
    Ejemplo:
        from src.00_database import get_database
        db = get_database()
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


if __name__ == "__main__":
    # Script de ejemplo
    print("=" * 60)
    print("Inicializando base de datos...")
    print("=" * 60)
    
    db = Database()
    
    print("\nTablas disponibles:")
    for tabla in db.get_tables():
        print(f"  - {tabla}")
    
    print("\n" + "=" * 60)
    print("Estructura de la tabla 'customers_dataset':")
    print("=" * 60)
    print(db.describe_table("customers_dataset"))
    
    print("\n" + "=" * 60)
    print("Ejemplo de consulta:")
    print("=" * 60)
    print("SELECT COUNT(*) as total_clientes FROM customers_dataset")
    resultado = db.query("SELECT COUNT(*) as total_clientes FROM customers_dataset")
    print(resultado)
    
    print("\n" + "=" * 60)
    print("Ejemplo de JOIN:")
    print("=" * 60)
    print("SELECT o.order_id, c.customer_city, COUNT(*) as items")
    print("FROM orders_dataset o")
    print("JOIN customers_dataset c ON o.customer_id = c.customer_id")
    print("GROUP BY o.order_id, c.customer_city")
    print("LIMIT 5")
    resultado = db.query("""
        SELECT o.order_id, c.customer_city, COUNT(*) as items
        FROM orders_dataset o
        JOIN customers_dataset c ON o.customer_id = c.customer_id
        GROUP BY o.order_id, c.customer_city
        LIMIT 5
    """)
    print(resultado)
    
    print("\n" + "=" * 60)
    print("Conexión exitosa!")
    print("=" * 60)
