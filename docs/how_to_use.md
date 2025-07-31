# 🧬 Génomique Comparative - Guide Débutant Complet

> **Projet simple** : Comparer 3 bactéries et créer des graphiques automatiquement !

## 🎯 Ce que fait ce projet

Ce programme **compare automatiquement 3 souches de bactéries** et génère :
- 📊 Des graphiques comparatifs
- 📄 Un rapport HTML interactif  
- 📈 Des statistiques détaillées
- 🌳 Un arbre phylogénétique

**Temps requis :** 15-30 minutes  
**Niveau :** Débutant complet OK !

---

## 🖥️ Prérequis (À installer avant de commencer)

### 1. **macOS** (testé sur M1/M2/M3/M4 Pro)
- ✅ Si vous avez un Mac, c'est parfait !
- ⚠️ Linux possible mais non testé dans ce guide

### 2. **Terminal** 
- 🔍 Cherchez "Terminal" dans Spotlight (Cmd+Espace)
- 📱 Ou dans Applications > Utilitaires > Terminal

### 3. **Miniconda** (gestionnaire de logiciels Python)
- 🌐 Allez sur : https://docs.conda.io/en/latest/miniconda.html
- 📥 Téléchargez "Miniconda3 macOS Apple M1 64-bit pkg" 
- 🖱️ Double-cliquez le fichier téléchargé et suivez l'installation
- ✅ Redémarrez votre Terminal après installation

---

## 📥 Installation - Étape par Étape

### Étape 1 : Télécharger le projet

```bash
# Ouvrez votre Terminal et tapez (une ligne à la fois) :

# Aller sur votre Bureau
cd ~/Desktop

# Télécharger le projet
git clone https://github.com/saihi-chaimae/lactobacillus-comparative-genomics.git

# Entrer dans le dossier
cd lactobacillus-comparative-genomics
```

### Étape 2 : Installation automatique

```bash
# Lancer l'installation (ça prend 5-10 minutes)
./setup.sh
```

**⏳ Attendez que ça termine...**  
Vous devriez voir des ✅ partout à la fin.

### Étape 3 : Vérification

```bash
# Activer l'environnement Python
conda activate lacto-genomics

# Tester que tout marche
python -c "import pandas, numpy, matplotlib; print('✅ Tout fonctionne !')"
```

Si vous voyez "✅ Tout fonctionne !", c'est parfait ! 🎉

---

## 🚀 Utilisation - Super Simple !

### Option 1 : **Automatique** (Recommandé pour débutants)

```bash
# Activer l'environnement
conda activate lacto-genomics

# Lancer tout le pipeline automatiquement
./run_pipeline.sh
```

**C'est tout !** 🎉 Le programme va :
1. Télécharger 3 génomes de bactéries
2. Les analyser automatiquement  
3. Créer des graphiques
4. Générer un rapport HTML

**⏱️ Temps d'attente :** 5-15 minutes

### Option 2 : **Manuel** (Pour comprendre chaque étape)

```bash
# Activer l'environnement
conda activate lacto-genomics

# Étape 1 : Télécharger les génomes
./scripts/01_download_genomes.sh

# Étape 2 : Analyser les séquences
python3 scripts/02_sequence_analysis.py

# Étape 3 : Comparer les génomes
python3 scripts/03_genome_comparison.py

# Étape 4 : Créer les visualisations
python3 scripts/04_visualize_results.py
```

---

## 📊 Voir les Résultats

### Rapport Principal (le plus important !)

```bash
# Ouvrir le rapport dans votre navigateur
open data/results/rapport_final.html
```

### Autres fichiers intéressants

```bash
# Voir tous les fichiers générés
ls data/results/

# Voir les graphiques
open data/results/plots/
```

---

## ❓ Problèmes Courants et Solutions

### ❌ "conda: command not found"

**Solution :**
```bash
# Redémarrer le Terminal complètement
# Ou taper :
source ~/.bash_profile
```

### ❌ "Permission denied"

**Solution :**
```bash
# Donner les permissions d'exécution
chmod +x *.sh
chmod +x scripts/*.sh
```

### ❌ "No such file or directory"

**Solution :**
```bash
# Vérifier que vous êtes dans le bon dossier
pwd
# Vous devriez voir quelque chose comme "/Users/[votre-nom]/Desktop/lactobacillus-comparative-genomics"

# Si ce n'est pas le cas :
cd ~/Desktop/lactobacillus-comparative-genomics
```

### ❌ L'installation est très lente

**C'est normal !** L'installation de tous les outils peut prendre 10-20 minutes.  
☕ Prenez un café et attendez !

### ❌ "Import Error" ou erreurs Python

**Solution :**
```bash
# Réinstaller l'environnement
conda env remove -n lacto-genomics
conda env create -f environment.yaml
conda activate lacto-genomics
```

---

## 🎯 Ce que vous allez obtenir

### 📊 Graphiques générés automatiquement :
- **Taille des génomes** : Comparaison des 3 bactéries
- **Contenu GC** : Composition génétique
- **Arbre phylogénétique** : Relations entre les souches
- **Heatmap de similarité** : Qui ressemble à qui

### 📄 Fichiers de données :
- `genome_statistics.csv` : Statistiques détaillées
- `similarity_matrix.csv` : Matrice de comparaison
- `rapport_final.html` : Rapport complet interactif

### 🎨 Rapport HTML interactif avec :
- Graphiques cliquables
- Tableaux de données
- Explications biologiques
- Design professionnel

---

## 🔧 Commandes Utiles

### Nettoyer et recommencer
```bash
# Supprimer tous les résultats pour recommencer
rm -rf data/results/*
rm -rf data/analysis/*

# Relancer l'analyse
./run_pipeline.sh
```

### Voir les logs en cas de problème
```bash
# Voir les derniers logs
ls logs/
cat logs/pipeline_*.log
```

### Désactiver l'environnement Python
```bash
conda deactivate
```

### Voir l'aide
```bash
# Voir les options disponibles
./run_pipeline.sh --help
```

---

## 🎓 Pour Comprendre Plus

### Ce que fait chaque script :

1. **`01_download_genomes.sh`** : Télécharge 3 génomes de bactéries depuis NCBI
2. **`02_sequence_analysis.py`** : Analyse chaque génome (taille, composition, etc.)
3. **`03_genome_comparison.py`** : Compare les génomes entre eux
4. **`04_visualize_results.py`** : Crée les graphiques et le rapport final

### Technologies utilisées :
- **Python** : Langage de programmation
- **Biopython** : Analyse des séquences biologiques
- **Pandas** : Manipulation de données
- **Matplotlib/Plotly** : Création de graphiques

---

## 🆘 Besoin d'Aide ?

### 1. Vérifier les prérequis
```bash
# Vérifier que conda est installé
conda --version

# Vérifier que vous êtes dans le bon dossier
pwd
ls -la
```

### 2. Logs détaillés
```bash
# Voir tous les fichiers de log
ls logs/

# Voir le log le plus récent
cat logs/pipeline_*.log | tail -50
```

### 3. Test minimal
```bash
# Test simple pour voir si Python marche
conda activate lacto-genomics
python -c "print('Hello, genomics!')"
```

### 4. Recommencer from scratch
```bash
# Supprimer l'environnement et recommencer
conda env remove -n lacto-genomics
./setup.sh
```

---

## ✅ Check-list de Vérification

Avant de demander de l'aide, vérifiez :

- [ ] ✅ Miniconda installé
- [ ] ✅ Terminal ouvert dans le bon dossier
- [ ] ✅ `./setup.sh` exécuté sans erreur
- [ ] ✅ `conda activate lacto-genomics` fonctionne
- [ ] ✅ Test Python réussi
- [ ] ✅ Connexion internet active

---



---

**🚀 Bon voyage dans le monde de la génomique ! 🧬**