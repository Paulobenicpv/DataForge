# Configuração

Arquivos JSON aceitam somente as opções abaixo. Opções desconhecidas causam erro.

| Chave | Tipo | Padrão | Efeito |
| --- | --- | --- | --- |
| `trim` | booleano | true | Remove espaços das extremidades |
| `normalize_headers` | booleano | false | Converte cabeçalhos para minúsculas, sem acentos, com `_` |
| `drop_duplicates` | booleano | false | Exclui linhas idênticas em todas as colunas após tratamento |
| `drop_empty_rows` | booleano | false | Exclui linhas totalmente vazias |
| `drop_empty_columns` | booleano | false | Exclui colunas totalmente vazias |
| `uppercase` | lista de nomes | [] | Colunas de texto convertidas para maiúsculas |
| `conversions` | objeto por coluna | {} | Converte números ou datas explicitamente |

Exemplo:

```json
{
  "trim": true,
  "normalize_headers": true,
  "uppercase": ["cidade"],
  "conversions": {
    "data_venda": {"type": "date", "format": "%d/%m/%Y"},
    "valor": {"type": "number", "decimal": ",", "thousands": "."}
  }
}
```

Regras usam nomes posteriores à normalização. Acentos e símbolos podem gerar nomes iguais; o sistema cria sufixos únicos. Consulte `reader.headers` e `header_mapping` no relatório para mapear os nomes.

Datas usam formato explícito: `%d/%m/%Y` para 31/12/2026 e `%Y-%m-%d` para 2026-12-31. A exportação preserva horários e frações quando presentes na coluna convertida; colunas com somente datas podem ser exportadas como AAAA-MM-DD. Datas com fusos mistos não são suportadas nesta revisão.

`number` usa `decimal.Decimal` para evitar arredondamento binário, inclusive em inteiros longos. O CSV preserva os dígitos; o tipo escolhido no Power BI pode impor seus próprios limites de precisão. Identificadores devem permanecer como texto para preservar zeros à esquerda.

Os separadores devem descrever a origem. Agrupamentos de milhar precisam ter grupos de três dígitos: `1.234,50` é válido para milhar ponto/decimal vírgula; `12.34,50` é recusado. Símbolos monetários como R$ não são removidos automaticamente. Configurações com tipos incorretos ou opções incompatíveis são recusadas com mensagem de validação.

Strings vazias são consideradas vazias no perfil, sem converter textos NA/NULL automaticamente. Contagem de distintos desconsidera valores nulos, mas inclui string vazia como uma categoria. Perfis de duplicidade são calculados antes/depois de cada conjunto de transformações.

A exclusão de linhas vazias ocorre antes de duplicados. Colunas vazias são avaliadas sobre o quadro antes dessas exclusões. Não é permitido gerar saída sem colunas.
