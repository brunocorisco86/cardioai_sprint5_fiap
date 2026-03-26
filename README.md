# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

## 👨‍🎓 Integrantes:
- Bruno Henrique Nielsen Conter (RM560518)
- Fabio Santos Cardoso (RM560479)

## 👩‍🏫 Professores:
### Tutor(a)
- Lucas Gomes Moreira
### Coordenador(a)
- André Godoi

---

# CardioIA – Assistente Cardiológico Conversacional

Protótipo funcional de um assistente cardiológico baseado em linguagem natural que integra IBM Watson Assistant (NLP) a um backend FastAPI e a uma interface web estática. O objetivo é simular o primeiro atendimento em saúde, organizar informações clínicas e demonstrar boas práticas de colaboração entre áreas técnicas e de saúde.

## Visão Geral
- **Plataforma NLP**: IBM Watson Assistant (Assistant V2) com com abordagem baseada em Actions (equivalente a intents e dialog nodes), além de entities para estruturação dos dados clínicos modelados para triagem cardiológica inicial.
- **Backend**: FastAPI exposto via `uvicorn`, responsável por intermediar sessões, encaminhar mensagens ao Watson e servir arquivos estáticos.
- **Frontend**: Página HTML/CSS/JS simples que cria sessões, envia perguntas e exibe respostas em tempo real.
- **Entregáveis solicitados**: código fonte completo, export do assistente (JSON), relatório curto (1–2 páginas) e vídeo demonstrativo de até 3 minutos.

## Modelagem Conversacional

O assistente foi modelado utilizando a abordagem de Actions do Watson Assistant, que unifica os conceitos tradicionais de intents e dialog nodes em uma estrutura orientada a ações.

As principais ações implementadas foram:

- Saudação e início do atendimento
- Relatar sintoma cardiovascular
- Coleta de informações clínicas
- Avaliação de sinais de alerta
- Orientação inicial e resumo
- Dúvidas sobre exames e consulta
- Fallback (tratamento de exceções)

Além disso, foram consideradas entidades (entities) para estruturação de informações clínicas, como:

- Sintomas (dor no peito, falta de ar, palpitação)
- Intensidade (leve, moderada, intensa)
- Duração (minutos, horas, dias)
- Sintomas associados (suor frio, tontura, náusea)

## Fluxo Conversacional

O fluxo principal do assistente segue uma lógica de triagem inicial:

1. Saudação e contextualização do atendimento
2. Identificação do sintoma principal
3. Coleta estruturada de informações clínicas
4. Avaliação de sinais de alerta
5. Orientação inicial ao usuário

Esse fluxo permite organizar as informações de forma progressiva e compreensível, simulando um atendimento inicial em saúde.

## Limitações

- O assistente não realiza diagnóstico médico
- Não substitui avaliação profissional
- O fluxo é baseado em regras definidas (não adaptativo)
- Não há persistência de histórico
- A interpretação depende das frases de treinamento configuradas

## Arquitetura
1. O usuário acessa o portal na porta `8000` para teste local hospedado pelo fastapi.
2. Ao clicar em "Iniciar sessão", o frontend chama `POST /api/session`; o backend cria/recupera uma sessão no Watson Assistant e devolve um `client_id` persistido localmente.
3. Cada mensagem do usuário envia um `POST /api/chat` contendo `client_id` e texto. O backend encaminha o texto ao Watson e retorna a lista de respostas.
4. Em `POST /api/reset`, a sessão do Watson é encerrada e o frontend limpa o histórico, permitindo recomeçar o atendimento.
5. O backend mantém um cache em memória (`watson_sessions`) mapeando `client_id` → `session_id` do Watson para reutilizar sessões enquanto a conversa estiver ativa.

```
Frontend (HTML/CSS/JS)
        ↕  HTTP (fetch)
FastAPI (app.py) ↔ IBM Watson Assistant (AssistantV2)
```

## Requisitos
- Python 3.11+
- Conta IBM Cloud com Watson Assistant V2 provisionado
- Dependências listadas em `requirements.txt`

```txt
fastapi==0.115.0
uvicorn==0.30.6
python-dotenv==1.0.1
ibm-watson==8.1.0
```

## Configuração do Watson Assistant
1. Crie o arquivo `.env` na raiz do projeto com as credenciais (nunca versione chaves reais):
   ```env
   WATSON_API_KEY=coloque_sua_chave_aqui
   WATSON_URL=https://api.us-south.assistant.watson.cloud.ibm.com
   WATSON_ASSISTANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   WATSON_VERSION=2024-08-25
   PORT=8000
   ```

## Como executar o backend
1. Crie e ative um ambiente virtual (opcional, porém recomendado).
2. Instale as dependências: `pip install -r requirements.txt`.
3. Verifique se `.env` contém as variáveis obrigatórias (`WATSON_API_KEY`, `WATSON_URL`, `WATSON_ASSISTANT_ID`).
4. Inicie o servidor: `uvicorn app:app --reload --host 0.0.0.0 --port 8000`.

## Interface Web
- Localizada em `frontend/` e servida automaticamente como estático em `/static`.
- `frontend/script.js` controla a criação de sessão, envio de mensagens (fetch API) e reset da conversa.
- `API_BASE_URL` pode ser ajustada caso o frontend seja hospedado separadamente (ex.: apontar para um backend remoto).
- Layout responsivo básico descrito em `frontend/style.css`.

## Endpoints principais
| Método | Rota         | Descrição                                                                 |
| ------ | ------------ | ------------------------------------------------------------------------- |
| GET    | `/health`    | Diagnóstico rápido do backend.                                            |
| POST   | `/api/session` | Cria ou recupera uma sessão no Watson Assistant e retorna `client_id`.    |
| POST   | `/api/chat`  | Encaminha a mensagem do usuário e devolve as respostas do Watson.          |
| POST   | `/api/reset` | Encerra a sessão associada ao `client_id` informado.                       |

## Estrutura do projeto
```
cardioia/
├── app.py               # Backend FastAPI + integração Watson
├── requirements.txt     # Dependências Python
├── watson.txt           # Referência local com URLs/IDs do serviço
├── frontend/
│   ├── index.html       # UI principal
│   ├── script.js        # Lógica de sessão e chat
│   └── style.css        # Estilos da interface
└── README.md            # Você está aqui
```

## Entregáveis
1. **Código fonte + README** (este repositório).
2. **Export JSON do Watson Assistant** contendo actions/intents foi exportado para a pasta `docs` com o nome `cardioai-action.json`.
3. **Relatório e um resumo (PDF)** criados dentro da pasta `docs`: público-alvo, actions modeladas, fluxos principais, limitações e próximos passos.
4. **Vídeo (≤ 3 minutos)** demonstrando fluxo completo (início de sessão → perguntas → recomendações → reset).
```
URL: 
```
## Trabalho em Equipe

O desenvolvimento foi realizado de forma colaborativa, com divisão de responsabilidades entre os integrantes:

- Modelagem do assistente (Watson Assistant)
- Desenvolvimento backend (FastAPI)
- Desenvolvimento frontend (interface web)
- Testes e validação
- Documentação e apresentação
