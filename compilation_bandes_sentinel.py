import os
from qgis.core import QgsProject, QgsRasterLayer
import processing

def compiler_sentinel_l2a_gdal_strict_10m(dossier_safe, dossier_sortie):
    """
    Fouille l'arborescence complète d'un produit Sentinel-2.
    Rééchantillonne B11/B12 STRICTEMENT à 10m en X et Y avant empilement.
    """
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
        
    print(f"--- Traitement du produit L2A : {os.path.basename(dossier_safe)} ---")
    
    chemins_bandes = {}
    bandes_recherchees = ["B02", "B03", "B04", "B08", "B11", "B12"]
    
    for racine, dirs, fichiers in os.walk(dossier_safe):
        for fichier in fichiers:
            nom_minuscule = fichier.lower()
            if nom_minuscule.endswith(".jp2"):
                if "tci" in nom_minuscule or "pvi" in nom_minuscule or "msk" in nom_minuscule:
                    continue
                    
                for b in bandes_recherchees:
                    b_minuscule = b.lower()
                    if b_minuscule in nom_minuscule:
                        if "r10m" in racine.lower() or "r20m" in racine.lower():
                            chemins_bandes[b] = os.path.join(racine, fichier)
                        elif b not in chemins_bandes:
                            chemins_bandes[b] = os.path.join(racine, fichier)

    bandes_manquantes = [b for b in bandes_recherchees if b not in chemins_bandes]
    if bandes_manquantes:
        print(f"Erreur : Impossible de localiser les bandes suivantes : {bandes_manquantes}")
        return

    print("Toutes les bandes nécessaires ont été localisées avec succès !")
    bandes_finales_pour_stack = []
    fichiers_temporaires_a_nettoyer = []

    # 2. Rééchantillonnage STRICT à 10m avec XRES et YRES
    for b in bandes_recherchees:
        chemin_origine = chemins_bandes[b]
        
        if b in ["B11", "B12"]:
            print(f"Rééchantillonnage de la bande {b} (Pixels forcés à 10m)...")
            fichier_resampled = os.path.join(dossier_sortie, f"temp_resampled_{b}_10m.tif")
            
            parametres_warp = {
                'INPUT': chemin_origine,
                'XRES': 10,       # Résolution stricte en X (10 mètres)
                'YRES': 10,       # Résolution stricte en Y (10 mètres)
                'RESAMPLING': 1,   # 1 = Bilinéaire
                'OUTPUT': fichier_resampled
            }
            processing.run("gdal:warpreproject", parametres_warp)
            bandes_finales_pour_stack.append(fichier_resampled)
            fichiers_temporaires_a_nettoyer.append(fichier_resampled)
        else:
            bandes_finales_pour_stack.append(chemin_origine)

    # 3. Compilation des bandes
    vrt_temporaire = os.path.join(dossier_sortie, "stack_temporaire.vrt")
    tiff_final = os.path.join(dossier_sortie, "image_compilee_10m_strict.tif")
    
    print("Création du fichier virtuel d'empilement (VRT)...")
    processing.run("gdal:buildvirtualraster", {
        'INPUT': bandes_finales_pour_stack,
        'SEPARATE': True,
        'OUTPUT': vrt_temporaire
    })
    
    print("Exportation finale vers le fichier GeoTIFF multicouche...")
    processing.run("gdal:translate", {
        'INPUT': vrt_temporaire,
        'OUTPUT': tiff_final
    })
    
    # 4. Nettoyage des fichiers temporaires
    print("Nettoyage des fichiers intermédiaires...")
    if os.path.exists(vrt_temporaire):
        os.remove(vrt_temporaire)
    for f_temp in fichiers_temporaires_a_nettoyer:
        if os.path.exists(f_temp):
            os.remove(f_temp)
        
    # 5. Chargement dans l'interface QGIS
    if os.path.exists(tiff_final):
        couche = QgsRasterLayer(tiff_final, "Sentinel-2 Composite Strict (10m)")
        QgsProject.instance().addMapLayer(couche)
        print(f"Traitement terminé ! Fichier 10m vérifié ici : {tiff_final}")
    else:
        print("Erreur critique lors de la génération du TIFF final.")

# --- CONFIGURATION DE VOS CHEMINS ---
DOSSIER_SAFE_INPUT = r"D:\Sentinel2\S2A_MSIL2A_20200127T093241_N0500_R136_T32NQK_20230515T044541.SAFE"
DOSSIER_SORTIE = r"D:\Sentinel2\sortie"

# Lancement du traitement corrigé
compiler_sentinel_l2a_gdal_strict_10m(DOSSIER_SAFE_INPUT, DOSSIER_SORTIE)
