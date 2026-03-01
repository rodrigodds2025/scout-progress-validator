# 🏕️ Scout Progress Validator

Sistema Web de Validação de Progressões Escoteiras

## 🚀 Acesse o App

Link do app funcionando: (será gerado após deploy)

## 📋 Funcionalidades

- ✅ Upload de imagens de progressões
- ✅ OCR automático (EasyOCR)
- ✅ Separação por 6 áreas de desenvolvimento
- ✅ Identificação de concluídas vs pendentes
- ✅ Planilha Excel com 3 abas profissionais
- ✅ Interface moderna e responsiva

## 🎯 Como Usar

1. Faça upload da imagem de progressões
2. Digite o nome do jovem escoteiro
3. Selecione o nível (Pista/Trilha ou Rumo/Travessia)
4. Clique em "GERAR VALIDAÇÃO"
5. Aguarde o processamento (5-10 min na primeira vez)
6. Baixe a planilha Excel gerada!

## 📊 Planilha Gerada

**Nome do arquivo:** `Nome_Nivel_Data_Hora.xlsx`

**3 Abas:**
1. **Resumo Geral** - Estatísticas completas
2. **Por Área** - Separado por desenvolvimento
3. **Detalhamento** - Lista completa ordenada

## 🛠️ Tecnologias

- Python 3.9+
- Streamlit (interface web)
- EasyOCR (reconhecimento de texto)
- OpenPyXL (geração de Excel)
- Pillow (processamento de imagens)

## ⚙️ Instalação Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/scout-validator.git

# Entre na pasta
cd scout-validator

# Instale as dependências
pip install -r requirements.txt

# Execute o app
streamlit run app.py
```

## 📱 Deploy no Streamlit Cloud

Este app está configurado para deploy automático no Streamlit Cloud.

**Primeira execução:**
- EasyOCR baixa modelos de IA (~100MB)
- Pode demorar 5-10 minutos
- Depois fica no cache e é rápido!

## 🏕️ Áreas de Desenvolvimento

O sistema identifica automaticamente:
- 💪 Físico
- 🧠 Intelectual  
- ❤️ Caráter
- 🤝 Afetivo
- 👥 Social
- ✨ Espiritual

## 📄 Licença

Livre para uso em grupos escoteiros!

---

**Sempre Alerta! ⚜️**
