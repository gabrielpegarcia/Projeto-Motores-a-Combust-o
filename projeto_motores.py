import math
###########################
import PySimpleGUI as sg
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


class Dados:
    def __init__(self, raio, rpm, raio_mancal, lambda_):
        self.raio = raio
        self.rpm = rpm
        self.lambda_ = lambda_
        self.massa = massa
        self.raio_mancal = raio_mancal
        self.area = math.pi*(raio**2)
        self.vel_angular = rpm*2*math.pi/60


    def angulo_rad(self, angulos):
        angulo_rad = angulos*math.pi/180
        return angulo_rad

    def calcula_forca_pistao(self, pressoes):
        forca = self.area*pressao
        return forca

    def calcula_forca_inercia(self, pressao, angulo_rad, lambda_):
        lista_forca_inercia = self.massa*(self.vel_angular**2)*self.raio_mancal*(
                np.cos(angulo_rad) + lambda_*np.cos(2*angulo_rad))
        return lista_forca_inercia

    def calcula_torque(self, angulo_rad, pressao, forca_inercia, forca_pistao):
        lista_torque = (forca_pistao - forca_inercia)*self.raio_mancal*(
                np.sin(angulo_rad) + (self.lambda_/2)*np.sin(2*angulo_rad))
       
        return lista_torque

    def calcula_lista_torque_defasada(self, angulos, torque, defasagem):
        angulo_defasado = angulos[0] + defasagem
        index = list(angulos).index(angulo_defasado)
        print("O index é", index)
        inicio = torque[0:index]
        fim = torque[index:]
        torque_defasado = np.concatenate((fim, inicio), axis=None)
        
        return torque_defasado

 
    def calcula_torque_total(self, angulos, torque, defasagem, num_cilindros):

        torque_total = torque

        for i in range(num_cilindros - 1):
            torque_defasado = self.calcula_lista_torque_defasada(
                angulos, torque, (i+1)*defasagem)

            torque_total = torque_total + torque_defasado
        print(torque_total)
        return torque_total




#Functions to prevent GUI blurring
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


# ------------------------------- PySimpleGUI CODE


layout = [
    [sg.Text('Separe as casas decimais com ponto final "."')],
    [sg.Text("RPM:"), sg.Input(size=(5,0), key='rpm'), sg.Text("Massa:"), sg.Input(size=(5,0), key='massa'), sg.Text("Raio do Pistão:"), sg.Input(size=(5,0), key='raio'),
    sg.Text("N° de Cilindros:"), sg.Input(size=(5,0), key='num_cilindros'), sg.Text("Raio do Mancal:"), sg.Input(size=(5,0), key='raio_mancal')],
    [sg.B('Plotar Força do Pistão'), sg.B('Plotar Torque'), sg.B('Plotar Força de Inércia'), sg.B('Plotar Todos')],
    [sg.T('Controls:')],
    [sg.Canvas(key='controls_cv')],
    [sg.T('Figure:')],
    [sg.Column(
        layout=[
            [sg.Canvas(key='fig_cv',
                       # it's important that you set this size
                       size=(400 * 2, 400)
                       )]
        ],
        background_color='#DAE0E6',
        pad=(0, 0)
    )],
    [sg.B('Alive?')]

]

window = sg.Window('Graph with controls', layout)

#############   Input de Dados  ###############






while True:
    event, values = window.read()

    massa = float(values['massa']) # Em Kg
    raio = float(values['raio'])
    rpm = float(values['rpm'])
    raio_mancal = float(values['raio_mancal'])
    lambda_ = 0.26
    num_cilindros = int(values['num_cilindros'])

    tempos = 4
    defasagem = int(180*tempos/num_cilindros)

    ###########################    Recebe os cálculos e coloca em listas   ##########################
    dados = Dados(raio, rpm, raio_mancal, lambda_)
    pressao = np.loadtxt("dados_pressao.txt")
    angulos = np.loadtxt("dados_angulos.txt")

    forca_pistao = dados.calcula_forca_pistao(pressao)

    angulo_rad = dados.angulo_rad(angulos)

    forca_inercia = dados.calcula_forca_inercia(pressao, angulo_rad, lambda_)

    torque = dados.calcula_torque(angulo_rad, pressao, forca_inercia, forca_pistao)

    torque_total = dados.calcula_torque_total(angulos, torque, defasagem, num_cilindros)

    print(event, values)
    if event in 'Plotar Torque':  # always,  always give a way out!
        plt.clf()
        plt.figure(1)
        fig = plt.gcf()
        DPI = fig.get_dpi()
        
        # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
        fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
        plt.plot(angulos, torque_total)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
    
    elif event in 'Plotar Força de Inércia':
        plt.clf()
        plt.figure(1)
        fig = plt.gcf()
        DPI = fig.get_dpi()
        # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
        fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
        plt.plot(angulos, forca_inercia)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
    
    elif event in 'Plotar Força do Pistão':
        plt.clf()
        plt.figure(1)
        fig = plt.gcf()
        DPI = fig.get_dpi()
        # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
        fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
        plt.plot(angulos, forca_pistao)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

    elif event in 'Plotar Todos':
        # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE
        plt.clf()
        plt.figure(1)
        fig = plt.gcf()
        DPI = fig.get_dpi()
        # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
        fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
        # -------------------------------
        plt.subplot(221)
        plt.plot(angulos, torque_total)

        plt.subplot(222)
        plt.plot(angulos, forca_inercia)

        plt.subplot(223)
        plt.plot(angulos, pressao)

        plt.subplot(224)
        plt.plot(angulos, forca_pistao)
        
        
    # ------------------------------- Instead of plt.show()
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

window.close()
