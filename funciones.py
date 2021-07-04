def diagramaStiff(a, maxConNorm, index):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    

    fig, ax = plt.subplots()
    patches = []

    polygon = Polygon(a, True)
    patches.append(polygon)

    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)

    colors = 100*np.random.rand(len(patches))
    p.set_array(np.array(colors))

    ax.add_collection(p)

    #alteramos los ejes
    x = [0, .125, .25, .375, .5, .625, .75, .875, 1]
    labels = [maxConNorm/2, .75*maxConNorm/2, .5*maxConNorm/2, .25*maxConNorm/2,
             0, .25*maxConNorm/2, .5*maxConNorm/2, .75*maxConNorm/2, maxConNorm/2]
    formattedLabels = ["%.1f" % label for label in labels]
    plt.yticks([0,0.5,1],[0,0.5,1], fontsize=0 )
    plt.xticks(x, formattedLabels, fontsize=12)
    plt.grid(b=True, which='minor', linestyle='-')
	
    ax.set_title(index)

    ax.set_xlabel('meq/l', fontsize=12)
	
	

    #Generamos las etiquetas de los cationes
    ax.text(-0.02, 1, 'Na + K', fontsize=12, horizontalalignment='right')
    ax.text(-0.02, 0.5, 'Ca', fontsize=12, horizontalalignment='right')
    ax.text(-0.02, 0, 'Mg', fontsize=12, horizontalalignment='right')

    #Generamos las etiquetas de los aniones
    ax.text(1.02, 1, 'Cl', fontsize=12)
    ax.text(1.02, 0.5, 'SO4', fontsize=12)
    ax.text(1.02, 0, 'HCO3+CO3', fontsize=12)
    
    
    plt.close()
    
    return fig
    
import imageio
import pandas as pd
import numpy as np
import base64
import io 
import os
  
#download files  
def get_binary_file_downloader_html(bin_file, file_label='File'):
            with open(bin_file, 'rb') as f:
                data = f.read()
            bin_str = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">🔷 Download {file_label}</a>'
            return href