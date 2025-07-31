# Génomique Comparative - *Lactobacillus bulgaricus*

> **Projet de bioinformatique** : Pipeline Python d'analyse comparative de 3 souches de *Lactobacillus bulgaricus*

## Description

Ce projet compare **3 souches différentes** de *Lactobacillus bulgaricus* en utilisant un pipeline Python natif pour identifier les similitudes et différences génomiques, crée des visualisations scientifiques, et comprend la diversité génétique de cette espèce importante en industrie alimentaire.

### Objectifs
- Développer un pipeline bioinformatique en Python
- Analyser et comparer des génomes bactériens
- Visualiser les résultats obtenues
- Interpréter des données génomiques

## Souches Analysées

| Souche | Code NCBI | Description | Application |
|--------|-----------|-------------|-------------|
| **ATCC 11842** | GCF_000196515.1 | Souche type de référence | Standard taxonomique |
| **DSM 20081** | GCF_000027045.1 | Souche commerciale | Industrie alimentaire |
| **CNCM I-1519** | GCF_000006865.2 | Souche probiotique | Applications thérapeutiques |

## Installation et Configuration

### Prérequis
- **Système** : macOS (testé sur M4 Pro), Linux
- **Espace disque** : 2 GB libre
- **RAM** : 4 GB minimum
- **Temps d'exécution** : 15-30 minutes

### 1. Cloner le projet
```bash
git clone https://github.com/shaimamia/lactobacillus-comparative-genomics.git
cd lactobacillus-comparative-genomics
```

### 2. Préparation de l'environnement conda
```bash
# Puis créer l'environnement
conda env create -f environment.yaml
conda activate lacto-genomics
```

### 3. Configuration initiale
```bash
./setup.sh
```

## Utilisation

### Option 1: Pipeline automatique 
```bash
./run_pipeline.sh
```

### Option 2: Étape par étape
```bash
# Étape 1: Télécharger les génomes
./scripts/01_download_genomes.sh

# Étape 2: Analyser les séquences
python3 scripts/02_sequence_analysis.py

# Étape 3: Comparaison génomique
python3 scripts/03_genome_comparison.py

# Étape 4: Visualisation des résultats
python3 scripts/04_visualize_results.py
```

## Résultats Attendus

### Structure des fichiers générés
```
data/
├── genomes/              # Génomes téléchargés (.fna)
├── analysis/             # Analyses de séquences
└── results/
    ├── genome_stats.csv         # Statistiques des génomes
    ├── comparison_matrix.csv    # Matrice de comparaison
    ├── similarity_analysis.csv  # Analyse de similarité
    ├── report.html             # Rapport complet
    └── plots/                  # Visualisations
        ├── genome_composition.png
        ├── length_distribution.png
        ├── similarity_heatmap.png
        └── phylogenetic_tree.png
```

### Métriques calculées
- **Composition nucléotidique** : %GC, distribution des bases
- **Statistiques de séquence** : Longueur, nombre de contigs, N50
- **Similarité inter-génomes** : Comparaisons deux à deux
- **Analyses phylogénétiques** : Relations évolutives

## Visualisations

1. **Composition des génomes** : Graphiques en barres et secteurs
2. **Distribution des longueurs** : Histogrammes des contigs
3. **Heatmap de similarité** : Matrice de comparaison
4. **Arbre phylogénétique** : Relations entre souches

## Interprétation Biologique

### Analyse de composition
- **Contenu GC** : Indicateur de stabilité thermique
- **Taille du génome** : Complexité métabolique
- **Nombre de contigs** : Qualité d'assemblage

### Comparaisons inter-souches
- **Similarité élevée** : Gènes conservés essentiels
- **Différences** : Adaptations environnementales spécifiques
- **Clustering** : Relations phylogénétiques

