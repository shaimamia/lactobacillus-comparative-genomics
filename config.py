"""
Configuration du pipeline de génomique comparative
Lactobacillus bulgaricus - Version Python native
"""

# Informations du projet
PROJECT_NAME = "lactobacillus-comparative-genomics"
PROJECT_VERSION = "2.0"
AUTHOR = "[Votre Nom]"
ORGANISM = "Lactobacillus bulgaricus"

# Souches analysées
STRAINS = {
    "ATCC11842": {
        "accession": "GCF_000196515.1",
        "description": "Souche type de référence",
        "filename": "LB_ATCC11842.fna"
    },
    "DSM20081": {
        "accession": "GCF_000027045.1", 
        "description": "Souche commerciale",
        "filename": "LB_DSM20081.fna"
    },
    "CNCM1519": {
        "accession": "GCF_000006865.2",
        "description": "Souche probiotique",
        "filename": "LB_CNCM1519.fna"
    }
}

# Paramètres d'analyse
ANALYSIS_PARAMS = {
    "min_contig_length": 500,      # Longueur minimale des contigs à analyser
    "window_size": 1000,           # Taille de fenêtre pour analyses locales
    "similarity_threshold": 0.8,    # Seuil de similarité
    "gc_window": 100              # Fenêtre pour calcul GC local
}

# Dossiers
PATHS = {
    "genomes": "data/genomes",
    "analysis": "data/analysis", 
    "results": "data/results",
    "plots": "data/results/plots",
    "logs": "logs"
}

# URLs et paramètres de téléchargement
NCBI_BASE_URL = "https://ftp.ncbi.nlm.nih.gov/genomes/all"
DOWNLOAD_TIMEOUT = 300  # 5 minutes

# Paramètres de visualisation
PLOT_PARAMS = {
    "figsize": (12, 8),
    "dpi": 300,
    "style": "seaborn-v0_8",
    "colormap": "viridis"
}
