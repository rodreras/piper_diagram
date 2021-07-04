#importando streamlit, ferramenta para dashboard
import streamlit as st

#importando as libs essenciais
import os, math, re
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib import cm
import matplotlib


import imageio
import pandas as pd
import numpy as np
import base64
import io 
from PIL import Image
import xlrd

#importando folium para integrar com o streamlit
#from streamlit_folium import folium_static
#import folium

#importando as funções 
from funciones import *


# configurando a página para modo wide
st.set_page_config(layout="wide", page_title = 'Piper Diagram' )

#Título e Subtítulo

st.title( 'GeoApps: Hydrogeochemistry')
st.header('Piper Diagram')
    

#Apresentação Inicial
st.markdown('''
The **Piper Diagram** is a graphical representation, developed in 1944, by Arthur Piper,
with the aim of understanding the chemistry of water and the sources of the 
constituents dissolved in the samples. Nowadays, it is widely used in hydrogeochemical studies in 
several areas.



''')

st.header('Stiff Diagrams')

st.markdown('''
The **Stiff Diagram** is a graphical representation of chemical analyses, and just like Piper Diagram,
it is widely used by the geoscience comunity. One of the biggest differentials in this
diagram is that you can asign the geospatial variable, being able to see how's the
water chemistry in each point of the basin.
''')

option = st.radio('What diagrams would you like??', ['Piper Diagrams','Stiff Diagrams'])

#Mostrando o padrão das colunas 
st.markdown('''
To use this GeoApp, it is necessary to import a `XLS` file,
with the columns defined just like the table below:
 ''')

#tabela de exemplo
table = pd.read_excel('exemple.xls')
#table = xlrd.open_workbook('exemple.xls')
st.table(table)

uploaded_file = st.file_uploader("Choose a file")



if option == 'Piper Diagrams':
    #importando arquivo via CSV para o Streamlit
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
     
        st.markdown(''':scroll: Processing...''')
        
        #lendo a imagem para fazer o diagrama 
        img = imageio.imread("PiperCompleto.png")

        #Dicionário de Íons - Massa molecular de cada íon
        ions = {
        'HCO3': 61, 'CO3' : 30, 'Cl' : 35, 'SO4': 48,
        'Na' : 23, 'Ca' : 20, 'Mg' : 12, 'K'  : 39
        }

        #gerando colunas com as concentrações de equivalentes
        for ion in ions.keys():
            df[str(ion)+'_meq'] = df[ion]/ions[ion]
            
        

        #normalizando os ânions

        #SO4
        df['SO4_norm'] = df['SO4_meq'] / (df['SO4_meq'] +
                                    df['HCO3_meq']+df['CO3_meq']+df['Cl_meq']) * 100

        #HCO3
        df['HCO3_CO3_norm'] = (df['HCO3_meq']+df['CO3_meq']) / (df['SO4_meq'] +
                                    df['HCO3_meq']+df['CO3_meq']+df['Cl_meq']) * 100

        #Cl
        df['Cl_norm'] = df['Cl_meq'] / (df['SO4_meq'] +
                                    df['HCO3_meq']+df['CO3_meq']+df['Cl_meq']) * 100

        #normalizando os cátions 

        #Mg
        df['Mg_norm'] = df['Mg_meq'] / (df['Mg_meq'] +
                                    df['Ca_meq']+df['K_meq']+df['Na_meq']) * 100

        #K
        df['Na_K_norm'] = (df['K_meq']+df['Na_meq']) / (df['Mg_meq'] +
                                    df['Ca_meq']+df['K_meq']+df['Na_meq']) * 100

        #Ca
        df['Ca_norm'] = df['Ca_meq'] / (df['Mg_meq'] +
                                    df['Ca_meq']+df['K_meq']+df['Na_meq']) * 100

        st.markdown(''':chart_with_upwards_trend: Finishing the diagram...''')
        #função das coordenadas
        def coordenada(Ca,Mg,Cl,SO4,Label):
            xcation = 40 + 360 - (Ca + Mg / 2) * 3.6
            ycation = 40 + (math.sqrt(3) * Mg / 2)* 3.6
            xanion = 40 + 360 + 100 + (Cl + SO4 / 2) * 3.6
            yanion = 40 + (SO4 * math.sqrt(3) / 2)* 3.6
            xdiam = 0.5 * (xcation + xanion + (yanion - ycation) / math.sqrt(3))
            ydiam = 0.5 * (yanion + ycation + math.sqrt(3) * (xanion - xcation))
            #print(str(xanion) + ' ' + str(yanion))
            c=np.random.rand(3,1).ravel()
            listagraph=[]
            listagraph.append(plt.scatter(xcation,ycation,zorder=1,c=c, s=60, edgecolors='#4b4b4b',label=Label))
            listagraph.append(plt.scatter(xanion,yanion,zorder=1,c=c, s=60, edgecolors='#4b4b4b'))
            listagraph.append(plt.scatter(xdiam,ydiam,zorder=1,c=c, s=60, edgecolors='#4b4b4b'))
            return listagraph
        
        #desabilitando os possíveis erros.
        st.set_option('deprecation.showPyplotGlobalUse', False)    
        
        #plotando o gráfico
        plt.figure(figsize=(20,15))
        plt.imshow(np.flipud(img),zorder=0)
        for index, row in df.iterrows():
            coordenada(row['Ca_norm'],row['Mg_norm'],row['Cl_norm'],row['SO4_norm'],row['station'])
        plt.ylim(0,830)
        plt.xlim(0,900)
        plt.axis('off')
        plt.title('Piper Diagram', fontsize = 20, fontweight = 'bold')
        plt.legend(loc='upper right',prop={'size':10}, frameon=False, scatterpoints=1)
        plt.savefig('diagrama_piper.jpeg')
        st.pyplot()
        
        
        #baixar imagem
            
        st.markdown(get_binary_file_downloader_html('diagrama_piper.jpeg', 'Diagram'), unsafe_allow_html=True)
        
        #baixar tabela
        towrite = io.BytesIO()
        downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
        towrite.seek(0)  # reset pointer
        b64 = base64.b64encode(towrite.read()).decode()  # some strings
        linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="geoapp_hidro_table.xlsx">📂 Download Table</a>'
        st.markdown(linko, unsafe_allow_html=True)


elif option == 'Stiff Diagrams':
    
    #importando arquivo via CSV para o Streamlit
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
     
        st.markdown(''':scroll: Processing both diagrams.
                       It might take some time...''')
        
        
        #Dicionário de Íons - Massa molecular de cada íon
        ions = {
        'HCO3': 61, 'CO3' : 30, 'Cl' : 35, 'SO4': 48,
        'Na' : 23, 'Ca' : 20, 'Mg' : 12, 'K'  : 39
        }

        #gerando colunas com as concentrações de equivalentes
        for ion in ions.keys():
            df[str(ion)+'_meq'] = df[ion]/ions[ion]
            
        

        #normalizando os ânions

        #SO4
        df['SO4_norm'] = df['SO4_meq'] / (df['SO4_meq'] +
                                    df['HCO3_meq']+df['CO3_meq']+df['Cl_meq']) * 100

        #HCO3
        df['HCO3_CO3_norm'] = (df['HCO3_meq']+df['CO3_meq']) / (df['SO4_meq'] +
                                    df['HCO3_meq']+df['CO3_meq']+df['Cl_meq']) * 100

        #Cl
        df['Cl_norm'] = df['Cl_meq'] / (df['SO4_meq'] +
                                    df['HCO3_meq']+df['CO3_meq']+df['Cl_meq']) * 100

        #normalizando os cátions 

        #Mg
        df['Mg_norm'] = df['Mg_meq'] / (df['Mg_meq'] +
                                    df['Ca_meq']+df['K_meq']+df['Na_meq']) * 100

        #K
        df['Na_K_norm'] = (df['K_meq']+df['Na_meq']) / (df['Mg_meq'] +
                                    df['Ca_meq']+df['K_meq']+df['Na_meq']) * 100

        #Ca
        df['Ca_norm'] = df['Ca_meq'] / (df['Mg_meq'] +
                                    df['Ca_meq']+df['K_meq']+df['Na_meq']) * 100

        st.markdown(''':chart_with_upwards_trend: Finishing the diagram...''')
        
        #criando lista de nome das estações. Importante para dar nome ao gráfico
        stations = df.station.to_list()
        
        for index, row in df.iterrows():
            
            Na_K, Ca, Mg = row['Na_meq'] + row['K_meq'], row['Ca_meq'], row['Mg_meq']
            Cl, SO4, HCO3_CO3 = row['Cl_meq'], row['SO4_meq'], row['HCO3_meq'] + row['CO3_meq']
            
            #aplicando um fator no eixo
            maxConNorm = max([Na_K, Ca, Mg, Cl, SO4, HCO3_CO3])*2
            
            #conjunto de pontos no diagrama stiff
            a = np.array([[0.5 + Cl/maxConNorm,1],[0.5 + SO4/maxConNorm,.5],[0.5 + HCO3_CO3/maxConNorm,0]
                  ,[0.5 - Mg/maxConNorm,0],[0.5 - Ca/maxConNorm,.5],[0.5 - Na_K/maxConNorm,1]])
            
            
            #criando  a figura
            figura = diagramaStiff(a, maxConNorm, stations[index])
            
            #salvando a figura 
            figura.savefig('stiff_diagram_{}.jpeg'.format(stations[index]))
            
            #plotando a figura 
            st.pyplot(figura)
            
            
            #baixar imagem
          
            st.markdown(get_binary_file_downloader_html('stiff_diagram_{}.jpeg'.format(stations[index]), 'Diagram'), unsafe_allow_html=True)
            
             
st.sidebar.title('About the app')

st.sidebar.markdown('''
The purpose of this GeoApp is to allow chemical analysis of waters to be 
done faster and easier, ensuring the data processing's democratization for the 
geoscience community with the support of the open source programs.
''')

st.sidebar.title('About Me')

st.sidebar.subheader('Hello, folks!')
st.sidebar.markdown("I'm Rodrigo, a geology student from Brazil,that enjoys to mix Geoscience subject with programming. One of my personal goals now is to develop geoapps that helps a lot of students and geoscientists around the world")

st.sidebar.title("Get in Touch")
st.sidebar.markdown("[![Linkedin Badge](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&link=https://www.linkedin.com/in/rodrigobrust/)](https://www.linkedin.com/in/rodrigobrust/)")
st.sidebar.markdown("[![Github Badge] (https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white&link=https://github.com/rodreras)](https://github.com/rodreras)")
st.sidebar.markdown("[![Gmail Badge] (https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)] (rodrigobrusts@gmail.com)")

st.sidebar.title('Sources') 

st.sidebar.markdown('''

[Piper Diagrams - Wikipedia](https://en.wikipedia.org/wiki/Piper_diagram)

[Stiff Diagrams - Wikipedia](https://en.wikipedia.org/wiki/Stiff_diagram)

[Piper Diagram (Hatarilabs - Saul Montoya)](https://hatarilabs.com/ih-en/how-to-make-a-piper-diagram-in-python-tutorial)

[Stiff Diagram (Hatarilabs - Saul Montoya)](https://hatarilabs.com/ih-en/how-to-do-a-georeferenced-stiff-diagram-with-python-3-and-qgis-3-tutorial)
''')
