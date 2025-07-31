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
