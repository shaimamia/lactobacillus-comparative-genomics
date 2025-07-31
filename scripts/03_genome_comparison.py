#!/usr/bin/env python3
"""
Script 3: Comparaison génomique - Version simplifiée et corrigée
Compatible avec toutes les versions de Biopython
"""

import os
import sys
import pandas as pd
import numpy as np
from Bio import SeqIO
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import dendrogram, linkage
import itertools

# Configuration simple
STRAINS = {
    "ATCC11842": {"filename": "LB_ATCC11842.fna", "description": "Souche type"},
    "DSM20081": {"filename": "LB_DSM20081.fna", "description": "Souche commerciale"}, 
    "CNCM1519": {"filename": "LB_CNCM1519.fna", "description": "Souche probiotique"}
}

def print_status(status, message):
    colors = {'success': '\033[92m✅', 'error': '\033[91m❌', 'warning': '\033[93m⚠️', 'info': '\033[94mℹ️'}
    print(f"{colors.get(status, '')} {message}\033[0m")

def calculate_gc_content(sequence):
    """Calculer le contenu GC manuellement"""
    if not sequence:
        return 0
    g_count = sequence.upper().count('G')
    c_count = sequence.upper().count('C')
    total_bases = len([base for base in sequence.upper() if base in 'ATGC'])
    if total_bases == 0:
        return 0
    return (g_count + c_count) / total_bases * 100

def load_genome_sequences(genome_path):
    """Charger toutes les séquences d'un génome"""
    sequences = []
    try:
        for record in SeqIO.parse(genome_path, "fasta"):
            sequences.append(str(record.seq).upper())
        return ''.join(sequences)  # Concaténer tous les contigs
    except Exception as e:
        print_status('error', f"Erreur lors du chargement de {genome_path}: {e}")
        return None

def calculate_kmer_profile(sequence, k=4):
    """Calculer le profil de k-mers d'une séquence"""
    if len(sequence) < k:
        return {}
    
    kmer_counts = {}
    total_kmers = 0
    
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i + k]
        if 'N' not in kmer:  # Ignorer les k-mers avec des ambiguïtés
            kmer_counts[kmer] = kmer_counts.get(kmer, 0) + 1
            total_kmers += 1
    
    # Normaliser en fréquences
    if total_kmers > 0:
        kmer_freqs = {kmer: count / total_kmers for kmer, count in kmer_counts.items()}
    else:
        kmer_freqs = {}
    
    return kmer_freqs

def compare_kmer_profiles(profile1, profile2):
    """Comparer deux profils de k-mers en utilisant la similarité cosinus"""
    # Obtenir tous les k-mers uniques
    all_kmers = set(profile1.keys()) | set(profile2.keys())
    
    if not all_kmers:
        return 0.0
    
    # Créer des vecteurs
    vector1 = np.array([profile1.get(kmer, 0) for kmer in all_kmers])
    vector2 = np.array([profile2.get(kmer, 0) for kmer in all_kmers])
    
    # Calculer la similarité cosinus
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def calculate_sequence_similarity(seq1, seq2, window_size=1000):
    """Calculer un score de similarité approximatif basé sur des fenêtres"""
    min_len = min(len(seq1), len(seq2))
    if min_len < window_size:
        window_size = min_len // 2
    
    if window_size < 10:
        return 0.0
    
    scores = []
    num_windows = min_len // window_size
    
    for i in range(num_windows):
        start = i * window_size
        end = start + window_size
        
        window1 = seq1[start:end]
        window2 = seq2[start:end]
        
        # Score basé sur les correspondances exactes
        matches = sum(1 for a, b in zip(window1, window2) if a == b)
        score = matches / len(window1)
        scores.append(score)
    
    return np.mean(scores) if scores else 0.0

def analyze_gc_content_similarity(seq1, seq2, window_size=1000):
    """Analyser la similarité du contenu GC entre deux séquences"""
    def get_gc_windows(sequence, window_size):
        gc_values = []
        for i in range(0, len(sequence) - window_size + 1, window_size):
            window = sequence[i:i + window_size]
            if len(window) == window_size:
                gc_values.append(calculate_gc_content(window))  # ✅ Corrigé
        return gc_values
    
    gc1 = get_gc_windows(seq1, window_size)
    gc2 = get_gc_windows(seq2, window_size)
    
    if not gc1 or not gc2:
        return 0.0
    
    # Prendre la longueur minimale
    min_windows = min(len(gc1), len(gc2))
    gc1 = gc1[:min_windows]
    gc2 = gc2[:min_windows]
    
    # Calculer la corrélation de Pearson
    if len(gc1) > 1:
        correlation = np.corrcoef(gc1, gc2)[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    else:
        return 0.0

def create_comparison_matrix(genomes_data):
    """Créer une matrice de comparaison entre tous les génomes"""
    strain_names = list(genomes_data.keys())
    n_strains = len(strain_names)
    
    # Matrices pour différents types de comparaisons
    kmer_similarity_matrix = np.zeros((n_strains, n_strains))
    sequence_similarity_matrix = np.zeros((n_strains, n_strains))
    gc_similarity_matrix = np.zeros((n_strains, n_strains))
    size_similarity_matrix = np.zeros((n_strains, n_strains))
    
    # Calculer les profils de k-mers pour toutes les souches
    print_status('info', "Calcul des profils de k-mers...")
    kmer_profiles = {}
    for strain, sequence in genomes_data.items():
        if sequence:
            kmer_profiles[strain] = calculate_kmer_profile(sequence, k=4)
    
    print_status('info', "Calcul des matrices de comparaison...")
    
    for i, strain1 in enumerate(strain_names):
        for j, strain2 in enumerate(strain_names):
            if i == j:
                # Diagonale = 1 (similarité parfaite avec soi-même)
                kmer_similarity_matrix[i, j] = 1.0
                sequence_similarity_matrix[i, j] = 1.0
                gc_similarity_matrix[i, j] = 1.0
                size_similarity_matrix[i, j] = 1.0
            elif i < j:  # Calculer seulement le triangle supérieur
                seq1 = genomes_data[strain1]
                seq2 = genomes_data[strain2]
                
                if seq1 and seq2:
                    # Similarité k-mers
                    kmer_sim = compare_kmer_profiles(kmer_profiles[strain1], kmer_profiles[strain2])
                    kmer_similarity_matrix[i, j] = kmer_sim
                    kmer_similarity_matrix[j, i] = kmer_sim
                    
                    # Similarité de séquence approximative
                    seq_sim = calculate_sequence_similarity(seq1, seq2)
                    sequence_similarity_matrix[i, j] = seq_sim
                    sequence_similarity_matrix[j, i] = seq_sim
                    
                    # Similarité de contenu GC
                    gc_sim = analyze_gc_content_similarity(seq1, seq2)
                    if np.isnan(gc_sim):
                        gc_sim = 0.0
                    gc_similarity_matrix[i, j] = gc_sim
                    gc_similarity_matrix[j, i] = gc_sim
                    
                    # Similarité de taille
                    size_diff = abs(len(seq1) - len(seq2)) / max(len(seq1), len(seq2))
                    size_sim = 1 - size_diff
                    size_similarity_matrix[i, j] = size_sim
                    size_similarity_matrix[j, i] = size_sim
                    
                    print_status('info', f"Comparaison {strain1} vs {strain2}: "
                               f"k-mer={kmer_sim:.3f}, seq={seq_sim:.3f}, "
                               f"GC={gc_sim:.3f}, taille={size_sim:.3f}")
    
    return {
        'strain_names': strain_names,
        'kmer_similarity': kmer_similarity_matrix,
        'sequence_similarity': sequence_similarity_matrix,
        'gc_similarity': gc_similarity_matrix,
        'size_similarity': size_similarity_matrix
    }

def create_composite_similarity_matrix(comparison_data):
    """Créer une matrice de similarité composite pondérée"""
    weights = {
        'kmer': 0.4,      # Plus important pour la similarité globale
        'sequence': 0.3,  # Important pour la structure
        'gc': 0.2,        # Composition
        'size': 0.1       # Taille moins critique
    }
    
    composite_matrix = (
        weights['kmer'] * comparison_data['kmer_similarity'] +
        weights['sequence'] * comparison_data['sequence_similarity'] +
        weights['gc'] * comparison_data['gc_similarity'] +
        weights['size'] * comparison_data['size_similarity']
    )
    
    return composite_matrix

def plot_similarity_matrices(comparison_data):
    """Créer des heatmaps pour toutes les matrices de similarité"""
    strain_names = comparison_data['strain_names']
    matrices = {
        'K-mers (4-mers)': comparison_data['kmer_similarity'],
        'Similarité de séquence': comparison_data['sequence_similarity'],
        'Contenu GC': comparison_data['gc_similarity'],
        'Taille relative': comparison_data['size_similarity']
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Matrices de Similarité - Lactobacillus bulgaricus', fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    
    for idx, (title, matrix) in enumerate(matrices.items()):
        im = axes[idx].imshow(matrix, cmap='RdYlBu_r', vmin=0, vmax=1)
        axes[idx].set_title(title, fontsize=12, fontweight='bold')
        axes[idx].set_xticks(range(len(strain_names)))
        axes[idx].set_yticks(range(len(strain_names)))
        axes[idx].set_xticklabels(strain_names, rotation=45)
        axes[idx].set_yticklabels(strain_names)
        
        # Ajouter les valeurs dans les cellules
        for i in range(len(strain_names)):
            for j in range(len(strain_names)):
                text = axes[idx].text(j, i, f'{matrix[i, j]:.3f}',
                                    ha="center", va="center", color="black", fontweight='bold')
        
        # Colorbar
        plt.colorbar(im, ax=axes[idx], fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    
    output_path = 'data/results/plots/similarity_matrices.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print_status('success', f"Matrices de similarité: {output_path}")
    plt.close()

def plot_phylogenetic_tree(composite_matrix, strain_names):
    """Créer un dendrogramme (arbre phylogénétique)"""
    # Convertir similarité en distance
    distance_matrix = 1 - composite_matrix
    
    # Pour scipy, on a besoin d'une matrice condensée
    condensed_distances = squareform(distance_matrix, checks=False)
    
    # Clustering hiérarchique
    linkage_matrix = linkage(condensed_distances, method='ward')
    
    plt.figure(figsize=(10, 6))
    
    dendrogram(linkage_matrix, 
               labels=strain_names,
               leaf_rotation=45,
               leaf_font_size=12)
    
    plt.title('Arbre Phylogénétique - Lactobacillus bulgaricus\n(Basé sur la similarité génomique)', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Souches')
    plt.ylabel('Distance génomique')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path = 'data/results/plots/phylogenetic_tree.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print_status('success', f"Arbre phylogénétique: {output_path}")
    plt.close()

def create_comparison_summary(comparison_data, composite_matrix):
    """Créer un résumé des comparaisons sous forme de DataFrame"""
    strain_names = comparison_data['strain_names']
    n_strains = len(strain_names)
    
    comparisons = []
    
    for i in range(n_strains):
        for j in range(i + 1, n_strains):
            comparison = {
                'Souche_1': strain_names[i],
                'Souche_2': strain_names[j],
                'Similarite_kmers': comparison_data['kmer_similarity'][i, j],
                'Similarite_sequence': comparison_data['sequence_similarity'][i, j],
                'Similarite_GC': comparison_data['gc_similarity'][i, j],
                'Similarite_taille': comparison_data['size_similarity'][i, j],
                'Similarite_composite': composite_matrix[i, j],
                'Distance_genetique': 1 - composite_matrix[i, j]
            }
            comparisons.append(comparison)
    
    return pd.DataFrame(comparisons)

def main():
    """Fonction principale"""
    print("🔬 === COMPARAISON GÉNOMIQUE ===")
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Créer les dossiers
    os.makedirs('data/results', exist_ok=True)
    os.makedirs('data/results/plots', exist_ok=True)
    
    # Charger les génomes
    print_status('info', "Chargement des génomes...")
    genomes_data = {}
    
    for strain_name, strain_info in STRAINS.items():
        filename = strain_info['filename']
        genome_path = os.path.join('data/genomes', filename)
        
        if os.path.exists(genome_path):
            sequence = load_genome_sequences(genome_path)
            if sequence:
                genomes_data[strain_name] = sequence
                print_status('success', f"{strain_name}: {len(sequence):,} bp chargés")
            else:
                print_status('error', f"Échec du chargement de {strain_name}")
        else:
            print_status('warning', f"Fichier non trouvé: {genome_path}")
    
    if len(genomes_data) < 2:
        print_status('error', "Au moins 2 génomes sont nécessaires pour la comparaison!")
        sys.exit(1)
    
    print()
    print_status('info', f"Comparaison de {len(genomes_data)} génomes...")
    print()
    
    # Créer les matrices de comparaison
    comparison_data = create_comparison_matrix(genomes_data)
    
    # Créer la matrice composite
    print_status('info', "Calcul de la similarité composite...")
    composite_matrix = create_composite_similarity_matrix(comparison_data)
    
    # Créer les visualisations
    print_status('info', "Création des visualisations...")
    plot_similarity_matrices(comparison_data)
    plot_phylogenetic_tree(composite_matrix, comparison_data['strain_names'])
    
    # Créer le résumé des comparaisons
    print_status('info', "Création du résumé des comparaisons...")
    comparison_summary = create_comparison_summary(comparison_data, composite_matrix)
    
    # Sauvegarder les résultats
    
    # 1. Matrice de similarité composite
    composite_df = pd.DataFrame(composite_matrix, 
                               index=comparison_data['strain_names'],
                               columns=comparison_data['strain_names'])
    composite_path = 'data/results/similarity_matrix.csv'
    composite_df.to_csv(composite_path)
    print_status('success', f"Matrice de similarité: {composite_path}")
    
    # 2. Résumé des comparaisons par paires
    summary_path = 'data/results/pairwise_comparisons.csv'
    comparison_summary.to_csv(summary_path, index=False)
    print_status('success', f"Comparaisons par paires: {summary_path}")
    
    # 3. Données détaillées (JSON)
    detailed_data = {
        'strain_names': comparison_data['strain_names'],
        'kmer_similarity': comparison_data['kmer_similarity'].tolist(),
        'sequence_similarity': comparison_data['sequence_similarity'].tolist(),
        'gc_similarity': comparison_data['gc_similarity'].tolist(),
        'size_similarity': comparison_data['size_similarity'].tolist(),
        'composite_similarity': composite_matrix.tolist()
    }
    
    json_path = 'data/results/detailed_comparisons.json'
    with open(json_path, 'w') as f:
        json.dump(detailed_data, f, indent=2)
    print_status('success', f"Données détaillées: {json_path}")
    
    # 4. Affichage des résultats
    print()
    print("📊 === RÉSUMÉ DES COMPARAISONS ===")
    print()
    print("Matrice de similarité composite:")
    print(composite_df.round(3))
    print()
    
    print("Comparaisons par paires:")
    for _, row in comparison_summary.iterrows():
        print(f"{row['Souche_1']} vs {row['Souche_2']}: "
              f"Similarité = {row['Similarite_composite']:.3f}, "
              f"Distance = {row['Distance_genetique']:.3f}")
    
    # 5. Rapport textuel
    report_path = 'data/results/comparison_report.txt'
    with open(report_path, 'w') as f:
        f.write("=== RAPPORT DE COMPARAISON GÉNOMIQUE ===\n")
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"Projet: Lactobacillus bulgaricus - Génomique comparative\n\n")
        
        f.write("GÉNOMES COMPARÉS:\n")
        for strain in comparison_data['strain_names']:
            f.write(f"  - {strain}: {len(genomes_data[strain]):,} bp\n")
        
        f.write(f"\nMÉTHODES DE COMPARAISON:\n")
        f.write("  - Profils de k-mers (k=4): Composition en tétranucléotides\n")
        f.write("  - Similarité de séquence: Correspondances par fenêtres\n")
        f.write("  - Contenu GC: Corrélation des profils GC\n")
        f.write("  - Taille relative: Similarité basée sur la taille\n")
        
        upper_triangle = np.triu_indices_from(composite_matrix, k=1)
        f.write(f"\nRÉSULTATS PRINCIPAUX:\n")
        f.write(f"  - Similarité moyenne: {composite_matrix[upper_triangle].mean():.3f}\n")
        f.write(f"  - Distance moyenne: {1 - composite_matrix[upper_triangle].mean():.3f}\n")
    
    print_status('success', f"Rapport détaillé: {report_path}")
    
    print()
    print_status('success', "🎉 Comparaison génomique terminée!")
    print_status('info', "➡️  Prochaine étape: python3 scripts/04_visualize_results.py")
    print()

if __name__ == "__main__":
    main()