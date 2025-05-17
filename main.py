#Sara Ines Arcos Peña
import tkinter as tk
from pyo import Sine, Server, LFO, Adsr, Biquad, Delay, Mixer


class PianoSynthesizer:
    def __init__(self, root):
        #Contruccion ventana principal
        self.root = root
        self.root.title("Saris Piano Sintetizador")
        self.root.geometry("1200x580")
        self.root.resizable(True, True)

        #Definiocion e inicio del servidor de sonido
        self.server = Server().boot()
        self.server.start()

        #Definicion de variables y datos
        self.basic_scale = {
            # White keys
            "q": 261.624,  # Do
            "w": 293.664,  # Re
            "e": 329.624,  # Mi
            "r": 349.232,  # Fa
            "t": 391.992,  # Sol
            "y": 440,  # La
            "u": 493.888,  # Si
            "i": 523.248,  # Do Octava
            "o": 587.328,  # Re Octava
            "p": 659.248,  # Mi Octava

            # Black keys
            "2": 277.184,  # Do#
            "3": 311.184,  # Re#
            "5": 369.992,  # Fa#
            "6": 415.304,  # Sol#
            "7": 466.16,  # La#
            "9": 554.368,  # Do# Octava
            "0": 622.368  # Re# Octava
        }
        self.oscillator = {}
        self.octave = 4
        self.synth_params = {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.7,
            'release': 0.3,
            'volume': 0.4,
            'filter_freq': 1000,
            'filter_res': 1,
            'lfo_rate': 0,
            'lfo_spd': 0,
            'lfo_depth': 0,
            'filter_type': 0,  # 0: lowpass, 1: highpass, 2: bandpass
            'echo_time': 0.2,
            'echo_feedback': 0,
            'echo_mix': 0
        }
        self.waveforms = [
            lambda freq, mul=1: Sine(freq, mul=mul),  # Onda Senoidal
            lambda freq, mul=1: Sine(freq, mul=mul),  # Onda Senoidal
            lambda freq, mul=1: LFO(freq=freq, type=1, mul=mul),  # Onda Cuadrada
            lambda freq, mul=1: LFO(freq=freq, type=3, mul=mul),  # Onda Triangular
            lambda freq, mul=1: LFO(freq=freq, type=2, mul=mul)  # Onda Diente de Sierra
        ]
        self.current_waveform = 1

        #Creacion main principal
        self.main_frame = tk.Frame(self.root, bg="#94BFAE")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        #Metodos constructores
        self.create_octave_control()
        self.create_piano()
        self.create_control_panel()

        #Eventos del teclado
        self.root.bind("<KeyPress>", self.press_key)
        self.root.bind("<KeyRelease>", self.free_key)

    def create_octave_control(self):
        #Creacion de los frames o marcos del control de octava principales
        ct_frame = tk.Frame(self.main_frame, bg="#0f302c", bd=2, relief=tk.SUNKEN)
        ct_frame.pack(fill=tk.X, pady=(0, 20))

        left_frame = tk.Frame(ct_frame, bg="#0f302c")
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, pady=10)

        right_frame = tk.Frame(ct_frame, bg="#0f302c")
        right_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, pady=10)

        octave_label = tk.Label(left_frame, text="OCT RANGE", bg="#0f302c",
                                font=("Britannic Bold", 10), fg="#acb8b6", width=10)
        octave_label.pack(side=tk.LEFT, pady=10)

        #Marcos, etiquetas y botones para cambiar la octava
        octave_frame = tk.Frame(left_frame, bg="#0f302c", bd=2, relief=tk.SUNKEN)
        octave_frame.pack(side=tk.LEFT, pady=10)
        btn_go_down = self.creat_button(octave_frame, "-", command_param=lambda: self.change_octave(-1)
                                        , width_param=2)
        btn_go_down.pack(side=tk.LEFT, padx=10)
        self.oct_label = tk.Label(octave_frame, text=" 4 ", bg="#052420", fg="#acb8b6",
                                  font=("Britannic Bold", 10), width=4)
        self.oct_label.pack(side=tk.LEFT, padx=10)
        btn_go_up = self.creat_button(octave_frame, "+", command_param=lambda: self.change_octave(+1)
                                      , width_param=2)
        btn_go_up.pack(side=tk.LEFT, padx=10)

        #Etiquetas, marcos y botones para cambiar de tipo de onda
        self.wave_label = tk.Label(right_frame, text="WAVE", bg="#0f302c", font=("Britannic Bold", 10),
                                   fg="#acb8b6", width=10)
        self.wave_label.pack(side=tk.LEFT, pady=10)
        waveform_frame = tk.Frame(right_frame, bg="#0f302c", bd=2, relief=tk.SUNKEN)
        waveform_frame.pack(side=tk.LEFT, pady=10)

        list_waves = ["SINE", "SQUARE", "TRIANGLE", "SAW"]
        self.waveforms_button = []

        for i, tw in enumerate(list_waves, start=1):
            mi_btn = self.creat_button(waveform_frame,
                                       tw,
                                       width_param=10,
                                       height_param=1,
                                       command_param=lambda idx=i: self.set_waveform(idx)
                                       )
            mi_btn.grid(row=0, column=i - 1, padx=10, pady=10)
            self.waveforms_button.append(mi_btn)
        self.waveforms_button[0].config(bg="#338375", fg="white")

    def create_piano(self):
        keyboard_frame = tk.Frame(self.main_frame, bg="#94BFAE", height=200)
        keyboard_frame.pack(fill=tk.X, pady=(0, 20))
        self.canvas = tk.Canvas(keyboard_frame, bg="#94BFAE", height=200, highlightthickness=0)
        self.canvas.pack(fill=tk.X)
        self.draw_piano_keys()

    def draw_piano_keys(self):
        start_x, start_y = 100, 10
        white_key_width, white_key_height = 50, 180
        black_key_width, black_key_height = 30, 110
        self.white_keys = {}
        self.black_keys = {}
        self.key_rect = {}

        # Teclas Blancas
        white_notes = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
        for i, note in enumerate(white_notes):
            x = start_x + (i * white_key_width)
            key = self.canvas.create_rectangle(x, start_y, x + white_key_width, start_y + white_key_height,
                                               fill="white", outline="black", width=1)
            self.canvas.create_text(x + (white_key_width / 2), 170, text=note.upper(), fill="gray",
                                    font=("Britannic Bold", 12))
            self.white_keys[note] = key
            self.key_rect[key] = note

            #Eventos del mouse
            self.canvas.tag_bind(key, "<ButtonPress-1>", self.mouse_press)
            self.canvas.tag_bind(key, "<ButtonRelease-1>", self.mouse_release)

        # Teclas Negras
        lista = [("2", 0), ("3", 1), ("5", 3), ("6", 4), ("7", 5), ("9", 7), ("0", 8)]
        for note, i in lista:
            xb = start_x + (i * white_key_width) + (white_key_width - (black_key_width / 2))
            key = self.canvas.create_rectangle(xb, start_y, xb + black_key_width, 120, fill="black",
                                               outline="black", width=1)
            self.canvas.create_text(xb + (black_key_width / 2), 100, text=note.upper(), fill="white",
                                    font=("Britannic Bold", 10))
            self.black_keys[note] = key
            self.key_rect[key] = note

            #Eventos del mouse
            self.canvas.tag_bind(key, "<ButtonPress-1>", self.mouse_press)
            self.canvas.tag_bind(key, "<ButtonRelease-1>", self.mouse_release)

    def create_control_panel(self):
        #Marco o frame principal de Envolventes, Filtros y Ecos
        controls_frame = tk.Frame(root, bg="#333333")
        controls_frame.pack(fill=tk.X,padx=20)

        #Marco para envoleventes y volumen (evolucion del sonido en el tiempo)
        envelope_frame = self.create_frame(controls_frame, name_label="ENVELOPES / VOLUME", bg_param="#166659")
        envelope_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        envelope_params = [
            ("ATTK", "attack", 0, 1),
            ("DCV", "decay", 0, 1),
            ("STN", "sustain", 0, 1),
            ("REL", "release", 0, 1),
            ("VOL", "volume", 0, 1)
        ]

        self.create_sliders(envelope_frame, envelope_params)

        #Marco para los Filtros (contenido armonico del sonido)
        filter_frame = self.create_frame(controls_frame, "#34756a", "FILTER")
        filter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        filter_params = [
            ("FREQ", "filter_freq", 50, 5000),
            ("RES", "filter_res", 0.1, 10),
            ("LFO", "lfo_rate", 0, 10),
            ("SPD", "lfo_spd", 0, 1),
            ("DPTH", "lfo_depth", 0, 1)
        ]
        self.create_sliders(filter_frame, filter_params)

        #Marco para Ecos (repeticiones del sonido)
        echo_frame = self.create_frame(controls_frame, "#43736b", "ECHO")
        echo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        echo_params = [
            ("TIME", "echo_time", 0, 1),
            ("FBCK", "echo_feedback", 0, 0.9),
            ("FREQ", "echo_freq", 50, 5000),
            ("MIX", "echo_mix", 0, 1)
        ]
        self.create_sliders(echo_frame, echo_params)

    def create_frame(self, parent, bg_param, name_label, width_param=20, height_param=None):
        #Crea los frames que contienen los titulos de los controles Ënvolventes, Filtros y Echos
        mi_frame = tk.Frame(
            parent,
            bg=bg_param,
            relief=tk.RAISED,
            bd=2,
            padx=10,
            pady=15
        )
        mi_label = tk.Label(
            mi_frame,
            text=name_label,
            bg="black",
            fg="white",
            width=width_param,
            height=height_param,
            pady=5,
            font=("Britannic Bold", 10)
        )
        mi_label.pack(fill=tk.X, pady=5)
        return mi_frame

    def create_sliders(self, parent, params):
        # Etiquetas
        mi_frame = tk.Frame(
            parent,
            bg=parent["bg"]
        )
        mi_frame.pack(fill=tk.X, pady=5)
        for i, (label, param, min_val, max_val) in enumerate(params):
            mi_label = tk.Label(
                mi_frame,
                text=label,
                bg=parent["bg"],
                fg="black",
                font=("Britannic Bold", 10)
            )
            mi_label.grid(row=0, column=i, padx=17)

        # Escalas o deslizadores verticales
        sliders_frame = tk.Frame(parent, bg=parent["bg"])
        sliders_frame.pack(fill=tk.X)
        for i, (label, param, min_val, max_val) in enumerate(params):
            slider_frame = tk.Frame(sliders_frame, bg="black", bd=1, relief=tk.SUNKEN, width=50, height=100)
            slider_frame.grid(row=0, column=i, padx=10, pady=5)

            knob = tk.Frame(slider_frame, width=30, height=30, bg="black", bd=1, relief=tk.RAISED)
            knob.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

            circle = tk.Canvas(knob, width=20, height=20, bg="black", highlightthickness=0)
            circle.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            circle.create_oval(2, 2, 18, 18, fill="black", outline="white")
            slider_frame.bind("<Button-1>", lambda event, p=param, min_v=min_val, max_v=max_val:
            self.start_dragging(event, p, min_v, max_v))

            # guarda el estado del boton o perilla
            setattr(self, f"{param}_knob", knob)

    def creat_button(self,
                     frame_param,
                     text_param,
                     bg_param="#052420",
                     fg_param="#acb8b6",
                     width_param=None,
                     height_param=None,
                     command_param=None,
                     ):
        #Crea los botones de los tipos de ondas
        btn = tk.Button(
            frame_param,
            text=text_param,
            bg=bg_param,
            fg=fg_param,
            width=width_param,
            height=height_param,
            font=("Britannic Bold", 10),
            command=command_param,
            bd=2,
            relief=tk.RAISED
        )
        return btn

    def change_octave(self, delta):
        self.octave = max(0, min(8, self.octave + delta))
        self.oct_label.config(text=str(self.octave))
        if self.oscillator:
            self.update_active_oscillators()

    def start_dragging(self, event, param, min_val, max_val):
        #Movimiento de los controles
        frame = event.widget
        knob = getattr(self, f"{param}_knob")

        def on_drag(e):
            # Calcula la posicion del deslizador
            frame_height = frame.winfo_height()
            y = max(0, min(frame_height, e.y))
            rel_y = 1 - (y / frame_height)
            knob.place(relx=0.5, rely=1 - rel_y, anchor=tk.CENTER)
            value = (max_val - min_val) * rel_y + min_val
            self.synth_params[param] = value
            self.update_active_oscillators()

        frame.bind("<B1-Motion>", on_drag)

        def stop_dragging(e):
            frame.unbind("<B1-Motion>")
            frame.unbind("<ButtonRelease-1>")

        frame.bind("<ButtonRelease-1>", stop_dragging)

    def set_waveform(self, waveform_index):
        self.waveforms_button[self.current_waveform - 1].config(bg="#052420", fg="#acb8b6")

        self.current_waveform = waveform_index
        self.waveforms_button[waveform_index - 1].config(bg="#338375", fg="white")
        self.update_active_oscillators()

    def update_active_oscillators(self):
        for note in list(self.oscillator.keys()):
            self.stop_note(note)
            self.play_note(note)

    def press_key(self, event):
        note = event.char.lower()
        if note in self.basic_scale and note not in self.oscillator:
            self.play_note(note)

    def free_key(self, event):
        note = event.char.lower()
        if note in self.oscillator:
            self.stop_note(note)

    def mouse_press(self, event):
        key_id = self.canvas.find_closest(event.x, event.y)[0]
        note = self.key_rect.get(key_id, None)
        if note in self.basic_scale and note not in self.oscillator:
            self.play_note(note)

    def mouse_release(self, event):
        key_id = self.canvas.find_closest(event.x, event.y)[0]
        note = self.key_rect.get(key_id, None)
        if note in self.oscillator:
            self.stop_note(note)

    def play_note(self, note):
        if note in self.white_keys:
            self.canvas.itemconfig(self.white_keys[note], fill="#828e8c")
        elif note in self.black_keys:
            self.canvas.itemconfig(self.black_keys[note], fill="#828e8c")

        base_freq = self.basic_scale[note]
        octave_diff = self.octave - 4
        adjusted_freq = base_freq + (2 ** octave_diff)

        #Gestiona los cambio en el control de envolventes y volumen
        waveform_class = self.waveforms[self.current_waveform]
        env = Adsr(
            attack=self.synth_params["attack"],
            decay=self.synth_params["decay"],
            sustain=self.synth_params["sustain"],
            release=self.synth_params["release"],
            mul=self.synth_params["volume"]
        ).play()
        sound = waveform_class(freq=adjusted_freq, mul=env)
        #Verifica y aolica cambios en el control de Filtros
        if self.synth_params["filter_freq"] > 10:
            filt = Biquad(
                input=sound,
                freq=self.synth_params["filter_freq"],
                q=self.synth_params["filter_res"],
                type=self.synth_params["filter_type"]
            )
            if self.synth_params["lfo_rate"] > 0:
                lfo_actual_freq = self.synth_params["lfo_spd"] * 10
                lfo = Sine(
                    freq=lfo_actual_freq,
                    mul=self.synth_params["lfo_depth"] * 1000
                )
                filt.freq = self.synth_params["filter_freq"] + lfo
            signal = filt
        else:
            signal = sound

        #verifica cambios en el control de Echos y los palica
        if self.synth_params["echo_feedback"] > 0:
            echo = Delay(
                input=signal,
                delay=self.synth_params["echo_time"],
                feedback=self.synth_params["echo_feedback"],
            )
            mixer = Mixer(outs=2, chnls=2)
            mixer.addInput(0, signal)
            mixer.addInput(1, echo)
            mixer.setAmp(0, 0, 1 - self.synth_params["echo_mix"])
            mixer.setAmp(0, 1, self.synth_params["echo_mix"])
            final_signal = mixer
        else:
            final_signal = signal

        final_signal.out()
        self.oscillator[note] = (sound, env, final_signal)

    def stop_note(self, note):
        if note in self.oscillator:
            sound, env, final_signal = self.oscillator[note]
            env.stop()
            del self.oscillator[note]

            if note in self.white_keys:
                self.canvas.itemconfig(self.white_keys[note], fill="white")
            elif note in self.black_keys:
                self.canvas.itemconfig(self.black_keys[note], fill="black")

    def on_close(self):
        self.server.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    synthe = PianoSynthesizer(root)
    root.protocol("WM_DELETE_WINDOW", synthe.on_close)
    root.mainloop()
