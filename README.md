# doctoralia-scraper-brasil

🕷️ Web scraper para coletar dados de profissionais de saúde do Doctoralia Brasil. Extrai informações como nome, cidade, especialização, avaliações, preços e telemedicina usando Scrapy. Ideal para análise de dados, pesquisa de mercado e criação de datasets.

## Sobre o Doctoralia

O Doctoralia é uma plataforma online global que permite aos usuários buscar, ler avaliações e agendar consultas com profissionais de saúde. É altamente popular no Brasil.

## Motivação

Escolher um profissional de saúde é uma decisão importante e pode ser desafiador encontrar a pessoa certa para você.

Este scraper foi criado para gerar um dataset de todos os profissionais de saúde no 🇧🇷 Brasil, incluindo preço, localização, especialização e número de avaliações, ajudando a encontrar os melhores profissionais.

## Requisitos

- Python 3.8+
- [Scrapy](https://scrapy.org)
- [tqdm](https://tqdm.github.io)
- [Pandas](https://pandas.pydata.org) (opcional, para análise de dados)

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seabra27/doctoralia-scraper-brasil.git
cd doctoralia-scraper-brasil
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### 1. Executar o Scraper

Execute o scraper para coletar os dados:

```bash
cd scrapy-project
scrapy crawl DoctoraliaScraper -o ../output.jl
```

Ou a partir do diretório raiz:

```bash
scrapy runspider scrapy-project/doctoralia/spiders/doctoralia.py -o output.jl
```

Isso gera um arquivo JSON Lines (`output.jl`) com todos os dados coletados.

### 2. Converter para CSV

Para converter o arquivo JSON Lines para CSV com dados tratados e normalizados:

```bash
python convert_to_csv.py output.jl doctoralia_data.csv
```

O script `convert_to_csv.py` realiza as seguintes operações:
- ✅ Decodifica corretamente caracteres Unicode escapados (ex: `\u00e3` → `ã`)
- ✅ Remove espaços extras no início, meio e fim dos textos
- ✅ Normaliza nomes de profissionais (corrige títulos truncados como `ra.` → `Dra.`)
- ✅ Converte tipos de dados apropriados (inteiros, floats)
- ✅ Salva em formato CSV compatível com Excel (UTF-8-SIG)

### 3. Acessar os Dados

#### Usando Pandas (Python):

```python
import pandas as pd

# Ler arquivo JSON Lines
df = pd.read_json('./output.jl', lines=True)

# Ou ler arquivo CSV
df = pd.read_csv('./doctoralia_data.csv', encoding='utf-8-sig')

# Ver dados
print(df.head())
print(f"Total de registros: {len(df):,}")
```

#### Usando Excel ou outras ferramentas:

O arquivo `doctoralia_data.csv` pode ser aberto diretamente no Excel, Google Sheets ou qualquer ferramenta de análise de dados.

## Atributos dos Dados

| Atributo            | Descrição                                                                         | Tipo de Dado |
| ------------------- | --------------------------------------------------------------------------------- | ------------ |
| doctor_id           | Número de identificação do profissional fornecido pelo Doctoralia                 | int          |
| name1               | Nome completo do profissional com título (ex: 'Dr. João Silva')                  | string       |
| name2               | Nome completo do profissional sem título                                          | string       |
| city1               | Nome da cidade com acentuação correta (ex: São Paulo)                             | string       |
| city2               | Nome da cidade em minúsculas e com hífens (ex: sao-paulo)                        | string       |
| region              | Nome da região incluindo sigla do estado (ex: sao-paulo-sp)                       | string       |
| specialization      | Especialização principal do profissional (ex: cardiologista)                      | string       |
| reviews             | Quantidade de avaliações/opiniões                                                 | float        |
| newest_review_date  | Data da avaliação mais recente postada                                            | string (ISO) |
| telemedicine        | Se o profissional oferece atendimento remoto (1 = Sim, 0 = Não)                  | int          |
| price               | Preço mais comum de todos os serviços oferecidos pelo profissional                | string       |
| url                 | URL da página do profissional no Doctoralia                                       | string       |
| fetch_time          | Data e hora em que os dados foram coletados                                       | string (ISO) |

## Exemplo de Dados

| doctor_id | name1                     | city1         | city2         | region            | specialization           | reviews | newest_review_date      | telemedicine | price | url                                                   | fetch_time          |
| --------- | ------------------------- | ------------- | ------------- | ----------------- | ------------------------ | ------- | ----------------------- | ------------ | ----- | ----------------------------------------------------- | ------------------- |
| 357421    | Marília Rocha             | Porto Velho   | porto-velho   | rondonia-ro       | alergista-pediatrico     | 244     | 2022-10-23T15:00:55-03:00 | 0            |       | http://www.doctoralia.com.br/marilia-rocha            | 2022-10-28 12:02:04 |
| 621416    | Juliana Murata            | Curitiba      | curitiba      | parana-pr         | pneumologista-pediatrico | 324     | 2022-10-27T17:40:27-03:00 | 0            | 300   | http://www.doctoralia.com.br/juliana-murata           | 2022-10-28 12:02:04 |
| 691614    | Queise Cettolin           | Salvador      | salvador      | bahia-ba          | cirurgiao-vascular       | 46      | 2022-10-21T18:06:29-03:00 | 0            | 250   | http://www.doctoralia.com.br/queise-cettolin          | 2022-10-28 12:02:46 |
| 43986     | Letícia Scolfaro Celegao  | Campinas      | campinas      | sao-paulo-sp      | angiologista             | 194     | 2022-10-27T23:43:16-03:00 | 1            | 650   | http://www.doctoralia.com.br/leticia-scolfaro-celegao | 2022-10-28 12:02:48 |
| 4828      | Priscilla Vogt            | Florianópolis | florianopolis | santa-catarina-sc | psicologo                | 46.0    | 2022-10-14T20:35:58-03:00 | 1            | 170   | http://www.doctoralia.com.br/priscilla-vogt           | 2022-10-27 23:28:43 |

## Dataset

Confira um dataset de 165k médicos e profissionais de saúde no Brasil publicado no [Kaggle.com](https://www.kaggle.com/datasets/miguelcorraljr/doctoralia-brasil).

## Funcionalidades

- ✅ Coleta recursiva de todos os profissionais de saúde do Doctoralia Brasil
- ✅ Extração de dados estruturados (nome, cidade, especialização, avaliações, preços, etc.)
- ✅ Conversão automática para CSV com tratamento de dados
- ✅ Normalização de caracteres especiais e acentuação
- ✅ Limpeza e padronização de nomes e títulos
- ✅ Respeita robots.txt e implementa throttling automático

## Estrutura do Projeto

```
doctoralia-scraper-brasil/
├── scrapy-project/
│   ├── doctoralia/
│   │   ├── spiders/
│   │   │   └── doctoralia.py      # Spider principal
│   │   ├── items.py
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   └── settings.py
│   └── scrapy.cfg
├── convert_to_csv.py               # Script de conversão JSON → CSV
├── requirements.txt
├── README.md
└── LICENSE
```

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](./LICENSE) para mais informações.

## Autor Original

**Miguel Corral Jr.**  
Email: corraljrmiguel@gmail.com  
LinkedIn: [https://www.linkedin.com/in/iMiguel](https://www.linkedin.com/in/iMiguel)  
GitHub: [https://github.com/corralm](https://github.com/corralm)

## Agradecimentos

Este projeto foi originalmente criado por Miguel Corral Jr. e adaptado para melhorias adicionais.
