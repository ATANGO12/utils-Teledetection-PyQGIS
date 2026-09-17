# utils-Teledetection-PyQGIS
Scripts Python pour l'automatisation des traitements d'images satellites dans QGIS.
# Outils de Télédétection avec PyQGIS

Ce dépôt contient des scripts Python développés pour automatiser le prétraitement des données d'observation de la Terre directement dans la console de QGIS.

## Script : Compilation et Rééchantillonnage Sentinel-2 (10m)

Ce script (`compiler_sentinel2_10m.py`) permet de :
* **Explorer automatiquement** l'arborescence complexe d'un produit Copernicus Sentinel-2 L2A (dossiers `.SAFE`).
* **Isoler les bandes spectrales** requises pour l'analyse environnementale (`B02`, `B03`, `B04`, `B08`, `B11`, `B12`).
* **Gérer la disparité spatiale** en rééchantillant strictement à **10 mètres** (interpolation bilinéaire) les bandes SWIR `B11` et `B12` natives à 20m.
* **Empiler les couches (Stacking)** dans l'ordre spectral pour générer un fichier GeoTIFF multicouche unique.
* **Optimiser le stockage** en gérant le processus via un raster virtuel (VRT) et en nettoyant automatiquement les fichiers intermédiaires après traitement.
