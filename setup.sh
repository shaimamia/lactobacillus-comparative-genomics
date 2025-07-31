#!/bin/bash

# Script de configuration et vérification - Version Simplifiée
# Projet: Lactobacillus bulgaricus - Génomique comparative Python
# Auteur: chaimae saihi

echo "🔧 === CONFIGURATION DU PROJET ==="
echo "Lactobacillus bulgaricus - Pipeline Python"
echo ""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages colorés
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "${GREEN}✅ $message${NC}" ;;
        "error")   echo -e "${RED}❌ $message${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "info")    echo -e "${BLUE}ℹ️  $message${NC}" ;;
    esac
}

# Vérifier si on est dans le bon dossier
if [[ ! -f "environment.yaml" ]]; then
    print_status "error" "Fichier environment.yaml non trouvé!"
    echo "Assurez-vous d'être dans le dossier racine du projet."
    exit 1
fi

echo "📁 === CRÉATION DE LA STRUCTURE DES DOSSIERS ==="
echo ""

# Créer tous les dossiers nécessaires
directories=(
    "data/genomes"
    "data/analysis" 
    "data/results"
    "data/results/plots"
    "logs"
    "scripts/utils"
    "docs"
    "tests"
)

for dir in "${directories[@]}"; do
    if mkdir -p "$dir" 2>/dev/null; then
        print_status "success" "Dossier créé: $dir"
    else
        print_status "error" "Impossible de créer: $dir"
    fi
done

echo ""

# Rendre les scripts exécutables
echo "🔧 === CONFIGURATION DES PERMISSIONS ==="
echo ""

scripts=(
    "run_pipeline.sh"
    "setup.sh"
    "scripts/01_download_genomes.sh"
    "scripts/02_sequence_analysis.py"
    "scripts/03_genome_comparison.py"
    "scripts/04_visualize_results.py"
)

for script in "${scripts[@]}"; do
    if [[ -f "$script" ]]; then
        chmod +x "$script"
        print_status "success" "Permissions définies: $script"
    else
        print_status "warning" "Script non trouvé: $script (sera créé plus tard)"
    fi
done

echo ""

# Vérification de l'environnement système
echo "🖥️  === VÉRIFICATION DU SYSTÈME ==="
echo ""

# Vérifier le système d'exploitation
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "success" "Système: Linux (compatible)"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "success" "Système: macOS (compatible)"
    
    # Détecter le processeur sur macOS
    arch_info=$(uname -m)
    if [[ "$arch_info" == "arm64" ]]; then
        print_status "success" "Processeur: Apple Silicon (M1/M2/M3/M4) - natif ARM64"
    else
        print_status "info" "Processeur: Intel x86_64"
    fi
else
    print_status "warning" "Système: $OSTYPE (non testé)"
fi

# Vérifier l'espace disque
available_space=$(df . | tail -1 | awk '{print $4}')
if command -v bc >/dev/null; then
    available_gb=$(echo "scale=1; $available_space/1024/1024" | bc)
    if (( $(echo "$available_gb > 2.0" | bc -l) )); then
        print_status "success" "Espace disque: ${available_gb} GB (suffisant)"
    else
        print_status "warning" "Espace disque: ${available_gb} GB (peut être insuffisant)"
    fi
else
    print_status "info" "Espace disque: $(df -h . | tail -1 | awk '{print $4}') disponible"
fi

# Vérifier la mémoire (approximatif)
if command -v free >/dev/null 2>&1; then
    total_mem_gb=$(free -g | awk 'NR==2{printf "%.1f", $2}')
    if (( $(echo "$total_mem_gb > 3.0" | bc -l) )); then
        print_status "success" "Mémoire: ${total_mem_gb} GB (suffisant)"
    else
        print_status "warning" "Mémoire: ${total_mem_gb} GB (peut être insuffisant)"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS alternative
    total_mem_bytes=$(sysctl -n hw.memsize)
    total_mem_gb=$(echo "scale=1; $total_mem_bytes/1073741824" | bc)
    print_status "success" "Mémoire: ${total_mem_gb} GB"
fi

echo ""

# Vérification des outils système
echo "🔍 === VÉRIFICATION DES OUTILS DE BASE ==="
echo ""

base_tools=("wget" "curl" "git")
missing_base=0

for tool in "${base_tools[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        print_status "success" "$tool installé"
    else
        print_status "error" "$tool manquant"
        ((missing_base++))
    fi
done

if [[ $missing_base -gt 0 ]]; then
    echo ""
    print_status "error" "$missing_base outil(s) de base manquant(s)"
    echo "Installez-les avec votre gestionnaire de paquets:"
    echo "  Ubuntu/Debian: sudo apt install wget curl git"
    echo "  CentOS/RHEL: sudo yum install wget curl git"
    echo "  macOS: brew install wget curl git"
fi

echo ""

# Vérification de conda
echo "🐍 === VÉRIFICATION DE CONDA ==="
echo ""

if command -v conda >/dev/null 2>&1; then
    conda_version=$(conda --version | cut -d' ' -f2)
    print_status "success" "Conda installé (version: $conda_version)"
    
    # Vérifier si l'environnement existe déjà
    if conda env list | grep -q "lacto-genomics"; then
        print_status "info" "Environnement 'lacto-genomics' déjà existant"
        echo ""
        echo "Voulez-vous recréer l'environnement? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "Suppression de l'ancien environnement..."
            conda env remove -n lacto-genomics -y
            echo "Création du nouvel environnement..."
            conda env create -f environment.yaml
        fi
    else
        echo "Création de l'environnement conda..."
        if conda env create -f environment.yaml; then
            print_status "success" "Environnement 'lacto-genomics' créé"
        else
            print_status "error" "Échec de la création de l'environnement"
        fi
    fi
else
    print_status "error" "Conda non installé"
    echo ""
    echo "📥 Installez Miniconda:"
    echo "  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-$(uname)-$(uname -m).sh"
    echo "  bash Miniconda3-latest-$(uname)-$(uname -m).sh"
    echo "  Puis relancez ce script."
fi

echo ""

# Test de l'environnement conda
echo "🧪 === TEST DE L'ENVIRONNEMENT PYTHON ==="
echo ""

if conda env list | grep -q "lacto-genomics"; then
    echo "Test des modules Python..."
    
    # Activer l'environnement et tester les modules
    eval "$(conda shell.bash hook)"
    conda activate lacto-genomics 2>/dev/null
    
    python_modules=("pandas" "numpy" "matplotlib" "seaborn" "plotly" "scipy")
    python_missing=0
    
    for module in "${python_modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            print_status "success" "Module Python: $module"
        else
            print_status "error" "Module Python manquant: $module"
            ((python_missing++))
        fi
    done
    
    # Test spécial pour Biopython
    if python3 -c "from Bio import SeqIO" 2>/dev/null; then
        print_status "success" "Module Python: biopython"
    else
        print_status "error" "Module Python manquant: biopython"
        ((python_missing++))
    fi
    
    # Test matplotlib-venn
    if python3 -c "import matplotlib_venn" 2>/dev/null; then
        print_status "success" "Module Python: matplotlib-venn"
    else
        print_status "warning" "Module Python optionnel: matplotlib-venn (pip install matplotlib-venn)"
    fi
    
    conda deactivate 2>/dev/null
    
    if [[ $python_missing -eq 0 ]]; then
        print_status "success" "Tous les modules Python requis sont installés!"
    else
        print_status "error" "$python_missing module(s) Python manquant(s)"
    fi
else
    print_status "error" "Environnement 'lacto-genomics' non trouvé"
fi

echo ""

# Créer un fichier de configuration
echo "⚙️  === CRÉATION DU FICHIER DE CONFIGURATION ==="
echo ""

config_file="config.py"
cat > "$config_file" << 'EOF'
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
EOF

print_status "success" "Fichier de configuration créé: $config_file"

echo ""

# Créer un script de test rapide
echo "🧪 === CRÉATION DU SCRIPT DE TEST ==="
echo ""

test_script="test_installation.sh"
cat > "$test_script" << 'EOF'
#!/bin/bash

# Test rapide de l'installation - Version simplifiée
echo "🧪 Test rapide de l'installation Python..."

# Activer l'environnement
eval "$(conda shell.bash hook)"
conda activate lacto-genomics

# Tester les modules Python
echo "Test des modules essentiels..."
python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from Bio import SeqIO
    import plotly
    
    print('✅ pandas:', pd.__version__)
    print('✅ numpy:', np.__version__)
    print('✅ matplotlib: OK')
    print('✅ seaborn: OK') 
    print('✅ biopython: OK')
    print('✅ plotly: OK')
    print()
    print('🎉 Tous les modules sont prêts!')
    print('🚀 Votre environnement Python est fonctionnel!')
    
except ImportError as e:
    print(f'❌ Erreur d\'importation: {e}')
    print('💡 Réinstallez l\'environnement: conda env create -f environment.yaml')
    sys.exit(1)
"

conda deactivate
echo ""
echo "✅ Test terminé!"
EOF

chmod +x "$test_script"
print_status "success" "Script de test créé: $test_script"

echo ""

# Résumé final
echo "📋 === RÉSUMÉ DE LA CONFIGURATION ==="
echo ""

print_status "info" "Structure des dossiers créée"
print_status "info" "Permissions des scripts configurées"
print_status "info" "Configuration Python générée"
print_status "info" "Script de test créé"

echo ""
echo "🚀 === PROCHAINES ÉTAPES ==="
echo ""
echo "1. Activez l'environnement conda:"
echo "   conda activate lacto-genomics"
echo ""
echo "2. Testez l'installation:"
echo "   ./test_installation.sh"
echo ""
echo "3. Lancez le pipeline:"
echo "   ./run_pipeline.sh"
echo ""
echo "4. Ou exécutez étape par étape:"
echo "   ./scripts/01_download_genomes.sh"
echo "   python3 scripts/02_sequence_analysis.py"
echo "   python3 scripts/03_genome_comparison.py"
echo "   python3 scripts/04_visualize_results.py"
echo ""

print_status "info" "Version Python native optimisée pour macOS M4 Pro"
print_status "info" "Pipeline simplifié mais puissant pour la génomique comparative"

echo ""
echo "✅ Configuration terminée!"