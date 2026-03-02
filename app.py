import streamlit as st
import pytesseract
from PIL import Image
import cv2
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
import io
import re

# Dados das progressões inline
PROGRESSOES_PISTA_TRILHA = {
    1: {"area": "Físico", "desc": "Participar de pelo menos cinco atividades de patrulha ao ar livre"},
    2: {"area": "Físico", "desc": "Conhecer e aplicar normas de limpeza no tratamento de alimentos"},
    3: {"area": "Físico", "desc": "Aferir seu passo duplo e conhecer medidas do corpo"},
    4: {"area": "Físico", "desc": "Conhecer elementos da Caixa de Primeiros Socorros"},
    5: {"area": "Físico", "desc": "Conhecer ações iniciais em acidentes e cuidar de ferimentos"},
    6: {"area": "Físico", "desc": "Aplicar medidas de segurança nas atividades"},
    7: {"area": "Físico", "desc": "Prevenir males da exposição ao sol"},
    8: {"area": "Físico", "desc": "Manter hábitos de higiene e cuidado com uniforme"},
    9: {"area": "Físico", "desc": "Classificar lixo e tratar resíduos"},
    10: {"area": "Físico", "desc": "Participar da manutenção do canto de patrulha"},
    11: {"area": "Físico", "desc": "Montar mochila para acampamento de 3 dias"},
    12: {"area": "Físico", "desc": "Montar cardápio com refeições equilibradas"},
    13: {"area": "Físico", "desc": "Colaborar na elaboração de alimentos"},
    14: {"area": "Físico", "desc": "Montar solução para purificação de água"},
    15: {"area": "Físico", "desc": "Utilizar diversos tipos de fogos"},
    16: {"area": "Físico", "desc": "Organizar tempo com agenda"},
    17: {"area": "Físico", "desc": "Realizar tarefas escolares no prazo"},
    18: {"area": "Físico", "desc": "Frequentar atividades da patrulha"},
    19: {"area": "Físico", "desc": "Realizar atividade física regularmente"},
    20: {"area": "Físico", "desc": "Participar de jogos respeitando regras"},
    21: {"area": "Intelectual", "desc": "Traçar e seguir sinais de pista"},
    22: {"area": "Intelectual", "desc": "Utilizar mapa e bússola"},
    23: {"area": "Intelectual", "desc": "Aplicar técnicas de tocaia"},
    24: {"area": "Intelectual", "desc": "Explorar comunidade identificando problemas"},
    25: {"area": "Intelectual", "desc": "Estimar altura e distâncias"},
    26: {"area": "Intelectual", "desc": "Ler livro e apresentar resumo"},
    27: {"area": "Intelectual", "desc": "Utilizar técnica de previsão do tempo"},
    28: {"area": "Intelectual", "desc": "Participar de Jogos Democráticos"},
    29: {"area": "Intelectual", "desc": "Participar do Conselho de Patrulha"},
    30: {"area": "Intelectual", "desc": "Participar do planejamento de excursão"},
    31: {"area": "Intelectual", "desc": "Avaliar atividades com patrulha"},
    32: {"area": "Intelectual", "desc": "Utilizar especialidades conquistadas"},
    33: {"area": "Intelectual", "desc": "Ajudar escoteiro a conquistar especialidade"},
    34: {"area": "Intelectual", "desc": "Participar de fogo de conselho"},
    35: {"area": "Intelectual", "desc": "Construir instrumento musical"},
    36: {"area": "Intelectual", "desc": "Conhecer e cantar canções tradicionais"},
    37: {"area": "Intelectual", "desc": "Ler e escrever em código secreto"},
    38: {"area": "Intelectual", "desc": "Utilizar rádio comunicador"},
    39: {"area": "Intelectual", "desc": "Montar blog ou projeto de comunicação"},
    40: {"area": "Intelectual", "desc": "Participar da construção de pioneirias"},
    41: {"area": "Intelectual", "desc": "Utilizar ferramentas de patrulha"},
    42: {"area": "Intelectual", "desc": "Participar da construção de Fogão Suspenso"},
    43: {"area": "Caráter", "desc": "Propor objetivos para melhorar vida"},
    44: {"area": "Caráter", "desc": "Participar da avaliação de progressão"},
    45: {"area": "Caráter", "desc": "Avaliar desempenho nos cargos"},
    46: {"area": "Caráter", "desc": "Explicar Lei e Promessa Escoteira"},
    47: {"area": "Caráter", "desc": "Participar de cerimônias cívicas"},
    48: {"area": "Caráter", "desc": "Explicar o que é ser leal"},
    49: {"area": "Caráter", "desc": "Aplicar conceito de lealdade"},
    50: {"area": "Caráter", "desc": "Participar como animador"},
    51: {"area": "Caráter", "desc": "Conhecer histórias de superação"},
    52: {"area": "Caráter", "desc": "Respeitar decisões do Conselho"},
    53: {"area": "Caráter", "desc": "Melhorar organização do Conselho"},
    54: {"area": "Caráter", "desc": "Participar da eleição do Monitor"},
    55: {"area": "Afetivo", "desc": "Pesquisar malefícios de drogas"},
    56: {"area": "Afetivo", "desc": "Contribuir com Livro de Patrulha"},
    57: {"area": "Afetivo", "desc": "Participar de turno de ronda"},
    58: {"area": "Afetivo", "desc": "Registrar momentos pessoais"},
    59: {"area": "Afetivo", "desc": "Participar de debate sobre filme"},
    60: {"area": "Afetivo", "desc": "Participar de Assembleias"},
    61: {"area": "Afetivo", "desc": "Propor temas para debate"},
    62: {"area": "Afetivo", "desc": "Avaliar acampamento"},
    63: {"area": "Afetivo", "desc": "Auxiliar novo integrante"},
    64: {"area": "Afetivo", "desc": "Convidar patrulha para reunião"},
    65: {"area": "Afetivo", "desc": "Participar de atividades de igualdade"},
    66: {"area": "Afetivo", "desc": "Compartilhar tarefas domésticas"},
    67: {"area": "Afetivo", "desc": "Investigar sobre mulheres na história"},
    68: {"area": "Afetivo", "desc": "Participar de cerimônia com pais"},
    69: {"area": "Afetivo", "desc": "Participar de atividade com família"},
    70: {"area": "Afetivo", "desc": "Solicitar ajuda de familiares"},
    71: {"area": "Social", "desc": "Investigar defensores de direitos humanos"},
    72: {"area": "Social", "desc": "Participar de atividades sobre Direitos Humanos"},
    74: {"area": "Social", "desc": "Colaborar para definir metas"},
    75: {"area": "Social", "desc": "Assumir cargo na patrulha"},
    76: {"area": "Social", "desc": "Participar das decisões do Conselho"},
    77: {"area": "Social", "desc": "Participar de Assembleia de Tropa"},
    78: {"area": "Social", "desc": "Estudar organização do Escotismo"},
    79: {"area": "Social", "desc": "Conhecer estrutura do Grupo"},
    80: {"area": "Social", "desc": "Realizar boas ações"},
    81: {"area": "Social", "desc": "Participar de MUTCOM"},
    82: {"area": "Social", "desc": "Fazer croqui da área de residência"},
    83: {"area": "Social", "desc": "Conhecer serviços públicos"},
    84: {"area": "Social", "desc": "Participar de comemoração regional"},
    85: {"area": "Social", "desc": "Participar de Jantar Festivo"},
    86: {"area": "Social", "desc": "Pesquisar jogos típicos"},
    87: {"area": "Social", "desc": "Participar de evento cívico"},
    88: {"area": "Social", "desc": "Explicar significado da Flor de Lis"},
    89: {"area": "Social", "desc": "Conhecer história do Grupo"},
    90: {"area": "Social", "desc": "Participar de atividade distrital"},
    91: {"area": "Social", "desc": "Participar de JOTI ou JOTA"},
    92: {"area": "Social", "desc": "Participar de atividade pela paz"},
    93: {"area": "Social", "desc": "Pesquisar sobre defensores da paz"},
    94: {"area": "Social", "desc": "Participar de projeto ambiental"},
    95: {"area": "Social", "desc": "Realizar levantamento de pegadas"},
    96: {"area": "Social", "desc": "Participar de excursão ecológica"},
    97: {"area": "Espiritual", "desc": "Fazer orações rotineiras"},
    98: {"area": "Espiritual", "desc": "Participar de celebrações religiosas"},
    99: {"area": "Espiritual", "desc": "Realizar reflexões em acampamentos"},
    100: {"area": "Espiritual", "desc": "Participar de serviço comunitário religioso"},
    101: {"area": "Espiritual", "desc": "Aplicar ensinamentos religiosos"},
    102: {"area": "Espiritual", "desc": "Apresentar relato de ensinamentos"},
    103: {"area": "Espiritual", "desc": "Participar da construção de espaço de reflexão"},
    104: {"area": "Espiritual", "desc": "Orar com oração da Tropa"},
    105: {"area": "Espiritual", "desc": "Praticar a oração"},
    106: {"area": "Espiritual", "desc": "Organizar livreto de orações"},
    107: {"area": "Espiritual", "desc": "Conhecer confissões religiosas dos amigos"},
    108: {"area": "Espiritual", "desc": "Pesquisar sobre confissão religiosa diferente"}
}

EMOJIS_AREAS = {
    "Físico": "💪",
    "Intelectual": "🧠",
    "Caráter": "❤️",
    "Afetivo": "🤝",
    "Social": "👥",
    "Espiritual": "✨"
}

# Configuração
st.set_page_config(page_title="Scout Progress Validator", page_icon="🏕️", layout="wide")

st.markdown("""
<style>
    .main {padding: 2rem;}
    .stButton>button {width: 100%; background-color: #4472C4; color: white; 
                      font-weight: bold; padding: 0.75rem; border-radius: 0.5rem;}
    .stButton>button:hover {background-color: #2952A3;}
    h1 {color: #4472C4; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🏕️ Scout Progress Validator v4.0")
st.markdown("### Sistema de Validação - 2 Modos de OCR")
st.markdown("---")

# Session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None
if 'stats' not in st.session_state:
    st.session_state.stats = None

# OCR Simplificado
def ocr_simplificado(image):
    """Detecta apenas números e checkmarks"""
    img_gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, img_thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
    
    text = pytesseract.image_to_string(img_thresh, config='--psm 6')
    
    # Detectar concluídas (com check)
    concluidas_matches = re.findall(r'[✓✔☑✅🗹]\s*(\d+)', text)
    concluidas = [int(x) for x in concluidas_matches if 1 <= int(x) <= 108]
    
    # Todos os números
    todos_matches = re.findall(r'\b(\d{1,3})\b', text)
    todos = [int(x) for x in todos_matches if 1 <= int(x) <= 108]
    
    # Pendentes
    pendentes = sorted(set(todos) - set(concluidas))
    concluidas = sorted(set(concluidas))
    
    # Datas
    datas = {}
    for match in re.finditer(r'(\d+)[^\d]*(\d{2}/\d{2}/\d{4})', text):
        num, data = match.groups()
        if 1 <= int(num) <= 108:
            datas[int(num)] = data
    
    return {'concluidas': concluidas, 'pendentes': pendentes, 'datas': datas}

# Gerar planilha simplificada
def gerar_planilha_simplificada(concluidas, pendentes, scout_name, level, datas={}):
    wb = Workbook()
    ws = wb.active
    ws.title = "Progressões"
    
    verde = PatternFill(start_color="C6E0B4", end_color="C6E0B4", fill_type="solid")
    amarelo = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    bold_font = Font(bold=True)
    
    # Cabeçalho
    ws.merge_cells('A1:E1')
    ws['A1'] = f"📊 VALIDAÇÃO DE PROGRESSÃO - {scout_name}"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].fill = header_fill
    ws['A1'].font = header_font
    ws['A1'].alignment = Alignment(horizontal='center')
    
    ws['A3'] = f"Nível: {level}"
    ws['A3'].font = bold_font
    ws['A4'] = f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws['A4'].font = bold_font
    
    total = len(concluidas) + len(pendentes)
    ws['A6'] = f"Total: {total} itens"
    ws['A7'] = f"✅ Concluídas: {len(concluidas)}"
    ws['A7'].fill = verde
    ws['A8'] = f"⏳ Pendentes: {len(pendentes)}"
    ws['A8'].fill = amarelo
    ws['A9'] = f"📊 % Conclusão: {(len(concluidas)/total*100 if total>0 else 0):.1f}%"
    ws['A9'].font = bold_font
    
    # Tabela
    row = 11
    headers = ['#', 'Área', 'Descrição', 'Status', 'Data']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
    
    row += 1
    
    # Concluídas
    for num in concluidas:
        info = PROGRESSOES_PISTA_TRILHA.get(num, {"area": "?", "desc": "?"})
        ws.cell(row=row, column=1, value=num).fill = verde
        ws.cell(row=row, column=2, value=f"{EMOJIS_AREAS.get(info['area'], '')} {info['area']}").fill = verde
        ws.cell(row=row, column=3, value=info['desc']).fill = verde
        ws.cell(row=row, column=4, value="✅ Concluída").fill = verde
        ws.cell(row=row, column=5, value=datas.get(num, '')).fill = verde
        row += 1
    
    # Pendentes
    for num in pendentes:
        info = PROGRESSOES_PISTA_TRILHA.get(num, {"area": "?", "desc": "?"})
        ws.cell(row=row, column=1, value=num).fill = amarelo
        ws.cell(row=row, column=2, value=f"{EMOJIS_AREAS.get(info['area'], '')} {info['area']}").fill = amarelo
        ws.cell(row=row, column=3, value=info['desc']).fill = amarelo
        ws.cell(row=row, column=4, value="⏳ Pendente").fill = amarelo
        row += 1
    
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 70
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer, total, len(concluidas), len(pendentes)

# Interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Upload da Imagem")
    uploaded_file = st.file_uploader("Arraste ou clique para selecionar", type=['png', 'jpg', 'jpeg', 'webp'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagem carregada", use_column_width=True)

with col2:
    st.markdown("### ⚙️ Configurações")
    
    modo_ocr = st.radio(
        "🎯 Modo de OCR",
        options=["OCR Simplificado", "OCR Completo"],
        help="Simplificado: apenas números + check (rápido e preciso) | Completo: extrai texto completo"
    )
    
    scout_name = st.text_input("Nome do Jovem", placeholder="Ex: Gustavo Santos")
    level = st.radio("Nível", options=["Pista/Trilha", "Rumo/Travessia"])
    
    st.markdown("---")
    
    if st.button("🚀 PROCESSAR", disabled=not (uploaded_file and scout_name)):
        with st.spinner("⏳ Processando..."):
            
            if modo_ocr == "OCR Simplificado":
                st.info("🎯 Modo Simplificado: Detectando números e checks...")
                resultado = ocr_simplificado(image)
                
                with st.expander("🔍 Detecção OCR"):
                    st.write(f"✅ Concluídas ({len(resultado['concluidas'])}): {resultado['concluidas'][:20]}{'...' if len(resultado['concluidas']) > 20 else ''}")
                    st.write(f"⏳ Pendentes ({len(resultado['pendentes'])}): {resultado['pendentes'][:20]}{'...' if len(resultado['pendentes']) > 20 else ''}")
                
                st.info("📊 Gerando planilha...")
                excel_buffer, total, conc, pend = gerar_planilha_simplificada(
                    resultado['concluidas'],
                    resultado['pendentes'],
                    scout_name,
                    level,
                    resultado['datas']
                )
                
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{scout_name.replace(' ', '_')}_Simples_{timestamp}.xlsx"
                
                st.session_state.processed = True
                st.session_state.excel_data = excel_buffer
                st.session_state.stats = {
                    'modo': 'simplificado',
                    'total': total,
                    'concluidas': conc,
                    'pendentes': pend
                }
                st.session_state.filename = filename
                
            else:
                st.info("Modo completo ainda não implementado nesta versão. Use o modo simplificado!")

# Resultados
if st.session_state.processed:
    st.markdown("---")
    st.success("🎉 Processamento Concluído!")
    
    stats = st.session_state.stats
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total", stats['total'])
    with col2:
        st.metric("✅ Concluídas", stats['concluidas'])
    with col3:
        st.metric("⏳ Pendentes", stats['pendentes'])
    with col4:
        perc = (stats['concluidas']/stats['total']*100) if stats['total']>0 else 0
        st.metric("📈 %", f"{perc:.1f}%")
    
    st.download_button(
        label="⬇️ BAIXAR PLANILHA",
        data=st.session_state.excel_data,
        file_name=st.session_state.filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    if st.button("🔄 Nova Validação"):
        st.session_state.processed = False
        st.rerun()

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏕️ <b>Scout Progress Validator</b> v4.0</p>
    <p>OCR Simplificado + OCR Completo | Sempre Alerta! ⚜️</p>
</div>
""", unsafe_allow_html=True)
