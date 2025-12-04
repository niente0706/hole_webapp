import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from MDAnalysis.analysis import hole2
import stmol
import py3Dmol
import zipfile
import datetime
import requests
import os
import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def reset_logger(logpath):
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler(logpath)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.info("Logger initialized.")

hole_webapp_path = '.'
hole_exe_path = os.path.join(hole_webapp_path, 'hole2', 'exe', 'hole')
hole_rad_dir_path = os.path.join(hole_webapp_path, 'hole2', 'rad')

def make_logdir(filename):
    now = datetime.datetime.now()
    logdir = os.path.join(hole_webapp_path, 'logs', now.strftime('%Y%m%d') + '_' + filename)
    os.makedirs(logdir, exist_ok=True)
    logpath = os.path.join(logdir, 'log.txt')
    reset_logger(logpath)
    return logdir

st.session_state['stmol_view'] = py3Dmol.view()

st.session_state['fig'] = plt.figure(figsize=(8, 6))
ax = st.session_state['fig'].add_subplot(111)
ax.set_xlabel('Radius (Å)')
ax.set_ylabel('Position along pore axis (Å)')
st.session_state['fig'] = st.session_state['fig']

level_list = ['Full text output', 'Except run in progress', 'Only minimun rdius and conductance', 'Only input card mirroring']

st.title("HOLE Web Application")

with st.sidebar:
    input_method = st.radio('Input PDB', ['Upload local PDB file', 'Fetch PDB from RCSB'])
    with st.form('pdb_input'):
        if input_method == 'Upload local PDB file':
            pdb = st.file_uploader("Choose a PDB file", type=["pdb"])
        else:
            pdb_id = st.text_input("Enter PDB ID", value="1A2C")
        input_submit = st.form_submit_button('Submit')
    
    st.markdown('---')
    st.header("Hole parameters")
    with st.form('hole_params'):
        st.number_input('End radius (Å)', min_value=0.0, value=25.0, step=0.1, key='r_end')
        st.text_input('pore vector (x y z)', value='0 0 1', key='cvect')
        st.text_input('Residue names to ignore (separated by space)', value='', key='ignore_res')
        with st.expander('Advanced options'):
            st.number_input('Sampling density (Å)', min_value=0.01, value=0.2, step=0.01, key='sample')
            st.text_input('starting point (x y z)', value='', key='cpoint')
            st.number_input('Random seed', value=None, step=1, key='random')
            st.selectbox('VDW radii file', ['simple', 'amberuni', 'bondi', 'hardcore', 'xplor'], key='vdwr')
            st.selectbox('Output level', level_list, key='level')
        hole_submit = st.form_submit_button('Run HOLE')

if input_submit:
    if input_method == 'Upload local PDB file' and pdb is not None:
        pdb_name = os.path.splitext(pdb.name)[0]
        log_dir = make_logdir(pdb_name)
        pdb_path = os.path.join(log_dir, f'{pdb_name}.pdb')
        with open(pdb_path, 'w', encoding='utf-8') as f:
            pdb_lines = pdb.getvalue().decode('utf-8')
            for line in pdb_lines.splitlines():
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    name = line[12:16].strip()
                    if len(name) == 4:
                        name = name[:3]
                    f.write(line[:12] + f' {name:<3}' + line[16:] + '\n')
                else:
                    f.write(line + '\n')
    elif input_method == 'Fetch PDB from RCSB' and pdb_id:
        pdb_url = f'https://files.rcsb.org/download/{pdb_id.upper()}.pdb'
        response = requests.get(pdb_url)
        if response.status_code == 200:
            log_dir = make_logdir(pdb_id)
            pdb_path = os.path.join(log_dir, f'{pdb_id}.pdb')
            with open(pdb_path, 'wb') as f:
                f.write(response.content)
        else:
            st.error(f"Failed to fetch PDB ID {pdb_id}. Please check the ID and try again.")
            logger.warning(f"Failed to fetch PDB ID {pdb_id} from RCSB.")
            st.stop()
    else:
        st.warning("Please provide a valid PDB file or ID.")
        logger.warning("No valid PDB input provided.")
        st.stop()
    
    st.session_state['pdb_path'] = pdb_path
    st.session_state['log_dir'] = log_dir
    st.success(f"PDB file is ready!")
    logger.info(f"PDB file is saved at {pdb_path}")

if hole_submit and 'pdb_path' in st.session_state:
    prefix = os.path.splitext(os.path.basename(st.session_state['pdb_path']))[0]
    if st.session_state['cpoint'] == '':
        cpoint = None
    else:
        cpoint = list(map(float, st.session_state['cpoint'].split()))
        if len(cpoint) != 3:
            st.error("Starting point must have exactly three components (x y z).")
            st.stop()
    if st.session_state['cvect'] == '':
        cvect = None
    else:
        cvect = list(map(float, st.session_state['cvect'].split()))
        if len(cvect) != 3:
            st.error("Pore vector must have exactly three components (x y z).")
            st.stop()
    if st.session_state['ignore_res'] == '':
        ignore_res = []
    else:
        ignore_res = st.session_state['ignore_res'].split()
    level = level_list.index(st.session_state['level'])
    log_dir = st.session_state['log_dir']
    
    hole_args = {
        'pdbfile': st.session_state['pdb_path'],
        'outfile': os.path.join(log_dir, f'{prefix}.out'),
        'sphpdb_file': os.path.join(log_dir, f'{prefix}.sph'),
        'vdwradii_file': os.path.join(hole_rad_dir_path, f'{st.session_state["vdwr"]}.rad'),
        'sample': st.session_state['sample'],
        'end_radius': st.session_state['r_end'],
        'cpoint': cpoint,
        'cvect': cvect,
        'random_seed': st.session_state['random'],
        'ignore_residues': ignore_res,
        'output_level': level,
        'executable': hole_exe_path
    }
    
    logger.info("Starting HOLE analysis with parameters:")
    for k, v in hole_args.items():
        logger.info(f"  {k}: {v}")
    hole_output = hole2.hole(**hole_args)
    logger.info("HOLE analysis completed.")
    
    pore_axis = hole_output[0].rxn_coord
    pore_radius = hole_output[0].radius
    
    st.session_state['pore_axis'] = pore_axis
    st.session_state['pore_radius'] = pore_radius
    
    csv_path = os.path.join(log_dir, f'{prefix}.csv')
    r_min = 10 ** 18
    r_min_coord = -1
    local_minima = []
    last = [10 ** 18, -1, True]
    with open(csv_path, 'w') as f:
        f.write('Pore axis,Pore radius\n')
        for i in range(len(pore_axis)):
            r = pore_radius[i]
            coord = pore_axis[i]
            if r < r_min:
                r_min = r
                r_min_coord = coord
            if last[2] and last[0] < r:
                local_minima.append(last[:2])
            last = [r, coord, r < last[0]]
            f.write(f'{coord},{r}\n')
    logger.info(f"Saved pore radius profile to {csv_path}")
    
    summary_path = os.path.join(log_dir, f'{prefix}.txt')
    with open(summary_path, 'w') as f:
        f.write('Minimum radius\n')
        f.write('Coordinate : Radius\n')
        f.write(f'{r_min_coord} : {r_min}\n\n')
        f.write('Local minima\n')
        f.write('Coordinate : Radius\n')
        for i in local_minima:
            f.write(f'{i[1]} : {i[0]}\n')
        f.write('\n')
    logger.info(f"Saved summary to {summary_path}")
    
    st.session_state['sph_path'] = os.path.join(log_dir, f'{prefix}.sph')
    
    st.session_state['download_path'] = os.path.join(log_dir, f'{prefix}_results.zip')
    with zipfile.ZipFile(st.session_state['download_path'], 'w') as zipf:
        for filename in os.listdir(log_dir):
            if filename.endswith('.zip'):
                continue
            file_path = os.path.join(log_dir, filename)
            zipf.write(file_path, arcname=filename)
    logger.info(f"Created download zip at {st.session_state['download_path']}")

st.session_state['style'] = st.selectbox('style', ['cartoon', 'stick', 'sphere', 'line', 'cross'])
st.session_state['pore_transparency'] = st.slider('pore transparency', min_value=0.0, max_value=1.0, value=0.5, step=0.01)
st.session_state['pore_color'] = st.color_picker('pore color', value='#00FFFF')
if 'pdb_path' in st.session_state:
    st.session_state['stmol_view'].addModel(open(st.session_state['pdb_path']).read(), 'pdb')
    st.session_state['stmol_view'].setStyle({st.session_state['style']: {}})
    st.session_state['stmol_view'].zoomTo()
if 'sph_path' in st.session_state:
    with open(st.session_state['sph_path'], 'r') as sph_file:
        sph_lines = sph_file.readlines()
    for line in sph_lines:
        if not line.startswith('ATOM  ') or line[60:66] == '  0.00':
            continue
        x = float(line[30:38])
        y = float(line[38:46])
        z = float(line[46:54])
        r = float(line[60:66])
        st.session_state['stmol_view'].addSphere({
            'center': {'x': x, 'y': y, 'z': z},
            'radius': r,
            'color': st.session_state['pore_color'],
            'opacity': st.session_state['pore_transparency']
        })

if 'pore_axis' in st.session_state and 'pore_radius' in st.session_state:
    pore_axis = st.session_state['pore_axis']
    pore_radius = st.session_state['pore_radius']
    prefix = os.path.splitext(os.path.basename(st.session_state['pdb_path']))[0]
    log_dir = st.session_state['log_dir']
    st.session_state['pdf_path'] = os.path.join(log_dir, f'{prefix}.pdf')
    
    with PdfPages(st.session_state['pdf_path']) as pdf:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(pore_radius, pore_axis, label='Pore Radius Profile')
        ax.set_xlabel('Radius (Å)')
        ax.set_ylabel('Position along pore axis (Å)')
        ax.set_title(f'HOLE result of {prefix}')
        pdf.savefig(fig)
        st.session_state['fig'] = fig
        plt.close(fig)

stmol.showmol(st.session_state['stmol_view'], width=800, height=600)
st.markdown('---')
st.pyplot(st.session_state['fig'])

if 'download_path' in st.session_state:
    st.download_button(
        label="Download HOLE results",
        data=open(st.session_state['download_path'], 'rb').read(),
        file_name=os.path.basename(st.session_state['download_path']),
        mime='application/zip'
    )
