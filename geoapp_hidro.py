#importando streamlit, ferramenta para dashboard
import streamlit as st

#importando plotly, para gráficos mais bonitos
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import os, math
import matplotlib.pyplot as plt
import imageio
import plotly.offline as pyo

# Set notebook mode to work in offline
pyo.init_notebook_mode()

#importando pandas para data frames
import pandas as pd

#importando numpy para números
import numpy as np

#importando folium para integrar com o streamlit
from streamlit_folium import folium_static
import folium
import base64
import io 
from PIL import Image

# configurando a página para modo wide
st.set_page_config(layout="wide")

#Título e Subtítulo

st.title('Piper Diagram' )
st.header('GeoApps: Hidrogeochemistry')
    

#Apresentação Inicial
st.write('The Piper Diagram is a graphical representation, developed in 1944, by Arthur Piper, with the aim of understanding the chemistry of water and the sources of the constituents dissolved in the samples. Widely used in hydrogeochemical studies in several areas.')
st.write('The purpose of this GeoApp is to allow chemical analysis of waters to be done faster and easier, ensuring the democratization of platforms with the power of the geoscience community and open source programs.')


#Mostrando o padrão das colunas 
st.markdown('To use this GeoApp, it is necessary to import a **XLSX** or **XLS** file, with the columns defined according to the table below:')
table = pd.read_excel('exemple.xls')
st.dataframe(table)

#importando arquivo via CSV para o Streamlit

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
 
    st.text('🎲 Processing...')
    
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
        
    st.text('🎲 Still processing...')

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

    st.text('🎲 Finishing the calculations... ')
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
    #plt.show()
    st.pyplot()
    
    
    #baixar imagem
    
    def get_binary_file_downloader_html(bin_file, file_label='File'):
        with open(bin_file, 'rb') as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">🔷 Download {file_label}</a>'
        return href
    
    st.markdown(get_binary_file_downloader_html('diagrama_piper.jpeg', 'Diagram'), unsafe_allow_html=True)
    
    #baixar tabela
    towrite = io.BytesIO()
    downloaded_file = df.to_excel(towrite, encoding='utf-8', index=False, header=True)
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()  # some strings
    linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="geoapp_hidro_table.xlsx">📂 Download Table</a>'
    st.markdown(linko, unsafe_allow_html=True)


st.sidebar.title('About Me')

st.sidebar.subheader('Hello, folks!')
st.sidebar.markdown("I'm Rodrigo, a geology student from Brazil,that enjoys to mix Geoscience subject with programming. One of my personal goals now is to develop geoapps that helps a lot of students and geoscientists around the world")

st.sidebar.title("Get in Touch")
st.sidebar.markdown("[![Linkedin Badge](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&link=https://www.linkedin.com/in/rodrigobrust/)](https://www.linkedin.com/in/rodrigobrust/)")
st.sidebar.markdown("[![Github Badge] (https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white&link=https://github.com/rodreras)](https://github.com/rodreras)")
st.sidebar.markdown("[![Gmail Badge] (https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)] (rodrigobrusts@gmail.com)")
