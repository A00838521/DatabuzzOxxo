# ====================
# 1. LIBRERÍAS
# ====================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, 
    precision_recall_curve, 
    average_precision_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score
)
from sklearn.utils import resample
from category_encoders import TargetEncoder

# ====================
# 2. CARGA Y PREPARACIÓN DE DATOS
# ====================
df = pd.read_csv("datos_limpiados.csv")
df["exito"] = (df["VENTA_TOTAL"] > df["Meta_venta"]).astype(int)

df_minority = df[df.exito == 0]
df_majority = df[df.exito == 1]

cols_numericas = [
    "MTS2VENTAS_NUM", "LATITUD_NUM", "LONGITUD_NUM", "Meta_venta"
]
cols_categoricas = [
    "NIVELSOCIOECONOMICO_DES", "ENTORNO_DES",
    "SEGMENTO_MAESTRO_DESC", "LID_UBICACION_TIENDA"
]

df_majority_downsampled = resample(df_majority,
                                   replace=False,
                                   n_samples=1000,
                                   random_state=42)

df_balanced = pd.concat([df_minority, df_majority_downsampled])
X = df_balanced[cols_numericas + cols_categoricas]
y = df_balanced["exito"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# ====================
# 3. PREPROCESAMIENTO
# ====================
preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", IterativeImputer(random_state=42)),
        ("scaler", RobustScaler())
    ]), cols_numericas),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", TargetEncoder())  # Puedes usar CatBoostEncoder si prefieres
    ]), cols_categoricas)
])

pipeline = Pipeline(steps=[
    ("pre", preprocessor),
    ("clf", RandomForestClassifier(
        random_state=42,
        class_weight="balanced_subsample",
        n_jobs=-1
    ))
])

# ====================
# 4. GRID SEARCH
# ====================
param_grid = {
    "clf__n_estimators": [100, 200],
    "clf__max_depth": [5, 10, 15],
    "clf__min_samples_split": [10, 20],
    "clf__min_samples_leaf": [5, 10],
    "clf__max_features": [0.3, 0.5]
}

grid = GridSearchCV(pipeline, param_grid, cv=5, scoring="accuracy", n_jobs=-1)
grid.fit(X_train, y_train)

modelo = grid.best_estimator_
print("Mejores parámetros encontrados:")
print(grid.best_params_)

# ====================
# 5. EVALUACIÓN DEL MODELO
# ====================
y_pred = modelo.predict(X_test)
y_proba = modelo.predict_proba(X_test)[:, 1]

print("\n== Clasificación ==")
print(classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

precision, recall, _ = precision_recall_curve(y_test, y_proba)
avg_precision = average_precision_score(y_test, y_proba)

plt.figure(figsize=(6, 4))
plt.plot(recall, precision, marker='.', label=f'AP = {avg_precision:.2f}')
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Curva Precision-Recall")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Validación cruzada con mejor modelo
scores = cross_val_score(modelo, X, y, cv=5, scoring="accuracy")
print("Accuracy promedio CV:", scores.mean())

# ====================
# 6. FUNCIÓN PARA HACER PREDICCIONES
# ====================
def predecir_con_dataframe(modelo, df, cols_numericas, cols_categoricas):
    columnas_requeridas = cols_numericas + cols_categoricas
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"El DataFrame no contiene la columna requerida: {col}")

    datos_para_prediccion = df[columnas_requeridas].copy()

    predicciones = modelo.predict(datos_para_prediccion)
    probabilidades = modelo.predict_proba(datos_para_prediccion)

    resultados = df.copy()
    resultados['Prediccion'] = predicciones
    resultados['Probabilidad_Cumplir'] = probabilidades[:, 1]
    resultados['Probabilidad_No_Cumplir'] = probabilidades[:, 0]
    resultados['Resultado'] = np.where(predicciones == 1, 'Cumplirá', 'No cumplirá')

    return resultados

# ====================
# 7. CARGA DEL CSV DE PRUEBA Y PREDICCIÓN
# ====================
meta_venta_data = {
    'ENTORNO_DES': ['Base', 'Hogar', 'Peatonal', 'Receso'],
    'Meta_venta': [480000, 490000, 420000, 516000]
}
df_meta_venta = pd.DataFrame(meta_venta_data)

def cargar_y_preparar_datos(ruta_csv, df_meta_venta):
    df_tiendas = pd.read_csv(ruta_csv)

    column_rename = {
        'MTS2VENTAS': 'MTS2VENTAS_NUM',
        'PUERTASREFI': 'PUERTASREFRIG_NUM',
        'CAJONESEST': 'CAJONESESTACIONAMIENTO_NUM',
        'LATITUD_NUN': 'LATITUD_NUM',
        'LONGITUD_NI': 'LONGITUD_NUM',
        'SEGMENTO_N': 'SEGMENTO_MAESTRO_DESC',
        'ID_USICACIC': 'LID_UBICACION_TIENDA'
    }
    df_tiendas = df_tiendas.rename(columns=column_rename)

    df_completo = pd.merge(
        df_tiendas,
        df_meta_venta,
        on='ENTORNO_DES',
        how='left'
    )

    if df_completo['Meta_venta'].isnull().any():
        entornos_faltantes = df_completo[df_completo['Meta_venta'].isnull()]['ENTORNO_DES'].unique()
        raise ValueError(f"Faltan metas de venta para los entornos: {entornos_faltantes}")

    return df_completo

ruta_csv = "/content/oxxo_dataset_final.csv"
df_tiendas_completo = cargar_y_preparar_datos(ruta_csv, df_meta_venta)

print("\n=== Verificación de Data Leakage ===")
print("Columnas en datos de prueba:", df_tiendas_completo.columns.tolist())

resultados = predecir_con_dataframe(
    modelo=modelo,
    df=df_tiendas_completo,
    cols_numericas=cols_numericas,
    cols_categoricas=cols_categoricas
)

print("\n=== Primeras 5 predicciones ===")
print(resultados[['TIENDA_ID', 'ENTORNO_DES', 'Meta_venta', 'Resultado', 'Probabilidad_Cumplir']].head())

# ====================
# 8. ANÁLISIS FINAL
# ====================
confianza_positiva = resultados[resultados['Resultado'] == 'Cumplirá']['Probabilidad_Cumplir'].mean()
confianza_negativa = resultados[resultados['Resultado'] == 'No cumplirá']['Probabilidad_No_Cumplir'].mean()
print(f"\nConfianza promedio 'Cumplirá': {confianza_positiva:.1%}")
print(f"Confianza promedio 'No cumplirá': {confianza_negativa:.1%}")

predicciones_seguras = resultados[
    (resultados['Probabilidad_Cumplir'] > 0.7) |
    (resultados['Probabilidad_No_Cumplir'] > 0.7)
].shape[0] / resultados.shape[0]
print(f"Porcentaje de predicciones seguras (>70%): {predicciones_seguras:.1%}")

print("\nDistribución por entorno:")
print(resultados.groupby('ENTORNO_DES')['Resultado'].value_counts(normalize=True).unstack().fillna(0))

# ====================
# 9. VISUALIZACIÓN
# ====================
plt.figure(figsize=(15, 5))
plt.subplot(1, 2, 1)
plt.hist(resultados['Probabilidad_Cumplir'], bins=20, color='skyblue', edgecolor='black')
plt.title('Distribución de Probabilidades de Cumplir')
plt.xlabel('Probabilidad')
plt.ylabel('Frecuencia')

plt.subplot(1, 2, 2)
resultados['Resultado'].value_counts().plot(kind='bar', color=['green', 'red'])
plt.title('Distribución de Predicciones')
plt.xticks(rotation=0)

plt.tight_layout()
plt.show()
