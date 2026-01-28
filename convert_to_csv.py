#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para converter output.jl (JSON Lines) para CSV com tratamento de dados.

Funcionalidades:
- Decodifica corretamente caracteres Unicode escapados
- Remove espaços extras no início, meio e fim dos textos
- Normaliza nomes e cidades
- Converte tipos de dados apropriados
- Salva em CSV com encoding UTF-8-SIG (compatível com Excel)
"""

import json
import pandas as pd
import re
from typing import Any, Dict, List
from tqdm import tqdm


def clean_text(text: Any) -> str:
    """
    Limpa e normaliza texto:
    - Remove espaços extras no início e fim
    - Normaliza múltiplos espaços para um único espaço
    - Retorna string vazia se o valor for None ou vazio
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Remove espaços no início e fim
    text = text.strip()
    
    # Normaliza múltiplos espaços para um único espaço
    text = re.sub(r'\s+', ' ', text)
    
    return text


def normalize_name(name: str) -> str:
    """
    Normaliza nomes de profissionais:
    - Remove espaços extras
    - Corrige títulos truncados (ra. -> Dra., rof. -> Prof., etc.)
    - Capitaliza corretamente títulos (Dr., Dra., Prof., etc.)
    - Mantém capitalização apropriada
    """
    name = clean_text(name)
    
    if not name:
        return ""
    
    # Correções para títulos truncados ou mal formatados
    corrections = {
        'ra.': 'Dra.',
        'rof.': 'Prof.',
        'rofª.': 'Profª.',
        'r.': 'Dr.',
        'dra.': 'Dra.',
        'dr.': 'Dr.',
        'prof.': 'Prof.',
        'profª.': 'Profª.',
    }
    
    # Aplica correções (case-insensitive)
    name_lower = name.lower()
    for wrong, correct in corrections.items():
        if name_lower.startswith(wrong):
            # Mantém o resto do nome após o título corrigido
            rest = name[len(wrong):].strip()
            name = correct + (' ' + rest if rest else '')
            break
    
    # Lista de títulos válidos (após correção)
    valid_titles = ['Dr.', 'Dra.', 'Prof.', 'Profª.', 'Licença']
    
    # Garante que o título está capitalizado corretamente
    for title in valid_titles:
        if name.lower().startswith(title.lower()):
            # Garante capitalização correta do título
            title_len = len(title)
            if len(name) > title_len:
                rest = name[title_len:].strip()
                return title + (' ' + rest if rest else '')
            else:
                return title
    
    return name


def convert_reviews(value: Any) -> float:
    """Converte reviews para float, retornando 0 se inválido."""
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def convert_telemedicine(value: Any) -> int:
    """Converte telemedicine para int (1=Sim, 0=Não)."""
    if value is None or value == "":
        return 0
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ['1', 'sim', 'yes', 'true']:
            return 1
        return 0
    return int(value) if value else 0


def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa um registro de dados aplicando todas as transformações.
    """
    processed = {}
    
    # Processa campos de texto
    text_fields = ['name1', 'name2', 'city1', 'city2', 'region', 
                   'specialization', 'price', 'url']
    
    for field in text_fields:
        if field in data:
            processed[field] = clean_text(data[field])
        else:
            processed[field] = ""
    
    # Normaliza nomes especificamente
    if 'name1' in processed:
        processed['name1'] = normalize_name(processed['name1'])
    if 'name2' in processed:
        processed['name2'] = normalize_name(processed['name2'])
    
    # Processa campos numéricos
    processed['doctor_id'] = int(data.get('doctor_id', 0)) if data.get('doctor_id') else 0
    processed['reviews'] = convert_reviews(data.get('reviews'))
    processed['telemedicine'] = convert_telemedicine(data.get('telemedicine'))
    
    # Mantém datas como estão (já estão em formato ISO)
    processed['newest_review_date'] = clean_text(data.get('newest_review_date', ''))
    processed['fetch_time'] = clean_text(data.get('fetch_time', ''))
    
    return processed


def convert_jl_to_csv(input_file: str, output_file: str):
    """
    Converte arquivo JSON Lines para CSV com tratamento de dados.
    
    Args:
        input_file: Caminho do arquivo .jl de entrada
        output_file: Caminho do arquivo .csv de saída
    """
    print(f"Lendo arquivo: {input_file}")
    
    records = []
    
    # Lê o arquivo linha por linha com barra de progresso
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # Conta linhas para barra de progresso
            total_lines = sum(1 for _ in f)
            f.seek(0)  # Volta ao início
            
            # Processa cada linha
            for line_num, line in enumerate(tqdm(f, total=total_lines, desc="Processando"), 1):
                try:
                    # json.loads automaticamente decodifica escapes Unicode
                    data = json.loads(line.strip())
                    
                    # Processa os dados
                    processed = process_data(data)
                    records.append(processed)
                    
                except json.JSONDecodeError as e:
                    print(f"\n[AVISO] Erro ao processar linha {line_num}: {e}")
                    continue
                except Exception as e:
                    print(f"\n[AVISO] Erro inesperado na linha {line_num}: {e}")
                    continue
    
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{input_file}' nao encontrado!")
        return
    except Exception as e:
        print(f"[ERRO] Erro ao ler arquivo: {e}")
        return
    
    if not records:
        print("[ERRO] Nenhum registro processado!")
        return
    
    print(f"\n[OK] Processados {len(records)} registros")
    print("Criando DataFrame...")
    
    # Cria DataFrame
    df = pd.DataFrame(records)
    
    # Define ordem das colunas (mais legível)
    column_order = [
        'doctor_id',
        'name1',
        'name2',
        'city1',
        'city2',
        'region',
        'specialization',
        'reviews',
        'newest_review_date',
        'telemedicine',
        'price',
        'url',
        'fetch_time'
    ]
    
    # Reordena colunas (mantém apenas as que existem)
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    print(f"Salvando CSV: {output_file}")
    
    # Salva em CSV com encoding UTF-8-SIG (BOM) para Excel abrir corretamente
    df.to_csv(
        output_file,
        index=False,
        encoding='utf-8-sig',  # UTF-8 com BOM para Excel
        sep=',',
        quoting=1  # QUOTE_ALL para evitar problemas com vírgulas nos dados
    )
    
    print(f"[OK] Arquivo CSV criado com sucesso: {output_file}")
    print(f"\nEstatisticas:")
    print(f"   - Total de registros: {len(df):,}")
    print(f"   - Colunas: {len(df.columns)}")
    print(f"   - Tamanho do arquivo: {len(df)} linhas")
    
    # Mostra algumas estatísticas úteis
    if 'city1' in df.columns:
        print(f"\nTop 5 cidades:")
        top_cities = df['city1'].value_counts().head(5)
        for city, count in top_cities.items():
            print(f"   - {city}: {count:,}")
    
    if 'specialization' in df.columns:
        print(f"\nTop 5 especializacoes:")
        top_specs = df['specialization'].value_counts().head(5)
        for spec, count in top_specs.items():
            print(f"   - {spec}: {count:,}")


if __name__ == "__main__":
    import sys
    
    input_file = "output.jl"
    output_file = "doctoralia_data.csv"
    
    # Permite especificar arquivos via argumentos
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print("=" * 60)
    print("Conversor JSON Lines -> CSV")
    print("=" * 60)
    print()
    
    convert_jl_to_csv(input_file, output_file)
    
    print("\n" + "=" * 60)
    print("Conversao concluida!")
    print("=" * 60)
