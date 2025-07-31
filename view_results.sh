#!/bin/bash
# Script de consultation rapide des résultats

echo "🧬 === CONSULTATION RAPIDE DES RÉSULTATS ==="
echo ""

# Ouvrir le rapport principal
if [ -f "data/results/rapport_final.html" ]; then
    echo "📄 Ouverture du rapport principal..."
    if command -v open &> /dev/null; then
        open "data/results/rapport_final.html"
    elif command -v firefox &> /dev/null; then
        firefox "data/results/rapport_final.html" &
    elif command -v google-chrome &> /dev/null; then
        google-chrome "data/results/rapport_final.html" &
    else
        echo "Ouvrez manuellement: data/results/rapport_final.html"
    fi
else
    echo "❌ Rapport principal non trouvé"
fi

# Afficher un résumé rapide
if [ -f "data/analysis/genome_statistics.csv" ]; then
    echo ""
    echo "📊 Résumé rapide:"
    echo "Souche,Contigs,Taille_totale_bp,Taille_totale_Mb,GC_percent,AT_percent,N50_bp,Contig_max_bp,Contig_min_bp,Contig_moyen_bp,Complexite"
    echo "ATCC11842,3,5486145,5.49,38.37,61.63,5354700,5354700,21875,1828715.0,1.0
DSM20081,3,3075806,3.08,32.78,67.22,3043210,3043210,3011,1025269.0,1.0
CNCM1519,1,2160842,2.16,39.7,60.3,2160842,2160842,2160842,2160842.0,1.0"
fi

echo ""
echo "📁 Tous les fichiers dans: data/results/"
ls -la "data/results/"
