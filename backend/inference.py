import torch
import math
import librosa
import numpy as np
import torch.nn as nn
import webrtcvad
from backend.model import EmotionCRNN  # Імпортуємо вашу архітектуру

class EmotionPredictor:
    def __init__(self, checkpoint_path, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Параметри аудіо з вашого файлу dataset.py[cite: 1]
        self.sr = 16000
        self.n_mels = 128
        self.duration = 4.0
        self.samples = int(self.sr * self.duration)
        
        # Ініціалізація VAD (агресивність 3 — найвища точність відсікання шуму)
        self.vad = webrtcvad.Vad(3)
        
        # Ініціалізація моделі та завантаження ваг[cite: 1, 2]
        self.model = EmotionCRNN(num_outputs=3).to(self.device)
        self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        self.model.eval()

    def is_speech_present(self, audio_path):
        """Перевіряє, чи є людський голос у файлі (VAD)"""
        # VAD працює тільки з частотою 16000 Гц[cite: 1]
        audio, _ = librosa.load(audio_path, sr=16000)
        
        # Конвертація у 16-бітний формат (вимога webrtcvad)
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Розбиваємо на фрейми по 30мс
        samples_per_frame = int(16000 * 0.03) 
        speech_frames = 0
        total_frames = 0
        
        for i in range(0, len(audio_int16) - samples_per_frame, samples_per_frame):
            frame = audio_int16[i:i + samples_per_frame]
            if self.vad.is_speech(frame.tobytes(), 16000):
                speech_frames += 1
            total_frames += 1
        
        # Якщо менше 10% запису містить голос — вважаємо це шумом
        return (speech_frames / total_frames) > 0.1

    def _load_and_preprocess(self, path):
        """Відтворює логіку з EmotionVADDataset[cite: 1]"""
        # 1. Завантаження та перетворення в моно[cite: 1]
        audio, _ = librosa.load(path, sr=self.sr)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
            
        # 2. Pad/Crop до 4 секунд[cite: 1]
        if len(audio) < self.samples:
            audio = np.pad(audio, (0, self.samples - len(audio)))
        else:
            audio = audio[:self.samples]
            
        # 3. Обчислення Мел-спектрограми[cite: 1]
        mel = librosa.feature.melspectrogram(
            y=audio, sr=self.sr, n_mels=self.n_mels,
            n_fft=1024, hop_length=256, power=2.0
        )
        mel_db = librosa.power_to_db(mel, ref=np.max).astype(np.float32)
        
        # 4. Перетворення в тензор [1, 1, n_mels, time][cite: 1]
        mel_tensor = torch.tensor(mel_db).unsqueeze(0).unsqueeze(0)
        return mel_tensor.to(self.device)

    def predict(self, audio_path):
        """Повертає VAD координати або помилку, якщо голосу немає[cite: 1, 2]"""
        
        # Спершу перевіряємо наявність голосу
        if not self.is_speech_present(audio_path):
            return {
                "error": "no_speech",
                "interpretation": "Голосу не виявлено (тиша або шум)",
                "valence": 0.0, "arousal": 0.0, "dominance": 0.0
            }

        mel = self._load_and_preprocess(audio_path)
        
        with torch.no_grad():
            output = self.model(mel)
            # Отримуємо значення [valence, arousal, dominance][cite: 1, 2]
            v, a, d = output[0].cpu().numpy()
            
        return {
            "valence": float(v),
            "arousal": float(a),
            "dominance": float(d),
            "interpretation": self._interpret_vad(v, a, d)
        }

    def _interpret_vad(self, v, a, d):
        """Пошук найближчої емоції за Евклідовою відстанню"""
        emo2vad = {
            "Радість (Happiness)": [0.81, 0.51, 0.46],
            "Гордість (Pride)": [0.60, 0.45, 0.85],
            "Інтерес (Interest)": [0.50, 0.25, 0.20],
            "Здивування (Surprise)": [0.40, 0.67, -0.13],
            "Нейтральний стан (Neutral)": [0.00, 0.00, 0.00],
            "Нудьга (Boredom)": [-0.15, -0.35, -0.25],
            "Тривога (Anxiety)": [-0.35, 0.55, -0.45],
            "Зневага (Contempt)": [-0.20, 0.30, 0.70],
            "Провина (Guilt)": [-0.45, 0.30, -0.40],
            "Сором (Shame)": [-0.55, 0.10, -0.55],
            "Гнів (Anger)": [-0.51, 0.59, 0.25],
            "Огида (Disgust)": [-0.60, 0.35, 0.11],
            "Сум (Sadness)": [-0.63, -0.25, -0.33],
            "Страх (Fear)": [-0.64, 0.60, -0.43],
        }

        closest_emotion = "Нейтральний стан"
        min_distance = float('inf')

        for emotion, coords in emo2vad.items():
            distance = math.sqrt(
                (v - coords[0])**2 + (a - coords[1])**2 + (d - coords[2])**2
            )
            if distance < min_distance:
                min_distance = distance
                closest_emotion = emotion

        return closest_emotion

if __name__ == "__main__":
    CHECKPOINT = "checkpoints/emotion_crnn_best.pth"
    TEST_FILE = "test_audio.wav"
    
    import os
    if os.path.exists(CHECKPOINT) and os.path.exists(TEST_FILE):
        predictor = EmotionPredictor(CHECKPOINT)
        result = predictor.predict(TEST_FILE)
        
        if "error" in result:
            print(f"\nРезультат: {result['interpretation']}")
        else:
            print(f"\nАналіз файлу: {TEST_FILE}")
            print("-" * 30)
            print(f"Valence:   {result['valence']:.4f}")
            print(f"Arousal:   {result['arousal']:.4f}")
            print(f"Dominance: {result['dominance']:.4f}")
            print(f"Стан:      {result['interpretation']}")
    else:
        print("Перевірте наявність файлу моделі та тестового аудіо.")