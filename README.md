# LES_LAB2

# Laboratório de Experimentação de Software

## Integrantes:
- Gabriel Faria  
- João Victor Salim  
- Lucas Garcia  
- Maísa Pires  
- Miguel Vieira  

---

## Descrição

Este repositório reúne o desenvolvimento completo do *Laboratório 02 - Análise de Qualidade em Repositórios Java* da disciplina *Laboratório de Experimentação de Software, ministrada pelo professor **João Paulo Carneiro Aramuni* no curso de *Engenharia de Software*.  

O objetivo principal é *analisar atributos de qualidade de repositórios escritos em Java* disponíveis no GitHub, correlacionando características de qualidade (como acoplamento, coesão e profundidade de herança) com aspectos do processo de desenvolvimento (popularidade, tamanho, atividade e maturidade).  

A análise foi realizada utilizando métricas obtidas pela ferramenta *CK* e dados coletados via *GitHub API*.  

---

## Questões de Pesquisa (RQs)

- *RQ01:* Qual a relação entre a popularidade dos repositórios e as suas características de qualidade?  
- *RQ02:* Qual a relação entre a maturidade dos repositórios e as suas características de qualidade?  
- *RQ03:* Qual a relação entre a atividade dos repositórios e as suas características de qualidade?  
- *RQ04:* Qual a relação entre o tamanho dos repositórios e as suas características de qualidade?  

---

## Etapas do Trabalho

### Lab02S01 – Seleção e Coleta Inicial  
- Seleção dos *1.000 repositórios Java mais populares* do GitHub.  
- Implementação de scripts para *automação de clone* e *coleta de métricas com CK*.  
- Armazenamento dos resultados em formato .csv.  

### Lab02S02 – Coleta Completa e Hipóteses  
- Coleta dos dados para todos os repositórios selecionados.  
- Elaboração das *hipóteses informais* para cada questão de pesquisa.  
- Organização dos dados em planilhas consolidadas.  

### Lab02S03 – Análise, Visualização e Relatório Final  
- Análise estatística das métricas obtidas (média, mediana, desvio padrão).  
- Geração de gráficos para visualização dos resultados.  
- Discussão dos resultados em comparação com as hipóteses.  
- Relatório final e apresentação dos achados em sala.  

(Bônus: correlação entre as métricas com gráficos adicionais e testes estatísticos, como Spearman ou Pearson).  

---

## Estrutura do Repositório

bash
├── data/        # Dados coletados (CSVs gerados pela ferramenta CK e APIs do GitHub)
├── results/     # Resultados das análises e gráficos gerados
├── scripts/     # Scripts utilizados para automação, coleta e análise
├── Relatorio.md # Relatório final com metodologia, resultados e discussão
├── Slide.pdf    # Apresentação utilizada na entrega
└── README.md    # Este arquivo

---

## Requisitos

- python 3.10+  
- java 8+  ]
- maven  
- token do GitHub no arquivo `secrets/.env`  

---

## Passos

1. Exportar variáveis do `.env`:  

   bash
   export $(cat secrets/.env | xargs)
