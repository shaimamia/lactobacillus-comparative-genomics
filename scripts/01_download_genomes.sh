#!/bin/bash

# Script 1: Téléchargement des génomes de Lactobacillus bulgaricus
# Pipeline Python de génomique comparative
# Auteur: [Votre Nom]
# Date: $(date)

echo "🦠 === TÉLÉCHARGEMENT DES GÉNOMES DE L. BULGARICUS ==="
echo "Date: $(date)"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p data/genomes
mkdir -p data/analysis
mkdir -p data/results
mkdir -p logs

# Variables des souches à analyser (correspondant à config.py)
declare -A STRAINS=(
    ["ATCC11842"]="GCF_000196515.1"
    ["DSM20081"]="GCF_000027045.1"
    ["CNCM1519"]="GCF_000006885.1" 
)

# URL de base NCBI
NCBI_BASE="https://ftp.ncbi.nlm.nih.gov/genomes/all"

echo "🌐 Téléchargement des génomes depuis NCBI..."
echo ""

# Fonction pour télécharger un génome avec URLs directes
download_genome_direct() {
    local strain_name=$1
    local url=$2
    
    echo "⬇️  Téléchargement de la souche $strain_name..."
    local output_file="data/genomes/LB_${strain_name}.fna"
    
    # Vérifier si le fichier existe déjà
    if [ -f "$output_file" ] && [ -s "$output_file" ]; then
        local existing_size=$(du -h "$output_file" | cut -f1)
        print_status "info" "Fichier déjà présent: $output_file ($existing_size)"
        echo "     Voulez-vous le retélécharger? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_status "info" "Conservation du fichier existant"
            return 0
        fi
    fi
    
    # Télécharger avec wget
    if wget -q --show-progress --timeout=300 -O "${output_file}.gz" "$url" 2>/dev/null; then
        # Décompresser
        if gunzip "${output_file}.gz" 2>/dev/null; then
            print_status "success" "Téléchargement réussi: $output_file"
            
            # Statistiques basiques
            local num_contigs=$(grep -c "^>" "$output_file")
            local total_bases=$(grep -v "^>" "$output_file" | tr -d '\n' | wc -c)
            local file_size=$(du -h "$output_file" | cut -f1)
            
            print_status "info" "Contigs: $num_contigs, Taille: $total_bases bp ($file_size)"
            
            # Log du succès
            echo "$(date): $strain_name téléchargé avec succès" >> logs/download.log
        else
            print_status "error" "Échec de la décompression pour $strain_name"
            rm -f "${output_file}.gz" "$output_file"
            return 1
        fi
    else
        print_status "error" "Échec du téléchargement pour $strain_name"
        print_status "info" "URL tentée: $url"
        rm -f "${output_file}.gz"
        return 1
    fi
    
    echo ""
}

# Fonction alternative pour construire l'URL NCBI automatiquement
build_ncbi_url() {
    local accession=$1
    
    # Extraire les parties de l'accession GCF_000196515.1
    local gcf_part=$(echo "$accession" | cut -d'_' -f1)  # GCF
    local num_part=$(echo "$accession" | cut -d'_' -f2)  # 000196515
    local ver_part=$(echo "$accession" | cut -d'_' -f3)  # 1
    
    # Construire le chemin: GCF/000/196/515/
    local path1=$(echo "$num_part" | cut -c1-3)   # 000
    local path2=$(echo "$num_part" | cut -c4-6)   # 196
    local path3=$(echo "$num_part" | cut -c7-9)   # 515
    
    # URL complète
    echo "$NCBI_BASE/$gcf_part/$path1/$path2/$path3/${accession}_*/${accession}_*_genomic.fna.gz"
}

# URLs directes testées et fonctionnelles
echo "🌐 Tentative de téléchargement avec URLs directes..."
echo ""

# Souche ATCC 11842
print_status "info" "Souche 1/3: ATCC 11842 (souche type de référence)"
download_genome_direct "ATCC11842" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/196/515/GCF_000196515.1_ASM19651v1/GCF_000196515.1_ASM19651v1_genomic.fna.gz"

# Souche DSM 20081  
print_status "info" "Souche 2/3: DSM 20081 (souche commerciale)"
download_genome_direct "DSM20081" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/027/045/GCF_000027045.1_ASM2704v1/GCF_000027045.1_ASM2704v1_genomic.fna.gz"

# Souche CNCM I-1519
print_status "info" "Souche 3/3: CNCM I-1519 (probiotique, substitut: ATCC BAA-365)"
download_genome_direct "CNCM1519" "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/006/885/GCF_000006885.1_ASM688v1/GCF_000006885.1_ASM688v1_genomic.fna.gz"

# Vérification des téléchargements
echo "🔍 === VÉRIFICATION DES TÉLÉCHARGEMENTS ==="
echo ""

success_count=0
total_count=3

for strain in ATCC11842 DSM20081 CNCM1519; do
    file="data/genomes/LB_${strain}.fna"
    if [ -f "$file" ] && [ -s "$file" ]; then
        # Vérifications supplémentaires
        num_contigs=$(grep -c "^>" "$file")
        total_bases=$(grep -v "^>" "$file" | tr -d '\n' | wc -c)
        file_size=$(du -h "$file" | cut -f1)
        
        # Vérifier que le fichier semble valide
        if [ $num_contigs -gt 0 ] && [ $total_bases -gt 100000 ]; then
            print_status "success" "$strain: $num_contigs contigs, $total_bases bp ($file_size)"
            ((success_count++))
        else
            print_status "error" "$strain: Fichier semble corrompu (trop petit)"
        fi
    else
        print_status "error" "$strain: MANQUANT ou VIDE"
        echo "     📝 Télécharger manuellement depuis:"
        case $strain in
            "ATCC11842") echo "        https://www.ncbi.nlm.nih.gov/assembly/GCF_000196515.1";;
            "DSM20081")  echo "        https://www.ncbi.nlm.nih.gov/assembly/GCF_000027045.1";;
            "CNCM1519")  echo "        https://www.ncbi.nlm.nih.gov/assembly/GCF_000006865.2";;
        esac
    fi
done

echo ""
echo "📊 === RÉSUMÉ DU TÉLÉCHARGEMENT ==="
print_status "info" "Génomes téléchargés: $success_count/$total_count"

# Créer un résumé dans le dossier analysis
summary_file="data/analysis/download_summary.txt"
cat > "$summary_file" << EOF
=== RÉSUMÉ DU TÉLÉCHARGEMENT ===
Date: $(date)
Projet: Lactobacillus bulgaricus - Génomique comparative

STATUT DES TÉLÉCHARGEMENTS:
EOF

for strain in ATCC11842 DSM20081 CNCM1519; do
    file="data/genomes/LB_${strain}.fna"
    echo "" >> "$summary_file"
    if [ -f "$file" ] && [ -s "$file" ]; then
        num_contigs=$(grep -c "^>" "$file")
        total_bases=$(grep -v "^>" "$file" | tr -d '\n' | wc -c)
        file_size=$(du -h "$file" | cut -f1)
        
        echo "Souche: $strain" >> "$summary_file"
        echo "  Fichier: $file" >> "$summary_file"
        echo "  Taille: $file_size" >> "$summary_file"
        echo "  Contigs: $num_contigs" >> "$summary_file"
        echo "  Bases totales: $total_bases bp" >> "$summary_file"
        echo "  Statut: ✅ SUCCÈS" >> "$summary_file"
    else
        echo "Souche: $strain" >> "$summary_file"
        echo "  Statut: ❌ ÉCHEC" >> "$summary_file"
    fi
done

echo "📄 Résumé sauvegardé: $summary_file"

if [ $success_count -eq $total_count ]; then
    echo ""
    print_status "success" "🎉 Tous les génomes sont prêts pour l'analyse!"
    print_status "info" "➡️  Prochaine étape: python3 scripts/02_sequence_analysis.py"
    
    # Log final
    echo "$(date): Téléchargement terminé - $success_count/$total_count réussis" >> logs/download.log
    
    # Préparer pour l'analyse
    echo ""
    echo "📋 Fichiers prêts pour l'analyse:"
    for strain in ATCC11842 DSM20081 CNCM1519; do
        file="data/genomes/LB_${strain}.fna"
        if [ -f "$file" ]; then
            echo "  - $file"
        fi
    done
else
    print_status "warning" "⚠️  $((total_count - success_count)) téléchargement(s) ont échoué"
    print_status "info" "Vous pouvez continuer avec les génomes disponibles ou réessayer le téléchargement"
fi

echo ""
echo "✅ Script 01_download_genomes.sh terminé!"
echo "🕒 Durée: quelques secondes à quelques minutes selon la connexion"