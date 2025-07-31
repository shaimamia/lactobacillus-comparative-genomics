# Aide-Mémoire - Lactobacillus Comparative Genomics

## Démarrage rapide

```bash
# Configuration initiale
./setup.sh

# Activation de l'environnement
conda activate lacto-genomics

# Test rapide
./test_installation.sh

# Pipeline complet
./run_pipeline.sh
```

## Structure des fichiers

```
lactobacillus-comparative-genomics/
├── data/
│   ├── genomes/           # Fichiers FASTA (.fna)
│   ├── annotations/       # Fichiers GFF de Prokka
│   └── results/           # Résultats de Roary
├── scripts/               # Scripts du pipeline
├── logs/                  # Logs d'exécution
└── docs/                  # Documentation
```

## Commandes utiles

### Gestion de l'environnement
```bash
conda activate lacto-genomics    # Activer
conda deactivate                 # Désactiver
conda env list                   # Lister les environnements
```

### Vérification des données
```bash
ls -la data/genomes/            # Vérifier les génomes
ls -la data/annotations/        # Vérifier les annotations
ls -la data/results/            # Vérifier les résultats
```

### Nettoyage
```bash
rm -rf data/annotations/*       # Supprimer les annotations
rm -rf data/results/*           # Supprimer les résultats
rm -rf logs/*                   # Supprimer les logs
```

## Dépannage

### Problème de téléchargement
```bash
# Vérifier la connexion internet
ping google.com

# Télécharger manuellement un génome
wget [URL] -O data/genomes/genome.fna.gz
gunzip data/genomes/genome.fna.gz
```

### Problème Prokka
```bash
# Vérifier l'installation
prokka --version

# Réinstaller
conda install -c bioconda prokka=1.14.6
```

### Problème Roary
```bash
# Vérifier les fichiers GFF
head data/annotations/*.gff

# Test simple
roary --help
```

## Interprétation des résultats

- **Core genome** : Gènes dans toutes les souches 
- **Accessory genome** : Gènes dans certaines souches 
- **Unique genes** : Gènes dans une seule souche 

## Visualisation

- **Rapport HTML** : `firefox data/results/report.html`
- **Graphiques** : Dossier `data/results/plots/`
- **Données brutes** : `data/results/gene_presence_absence.csv`
