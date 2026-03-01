# 🏕️ Scout Progress Validator v2.0

## ⚡ VERSÃO OTIMIZADA COM TESSERACT

Sistema Web de Validação de Progressões Escoteiras com OCR otimizado

---

## 🚀 MELHORIAS DESTA VERSÃO

### **Pré-processamento de Imagem:**
- ✅ Conversão para escala de cinza
- ✅ Aumento de contraste (CLAHE)
- ✅ Redução de ruído
- ✅ Binarização adaptativa
- ✅ Dilatação para conectar caracteres

### **Configuração Otimizada do Tesseract:**
- ✅ PSM 6 (bloco uniforme de texto)
- ✅ OEM 3 (melhor engine disponível)
- ✅ Idioma português configurado
- ✅ Pós-processamento de correções

### **Correções Automáticas:**
O sistema corrige automaticamente erros comuns do OCR:
- "partcpar" → "participar"
- "atvdades" → "atividades"
- "patruha" → "patrulha"
- "ogresstio" → "Progressão"
- E muitos outros...

### **Funcionalidades Extras:**
- ✅ Checkbox para ver imagem processada
- ✅ Expandir para ver texto extraído
- ✅ Debug facilitado
- ✅ Interface melhorada

---

## 📋 ARQUIVOS NECESSÁRIOS

São **3 arquivos** para fazer upload no GitHub:

1. **app.py** - Código principal
2. **requirements.txt** - Dependências Python
3. **packages.txt** - Tesseract e bibliotecas do sistema

---

## 🎯 COMO USAR

1. Faça upload da imagem de progressões
2. Digite o nome do jovem
3. Selecione o nível
4. (Opcional) Marque "Mostrar imagem processada" para ver o pré-processamento
5. Clique em "GERAR VALIDAÇÃO"
6. Confira o texto extraído no expander
7. Baixe a planilha!

---

## 🔧 TROUBLESHOOTING

### **OCR não está preciso?**

**1. Verifique a qualidade da imagem:**
- Use imagens com boa resolução (mín. 800x600)
- Evite fotos borradas
- Prefira screenshots ou PDFs digitalizados
- Boa iluminação (sem sombras)

**2. Use o preview:**
- Marque "Mostrar imagem processada"
- Veja se a imagem pré-processada está legível
- Se estiver muito escura/clara, ajuste a foto original

**3. Confira o texto extraído:**
- Expanda "Ver texto extraído"
- Veja se o OCR leu corretamente
- Se houver muitos erros, tire outra foto

**4. Dicas para melhor resultado:**
- ✅ Screenshot direto (melhor opção)
- ✅ Foto com celular estável
- ✅ Boa iluminação natural
- ✅ Documento reto (sem inclinação)
- ❌ Evite reflexos
- ❌ Evite sombras
- ❌ Evite fotos tremidas

---

## 📊 PLANILHA GERADA

**Nome:** `Nome_Nivel_Data_Hora.xlsx`

**3 Abas:**
1. **Resumo Geral** - Estatísticas e % por área
2. **Por Área** - Itens separados por desenvolvimento
3. **Detalhamento** - Lista completa ordenada

---

## 🛠️ INSTALAÇÃO NO STREAMLIT CLOUD

### **Upload dos arquivos:**
1. Crie repositório no GitHub
2. Faça upload dos 3 arquivos:
   - app.py
   - requirements.txt
   - packages.txt
3. No Streamlit Cloud, faça deploy
4. Aguarde instalação (3-5 minutos)

### **Primeira execução:**
- Tesseract instala automaticamente
- Configuração do português
- Pode demorar 2-3 minutos
- Depois fica rápido!

---

## ⚙️ TECNOLOGIAS

- **Streamlit** - Interface web
- **Tesseract OCR** - Reconhecimento de texto
- **OpenCV** - Pré-processamento de imagem
- **pytesseract** - Wrapper Python para Tesseract
- **OpenPyXL** - Geração de Excel
- **NumPy** - Processamento de arrays

---

## 🎯 ÁREAS DE DESENVOLVIMENTO

- 💪 Físico
- 🧠 Intelectual
- ❤️ Caráter
- 🤝 Afetivo
- 👥 Social
- ✨ Espiritual

---

## 📄 LICENÇA

Livre para uso em grupos escoteiros!

**Sempre Alerta! ⚜️**
