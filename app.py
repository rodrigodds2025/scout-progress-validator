import streamlit as st
import easyocr
from PIL import Image
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
import io
import re
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Scout Progress Validator",
    page_icon="🏕️",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4472C4;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #2952A3;
    }
    h1 {
        color: #4472C4;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown("# 🏕️ Scout Progress Validator")
st.markdown("### Sistema de Validação de Progressões Escoteiras")
st.markdown("---")

# Inicializar session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None
if 'stats' not in st.session_state:
    st.session_state.stats = None
if 'filename' not in st.session_state:
    st.session_state.filename = None

# Inicializar EasyOCR
@st.cache_resource
def get_ocr_reader():
    """Inicializa o leitor OCR"""
    return easyocr.Reader(['pt', 'en'], gpu=False)

def extract_text_from_image(image):
    """Extrai texto da imagem usando EasyOCR"""
    with st.spinner("📸 Inicializando OCR (primeira vez pode demorar)..."):
        reader = get_ocr_reader()
    
    img_array = np.array(image)
    results = reader.readtext(img_array)
    text = '\n'.join([result[1] for result in results])
    return text

def identify_areas(text):
    """Identifica áreas de desenvolvimento"""
    areas = {
        "Físico": {"concluidas": [], "pendentes": []},
        "Intelectual": {"concluidas": [], "pendentes": []},
        "Caráter": {"concluidas": [], "pendentes": []},
        "Afetivo": {"concluidas": [], "pendentes": []},
        "Social": {"concluidas": [], "pendentes": []},
        "Espiritual": {"concluidas": [], "pendentes": []}
    }
    
    lines = text.split('\n')
    current_area = "Físico"  # Default
    item_num = 0
    has_date = False
    current_desc = ""
    
    area_pattern = re.compile(r'(Físico|Intelectual|Caráter|Afetivo|Social|Espiritual)', re.IGNORECASE)
    item_pattern = re.compile(r'^\s*(\d+)\s*[-\.]')
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}|\d{2}/\d{4}')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        area_match = area_pattern.search(line)
        if area_match:
            if item_num > 0 and current_desc:
                if has_date:
                    areas[current_area]["concluidas"].append((item_num, current_desc))
                else:
                    areas[current_area]["pendentes"].append((item_num, current_desc))
            current_area = area_match.group(1).title()
            item_num = 0
            has_date = False
            current_desc = ""
            continue
        
        item_match = item_pattern.match(line)
        if item_match:
            if item_num > 0 and current_desc:
                if has_date:
                    areas[current_area]["concluidas"].append((item_num, current_desc))
                else:
                    areas[current_area]["pendentes"].append((item_num, current_desc))
            
            item_num = int(item_match.group(1))
            current_desc = line
            has_date = False
            continue
        
        if date_pattern.search(line):
            has_date = True
            continue
        
        if item_num > 0:
            current_desc += " " + line
    
    if item_num > 0 and current_desc:
        if has_date:
            areas[current_area]["concluidas"].append((item_num, current_desc))
        else:
            areas[current_area]["pendentes"].append((item_num, current_desc))
    
    return areas

def generate_excel(areas, scout_name, level):
    """Gera planilha Excel"""
    wb = Workbook()
    
    verde = PatternFill(start_color="C6E0B4", end_color="C6E0B4", fill_type="solid")
    amarelo = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    area_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    bold_font = Font(bold=True, size=11)
    border = Border(left=Side(style='thin'), right=Side(style='thin'),
                   top=Side(style='thin'), bottom=Side(style='thin'))
    
    total_concluidas = sum(len(areas[area]["concluidas"]) for area in areas)
    total_pendentes = sum(len(areas[area]["pendentes"]) for area in areas)
    total_geral = total_concluidas + total_pendentes
    
    emojis = {"Físico": "💪", "Intelectual": "🧠", "Caráter": "❤️",
              "Afetivo": "🤝", "Social": "👥", "Espiritual": "✨"}
    
    # ABA 1: Resumo Geral
    ws_resumo = wb.active
    ws_resumo.title = "Resumo Geral"
    
    ws_resumo.merge_cells('A1:E1')
    cell = ws_resumo['A1']
    cell.value = "📊 VALIDAÇÃO DE PROGRESSÃO ESCOTEIRA"
    cell.fill = header_fill
    cell.font = Font(bold=True, color="FFFFFF", size=14)
    cell.alignment = Alignment(horizontal='center')
    
    row = 3
    ws_resumo[f'A{row}'] = "👤 Jovem:"
    ws_resumo[f'B{row}'] = scout_name
    ws_resumo[f'B{row}'].font = bold_font
    row += 1
    ws_resumo[f'A{row}'] = "📍 Nível:"
    ws_resumo[f'B{row}'] = level
    ws_resumo[f'B{row}'].font = bold_font
    row += 1
    ws_resumo[f'A{row}'] = "📅 Data:"
    ws_resumo[f'B{row}'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ws_resumo[f'B{row}'].font = bold_font
    
    row += 2
    ws_resumo.merge_cells(f'A{row}:E{row}')
    cell = ws_resumo[f'A{row}']
    cell.value = "📈 ESTATÍSTICAS GERAIS"
    cell.fill = area_fill
    cell.font = Font(bold=True, color="FFFFFF", size=12)
    cell.alignment = Alignment(horizontal='center')
    
    row += 1
    ws_resumo[f'A{row}'] = "Total:"
    ws_resumo[f'B{row}'] = total_geral
    ws_resumo[f'B{row}'].font = bold_font
    
    row += 1
    ws_resumo[f'A{row}'] = "✅ Concluídas:"
    ws_resumo[f'B{row}'] = total_concluidas
    ws_resumo[f'B{row}'].fill = verde
    ws_resumo[f'B{row}'].font = bold_font
    
    row += 1
    ws_resumo[f'A{row}'] = "⏳ Pendentes:"
    ws_resumo[f'B{row}'] = total_pendentes
    ws_resumo[f'B{row}'].fill = amarelo
    ws_resumo[f'B{row}'].font = bold_font
    
    row += 1
    percentual = (total_concluidas / total_geral * 100) if total_geral > 0 else 0
    ws_resumo[f'A{row}'] = "📊 % Conclusão:"
    ws_resumo[f'B{row}'] = f"{percentual:.1f}%"
    ws_resumo[f'B{row}'].font = Font(bold=True, size=12)
    
    row += 3
    headers = ['Área', 'Total', 'Concluídas', 'Pendentes', '%']
    for col, header in enumerate(headers, 1):
        cell = ws_resumo.cell(row=row, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border
    
    row += 1
    for area_nome in areas:
        conc = len(areas[area_nome]["concluidas"])
        pend = len(areas[area_nome]["pendentes"])
        total_area = conc + pend
        perc = (conc / total_area * 100) if total_area > 0 else 0
        
        ws_resumo.cell(row=row, column=1, value=f"{emojis[area_nome]} {area_nome}").border = border
        ws_resumo.cell(row=row, column=2, value=total_area).border = border
        ws_resumo.cell(row=row, column=2).alignment = Alignment(horizontal='center')
        
        cell_conc = ws_resumo.cell(row=row, column=3, value=conc)
        cell_conc.fill = verde
        cell_conc.border = border
        cell_conc.alignment = Alignment(horizontal='center')
        
        cell_pend = ws_resumo.cell(row=row, column=4, value=pend)
        cell_pend.fill = amarelo
        cell_pend.border = border
        cell_pend.alignment = Alignment(horizontal='center')
        
        ws_resumo.cell(row=row, column=5, value=f"{perc:.1f}%").border = border
        ws_resumo.cell(row=row, column=5).alignment = Alignment(horizontal='center')
        
        row += 1
    
    ws_resumo.column_dimensions['A'].width = 25
    ws_resumo.column_dimensions['B'].width = 12
    ws_resumo.column_dimensions['C'].width = 12
    ws_resumo.column_dimensions['D'].width = 12
    ws_resumo.column_dimensions['E'].width = 12
    
    # ABA 2: Por Área
    ws_area = wb.create_sheet("Por Área")
    ws_area.column_dimensions['A'].width = 5
    ws_area.column_dimensions['B'].width = 80
    
    linha = 1
    for area_nome in areas:
        ws_area.merge_cells(f'A{linha}:B{linha}')
        cell = ws_area[f'A{linha}']
        cell.value = f"{emojis[area_nome]} {area_nome.upper()}"
        cell.fill = area_fill
        cell.font = Font(bold=True, color="FFFFFF", size=12)
        cell.alignment = Alignment(horizontal='center')
        linha += 1
        
        if areas[area_nome]["concluidas"]:
            ws_area[f'B{linha}'] = "✅ CONCLUÍDAS"
            ws_area[f'B{linha}'].fill = verde
            ws_area[f'B{linha}'].font = bold_font
            linha += 1
            
            for num, desc in areas[area_nome]["concluidas"]:
                ws_area.cell(row=linha, column=1, value=num).fill = verde
                ws_area.cell(row=linha, column=2, value=desc).fill = verde
                linha += 1
        
        if areas[area_nome]["pendentes"]:
            ws_area[f'B{linha}'] = "⏳ PENDENTES"
            ws_area[f'B{linha}'].fill = amarelo
            ws_area[f'B{linha}'].font = bold_font
            linha += 1
            
            for num, desc in areas[area_nome]["pendentes"]:
                ws_area.cell(row=linha, column=1, value=num).fill = amarelo
                ws_area.cell(row=linha, column=2, value=desc).fill = amarelo
                linha += 1
        
        linha += 2
    
    # ABA 3: Detalhamento
    ws_det = wb.create_sheet("Detalhamento")
    ws_det.column_dimensions['A'].width = 5
    ws_det.column_dimensions['B'].width = 18
    ws_det.column_dimensions['C'].width = 65
    ws_det.column_dimensions['D'].width = 12
    
    headers_det = ['#', 'Área', 'Descrição', 'Status']
    for col, header in enumerate(headers_det, 1):
        cell = ws_det.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border
    
    linha = 2
    for area_nome in areas:
        for num, desc in areas[area_nome]["concluidas"]:
            ws_det.cell(row=linha, column=1, value=num).fill = verde
            ws_det.cell(row=linha, column=2, value=area_nome).fill = verde
            ws_det.cell(row=linha, column=3, value=desc).fill = verde
            ws_det.cell(row=linha, column=4, value="✅").fill = verde
            linha += 1
        
        for num, desc in areas[area_nome]["pendentes"]:
            ws_det.cell(row=linha, column=1, value=num).fill = amarelo
            ws_det.cell(row=linha, column=2, value=area_nome).fill = amarelo
            ws_det.cell(row=linha, column=3, value=desc).fill = amarelo
            ws_det.cell(row=linha, column=4, value="⏳").fill = amarelo
            linha += 1
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer, total_geral, total_concluidas, total_pendentes, percentual

# Interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Upload da Imagem")
    uploaded_file = st.file_uploader(
        "Arraste a imagem ou clique para selecionar",
        type=['png', 'jpg', 'jpeg', 'webp']
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagem carregada", use_column_width=True)

with col2:
    st.markdown("### 📝 Informações")
    
    scout_name = st.text_input(
        "Nome do Jovem",
        placeholder="Ex: Matheus Oliveira"
    )
    
    level = st.radio(
        "Nível",
        options=["Pista/Trilha", "Rumo/Travessia"]
    )
    
    st.markdown("---")
    
    if st.button("🚀 GERAR VALIDAÇÃO", disabled=not (uploaded_file and scout_name)):
        with st.spinner("⏳ Processando..."):
            progress = st.progress(0)
            
            st.info("📸 Extraindo texto...")
            text = extract_text_from_image(image)
            progress.progress(33)
            
            st.info("🔍 Identificando áreas...")
            areas = identify_areas(text)
            progress.progress(66)
            
            st.info("📊 Gerando planilha...")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{scout_name.replace(' ', '_')}_{level.replace('/', '-')}_{timestamp}.xlsx"
            
            excel_buffer, total, concluidas, pendentes, percentual = generate_excel(
                areas, scout_name, level
            )
            progress.progress(100)
            
            st.session_state.processed = True
            st.session_state.excel_data = excel_buffer
            st.session_state.stats = {
                'total': total,
                'concluidas': concluidas,
                'pendentes': pendentes,
                'percentual': percentual,
                'areas': areas
            }
            st.session_state.filename = filename

if st.session_state.processed:
    st.markdown("---")
    st.markdown("## 🎉 Validação Concluída!")
    
    stats = st.session_state.stats
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total", stats['total'])
    with col2:
        st.metric("✅ Concluídas", stats['concluidas'])
    with col3:
        st.metric("⏳ Pendentes", stats['pendentes'])
    with col4:
        st.metric("📈 %", f"{stats['percentual']:.1f}%")
    
    st.markdown("### 🎯 Por Área")
    
    emojis = {"Físico": "💪", "Intelectual": "🧠", "Caráter": "❤️",
              "Afetivo": "🤝", "Social": "👥", "Espiritual": "✨"}
    
    cols = st.columns(3)
    for idx, (area_nome, area_data) in enumerate(stats['areas'].items()):
        with cols[idx % 3]:
            conc = len(area_data["concluidas"])
            pend = len(area_data["pendentes"])
            total_area = conc + pend
            perc = (conc / total_area * 100) if total_area > 0 else 0
            
            st.markdown(f"""
            <div style='padding: 1rem; background: #f0f2f6; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h4>{emojis[area_nome]} {area_nome}</h4>
                <p><b>Total:</b> {total_area}</p>
                <p><b>✅ Concluídas:</b> {conc}</p>
                <p><b>⏳ Pendentes:</b> {pend}</p>
                <p><b>%:</b> {perc:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### 📥 Download")
    st.download_button(
        label="⬇️ BAIXAR PLANILHA",
        data=st.session_state.excel_data,
        file_name=st.session_state.filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    if st.button("🔄 Nova Validação"):
        st.session_state.processed = False
        st.session_state.excel_data = None
        st.session_state.stats = None
        st.session_state.filename = None
        st.rerun()

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏕️ <b>Scout Progress Validator</b></p>
    <p>Sempre Alerta! ⚜️</p>
</div>
""", unsafe_allow_html=True)
