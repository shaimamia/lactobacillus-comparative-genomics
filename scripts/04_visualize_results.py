#!/usr/bin/env python3
"""
Script 4: Visualisation des résultats et création du rapport final
Pipeline Python de génomique comparative - Lactobacillus bulgaricus
Auteur: [Votre Nom]

Ce script crée des visualisations avancées et un rapport HTML interactif
compilant tous les résultats de l'analyse génomique comparative.
"""

import os
import sys
import pandas as pd
import numpy as np
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo

# Configuration
sys.path.append('.')
try:
    from config import STRAINS, PATHS, ANALYSIS_PARAMS, PROJECT_NAME, ORGANISM
except ImportError:
    print("❌ Erreur: fichier config.py non trouvé")
    sys.exit(1)

def print_status(status, message):
    """Afficher des messages avec des couleurs et icônes"""
    colors = {
        'success': '\033[92m✅',
        'error': '\033[91m❌', 
        'warning': '\033[93m⚠️',
        'info': '\033[94mℹ️'
    }
    print(f"{colors.get(status, '')} {message}\033[0m")

def load_analysis_results():
    """Charger tous les résultats des analyses précédentes"""
    results = {}
    
    # Charger les statistiques génomiques
    stats_path = os.path.join(PATHS['analysis'], 'genome_statistics.csv')
    if os.path.exists(stats_path):
        results['genome_stats'] = pd.read_csv(stats_path)
        print_status('success', "Statistiques génomiques chargées")
    else:
        print_status('warning', f"Fichier non trouvé: {stats_path}")
    
    # Charger les analyses détaillées JSON
    detailed_path = os.path.join(PATHS['analysis'], 'detailed_analysis.json')
    if os.path.exists(detailed_path):
        with open(detailed_path, 'r') as f:
            results['detailed_analysis'] = json.load(f)
        print_status('success', "Analyses détaillées chargées")
    else:
        print_status('warning', f"Fichier non trouvé: {detailed_path}")
    
    # Charger les comparaisons
    comparison_path = os.path.join(PATHS['results'], 'pairwise_comparisons.csv')
    if os.path.exists(comparison_path):
        results['comparisons'] = pd.read_csv(comparison_path)
        print_status('success', "Comparaisons par paires chargées")
    else:
        print_status('warning', f"Fichier non trouvé: {comparison_path}")
    
    # Charger la matrice de similarité
    similarity_path = os.path.join(PATHS['results'], 'similarity_matrix.csv')
    if os.path.exists(similarity_path):
        results['similarity_matrix'] = pd.read_csv(similarity_path, index_col=0)
        print_status('success', "Matrice de similarité chargée")
    else:
        print_status('warning', f"Fichier non trouvé: {similarity_path}")
    
    return results

def create_interactive_genome_overview(genome_stats):
    """Créer un graphique interactif de vue d'ensemble des génomes"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Taille des Génomes', 'Contenu GC', 'Nombre de Contigs', 'Valeur N50'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    strains = genome_stats['Souche'].tolist()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    # Taille des génomes
    fig.add_trace(
        go.Bar(x=strains, y=genome_stats['Taille_totale_Mb'], 
               name='Taille (Mb)', marker_color=colors[0],
               text=genome_stats['Taille_totale_Mb'], textposition='auto'),
        row=1, col=1
    )
    
    # Contenu GC
    fig.add_trace(
        go.Bar(x=strains, y=genome_stats['GC_percent'], 
               name='GC %', marker_color=colors[1],
               text=genome_stats['GC_percent'], textposition='auto'),
        row=1, col=2
    )
    
    # Nombre de contigs
    fig.add_trace(
        go.Bar(x=strains, y=genome_stats['Contigs'], 
               name='Contigs', marker_color=colors[2],
               text=genome_stats['Contigs'], textposition='auto'),
        row=2, col=1
    )
    
    # N50
    fig.add_trace(
        go.Bar(x=strains, y=genome_stats['N50_bp']/1000, 
               name='N50 (kb)', marker_color=colors[3],
               text=(genome_stats['N50_bp']/1000).round(0), textposition='auto'),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="Vue d'ensemble des Génomes - Lactobacillus bulgaricus",
        title_x=0.5,
        showlegend=False,
        height=600
    )
    
    return fig

def create_interactive_similarity_heatmap(similarity_matrix):
    """Créer une heatmap interactive de similarité"""
    
    fig = go.Figure(data=go.Heatmap(
        z=similarity_matrix.values,
        x=similarity_matrix.columns,
        y=similarity_matrix.index,
        colorscale='RdYlBu_r',
        zmin=0, zmax=1,
        text=similarity_matrix.values.round(3),
        texttemplate="%{text}",
        textfont={"size": 12},
        colorbar=dict(title="Similarité")
    ))
    
    fig.update_layout(
        title="Matrice de Similarité Génomique",
        title_x=0.5,
        xaxis_title="Souches",
        yaxis_title="Souches",
        height=500
    )
    
    return fig

def create_comparative_radar_chart(genome_stats):
    """Créer un graphique radar comparatif"""
    
    # Normaliser les données entre 0 et 1
    metrics = ['Taille_totale_Mb', 'GC_percent', 'Contigs', 'N50_bp', 'Complexite']
    
    # Vérifier quelles métriques sont disponibles
    available_metrics = [m for m in metrics if m in genome_stats.columns]
    
    if not available_metrics:
        print_status('warning', "Aucune métrique disponible pour le graphique radar")
        return None
    
    # Normaliser chaque métrique
    normalized_data = genome_stats.copy()
    for metric in available_metrics:
        if metric in normalized_data.columns:
            max_val = normalized_data[metric].max()
            min_val = normalized_data[metric].min()
            if max_val != min_val:
                normalized_data[metric] = (normalized_data[metric] - min_val) / (max_val - min_val)
            else:
                normalized_data[metric] = 0.5  # Valeur par défaut si toutes identiques
    
    fig = go.Figure()
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    for i, (_, row) in enumerate(normalized_data.iterrows()):
        values = [row[metric] for metric in available_metrics if metric in row]
        values.append(values[0])  # Fermer le polygone
        
        metric_labels = [metric.replace('_', ' ').title() for metric in available_metrics]
        metric_labels.append(metric_labels[0])  # Fermer le polygone
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metric_labels,
            fill='toself',
            name=row['Souche'],
            line_color=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        title="Profil Comparatif des Souches",
        title_x=0.5
    )
    
    return fig

def create_composition_sunburst(genome_stats):
    """Créer un graphique sunburst de la composition"""
    
    # Préparer les données pour le sunburst
    data = []
    
    for _, row in genome_stats.iterrows():
        strain = row['Souche']
        gc_percent = row['GC_percent']
        at_percent = row['AT_percent']
        
        # Niveau 1: Souche
        data.append(dict(ids=strain, labels=strain, parents=""))
        
        # Niveau 2: GC vs AT
        data.append(dict(ids=f"{strain}_GC", labels=f"GC ({gc_percent:.1f}%)", 
                        parents=strain, values=gc_percent))
        data.append(dict(ids=f"{strain}_AT", labels=f"AT ({at_percent:.1f}%)", 
                        parents=strain, values=at_percent))
    
    if data:
        fig = go.Figure(go.Sunburst(
            ids=[d['ids'] for d in data],
            labels=[d['labels'] for d in data],
            parents=[d['parents'] for d in data],
            values=[d.get('values', 1) for d in data],
        ))
        
        fig.update_layout(
            title="Composition Nucléotidique par Souche",
            title_x=0.5
        )
        
        return fig
    
    return None

def create_static_plots(results):
    """Créer des graphiques statiques supplémentaires"""
    
    # Configuration matplotlib
    plt.style.use('default')
    sns.set_palette("husl")
    
    if 'genome_stats' in results:
        genome_stats = results['genome_stats']
        
        # 1. Graphique de distribution des tailles
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Distribution des tailles
        plt.subplot(2, 2, 1)
        strains = genome_stats['Souche']
        sizes_mb = genome_stats['Taille_totale_Mb']
        
        bars = plt.bar(strains, sizes_mb, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        plt.title('Distribution des Tailles de Génomes', fontweight='bold')
        plt.ylabel('Taille (Mb)')
        plt.xticks(rotation=45)
        
        # Ajouter les valeurs
        for bar, size in zip(bars, sizes_mb):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{size:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # Subplot 2: Corrélation GC vs Taille
        plt.subplot(2, 2, 2)
        plt.scatter(genome_stats['GC_percent'], genome_stats['Taille_totale_Mb'], 
                   s=100, alpha=0.7, c=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        
        for i, strain in enumerate(strains):
            plt.annotate(strain, 
                        (genome_stats['GC_percent'].iloc[i], genome_stats['Taille_totale_Mb'].iloc[i]),
                        xytext=(5, 5), textcoords='offset points')
        
        plt.xlabel('Contenu GC (%)')
        plt.ylabel('Taille du génome (Mb)')
        plt.title('Corrélation GC vs Taille', fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Subplot 3: Complexité vs N50
        plt.subplot(2, 2, 3)
        if 'Complexite' in genome_stats.columns:
            plt.scatter(genome_stats['Complexite'], genome_stats['N50_bp']/1000, 
                       s=100, alpha=0.7, c=['#FF6B6B', '#4ECDC4', '#45B7D1'])
            
            for i, strain in enumerate(strains):
                plt.annotate(strain, 
                            (genome_stats['Complexite'].iloc[i], genome_stats['N50_bp'].iloc[i]/1000),
                            xytext=(5, 5), textcoords='offset points')
            
            plt.xlabel('Complexité de séquence')
            plt.ylabel('N50 (kb)')
            plt.title('Complexité vs Qualité d\'assemblage', fontweight='bold')
            plt.grid(True, alpha=0.3)
        
        # Subplot 4: Comparaison multi-métriques
        plt.subplot(2, 2, 4)
        metrics = ['GC_percent', 'Taille_totale_Mb', 'Contigs']
        x_pos = np.arange(len(strains))
        width = 0.25
        
        # Normaliser pour visualisation
        for i, metric in enumerate(metrics):
            if metric in genome_stats.columns:
                values = genome_stats[metric]
                normalized_values = (values - values.min()) / (values.max() - values.min())
                plt.bar(x_pos + i * width, normalized_values, width, 
                       label=metric.replace('_', ' ').title(), alpha=0.8)
        
        plt.xlabel('Souches')
        plt.ylabel('Valeurs normalisées')
        plt.title('Comparaison Multi-métriques', fontweight='bold')
        plt.xticks(x_pos + width, strains, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Sauvegarder
        output_path = os.path.join(PATHS['plots'], 'comprehensive_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print_status('success', f"Analyse complète: {output_path}")
        plt.close()

def generate_html_report(results):
    """Générer un rapport HTML interactif complet"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse Génomique - {ORGANISM}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            margin: 0.5rem 0 0 0;
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .content {{
            padding: 2rem;
        }}
        .section {{
            margin-bottom: 3rem;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #2E86AB;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 0.5rem;
            margin-top: 0;
        }}
        .plot-container {{
            margin: 1rem 0;
            background: white;
            border-radius: 5px;
            padding: 1rem;
            box-shadow: 0 1px 5px rgba(0,0,0,0.1);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            display: block;
        }}
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }}
        .table-container {{
            overflow-x: auto;
            margin: 1rem 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 1px 5px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #2E86AB;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .highlight {{
            background: linear-gradient(90deg, #FFD93D 0%, #FF6B6B 100%);
            color: white;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            text-align: center;
            font-weight: bold;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 2rem;
            text-align: center;
            margin-top: 2rem;
        }}
        .methodology {{
            background: #e8f4f8;
            border-left: 4px solid #2E86AB;
            padding: 1rem;
            margin: 1rem 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧬 Rapport d'Analyse Génomique</h1>
            <p><em>{ORGANISM}</em> - Génomique Comparative</p>
            <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>
        
        <div class="content">
"""
    
    # Section vue d'ensemble
    if 'genome_stats' in results:
        genome_stats = results['genome_stats']
        
        html_content += f"""
            <div class="section">
                <h2>📊 Vue d'Ensemble des Génomes</h2>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-number">{len(genome_stats)}</span>
                        <div class="stat-label">Souches analysées</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">{genome_stats['Taille_totale_Mb'].mean():.2f}</span>
                        <div class="stat-label">Taille moyenne (Mb)</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">{genome_stats['GC_percent'].mean():.1f}%</span>
                        <div class="stat-label">Contenu GC moyen</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">{genome_stats['Contigs'].sum()}</span>
                        <div class="stat-label">Contigs totaux</div>
                    </div>
                </div>
                
                <div class="plot-container">
                    <div id="overview-plot"></div>
                </div>
                
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Souche</th>
                                <th>Taille (Mb)</th>
                                <th>GC (%)</th>
                                <th>Contigs</th>
                                <th>N50 (kb)</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for _, row in genome_stats.iterrows():
            html_content += f"""
                            <tr>
                                <td><strong>{row['Souche']}</strong></td>
                                <td>{row['Taille_totale_Mb']:.2f}</td>
                                <td>{row['GC_percent']:.1f}</td>
                                <td>{row['Contigs']}</td>
                                <td>{row['N50_bp']/1000:.0f}</td>
                            </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        """
    
    # Section comparaisons
    if 'comparisons' in results:
        comparisons = results['comparisons']
        
        html_content += f"""
            <div class="section">
                <h2>🔬 Analyses Comparatives</h2>
                
                <div class="highlight">
                    Les souches montrent une similarité moyenne de {comparisons['Similarite_composite'].mean():.3f}
                    avec une distance génétique moyenne de {comparisons['Distance_genetique'].mean():.3f}
                </div>
                
                <div class="plot-container">
                    <div id="similarity-heatmap"></div>
                </div>
                
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Comparaison</th>
                                <th>Similarité K-mers</th>
                                <th>Similarité GC</th>
                                <th>Similarité Composite</th>
                                <th>Distance Génétique</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for _, row in comparisons.iterrows():
            html_content += f"""
                            <tr>
                                <td><strong>{row['Souche_1']} vs {row['Souche_2']}</strong></td>
                                <td>{row['Similarite_kmers']:.3f}</td>
                                <td>{row['Similarite_GC']:.3f}</td>
                                <td>{row['Similarite_composite']:.3f}</td>
                                <td>{row['Distance_genetique']:.3f}</td>
                            </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        """
    
    # Section méthodologie
    html_content += """
            <div class="section">
                <h2>🔬 Méthodologie</h2>
                
                <div class="methodology">
                    <h3>Pipeline d'Analyse</h3>
                    <ol>
                        <li><strong>Téléchargement :</strong> Récupération des génomes depuis NCBI</li>
                        <li><strong>Analyse des séquences :</strong> Calcul des statistiques génomiques avec Biopython</li>
                        <li><strong>Comparaison :</strong> Analyse de similarité multi-critères</li>
                        <li><strong>Visualisation :</strong> Création de graphiques interactifs</li>
                    </ol>
                </div>
                
                <div class="methodology">
                    <h3>Métriques Calculées</h3>
                    <ul>
                        <li><strong>K-mers :</strong> Profils de tétranucléotides pour la composition</li>
                        <li><strong>Contenu GC :</strong> Pourcentage de guanine et cytosine</li>
                        <li><strong>N50 :</strong> Métrique de qualité d'assemblage</li>
                        <li><strong>Complexité :</strong> Diversité des séquences</li>
                    </ul>
                </div>
                
                <div class="methodology">
                    <h3>Outils Utilisés</h3>
                    <ul>
                        <li><strong>Python 3.9 :</strong> Langage principal</li>
                        <li><strong>Biopython :</strong> Analyse des séquences biologiques</li>
                        <li><strong>Pandas/NumPy :</strong> Manipulation et calculs sur les données</li>
                        <li><strong>Plotly :</strong> Visualisations interactives</li>
                        <li><strong>Matplotlib/Seaborn :</strong> Graphiques statistiques</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Rapport généré par le pipeline de génomique comparative</p>
            <p>Projet développé pour l'analyse de <em>Lactobacillus bulgaricus</em></p>
            <p>© {datetime.now().year} - Pipeline Python de bioinformatique</p>
        </div>
    </div>
    
    <script>
    """
    
    # Ajouter les scripts Plotly pour les graphiques interactifs
    if 'genome_stats' in results:
        # Créer les graphiques interactifs
        overview_fig = create_interactive_genome_overview(results['genome_stats'])
        if overview_fig:
            html_content += f"""
        // Graphique vue d'ensemble
        var overviewData = {overview_fig.to_json()};
        Plotly.newPlot('overview-plot', overviewData.data, overviewData.layout);
            """
    
    if 'similarity_matrix' in results:
        similarity_fig = create_interactive_similarity_heatmap(results['similarity_matrix'])
        if similarity_fig:
            html_content += f"""
        // Heatmap de similarité
        var similarityData = {similarity_fig.to_json()};
        Plotly.newPlot('similarity-heatmap', similarityData.data, similarityData.layout);
            """
    
    html_content += """
    </script>
</body>
</html>
    """
    
    return html_content

def main():
    """Fonction principale"""
    print("🎨 === VISUALISATION ET RAPPORT FINAL ===")
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Charger tous les résultats
    print_status('info', "Chargement des résultats d'analyse...")
    results = load_analysis_results()
    
    if not results:
        print_status('error', "Aucun résultat trouvé ! Exécutez d'abord les étapes précédentes.")
        sys.exit(1)
    
    print()
    
    # Créer les visualisations statiques
    print_status('info', "Création des graphiques statiques...")
    create_static_plots(results)
    
    # Créer les graphiques interactifs individuels
    print_status('info', "Création des graphiques interactifs...")
    
    if 'genome_stats' in results:
        # Graphique radar
        radar_fig = create_comparative_radar_chart(results['genome_stats'])
        if radar_fig:
            radar_path = os.path.join(PATHS['plots'], 'radar_chart.html')
            pyo.plot(radar_fig, filename=radar_path, auto_open=False)
            print_status('success', f"Graphique radar: {radar_path}")
        
        # Graphique sunburst
        sunburst_fig = create_composition_sunburst(results['genome_stats'])
        if sunburst_fig:
            sunburst_path = os.path.join(PATHS['plots'], 'composition_sunburst.html')
            pyo.plot(sunburst_fig, filename=sunburst_path, auto_open=False)
            print_status('success', f"Graphique sunburst: {sunburst_path}")
    
    # Générer le rapport HTML principal
    print_status('info', "Génération du rapport HTML interactif...")
    html_content = generate_html_report(results)
    
    # Sauvegarder le rapport
    report_path = os.path.join(PATHS['results'], 'rapport_final.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print_status('success', f"Rapport principal: {report_path}")
    
    # Créer un index des fichiers générés
    print_status('info', "Création de l'index des résultats...")
    
    index_content = f"""
# 📊 Index des Résultats - {ORGANISM}

## 📁 Structure des Fichiers Générés

### Données d'Analyse
- `data/analysis/genome_statistics.csv` - Statistiques détaillées des génomes
- `data/analysis/detailed_analysis.json` - Données brutes complètes
- `data/analysis/analysis_report.txt` - Rapport textuel

### Comparaisons
- `data/results/similarity_matrix.csv` - Matrice de similarité
- `data/results/pairwise_comparisons.csv` - Comparaisons par paires
- `data/results/comparison_report.txt` - Rapport de comparaison

### Visualisations
- `data/results/plots/genome_statistics.png` - Vue d'ensemble des génomes
- `data/results/plots/similarity_matrices.png` - Matrices de similarité
- `data/results/plots/phylogenetic_tree.png` - Arbre phylogénétique
- `data/results/plots/comprehensive_analysis.png` - Analyse complète

### Rapports Interactifs
- `data/results/rapport_final.html` - **Rapport principal interactif**
- `data/results/plots/radar_chart.html` - Graphique radar comparatif
- `data/results/plots/composition_sunburst.html` - Composition nucléotidique

## 🌐 Comment Consulter les Résultats

### Rapport Principal (Recommandé)
```bash
open data/results/rapport_final.html
# ou
firefox data/results/rapport_final.html
```

### Graphiques Individuels
```bash
open data/results/plots/
```

### Données Brutes
```bash
cat data/analysis/genome_statistics.csv
cat data/results/pairwise_comparisons.csv
```

## 📈 Résumé des Analyses

Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Souches: {len(STRAINS)} génomes analysés
Pipeline: Python natif (compatible macOS M4 Pro)

---
*Généré automatiquement par le pipeline de génomique comparative*
    """
    
    index_path = os.path.join(PATHS['results'], 'INDEX.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print_status('success', f"Index créé: {index_path}")
    
    print()
    print("🎉 === VISUALISATION TERMINÉE ===")
    print()
    print("📊 Fichiers générés:")
    print(f"   📄 Rapport principal: {report_path}")
    print(f"   📋 Index: {index_path}")
    print(f"   📁 Graphiques: {PATHS['plots']}/")
    print()
    print("🌐 Pour consulter les résultats:")
    print(f"   open {report_path}")
    print("   ou")
    print(f"   firefox {report_path}")
    print()
    print_status('success', "🎯 Pipeline de génomique comparative terminé!")
    print()

if __name__ == "__main__":
    main()