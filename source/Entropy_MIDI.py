# Author --> Oscar Natera Barrios
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.ttk import Treeview
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pretty_midi as pm
import os
import pygame
from collections import Counter
import collections
from scipy.stats import entropy
import numpy as np
from PIL import ImageTk,Image
import random

class Main(Tk):
    def __init__(self):
        super().__init__()
        
        # setting up the window
        self.iconbitmap("piano_icon.ico")
        self.geometry("350x590+160+30")
        self.resizable(False, False)
        self.title('MIDI Entropy')
        
        # add functions

        def import_file():
            global file, but_delete

            file = fd.askopenfilename(title='Select midi file',
                                        filetypes=[('Midi','*.mid'),
                                                   ('All Files', '*')])
            filename = os.path.basename(file)
            self.textarea.insert(END, filename)

            ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
            self.but_delete = ttk.Button(main, text="Eliminar", command=delete_file)
            self.but_delete.place(x=130, y=40)

            #add button to analyze track midi
            ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
            self.MIDI_button = ttk.Button(text="Análisis MIDI", command = lambda: [readmidi(), treeview()]).place(x=210,y=40)


        def delete_file():
            self.textarea.delete(1.0, END)  #deletes the button when imports another midi file
        
        def readmidi():
            global midi_stream, bpm_label, pitch, velocity, time, timeround, list_midi_list, file, MUSICNOTATION 
            global musicnote, pitch_alt
    
            midi_stream = pm.PrettyMIDI(os.path.basename(file))

            #add label bpm and get bpm value
            bpm = midi_stream.get_tempo_changes()  #return bpm value
            bpm_label = Label(main, text=f"Tempo --> {int(bpm[1])}bpm").place(x=50, y=500)
            
            # add label keysignature 
            #key = midi_stream.get

            #create lists where stored pitch, velocity and time of each midi note
            pitch = []
            velocity = []
            start_note = []
            end_note = []
            time = []
            pitch_alt = pitch

            #iterate over the elements to fill above lists
            for i in midi_stream.instruments[0].notes:
                pitch.append(i.pitch)
                velocity.append(i.velocity)
                start_note.append(i.start)
                end_note.append(i.end)

            # get the end_note - start note so that i can get the time of the note
            for x, y in zip(start_note, end_note):
                rest = y - x
                time.append(rest)
                
            #get time list round to 2 decimals
            timeround = []
            for k in range(len(time)):
                timeround.append(round(time[k],2))
                
                
            # convert midi value to music notation by octaves   
                
            NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            OCTAVES = list(range(11))
            NOTES_IN_OCTAVE = len(NOTES)

            def number_to_note(number: int) -> list:
                octave = number // NOTES_IN_OCTAVE
                #assert octave in OCTAVES, errors['notes']
                #assert 0 <= number <= 88, errors['notes']
                note = NOTES[number % NOTES_IN_OCTAVE]     

                return note, octave    
                
            musicnote = []
            MUSICNOTATION = []
            for i in range(len(pitch)):
                musicnote.append(number_to_note(pitch[i]))
                MUSICNOTATION.append(f"{musicnote[i][0]}{musicnote[i][1]}")  # get --> ex: 'C4' not ('C', 4)
                 

            # create just a zip for the treeview 
            list_midi = zip(MUSICNOTATION, velocity, timeround) 
            list_midi_list = list(list_midi)
            
            #create play button
            ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
            self.playbut = ttk.Button(text="Play", command=play).place(x=50,y=100)

            #create stop button
            ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
            self.stopbut = ttk.Button(text="Stop", command=stop).place(x=210,y=100)
            
            #create pause button
            ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
            self.pausebut = ttk.Button(text="Pause", command=lambda: pause(paused)).place(x=130,y=100)
            
            #create show more button
            ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
            self.showmorebut = ttk.Button(text="ver más -->", command=showmore).place(x=260,y=330)
  
            
        def treeview():
            global table
            table = Treeview(main, selectmode='browse', height=17)
            table.place(x=50, y=130)
            table['columns'] = ('MUSICNOTATION', 'velocity', 'timeround')

            table.column("#0", width=0, stretch=NO)
            table.column("MUSICNOTATION", width=65, anchor=CENTER, stretch=NO)
            table.column("velocity", width=65, anchor=CENTER,stretch=NO)
            table.column("timeround", width=70, anchor=CENTER,stretch=NO)

            table.heading("MUSICNOTATION", text="Note Pitch", anchor=CENTER)
            table.heading("velocity", text="Velocity", anchor=CENTER)
            table.heading("timeround", text="Time (s)", anchor=CENTER)
            
            # loop so that it fills in the treeview
            count = 0
            for info in list_midi_list:
                table.insert(parent='', index='end', iid=count, text="", values=(info)) 
                count += 1   
            
            
            # Constructing vertical scrollbar
            # with treeview
            verscrlbar = Scrollbar(self, orient ="vertical", command = table.yview)
 
            # Calling pack method w.r.to vertical
            # scrollbar
            #verscrlbar.pack(side ='left', fill ='y')
            verscrlbar.place(x=10+20+2, y=100, height=200+220)
 
            # Configuring treeview
            table.configure(yscrollcommand = verscrlbar.set)
           
            
        pygame.mixer.init(44100,-16,2,2048)    # <-- initialized mixer fs:44.1Khz; 16bits, stereo, 2048 samples
        def play():
            pygame.mixer.music.load(os.path.basename(file))
            pygame.mixer.music.play()
        
        def stop():
            pygame.mixer.music.stop()
            
        global paused
        paused = False     
        def pause(is_paused):
            global paused
            paused = is_paused
            
            if paused:
                #unpaused
                pygame.mixer.music.unpause()
                paused = False
            else:
                #pause
                pygame.mixer.music.pause()
                paused = True
                
                   
# ------------------------------- show more analysis---------------------------------------------------------------
                           
        def showmore():
            
            self.geometry("1300x590+160+30")
            
            for n in range(len(pitch)):
                if pitch[n] == 21 or pitch[n] == 33 or pitch[n] == 45 or pitch[n] == 57 or pitch[n] == 69 or pitch[n] == 81 or pitch[n] == 93 or pitch[n] == 105:
                    pitch[n] = 'A'
                elif pitch[n] == 22 or pitch[n] == 34 or pitch[n] == 46 or pitch[n] == 58 or pitch[n] == 70 or pitch[n] == 82 or pitch[n] == 94 or pitch[n] == 106:
                    pitch[n] = 'A#'
                elif pitch[n] == 23 or pitch[n] == 35 or pitch[n] == 47 or pitch[n] == 59 or pitch[n] == 71 or pitch[n] == 83 or pitch[n] == 95 or pitch[n] == 107:
                    pitch[n] = 'B'
                elif pitch[n] == 24 or pitch[n] == 36 or pitch[n] == 48 or pitch[n] == 60 or pitch[n] == 72 or pitch[n] == 84 or pitch[n] == 96 or pitch[n] == 108:
                    pitch[n] = 'C'
                elif pitch[n] == 25 or pitch[n] == 37 or pitch[n] == 49 or pitch[n] == 61 or pitch[n] == 73 or pitch[n] == 85 or pitch[n] == 97:
                    pitch[n] = 'C#'
                elif pitch[n] == 26 or pitch[n] == 38 or pitch[n] == 50 or pitch[n] == 62 or pitch[n] == 74 or pitch[n] == 86 or pitch[n] == 98:
                    pitch[n] = 'D'
                elif pitch[n] == 27 or pitch[n] == 39 or pitch[n] == 51 or pitch[n] == 63 or pitch[n] == 75 or pitch[n] == 87 or pitch[n] == 99:
                    pitch[n] = 'D#'
                elif pitch[n] == 28 or pitch[n] == 40 or pitch[n] == 52 or pitch[n] == 64 or pitch[n] == 76 or pitch[n] == 88 or pitch[n] == 100:
                    pitch[n] = 'E'
                elif pitch[n] == 29 or pitch[n] == 41 or pitch[n] == 53 or pitch[n] == 65 or pitch[n] == 77 or pitch[n] == 89 or pitch[n] == 101:
                    pitch[n] = 'F'
                elif pitch[n] == 30 or pitch[n] == 42 or pitch[n] == 54 or pitch[n] == 66 or pitch[n] == 78 or pitch[n] == 90 or pitch[n] == 102:
                    pitch[n] = 'F#'
                elif pitch[n] == 31 or pitch[n] == 43 or pitch[n] == 55 or pitch[n] == 67 or pitch[n] == 79 or pitch[n] == 91 or pitch[n] == 103:
                    pitch[n] = 'G'
                elif pitch[n] == 32 or pitch[n] == 44 or pitch[n] == 56 or pitch[n] == 68 or pitch[n] == 80 or pitch[n] == 92 or pitch[n] == 104:
                    pitch[n] = 'G#'
            
            
            #plot velocity every note
            velC = []
            velCsos = []
            velD = []
            velDsos = []
            velE = []
            velF = []
            velFsos = []
            velG = []
            velGsos = []
            velA = []
            velAsos = []
            velB = []
            for r in range(len(pitch)):
                if pitch_alt[r] == 'C':
                    velC.append(velocity[r])
                elif pitch_alt[r] == 'C#':
                    velCsos.append(velocity[r])
                elif pitch_alt[r] == 'D':
                    velD.append(velocity[r])
                elif pitch_alt[r] == 'D#':
                    velDsos.append(velocity[r])
                elif pitch_alt[r] == 'E':
                    velE.append(velocity[r])
                elif pitch_alt[r] == 'F':
                    velF.append(velocity[r])
                elif pitch_alt[r] == 'F#':
                    velFsos.append(velocity[r])
                elif pitch_alt[r] == 'G':
                    velG.append(velocity[r])
                elif pitch_alt[r] == 'G#':
                    velGsos.append(velocity[r])
                elif pitch_alt[r] == 'A':
                    velA.append(velocity[r])
                elif pitch_alt[r] == 'A#':
                    velAsos.append(velocity[r])
                elif pitch_alt[r] == 'B':
                    velB.append(velocity[r])
        
            velocitydata = [velC,velCsos,velD,velDsos,velE,velF,velFsos,velG,velGsos,velA,velAsos,velB]
            #plt.boxplot(velocitydata)
            fig = plt.figure(figsize =(8, 5), facecolor="#f0f0f0", dpi=50)
            ax = fig.add_subplot(111)
            ax.set_facecolor('#f0f0f0')
            # Creating axes instance
            bp = ax.boxplot(velocitydata, patch_artist = True)
            colors = ['#ff9aa2', '#ffb7b2', '#ffdac1', '#f2f0cb','lightyellow','#c1ffc7', '#6dd87f', '#c7ceea',
                      '#afcffb', '#2645ab','#163587','#0f3758']
            for bplot in (bp):
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
            ax.set_xticklabels(['C', 'C#','D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])
            ax.set_title('Velocity de cada nota MIDI')
            ax.set_xlabel('Nota (notación musical)')
            ax.set_ylabel('Velocity (0-127)')
            ax.yaxis.grid(True)
            # creating the Tkinter canvas
            # containing the Matplotlib figure
            canvas = FigureCanvasTkAgg(fig,self)  
            # placing the canvas on the Tkinter window
            canvas.get_tk_widget().place(x=355, y=25)
                
                
            # ----------------- plot repetitions notepitch -------------------------------------------------------------
            
            count_notes = Counter(pitch)
            ordered_notes = Counter.most_common(count_notes)

            notes = []
            repetitions = []
            for i in ordered_notes:
                notes.append(i[0])
                repetitions.append(i[1])

            #print("the two most common notes are",count_notes.most_common(4))
            
            fig = plt.figure(figsize =(8, 5), facecolor="#f0f0f0", dpi=50)
            ax = fig.add_subplot(111)
            ax.set_facecolor('#f0f0f0')
            # Creating axes instance
            noteplot = ax.plot(notes, repetitions)
            ax.set_title('#de Repeticiones de cada nota MIDI')
            ax.set_xlabel('Nota (notación musical)')
            ax.set_ylabel('# de repeticiones')
            ax.yaxis.grid(True)
            # creating the Tkinter canvas
            # containing the Matplotlib figure
            canvas = FigureCanvasTkAgg(fig,self)  
            # placing the canvas on the Tkinter window
            canvas.get_tk_widget().place(x=730, y=25)
            
        
            
            # ----------------------------- plot repetitions timenote -------------------------------------------------------
            
            count_notes2 = Counter(timeround)
            ordered_notes2 = Counter.most_common(count_notes2)

            timenotes = []
            repetitionstime = []
            for i in ordered_notes2:
                timenotes.append(str(i[0]))
                repetitionstime.append(i[1])

            #print("the two most common notes are",count_notes2.most_common(4))

            #print("the two most common notes are",count_notes.most_common(4))
            
            fig = plt.figure(figsize =(8, 5), facecolor="#f0f0f0", dpi=50)
            ax = fig.add_subplot(111)
            ax.set_facecolor('#f0f0f0')
            # Creating axes instance
            noteplot = ax.plot(timenotes, repetitionstime, color="orange")
            ax.set_title('# de Reticiones del tiempo de cada figura')
            ax.set_xlabel('Tiempo de la figura (s)')
            ax.set_ylabel('# de repeticiones')
            ax.yaxis.grid(True)
            # creating the Tkinter canvas
            # containing the Matplotlib figure
            canvas = FigureCanvasTkAgg(fig,self)  
            # placing the canvas on the Tkinter window
            canvas.get_tk_widget().place(x=735, y=270)
            
            
            notes_text = Label(self, text=f"1) {ordered_notes[0][0]} --> {ordered_notes[0][1]} repeticiones \n"
                               f"2) {ordered_notes[1][0]} --> {ordered_notes[1][1]} repeticiones").place(x=1120,y=420)
            
            time_text = Label(self, text=f"1) {ordered_notes2[0][0]} --> {ordered_notes2[0][1]} repeticiones \n"
                               f"2) {ordered_notes2[1][0]} --> {ordered_notes2[1][1]} repeticiones").place(x=1120,y=460)
     
            
#--------------------------------plot entropy ---------------------------------------------------------------
            
            midi_stream2 = pm.PrettyMIDI(os.path.basename(file))
            tone = []
            for x in midi_stream.instruments[0].notes:
                tone.append(x.pitch)
                
            tonebases = collections.Counter([tmp_base for tmp_base in tone])
            divisor = len(tone)/len(tonebases.keys())
            divisor_int = round(divisor)
        
            tonedict = {key:divisor_int for key, value in tonebases.items()}
            res = []
            for key, val in tonedict.items():
                # getting values using * operator
                res += [key] * val
            
            ent =[]
            ent2 = []
            for s in range(len(pitch)):
                ent.append(entropy(tone[0:s+1], base=2))
                ent2.append(entropy(res[0:s+1], base=2))

            random.shuffle(res)
            
            def estimate_shannon_entropy(sequence):
                global dist1, bases1
                bases1 = collections.Counter([tmp_base for tmp_base in sequence])
                # define distribution
                dist1 = [x/sum(bases1.values()) for x in bases1.values()]

                # use scipy to calculate entropy
                entropy_value = entropy(dist1, base=2)

                return entropy_value
            
            
            entvalue = []
            entvalue2 = []

            for s in range(len(res)):
                entvalue.append(estimate_shannon_entropy(tone[:s+1]))
                entvalue2.append(estimate_shannon_entropy(res[:s+1]))
            
            
            fig = plt.figure(figsize =(8, 5), facecolor="#f0f0f0", dpi=50)
            ax = fig.add_subplot(111)
            ax.set_facecolor('#f0f0f0')
            # Creating axes instance
            entropyplot = ax.plot(entvalue, color="blue", label="melodía original Sf")
            entropyplot2 = ax.plot(entvalue2, color="orange", label="melodía aleatoria S max")
            ax.set_title('Nivel de Entropia de la linea melódica Midi')
            ax.set_xlabel('Paso del tiempo')
            ax.set_ylabel('Nivel de Entropia')
            ax.legend()
            ax.yaxis.grid(True)
            # creating the Tkinter canvas
            # containing the Matplotlib figure
            canvas = FigureCanvasTkAgg(fig,self)  
            # placing the canvas on the Tkinter window
            canvas.get_tk_widget().place(x=355, y=270)
            
            
            entropyround = []
            for S in range(len(entvalue)):
                entropyround.append(round(entvalue[S], 2))
                
            entropyroundmax = []
            for S in range(len(entvalue)):
                entropyroundmax.append(round(entvalue2[S], 2))
            
            entropymax = Label(self, text=f" >>>> La entropia final es: {max(entropyround)} <<<<").place(x=380,y=520)
            entropymaxrandom = Label(self, 
                                     text=f" >>>> La entropia máxima (melodía aleatoria): {max(entropyroundmax)} <<<<")
            entropymaxrandom.place(x=380,y=540)
            
            
            
            
            # first, let is get the total time of the song

            total_time = sum(time)
            total_time
            
            ctime = []
            for t in range(len(pitch)):
                if pitch[t] == 'C':
                    ctime.append(time[t])
            sum_ctime = round(sum(ctime),2)
            

            csostime = []
            for t in range(len(pitch)):
                if pitch[t] == 'C#':
                    csostime.append(time[t])
            sum_csostime = round(sum(csostime),2)
            

            dtime = []
            for t in range(len(pitch)):
                if pitch[t] == 'D':
                    dtime.append(time[t])
            sum_dtime = round(sum(dtime),2)
            


            dsostime = []
            for t in range(len(pitch)):
                if pitch[t] == 'D#':
                    dsostime.append(time[t])
            sum_dsostime = round(sum(dsostime),2)
            

            etime = []
            for t in range(len(pitch)):
                if pitch[t] == 'E':
                    etime.append(time[t])
            sum_etime = round(sum(etime),2)
            

            ftime = []
            for t in range(len(pitch)):
                if pitch[t] == 'F':
                    ftime.append(time[t])
            sum_ftime = round(sum(ftime),2)
            

            fsostime = []
            for t in range(len(pitch)):
                if pitch[t] == 'F#':
                    fsostime.append(time[t])
            sum_fsostime = round(sum(fsostime),2)
           

            gtime = []
            for t in range(len(pitch)):
                if pitch[t] == 'G':
                    gtime.append(time[t])
            sum_gtime = round(sum(gtime),2)

            gsostime = []
            for t in range(len(pitch)):
                if pitch[t] == 'G#':
                    gsostime.append(time[t])
            sum_gsostime = round(sum(gsostime), 2)
            
            atime = []
            for t in range(len(pitch)):
                if pitch[t] == 'A':
                    atime.append(time[t])
            sum_atime = round(sum(atime),4)
            


            asostime = []
            for t in range(len(pitch)):
                if pitch[t] == 'A#':
                    asostime.append(time[t])
            sum_asostime = round(sum(asostime),2)
           


            btime = []
            for t in range(len(pitch)):
                if pitch[t] == 'B':
                    btime.append(time[t])
            sum_btime = round(sum(btime), 2)
            
            
            
            times_notes = [sum_ctime, sum_csostime, sum_dtime, sum_dsostime, sum_etime, sum_ftime, sum_fsostime, 
                           sum_gtime, sum_gsostime, sum_atime, sum_asostime, sum_btime]
          
            
            #add labels for time every note has and th total time
            datos = Treeview(main, selectmode='browse', height=14)
            
            datos.place(x=1120, y=60)
            datos['columns'] = ('Nota', 'times_notes')
            
            datos.column("#0", width=0, stretch=NO)
            datos.column("Nota", width=40, anchor=CENTER, stretch=NO)
            datos.column("times_notes", width=100, anchor=CENTER, stretch=NO)
            
            datos.heading("Nota", text="Nota", anchor=CENTER)
            datos.heading("times_notes", text="Tiempo total (s)", anchor=CENTER)
                
            datos.insert(parent='', index='end', text="", values=('C', times_notes[0]))
            datos.insert(parent='', index='end', text="", values=('C#', times_notes[1]))
            datos.insert(parent='', index='end', text="", values=('D', times_notes[2]))
            datos.insert(parent='', index='end', text="", values=('D#',times_notes[3]))
            datos.insert(parent='', index='end', text="", values=('E', times_notes[4]))
            datos.insert(parent='', index='end', text="", values=('F', times_notes[5]))
            datos.insert(parent='', index='end', text="", values=('F#', times_notes[6]))
            datos.insert(parent='', index='end', text="", values=('G',times_notes[7]))
            datos.insert(parent='', index='end', text="", values=('G#', times_notes[8]))
            datos.insert(parent='', index='end', text="", values=('A', times_notes[9]))
            datos.insert(parent='', index='end', text="", values=('A#', times_notes[10]))
            datos.insert(parent='', index='end', text="", values=('B', times_notes[11]))
            datos.insert(parent='', index='end', text="", values=(' ', f"tiempo total: {total_time}"))
            
            
                        
#----------------------------------------- STATS ----------------------------------------------------------------

            def stats():
                global stats, desv_standard
            
                self.geometry("1300x710+160+30")
                
                pitch_num = []
                for i in midi_stream.instruments[0].notes:
                    pitch_num.append(i.pitch)
                    
               
                # standard deviation
                desv_standard = np.std(pitch_num)
                desv_standard_round = round(desv_standard,0)
                
                #media 
                media = int(np.mean(pitch_num))
                
                #median
                median = int(np.median(pitch_num))
                
                # max value 
                max_ = int(np.max(pitch_num))
                    
                # min value 
                min_ = int(np.min(pitch_num))    
                    
                NOTES2 = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                OCTAVES2 = list(range(11))
                NOTES_IN_OCTAVE2 = len(NOTES2)

                def number_to_note2(number2: int) -> list:
                    octave2 = number2 // NOTES_IN_OCTAVE2
                    assert octave2 in OCTAVES2, errors['notes']
                    assert 21 <= number2 <= 109, errors['notes']
                    note2 = NOTES2[number2 % NOTES_IN_OCTAVE2]

                    return note2, octave2
                
                pitch_music = list(number_to_note2(media))
                pitch_media = f"{pitch_music[0]}{pitch_music[1]}"
                
                pitch_music2 = list(number_to_note2(median))
                pitch_median = f"{pitch_music2[0]}{pitch_music2[1]}"
                
                pitch_music3 = list(number_to_note2(max_))
                pitch_max = f"{pitch_music3[0]}{pitch_music3[1]}"
                
                pitch_music4 = list(number_to_note2(min_))
                pitch_min = f"{pitch_music4[0]}{pitch_music4[1]}"
                
                stats = Treeview(main, selectmode='browse', height=2)
                stats.place(x=30, y=610)
                stats['columns'] = ('desv_standard', 'pitch_media', 'pitch_median','pitch_max', 'pitch_min')
                
                stats.column("#0", width=0, stretch=NO)
                stats.column("desv_standard", width=200, anchor=CENTER, stretch=NO)
                stats.column("pitch_media", width=100, anchor=CENTER,stretch=NO)
                stats.column("pitch_median", width=100, anchor=CENTER,stretch=NO)
                stats.column("pitch_max", width=100, anchor=CENTER,stretch=NO)
                stats.column("pitch_min", width=100, anchor=CENTER,stretch=NO)

                stats.heading("desv_standard", text="Desviación Estandar", anchor=CENTER)
                stats.heading("pitch_media", text="Media", anchor=CENTER)
                stats.heading("pitch_median", text="Mediana", anchor=CENTER)
                stats.heading("pitch_max", text="Valor Máximo", anchor=CENTER)
                stats.heading("pitch_min", text="Valor mínimo",anchor=CENTER)
                
                stats.insert(parent='', index='end', text="", values=(desv_standard_round, pitch_media,
                                                                      pitch_median, pitch_max, pitch_min))
                
                
            # create button to see stats
            ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
            self.showmorebut2 = ttk.Button(text="ver más ↓", command=stats).place(x=150,y=550)
            
                      
            
# ------------------------------------------------------ WIDGETS -----------------------------------------------
        
        #add frames
        frame1 = LabelFrame(self, width=320, height=570, text="Importe archivos").place(x=20,y=10)
        
        frame2 = LabelFrame(self,width=930, height=570, text="Análisis MIDI").place(x=350,y=10)
        
        frame3 = LabelFrame(self, width=620, height=100, text="Estadística Descriptiva").place(x=20,y=590)
        
        #add
        #add button import file
        ttk.Style().configure("TButton", padding=0, relief="flat", background="#ccc")
        self.importfile_button = ttk.Button(text="Importar", command=import_file).place(x=50,y=40)
        
        #add textare
        self.textarea = Text(self, width=30,height=1)
        self.textarea.place(x=50,y=70)   
        
        #add image midi file
        global label_midifile_img, midifile_img
        midifile_img = ImageTk.PhotoImage(Image.open("import_icon.png"))
        label_midifile_img = Label(self, image=midifile_img).place(x=110, y=250)

        
        
#creating the window
if __name__ == "__main__":
    main = Main()
    main.mainloop()
