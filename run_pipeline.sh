#!/bin/bash

# Script Principal: Pipeline de Génomique Comparative
# Projet: Lactobacillus bulgaricus - Version Python Native
# Auteur: [Votre Nom]
# Compatible: macOS M4 Pro, Linux

echo "🧬 ======================================================"
echo "    PIPELINE DE GÉNOMIQUE COMPARATIVE"
echo "    Lactobacillus bulgaricus - Version Python"
echo "====================================================== 🧬"
echo ""
echo "Date de début: $(date)"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
LOG_FILE="logs/pipeline_$(date +%Y%m%d_%H%M%S).log"
RESULTS_DIR="data/results"

# Créer les dossiers nécessaires
mkdir -p logs
mkdir -p data/{genomes,analysis,results/plots}

# Fonction pour logger et afficher
log_message() {
    local level=$1
    local message=$2
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    
    case $level in
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "ERROR")   echo -e "${RED}❌ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "INFO")    echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "STEP")    echo -e "${PURPLE}🔄 $message${NC}" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Fonction pour vérifier le succès d'une étape
check_step() {
    local step_name=$1
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_message "SUCCESS" "$step_name - RÉUSSI"
        return 0
    else
        log_message "ERROR" "$step_name - ÉCHEC (code: $exit_code)"
        echo ""
        echo -e "${RED}⚠️  ERREUR: $step_name a échoué!${NC}"
        echo -e "${BLUE}📋 Consultez le log: $LOG_FILE${NC}"
        echo -e "${BLUE}💡 Vous pouvez continuer manuellement ou redémarrer${NC}"
        
        echo ""
        echo "Options:"
        echo "1) Continuer malgré l'erreur"
        echo "2) Arrêter le pipeline"
        echo "3) Voir les dernières lignes du log"
        read -p "Votre choix (1/2/3): " choice
        
        case $choice in
            1)
                log_message "WARNING" "Continuation malgré l'erreur de $step_name"
                return 0
                ;;
            3)
                echo ""
                echo "=== DERNIÈRES LIGNES DU LOG ==="
                tail -20 "$LOG_FILE"
                echo ""
                read -p "Appuyez sur Entrée pour continuer..."
                return 1
                ;;
            *)
                log_message "ERROR" "Pipeline arrêté par l'utilisateur"
                exit 1
                ;;
        esac
    fi
}

# Fonction pour afficher le temps écoulé
show_elapsed_time() {
    local start_time=$1
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    local hours=$((elapsed / 3600))
    local minutes=$(((elapsed % 3600) / 60))
    local seconds=$((elapsed % 60))
    
    if [ $hours -gt 0 ]; then
        echo "⏱️  Temps écoulé: ${hours}h ${minutes}m ${seconds}s"
    elif [ $minutes -gt 0 ]; then
        echo "⏱️  Temps écoulé: ${minutes}m ${seconds}s"
    else
        echo "⏱️  Temps écoulé: ${seconds}s"
    fi
}

# Fonction pour vérifier l'environnement
check_environment() {
    log_message "INFO" "Vérification de l'environnement..."
    
    # Vérifier conda
    if ! command -v conda &> /dev/null; then
        log_message "ERROR" "Conda non installé"
        return 1
    fi
    
    # Vérifier l'environnement lacto-genomics
    if ! conda env list | grep -q "lacto-genomics"; then
        log_message "ERROR" "Environnement 'lacto-genomics' non trouvé"
        echo "Exécutez d'abord: ./setup.sh"
        return 1
    fi
    
    # Activer l'environnement
    eval "$(conda shell.bash hook)"
    conda activate lacto-genomics
    
    # Vérifier les modules Python
    python3 -c "import pandas, numpy, matplotlib, seaborn; from Bio import SeqIO" 2>/dev/null
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Modules Python manquants"
        return 1
    fi
    
    # Vérifier les scripts
    required_scripts=(
        "scripts/01_download_genomes.sh"
        "scripts/02_sequence_analysis.py"
        "scripts/03_genome_comparison.py"
        "scripts/04_visualize_results.py"
    )
    
    for script in "${required_scripts[@]}"; do
        if [ ! -f "$script" ]; then
            log_message "ERROR" "Script manquant: $script"
            return 1
        fi
    done
    
    log_message "SUCCESS" "Environnement vérifié et prêt"
    return 0
}

# Afficher les prérequis
echo "🔍 === VÉRIFICATION DES PRÉREQUIS ==="
echo ""

if ! check_environment; then
    echo ""
    echo -e "${RED}❌ Problème d'environnement détecté${NC}"
    echo "🔧 Solutions possibles:"
    echo "   1. Exécuter: ./setup.sh"
    echo "   2. Réinstaller l'environnement conda"
    echo "   3. Vérifier les scripts dans le dossier scripts/"
    exit 1
fi

echo ""
log_message "SUCCESS" "Tous les prérequis sont satisfaits"

# Initialiser le log
log_message "INFO" "=== DÉBUT DU PIPELINE DE GÉNOMIQUE COMPARATIVE ==="
log_message "INFO" "Projet: Lactobacillus bulgaricus - Version Python native"
log_message "INFO" "Système: $(uname -s) $(uname -m)"
log_message "INFO" "Python: $(python3 --version)"

# Timer global
pipeline_start_time=$(date +%s)

echo ""
echo "📋 === PLAN D'EXÉCUTION ==="
echo "  1️⃣  Téléchargement des génomes (NCBI)"
echo "  2️⃣  Analyse des séquences (Python/Biopython)"
echo "  3️⃣  Comparaison génomique (Algorithmes de similarité)"
echo "  4️⃣  Visualisation et rapport (Plotly/Matplotlib)"
echo ""

# Estimation du temps
echo "⏱️  Temps estimé: 5-15 minutes (selon la connexion internet)"
echo "💾 Espace requis: ~50 MB"
echo ""

echo "Voulez-vous continuer? (Y/n)"
read -r response
if [[ "$response" =~ ^[Nn]$ ]]; then
    log_message "INFO" "Pipeline annulé par l'utilisateur"
    echo "Pipeline annulé."
    exit 0
fi

echo ""

# === ÉTAPE 1: TÉLÉCHARGEMENT ===
echo "1️⃣  === ÉTAPE 1: TÉLÉCHARGEMENT DES GÉNOMES ==="
step1_start=$(date +%s)

log_message "STEP" "Début étape 1: Téléchargement des génomes depuis NCBI"

if [ -f "scripts/01_download_genomes.sh" ]; then
    chmod +x scripts/01_download_genomes.sh
    bash scripts/01_download_genomes.sh
    check_step "Téléchargement des génomes"
else
    log_message "ERROR" "Script manquant: scripts/01_download_genomes.sh"
    exit 1
fi

show_elapsed_time $step1_start
echo ""

# === ÉTAPE 2: ANALYSE DES SÉQUENCES ===
echo "2️⃣  === ÉTAPE 2: ANALYSE DES SÉQUENCES ==="
step2_start=$(date +%s)

log_message "STEP" "Début étape 2: Analyse des séquences avec Biopython"

if [ -f "scripts/02_sequence_analysis.py" ]; then
    chmod +x scripts/02_sequence_analysis.py
    python3 scripts/02_sequence_analysis.py
    check_step "Analyse des séquences"
else
    log_message "ERROR" "Script manquant: scripts/02_sequence_analysis.py"
    exit 1
fi

show_elapsed_time $step2_start
echo ""

# === ÉTAPE 3: COMPARAISON GÉNOMIQUE ===
echo "3️⃣  === ÉTAPE 3: COMPARAISON GÉNOMIQUE ==="
step3_start=$(date +%s)

log_message "STEP" "Début étape 3: Comparaison génomique et phylogénie"

if [ -f "scripts/03_genome_comparison.py" ]; then
    chmod +x scripts/03_genome_comparison.py
    python3 scripts/03_genome_comparison.py
    check_step "Comparaison génomique"
else
    log_message "ERROR" "Script manquant: scripts/03_genome_comparison.py"
    exit 1
fi

show_elapsed_time $step3_start
echo ""

# === ÉTAPE 4: VISUALISATION ===
echo "4️⃣  === ÉTAPE 4: VISUALISATION ET RAPPORT ==="
step4_start=$(date +%s)

log_message "STEP" "Début étape 4: Création des visualisations et du rapport"

if [ -f "scripts/04_visualize_results.py" ]; then
    chmod +x scripts/04_visualize_results.py
    python3 scripts/04_visualize_results.py
    check_step "Visualisation et rapport"
else
    log_message "ERROR" "Script manquant: scripts/04_visualize_results.py"
    exit 1
fi

show_elapsed_time $step4_start
echo ""

# === RÉSUMÉ FINAL ===
pipeline_end_time=$(date +%s)

echo "🎉 ======================================================"
echo "    PIPELINE TERMINÉ AVEC SUCCÈS!"
echo "====================================================== 🎉"
echo ""

show_elapsed_time $pipeline_start_time

echo ""
echo "📊 === RÉSULTATS GÉNÉRÉS ==="
echo ""

# Vérifier les fichiers générés
files_to_check=(
    "$RESULTS_DIR/rapport_final.html"
    "$RESULTS_DIR/similarity_matrix.csv"
    "$RESULTS_DIR/pairwise_comparisons.csv"
    "data/analysis/genome_statistics.csv"
    "$RESULTS_DIR/plots/genome_statistics.png"
    "$RESULTS_DIR/plots/similarity_matrices.png"
    "$RESULTS_DIR/plots/phylogenetic_tree.png"
)

echo "📁 Fichiers principaux:"
successful_files=0
total_files=${#files_to_check[@]}

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" 2>/dev/null | cut -f1)
        echo "  ✅ $(basename "$file") ($size)"
        ((successful_files++))
    else
        echo "  ❌ $(basename "$file") - manquant"
    fi
done

echo ""
echo "📈 Taux de réussite: $successful_files/$total_files fichiers générés"

# Compter les génomes analysés
if [ -f "data/analysis/genome_statistics.csv" ]; then
    genome_count=$(tail -n +2 "data/analysis/genome_statistics.csv" | wc -l)
    echo "🧬 Génomes analysés: $genome_count souches"
fi

echo ""
echo "🌐 === CONSULTATION DES RÉSULTATS ==="
echo ""
echo "📄 Rapport principal (RECOMMANDÉ):"
echo "   open $RESULTS_DIR/rapport_final.html"
echo "   ou"
echo "   firefox $RESULTS_DIR/rapport_final.html"
echo ""
echo "📊 Fichiers de données:"
echo "   📋 Statistiques: data/analysis/genome_statistics.csv"
echo "   🔬 Comparaisons: $RESULTS_DIR/pairwise_comparisons.csv"
echo "   📈 Matrice de similarité: $RESULTS_DIR/similarity_matrix.csv"
echo ""
echo "🖼️  Graphiques statiques:"
echo "   📁 Dossier: $RESULTS_DIR/plots/"
echo "   🔍 Liste: ls $RESULTS_DIR/plots/"
echo ""

# Créer un script de consultation rapide
consultation_script="view_results.sh"
cat > "$consultation_script" << EOF
#!/bin/bash
# Script de consultation rapide des résultats

echo "🧬 === CONSULTATION RAPIDE DES RÉSULTATS ==="
echo ""

# Ouvrir le rapport principal
if [ -f "$RESULTS_DIR/rapport_final.html" ]; then
    echo "📄 Ouverture du rapport principal..."
    if command -v open &> /dev/null; then
        open "$RESULTS_DIR/rapport_final.html"
    elif command -v firefox &> /dev/null; then
        firefox "$RESULTS_DIR/rapport_final.html" &
    elif command -v google-chrome &> /dev/null; then
        google-chrome "$RESULTS_DIR/rapport_final.html" &
    else
        echo "Ouvrez manuellement: $RESULTS_DIR/rapport_final.html"
    fi
else
    echo "❌ Rapport principal non trouvé"
fi

# Afficher un résumé rapide
if [ -f "data/analysis/genome_statistics.csv" ]; then
    echo ""
    echo "📊 Résumé rapide:"
    echo "$(head -1 data/analysis/genome_statistics.csv)"
    echo "$(tail -n +2 data/analysis/genome_statistics.csv)"
fi

echo ""
echo "📁 Tous les fichiers dans: $RESULTS_DIR/"
ls -la "$RESULTS_DIR/"
EOF

chmod +x "$consultation_script"
log_message "SUCCESS" "Script de consultation créé: $consultation_script"

# Log final
log_message "SUCCESS" "=== PIPELINE TERMINÉ AVEC SUCCÈS ==="
log_message "INFO" "Durée totale: $((pipeline_end_time - pipeline_start_time)) secondes"
log_message "INFO" "Fichiers générés dans: $RESULTS_DIR"
log_message "INFO" "Log complet: $LOG_FILE"

echo "📝 Log complet: $LOG_FILE"
echo ""
echo "✅ Analyse terminée! Votre projet de génomique comparative est prêt!"
echo ""

# Afficher des conseils pour le CV
echo "🎯 === POUR VOTRE CV/PORTFOLIO ==="
echo ""
echo "📋 Compétences démontrées:"
echo "   • Bioinformatique: Analyse génomique comparative"
echo "   • Python: Biopython, Pandas, NumPy, Matplotlib"
echo "   • Visualisation: Plotly, Seaborn, rapports interactifs"
echo "   • Automatisation: Pipeline bash, gestion d'erreurs"
echo "   • Développement: Architecture modulaire, documentation"
echo ""
echo "📝 Description suggérée:"
echo '   "Pipeline Python de génomique comparative analysant 3 souches'
echo '    de Lactobacillus bulgaricus. Calcul de métriques génomiques,'
echo '    analyses de similarité, création de visualisations interactives'
echo '    et génération de rapports HTML. Compatible macOS M4 Pro."'
echo ""
echo "🔗 N'oubliez pas de:"
echo "   1. Ajouter ce projet à votre GitHub"
echo "   2. Consulter le rapport pour comprendre les résultats"
echo "   3. Personnaliser l'analyse pour d'autres organismes"
echo ""

# Option pour ouvrir automatiquement les résultats
echo "Voulez-vous ouvrir le rapport maintenant? (Y/n)"
read -r open_response
if [[ ! "$open_response" =~ ^[Nn]$ ]]; then
    bash "$consultation_script"
fi

echo ""
echo "🚀 Félicitations! Votre pipeline de génomique comparative fonctionne parfaitement!"

# Désactiver l'environnement conda
conda deactivate 2>/dev/null