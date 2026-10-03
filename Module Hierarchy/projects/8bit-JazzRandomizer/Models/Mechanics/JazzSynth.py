import numpy as np
import pyaudio
import threading
import math

# Подключаем новую атомарную МИ-Модель для валидации параметров при сеттерах
from Models.Mechanics.RangeMapper import RangeMapper

class JazzSynth:
    """
    АТОМАРНАЯ МЕХАНИКА СИНТЕЗА ЗВУКА.
    
    Нижняя точка Ромба МИ - физика звука, фазовые накопители, 
    защита от щелчков. 
    Механика меняется лишь по крайней необходимости.
    
    ПРИНЦИП ДИНАМИЧЕСКОЙ НЕЯВНОЙ СИГНАТУРЫ:
    - play_chord() имеет МИНИМАЛЬНУЮ сигнатуру (только обязательные параметры)
    - ВСЕ остальные параметры передаются ИСКЛЮЧИТЕЛЬНО через сеттеры
    - Каждый сеттер = ровно 1 параметр!
    - Сеттеры используют экземпляр RangeMapper для гарантии корректности (приведение к базовой шкале)
    """
    
    def __init__(self, sample_rate=44100):
        """
        Инициализация синтезатора с дефолтными значениями всех параметров.
        """
        self.sample_rate = sample_rate
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sample_rate,
            output=True
        )
        self.voices = []
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._audio_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Создаем экземпляр МИ-Модели для валидации параметров
        self.mapper = RangeMapper()
        
        # ==========================================
        # ДЕФОЛТНЫЕ ЗНАЧЕНИЯ ВСЕХ ПАРАМЕТРОВ
        # ==========================================
        self._volume_pattern = 1.0
        self._pitch_pattern = 0.0
        self._harmonics = None
        self._waveform = 'sine'
        self._overtone_strength = 0.0
        self._fm_depth = 0.0
        self._fm_rate = 0.0
        self._distortion = 0.0
        self._noise_amount = 0.0
    
    # ==========================================
    # СЕТТЕРЫ (с защитой через RangeMapper)
    # ==========================================
    
    def set_volume_pattern(self, value):
        """Устанавливает паттерн громкости."""
        if isinstance(value, (int, float)):
            self.mapper.set_clamp_bounds(0.0, 1.0)
            self._volume_pattern = self.mapper.clamp(value)
        else:
            self._volume_pattern = value
    
    def set_pitch_pattern(self, value):
        """Устанавливает паттерн высоты тона (сдвиг в полутонах)."""
        if isinstance(value, (int, float)):
            self.mapper.set_clamp_bounds(-24.0, 24.0)
            self._pitch_pattern = self.mapper.clamp(value)
        else:
            self._pitch_pattern = value
    
    def set_harmonics(self, value):
        """Устанавливает спектр гармоник."""
        self._harmonics = value
    
    def set_waveform(self, value):
        """Устанавливает тип волны."""
        if value in ['sine', 'saw', 'square']:
            self._waveform = value
        else:
            self._waveform = 'sine'
    
    def set_overtone_strength(self, value):
        """Устанавливает силу обертонов."""
        self.mapper.set_clamp_bounds(0.0, 1.0)
        self._overtone_strength = self.mapper.clamp(value)
    
    def set_fm_depth(self, value):
        """Устанавливает глубину FM-модуляции."""
        self.mapper.set_clamp_bounds(0.0, 10.0)
        self._fm_depth = self.mapper.clamp(value)
    
    def set_fm_rate(self, value):
        """Устанавливает частоту FM-модуляции."""
        self.mapper.set_clamp_bounds(0.0, 100.0)
        self._fm_rate = self.mapper.clamp(value)
    
    def set_distortion(self, value):
        """Устанавливает уровень перегруза."""
        self.mapper.set_clamp_bounds(0.0, 2.0)
        self._distortion = self.mapper.clamp(value)
    
    def set_noise_amount(self, value):
        """Устанавливает уровень белого шума."""
        self.mapper.set_clamp_bounds(0.0, 1.0)
        self._noise_amount = self.mapper.clamp(value)
    
    # ==========================================
    # ФУНКЦИЯ ЗАПУСКА (строго минимальная сигнатура)
    # ==========================================
    
    def play_chord(self, frequencies, duration_sec):
        """
        Мгновенно добавляет аккорд в поток.
        
        СИГНАТУРА:
        Вход: 
            - frequencies (list[float]) - список частот в Гц
            - duration_sec (float) - длительность в секундах
        Выход: None
        
        ВСЕ параметры тембра и управления уже установлены через сеттеры!
        """
        final_params = {
            'volume_pattern': self._volume_pattern,
            'pitch_pattern': self._pitch_pattern,
            'harmonics': self._harmonics,
            'waveform': self._waveform,
            'overtone_strength': self._overtone_strength,
            'fm_depth': self._fm_depth,
            'fm_rate': self._fm_rate,
            'distortion': self._distortion,
            'noise_amount': self._noise_amount
        }
        
        with self.lock:
            self.voices.append({
                'frequencies': list(frequencies),
                'duration': duration_sec,
                'params': final_params,
                'current_time': 0.0,
                'phase_state': np.zeros(len(frequencies), dtype=np.float64)
            })
    
    # ==========================================
    # ВНУТРЕННЯЯ МЕХАНИКА (меняется лишь по крайней необходимости)
    # ==========================================
    
    def _evaluate_pattern(self, raw_value, t_array, duration):
        """Универсальный метод оценки паттерна."""
        if hasattr(raw_value, 'evaluate'):
            return np.array(
                [raw_value.evaluate(float(rt)) for rt in t_array],
                dtype=np.float32
            )
        else:
            return np.full(len(t_array), float(raw_value), dtype=np.float32)
    
    def _audio_loop(self):
        """Основной аудио-цикл (работает в отдельном потоке)."""
        block_size = 2205
        while self.running:
            t = np.arange(block_size) / self.sample_rate
            mix = np.zeros(block_size, dtype=np.float32)
            
            with self.lock:
                for voice in self.voices[:]:
                    p = voice['params']
                    global_t = voice['current_time'] + t
                    duration = voice['duration']
                    rel_t = np.clip(global_t / duration, 0.0, 1.0)
                    
                    vol_raw = p['volume_pattern']
                    env = self._evaluate_pattern(vol_raw, rel_t, duration)
                    
                    pitch_raw = p['pitch_pattern']
                    slide_semitones = self._evaluate_pattern(pitch_raw, rel_t, duration)
                    freq_multiplier = 2.0 ** (slide_semitones / 12.0)
                    
                    overtone_strength = p['overtone_strength']
                    waveform = p['waveform']
                    
                    wave = np.zeros_like(global_t, dtype=np.float32)
                    dt = 1.0 / self.sample_rate
                    
                    for i, freq in enumerate(voice['frequencies']):
                        inst_freq = freq * freq_multiplier
                        phase_inc = 2.0 * np.pi * inst_freq * dt
                        
                        current_phase = voice['phase_state'][i] + np.cumsum(phase_inc)
                        voice['phase_state'][i] = current_phase[-1]
                        
                        harmonics = p['harmonics']
                        if harmonics is not None and len(harmonics) > 1:
                            w = np.zeros_like(current_phase, dtype=np.float32)
                            for h_idx, amp in enumerate(harmonics):
                                if amp > 0.001:
                                    w += amp * np.sin(current_phase * (h_idx + 1))
                        else:
                            if waveform == 'saw':
                                w = 2.0 * ((current_phase / (2.0 * np.pi)) % 1.0) - 1.0
                            elif waveform == 'square':
                                w = np.sign(np.sin(current_phase)).astype(np.float32)
                            else:
                                w = np.sin(current_phase)
                        
                        wave += w
                    
                    num_notes = len(voice['frequencies'])
                    wave = (wave / max(num_notes, 1)) * env
                    
                    if len(env) > 5:
                        kernel = np.ones(5, dtype=np.float32) / 5.0
                        env_smooth = np.convolve(env, kernel, mode='same').astype(np.float32)
                        wave = (wave / max(num_notes, 1)) * env_smooth
                    
                    fade_samples = int(self.sample_rate * 0.01)
                    if len(wave) > fade_samples * 2:
                        wave[:fade_samples] *= np.linspace(0.0, 1.0, fade_samples, dtype=np.float32)
                        wave[-fade_samples:] *= np.linspace(1.0, 0.0, fade_samples, dtype=np.float32)
                    elif len(wave) > 0:
                        half = len(wave) // 2
                        wave[:half] *= np.linspace(0.0, 1.0, half, dtype=np.float32)
                        wave[half:] *= np.linspace(1.0, 0.0, len(wave) - half, dtype=np.float32)
                    
                    mix = mix + wave
                    voice['current_time'] += block_size / self.sample_rate
                    
                    if voice['current_time'] >= duration:
                        self.voices.remove(voice)
            
            max_amp = max(1.0, float(np.max(np.abs(mix))))
            mix = np.clip(mix / max_amp, -1.0, 1.0)
            self.stream.write(mix.astype(np.float32).tobytes())
    
    def stop(self):
        """Останавливает синтезатор и освобождает ресурсы."""
        self.running = False
        self.thread.join(timeout=2.0)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
