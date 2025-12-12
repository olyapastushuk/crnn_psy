import os
import pandas as pd
from sklearn.model_selection import train_test_split

# шлях до RAVDESS
AUDIO_DIR = "audio"
OUT_DIR = "data"

# мапа емоцій -> VA
emo2va = {
    "01": [0.0, 0.1],   # neutral
    "02": [0.2, 0.2],   # calm
    "03": [0.8, 0.6],   # happy
    "04": [-0.6, -0.3], # sad
    "05": [-0.7, 0.8],  # angry
    "06": [-0.8, 0.9],  # fear
    "07": [-0.6, 0.5],  # disgust
    "08": [0.3, 0.7],   # surprise
}

rows = []

for root, _, files in os.walk(AUDIO_DIR):
    for f in files:
        if f.endswith(".wav"):
            parts = f.split("-")
            emo_code = parts[2]  # третій елемент = емоція
            val, aro = emo2va[emo_code]
            path = os.path.join(root, f)
            rows.append([path, val, aro])

# розбивка на train/val
train, val = train_test_split(rows, test_size=0.2, random_state=42)

pd.DataFrame(train, columns=["path","valence","arousal"]).to_csv(os.path.join(OUT_DIR,"labels_train.csv"), index=False)
pd.DataFrame(val, columns=["path","valence","arousal"]).to_csv(os.path.join(OUT_DIR,"labels_val.csv"), index=False)
