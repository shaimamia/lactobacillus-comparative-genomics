#!/usr/bin/env python3
"""
Script 2: Analyse des séquences génomiques - Version simplifiée
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

def calculate_n50(lengths):
    """Calculer N50"""
    if not lengths:
        return 0
    sorted_lengths = sorted(lengths, reverse=True)
    total_length = sum(sorted_lengths)
    target = total_length / 2
    cumulative = 0
    for length in sorted_lengths:
        cumulative += length
        if cumulative >= target:
            return length
    return 0

def analyze_fasta_file(fasta_path, strain_name):
    """Analyser un fichier FASTA"""
    print_status('info', f"Analyse de {strain_name}...")
    
    if not os.path.exists(fasta_path):
        print_status('error', f"Fichier non trouvé: {fasta_path}")
        return None
    
    sequences = []
    sequence_lengths = []
    sequence_names = []
    
    try:
        for record in SeqIO.parse(fasta_path, "fasta"):
            sequences.append(str(record.seq))
            sequence_lengths.append(len(record.seq))
            sequence_names.append(record.id)
    except Exception as e:
        print_status('error', f"Erreur lecture {fasta_path}: {e}")
        return None
    
    if not sequences:
        print_status('error', f"Aucune séquence dans {fasta_path}")
        return None
    
    # Concaténer toutes les séquences
    full_genome = ''.join(sequences)
    
    # Calculer les statistiques
    stats = {
        'strain_name': strain_name,
        'file_path': fasta_path,
        'analysis_date': datetime.now().isoformat(),
        'num_contigs': len(sequences),
        'contig_lengths': sequence_lengths,
        'contig_names': sequence_names,
        'total_length': len(full_genome),
        'longest_contig': max(sequence_lengths) if sequence_lengths else 0,
        'shortest_contig': min(sequence_lengths) if sequence_lengths else 0,
        'mean_contig_length': np.mean(sequence_lengths) if sequence_lengths else 0,
        'median_contig_length': np.median(sequence_lengths) if sequence_lengths else 0,
        'n50': calculate_n50(sequence_lengths),
        'gc_content': calculate_gc_content(full_genome),
        'a_count': full_genome.count('A'),
        't_count': full_genome.count('T'),
        'g_count': full_genome.count('G'),
        'c_count': full_genome.count('C'),
        'n_count': full_genome.count('N'),
    }
    
    # Calculer AT content
    total_at = stats['a_count'] + stats['t_count']
    stats['at_content'] = (total_at / len(full_genome) * 100) if full_genome else 0
    
    print_status('success', f"{strain_name}: {stats['num_contigs']} contigs, {stats['total_length']:,} bp, GC: {stats['gc_content']:.1f}%")
    
    return stats

def create_summary_table(all_stats):
    """Créer un tableau de résumé"""
    summary_data = []
    
    for stats in all_stats:
        if stats:
            summary_data.append({
                'Souche': stats['strain_name'],
                'Contigs': stats['num_contigs'],
                'Taille_totale_bp': stats['total_length'],
                'Taille_totale_Mb': round(stats['total_length'] / 1_000_000, 2),
                'GC_percent': round(stats['gc_content'], 2),
                'AT_percent': round(stats['at_content'], 2),
                'N50_bp': stats['n50'],
                'Contig_max_bp': stats['longest_contig'],
                'Contig_min_bp': stats['shortest_contig'],
                'Contig_moyen_bp': round(stats['mean_contig_length'], 0),
                'Complexite': round(len(set(stats['contig_names'])) / stats['num_contigs'], 3) if stats['num_contigs'] > 0 else 0
            })
    
    return pd.DataFrame(summary_data)

def create_basic_plots(all_stats):
    """Créer des graphiques de base"""
    if not all_stats or all([s is None for s in all_stats]):
        print_status('warning', "Aucune donnée pour les graphiques")
        return
    
    valid_stats = [s for s in all_stats if s is not None]
    strains = [s['strain_name'] for s in valid_stats]
    
    # Créer les dossiers
    os.makedirs('data/results/plots', exist_ok=True)
    
    plt.style.use('default')
    
    # Graphique des statistiques de base
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Statistiques Génomiques - Lactobacillus bulgaricus', fontsize=14, fontweight='bold')
    
    # Taille des génomes
    genome_sizes = [s['total_length'] / 1_000_000 for s in valid_stats]
    bars1 = axes[0, 0].bar(strains, genome_sizes, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    axes[0, 0].set_title('Taille des Génomes (Mb)')
    axes[0, 0].set_ylabel('Taille (Mb)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    for bar, size in zip(bars1, genome_sizes):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       f'{size:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Contenu GC
    gc_contents = [s['gc_content'] for s in valid_stats]
    bars2 = axes[0, 1].bar(strains, gc_contents, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    axes[0, 1].set_title('Contenu GC (%)')
    axes[0, 1].set_ylabel('GC (%)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    for bar, gc in zip(bars2, gc_contents):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       f'{gc:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Nombre de contigs
    contig_counts = [s['num_contigs'] for s in valid_stats]
    bars3 = axes[1, 0].bar(strains, contig_counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    axes[1, 0].set_title('Nombre de Contigs')
    axes[1, 0].set_ylabel('Contigs')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    for bar, count in zip(bars3, contig_counts):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       f'{count}', ha='center', va='bottom', fontweight='bold')
    
    # N50
    n50_values = [s['n50'] / 1000 for s in valid_stats]
    bars4 = axes[1, 1].bar(strains, n50_values, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    axes[1, 1].set_title('N50 (kb)')
    axes[1, 1].set_ylabel('N50 (kb)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    for bar, n50 in zip(bars4, n50_values):
        axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(n50_values)*0.02,
                       f'{n50:.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    output_path = 'data/results/plots/genome_statistics.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print_status('success', f"Graphique sauvegardé: {output_path}")
    plt.close()

def main():
    """Fonction principale"""
    print("🧬 === ANALYSE DES SÉQUENCES GÉNOMIQUES ===")
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Créer les dossiers
    os.makedirs('data/analysis', exist_ok=True)
    os.makedirs('data/results/plots', exist_ok=True)
    
    # Analyser chaque souche
    all_stats = []
    
    print_status('info', f"Analyse de {len(STRAINS)} souches...")
    print()
    
    for strain_name, strain_info in STRAINS.items():
        filename = strain_info['filename']
        fasta_path = os.path.join('data/genomes', filename)
        
        stats = analyze_fasta_file(fasta_path, strain_name)
        all_stats.append(stats)
    
    print()
    
    # Filtrer les analyses réussies
    successful_analyses = [s for s in all_stats if s is not None]
    
    if not successful_analyses:
        print_status('error', "Aucune analyse réussie !")
        sys.exit(1)
    
    print_status('success', f"{len(successful_analyses)}/{len(all_stats)} analyses réussies")
    print()
    
    # Créer le tableau de résumé
    print_status('info', "Création du tableau de résumé...")
    summary_df = create_summary_table(successful_analyses)
    
    # Sauvegarder les résultats
    json_path = 'data/analysis/detailed_analysis.json'
    with open(json_path, 'w') as f:
        json.dump(successful_analyses, f, indent=2, default=str)
    print_status('success', f"Analyse détaillée: {json_path}")
    
    csv_path = 'data/analysis/genome_statistics.csv'
    summary_df.to_csv(csv_path, index=False)
    print_status('success', f"Tableau de résumé: {csv_path}")
    
    # Affichage du résumé
    print()
    print("📊 === RÉSUMÉ DES ANALYSES ===")
    print()
    print(summary_df.to_string(index=False))
    print()
    
    # Créer des graphiques
    print_status('info', "Création des visualisations...")
    create_basic_plots(successful_analyses)
    
    # Rapport textuel
    report_path = 'data/analysis/analysis_report.txt'
    with open(report_path, 'w') as f:
        f.write("=== RAPPORT D'ANALYSE GÉNOMIQUE ===\n")
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"Projet: Lactobacillus bulgaricus - Génomique comparative\n\n")
        
        f.write("SOUCHES ANALYSÉES:\n")
        for stats in successful_analyses:
            f.write(f"\n{stats['strain_name']}:\n")
            f.write(f"  - Taille: {stats['total_length']:,} bp ({stats['total_length']/1_000_000:.2f} Mb)\n")
            f.write(f"  - Contigs: {stats['num_contigs']}\n")
            f.write(f"  - GC: {stats['gc_content']:.1f}%\n")
            f.write(f"  - N50: {stats['n50']:,} bp\n")
        
        f.write(f"\nSTATISTIQUES COMPARATIVES:\n")
        f.write(f"  - Taille moyenne: {summary_df['Taille_totale_bp'].mean():,.0f} bp\n")
        f.write(f"  - GC moyen: {summary_df['GC_percent'].mean():.1f}%\n")
        f.write(f"  - Variation de taille: {summary_df['Taille_totale_bp'].std():,.0f} bp\n")
        f.write(f"  - Variation GC: {summary_df['GC_percent'].std():.2f}%\n")
    
    print_status('success', f"Rapport textuel: {report_path}")
    
    print()
    print_status('success', "🎉 Analyse des séquences terminée!")
    print_status('info', "➡️  Prochaine étape: python3 scripts/03_genome_comparison.py")
    print()

if __name__ == "__main__":
    main()