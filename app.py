import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
import io
import re

# Configuração da página
st.set_page_config(
    page_title="Scout Progress Validator",
    page_icon="🏕️",
    layout="wide"
)

# CSS customizado
st.markdown("""
<style>
    .main {padding: 2rem;}
    .stButton>button {
        width: 100%;
        background-color: #4472C4;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {background-color: #2952A3;}
    h1 {color: #4472C4; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🏕️ Scout Progress Validator v3.0")
st.markdown("### Sistema de Validação de Progressões Escoteiras")
st.markdown("---")

# Session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None
if 'stats' not in st.session_state:
    st.session_state.stats = None
if 'filename' not in st.session_state:
    st.session_state.filename = None

def preprocess_image(image):
    """Pré-processa imagem para OCR"""
    img = np.array(image)
    
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
    
    binary = cv2.adaptiveThreshold(
        denoised, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    kernel = np.ones((1,1), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)
    
    return Image.fromarray(dilated)

def extract_text_from_image(image):
    """Extrai texto com Tesseract otimizado"""
    processed_img = preprocess_image(image)
    custom_config = r'--oem 3 --psm 6 -l por'
    text = pytesseract.image_to_string(processed_img, config=custom_config)
    return post_process_text(text)

def post_process_text(text):
    """Limpa texto extraído"""
    # Remover símbolos estranhos do OCR
    text = re.sub(r'\b(IS\)|SA\)|O\)|há|q|v|Y|GQ|\[AN|FEZ\)|EO|\[SG\]|G,\)|1S,\)|1S4\)|S,\)|OQ)\b', '', text)
    text = re.sub(r'[«»""]', '', text)
    
    # Correções comuns
    corrections = {
        'partcpar': 'participar',
        'atvdades': 'atividades',
        'patruha': 'patrulha',
        'construiruir': 'construir',
        'cansertados': 'consertados',
        'Escotsmo': 'Escotismo',
        'escateira': 'escoteira',
    }
    
    for wrong, correct in corrections.items():
        text = re.sub(wrong, correct, text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text

def identify_areas(text, level):
    """Identifica e processa áreas de desenvolvimento"""
    # Definir quantidade esperada por nível
    ITENS_ESPERADOS = {
        "Pista/Trilha": 108,
        "Rumo/Travessia": 113
    }
    
    areas_raw = {
        "Físico": [],
        "Intelectual": [],
        "Caráter": [],
        "Afetivo": [],
        "Social": [],
        "Espiritual": []
    }
    
    # Dividir por áreas
    partes = re.split(r'Desenvolvimento\s+(Físico|Intelectual|do\s+Caráter|Afetivo|Social|Espiritual)', 
                      text, flags=re.IGNORECASE)
    
    area_map = {
        'Físico': 'Físico',
        'Intelectual': 'Intelectual',
        'do Caráter': 'Caráter',
        'Afetivo': 'Afetivo',
        'Social': 'Social',
        'Espiritual': 'Espiritual'
    }
    
    current_area = None
    for i, parte in enumerate(partes):
        parte_clean = parte.strip()
        
        if parte_clean in area_map:
            current_area = area_map[parte_clean]
            continue
        
        if current_area and len(parte_clean) > 20:
            areas_raw[current_area].append(parte_clean)
    
    # Processar cada área E REMOVER DUPLICATAS
    areas = {}
    itens_processados = set()
    
    for area_nome, textos in areas_raw.items():
        texto_completo = ' '.join(textos)
        conc, pend = processar_area(texto_completo, itens_processados)
        areas[area_nome] = {
            "concluidas": conc,
            "pendentes": pend
        }
    
    # Validação
    total_detectado = len(itens_processados)
    esperado = ITENS_ESPERADOS.get(level, 108)
    
    validacao = {
        "esperado": esperado,
        "detectado": total_detectado,
        "diferenca": total_detectado - esperado,
        "percentual": (total_detectado / esperado * 100) if esperado > 0 else 0
    }
    
    return areas, validacao

def processar_area(texto_area, itens_processados):
    """Processa itens de uma área, evitando duplicatas"""
    concluidas = []
    pendentes = []
    
    itens = re.split(r'(?=\b\d{1,3}\s*[-\.\)])', texto_area)
    
    for item_text in itens:
        item_text = item_text.strip()
        if not item_text or len(item_text) < 10:
            continue
        
        num_match = re.match(r'(\d{1,3})\s*[-\.\)]?\s*(.+)', item_text, re.DOTALL)
        if not num_match:
            continue
        
        num = int(num_match.group(1))
        
        # ANTI-DUPLICATA: Pular se já foi processado
        if num in itens_processados:
            continue
        
        itens_processados.add(num)
        
        descricao = num_match.group(2).strip()
        
        date_match = re.search(r'\b(\d{1,2}/\d{1,2}/\d{4})\b', descricao)
        
        descricao_limpa = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', '', descricao)
        descricao_limpa = re.sub(r'\s+', ' ', descricao_limpa).strip()
        
        if len(descricao_limpa) > 300:
            descricao_limpa = descricao_limpa[:297] + '...'
        
        if date_match:
            data = date_match.group(1)
            concluidas.append((num, descricao_limpa, data))
        else:
            pendentes.append((num, descricao_limpa))
    
    return concluidas, pendentes

def generate_excel(areas, scout_name, level):
    """Gera planilha Excel completa"""
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
    ws_resumo[f'B{row}'].font = Font(bold=True, size=12, color="00B050" if percentual >= 50 else "FF0000")
    
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
    ws_area.column_dimensions['C'].width = 15
    
    linha = 1
    for area_nome in areas:
        ws_area.merge_cells(f'A{linha}:C{linha}')
        cell = ws_area[f'A{linha}']
        cell.value = f"{emojis[area_nome]} {area_nome.upper()}"
        cell.fill = area_fill
        cell.font = Font(bold=True, color="FFFFFF", size=12)
        cell.alignment = Alignment(horizontal='center')
        linha += 1
        
        if areas[area_nome]["concluidas"]:
            ws_area[f'A{linha}'] = "#"
            ws_area[f'A{linha}'].fill = verde
            ws_area[f'A{linha}'].font = bold_font
            ws_area[f'B{linha}'] = "✅ CONCLUÍDAS"
            ws_area[f'B{linha}'].fill = verde
            ws_area[f'B{linha}'].font = bold_font
            ws_area[f'C{linha}'] = "Data"
            ws_area[f'C{linha}'].fill = verde
            ws_area[f'C{linha}'].font = bold_font
            linha += 1
            
            for num, desc, data in areas[area_nome]["concluidas"]:
                ws_area.cell(row=linha, column=1, value=num).fill = verde
                ws_area.cell(row=linha, column=2, value=desc).fill = verde
                ws_area.cell(row=linha, column=3, value=data).fill = verde
                linha += 1
        
        if areas[area_nome]["pendentes"]:
            ws_area[f'A{linha}'] = "#"
            ws_area[f'A{linha}'].fill = amarelo
            ws_area[f'A{linha}'].font = bold_font
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
    ws_det.column_dimensions['E'].width = 15
    
    headers_det = ['#', 'Área', 'Descrição', 'Status', 'Data']
    for col, header in enumerate(headers_det, 1):
        cell = ws_det.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border
    
    linha = 2
    for area_nome in areas:
        for num, desc, data in areas[area_nome]["concluidas"]:
            ws_det.cell(row=linha, column=1, value=num).fill = verde
            ws_det.cell(row=linha, column=2, value=area_nome).fill = verde
            ws_det.cell(row=linha, column=3, value=desc).fill = verde
            ws_det.cell(row=linha, column=4, value="✅").fill = verde
            ws_det.cell(row=linha, column=5, value=data).fill = verde
            linha += 1
        
        for num, desc in areas[area_nome]["pendentes"]:
            ws_det.cell(row=linha, column=1, value=num).fill = amarelo
            ws_det.cell(row=linha, column=2, value=area_nome).fill = amarelo
            ws_det.cell(row=linha, column=3, value=desc).fill = amarelo
            ws_det.cell(row=linha, column=4, value="⏳").fill = amarelo
            ws_det.cell(row=linha, column=5, value="").fill = amarelo
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
            
            st.info("📸 Extraindo texto (OCR otimizado)...")
            text = extract_text_from_image(image)
            progress.progress(33)
            
            with st.expander("📄 Ver texto extraído"):
                st.text_area("Texto detectado:", text, height=200)
            
            st.info("🔍 Processando áreas...")
            areas, validacao = identify_areas(text, level)
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
                'areas': areas,
                'validacao': validacao
            }
            st.session_state.filename = filename

if st.session_state.processed:
    st.markdown("---")
    st.markdown("## 🎉 Validação Concluída!")
    
    stats = st.session_state.stats
    validacao = stats.get('validacao', {})
    
    # Alerta de validação
    if validacao:
        esperado = validacao['esperado']
        detectado = validacao['detectado']
        diferenca = validacao['diferenca']
        
        if diferenca == 0:
            st.success(f"✅ Perfeito! {detectado} itens detectados (esperado: {esperado})")
        elif abs(diferenca) <= 2:
            st.warning(f"⚠️ Detectados {detectado} itens de {esperado} esperados (diferença: {diferenca:+d})")
        else:
            st.error(f"❌ Detectados {detectado} itens, mas esperado {esperado} (diferença: {diferenca:+d})")
    
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
                <p><b>✅:</b> {conc} | <b>⏳:</b> {pend}</p>
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
    <p>🏕️ <b>Scout Progress Validator</b> v3.0 FINAL</p>
    <p>Tesseract OCR + Processamento Avançado | Sempre Alerta! ⚜️</p>
</div>
""", unsafe_allow_html=True)
