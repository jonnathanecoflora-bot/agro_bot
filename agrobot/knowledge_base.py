
KNOWLEDGE_BASE = {
    "versao": "1.0",
    "data_atualizacao": "2024-11-30",
    "fonte_referencia": "SOUSA, D. M. G. de; LOBATO, E. (Ed.). Cerrado: correção do solo e adubação. 2. ed. Brasília, DF: Embrapa Informação Tecnológica, 2004. 416 p.",
    "autor": "Prof. Dr. Anísio da Silva Nunes - Disciplina de Fitotecnia III",
    
    "configuracoes": {
      "culturas_disponiveis": ["Soja", "Milho", "Trigo", "Arroz", "Sorgo", "Milheto", "Outras"],
      "prnt_opcoes": [70, 75, 80, 85, 90, 95, 100],
      "formulacao_opcoes": ["NPK Pronta", "Fontes Simples", "Mista"],
      "expectativa_opcoes": {
        "Soja": ["3,5-4,0 t/ha", "4,0-4,5 t/ha", "4,5-5,0 t/ha"],
        "Milho": ["6,0 t/ha", "8,0 t/ha", "10,0 t/ha"],
        "Trigo": ["3,0 t/ha", "4,0 t/ha", "5,0 t/ha"],
        "Arroz": ["3,0 t/ha", "4,0 t/ha", "5,0 t/ha"],
        "Sorgo": ["4,0 t/ha", "5,0 t/ha", "6,0 t/ha"],
        "Milheto": ["2,0 t/ha", "3,0 t/ha"]
      }
    },
    
    "interpretacao_solo": {
      "camada": "0-20 cm",
      "parametros": {
        "ph": {
          "agua": {
            "muito_baixo": {"max": 5.1},
            "baixo": {"min": 5.2, "max": 5.5},
            "medio": {"min": 5.6, "max": 6.3},
            "adequado": {"min": 6.4, "max": 6.6},
            "alto": {"min": 6.7}
          },
          "cacl2": {
            "muito_baixo": {"max": 4.4},
            "baixo": {"min": 4.5, "max": 4.8},
            "medio": {"min": 4.9, "max": 5.5},
            "adequado": {"min": 5.6, "max": 5.8},
            "alto": {"min": 5.9}
          }
        },
        
        "fosforo": {
          "mehlich1": [
            {
              "argila_min": 0,
              "argila_max": 15,
              "classes": {
                "muito_baixo": {"min": 0, "max": 6.0},
                "baixo": {"min": 6.1, "max": 12.0},
                "medio": {"min": 12.1, "max": 18.0},
                "adequado": {"min": 18.1, "max": 25.0},
                "alto": {"min": 25.1}
              }
            },
            {
              "argila_min": 16,
              "argila_max": 35,
              "classes": {
                "muito_baixo": {"min": 0, "max": 5.0},
                "baixo": {"min": 5.1, "max": 10.0},
                "medio": {"min": 10.1, "max": 15.0},
                "adequado": {"min": 15.1, "max": 20.0},
                "alto": {"min": 20.1}
              }
            },
            {
              "argila_min": 36,
              "argila_max": 60,
              "classes": {
                "muito_baixo": {"min": 0, "max": 3.0},
                "baixo": {"min": 3.1, "max": 5.0},
                "medio": {"min": 5.1, "max": 8.0},
                "adequado": {"min": 8.1, "max": 12.0},
                "alto": {"min": 12.1}
              }
            },
            {
              "argila_min": 61,
              "argila_max": None,
              "classes": {
                "muito_baixo": {"min": 0, "max": 2.0},
                "baixo": {"min": 2.1, "max": 3.0},
                "medio": {"min": 3.1, "max": 4.0},
                "adequado": {"min": 4.1, "max": 6.0},
                "alto": {"min": 6.1}
              }
            }
          ],
          "resina": {
            "classes": {
              "muito_baixo": {"min": 0, "max": 5},
              "baixo": {"min": 6, "max": 8},
              "medio": {"min": 9, "max": 14},
              "adequado": {"min": 15, "max": 20},
              "alto": {"min": 21}
            }
          }
        },
        
        "potassio": {
          "mg_dm3": [
            {
              "ctc_ph7_min": 0,
              "ctc_ph7_max": 4,
              "classes": {
                "baixo": {"max": 15},
                "medio": {"min": 16, "max": 30},
                "adequado": {"min": 31, "max": 40},
                "alto": {"min": 41}
              }
            },
            {
              "ctc_ph7_min": 4,
              "ctc_ph7_max": None,
              "classes": {
                "baixo": {"max": 25},
                "medio": {"min": 26, "max": 50},
                "adequado": {"min": 51, "max": 80},
                "alto": {"min": 81}
              }
            }
          ],
          "cmolc_dm3": [
            {
              "ctc_ph7_min": 0,
              "ctc_ph7_max": 4,
              "classes": {
                "baixo": {"max": 0.038},
                "medio": {"min": 0.039, "max": 0.078},
                "adequado": {"min": 0.079, "max": 0.100},
                "alto": {"min": 0.101}
              }
            },
            {
              "ctc_ph7_min": 4,
              "ctc_ph7_max": None,
              "classes": {
                "baixo": {"max": 0.064},
                "medio": {"min": 0.065, "max": 0.128},
                "adequado": {"min": 0.129, "max": 0.200},
                "alto": {"min": 0.201}
              }
            }
          ]
        },
        
        "calcio_magnesio": {
          "calcio": {
            "baixo": {"max": 1.5},
            "medio": {"min": 1.6, "max": 2.4},
            "adequado": {"min": 2.5, "max": 7.0},
            "alto": {"min": 7.1}
          },
          "magnesio": {
            "baixo": {"max": 0.4},
            "medio": {"min": 0.5, "max": 1.9},
            "adequado": {"min": 2.0, "max": 2.0},
            "alto": {"min": 2.1}
          }
        },
        
        "acidez": {
          "al_trocavel": {
            "muito_baixo": {"max": 0.20},
            "baixo": {"min": 0.21, "max": 0.50},
            "medio": {"min": 0.51, "max": 1.00},
            "alto": {"min": 1.01, "max": 2.00},
            "muito_alto": {"min": 2.01}
          },
          "acidez_potencial": {
            "muito_baixo": {"max": 1.00},
            "baixo": {"min": 1.01, "max": 2.50},
            "medio": {"min": 2.51, "max": 5.00},
            "alto": {"min": 5.01, "max": 9.00},
            "muito_alto": {"min": 9.01}
          }
        },
        
        "materia_organica": {
          "arenosa": {
            "baixa": {"max": 8},
            "media": {"min": 8, "max": 10},
            "adequada": {"min": 11, "max": 15},
            "alta": {"min": 16}
          },
          "media": {
            "baixa": {"max": 16},
            "media": {"min": 16, "max": 20},
            "adequada": {"min": 21, "max": 30},
            "alta": {"min": 31}
          },
          "argilosa": {
            "baixa": {"max": 24},
            "media": {"min": 24, "max": 30},
            "adequada": {"min": 31, "max": 45},
            "alta": {"min": 46}
          },
          "muito_argilosa": {
            "baixa": {"max": 28},
            "media": {"min": 28, "max": 35},
            "adequada": {"min": 36, "max": 52},
            "alta": {"min": 53}
          }
        },
        
        "ctc": {
          "arenosa": {
            "baixa": {"max": 3.2},
            "media": {"min": 3.2, "max": 4.0},
            "adequada": {"min": 4.1, "max": 6.0},
            "alta": {"min": 6.1}
          },
          "media": {
            "baixa": {"max": 4.8},
            "media": {"min": 4.8, "max": 6.0},
            "adequada": {"min": 6.1, "max": 9.0},
            "alta": {"min": 9.1}
          },
          "argilosa": {
            "baixa": {"max": 7.2},
            "media": {"min": 7.2, "max": 9.0},
            "adequada": {"min": 9.1, "max": 13.5},
            "alta": {"min": 13.6}
          },
          "muito_argilosa": {
            "baixa": {"max": 9.6},
            "media": {"min": 9.6, "max": 12.0},
            "adequada": {"min": 12.1, "max": 18.0},
            "alta": {"min": 18.1}
          }
        },
        
        "saturacao": {
          "por_bases": {
            "baixa": {"max": 20},
            "media": {"min": 21, "max": 35},
            "adequada": {"min": 36, "max": 60},
            "alta": {"min": 61}
          },
          "por_aluminio": {
            "baixa": {"max": 20},
            "alta": {"min": 21}
          }
        },
        
        "relacoes": {
          "ca_mg_k": {
            "baixa": {"max": 10},
            "media": {"min": 10, "max": 19},
            "adequada": {"min": 20, "max": 30},
            "alta": {"min": 31}
          },
          "ca_k": {
            "baixa": {"max": 7},
            "media": {"min": 7, "max": 14},
            "adequada": {"min": 15, "max": 25},
            "alta": {"min": 26}
          },
          "mg_k": {
            "baixa": {"max": 2},
            "media": {"min": 2, "max": 4},
            "adequada": {"min": 5, "max": 15},
            "alta": {"min": 16}
          }
        },
        
        "micronutrientes": {
          "b": {
            "baixo": {"max": 0.2},
            "adequado": {"min": 0.3, "max": 0.5},
            "alto": {"min": 0.6}
          },
          "cu": {
            "baixo": {"max": 0.4},
            "adequado": {"min": 0.5, "max": 0.8},
            "alto": {"min": 0.9}
          },
          "fe": {
            "baixo": {"max": 31.0},
            "adequado": {"min": 31.1, "max": 45.0},
            "alto": {"min": 45.1}
          },
          "mn": {
            "baixo": {"max": 1.9},
            "adequado": {"min": 2.0, "max": 5.0},
            "alto": {"min": 5.1}
          },
          "zn": {
            "baixo": {"max": 1.0},
            "adequado": {"min": 1.1, "max": 1.6},
            "alto": {"min": 1.7}
          },
          "s": {
            "baixo": {"max": 4.0},
            "adequado": {"min": 5.0, "max": 9.0},
            "alto": {"min": 10.0}
          }
        }
      },
      
      "classificacao_textura": {
        "tipo1": {
          "nome": "Arenosa",
          "descricao": "Solos de textura arenosa",
          "condicao": "argila < 15% OU (15% <= argila < 35% AND delta >= 50%)"
        },
        "tipo2": {
          "nome": "Média",
          "descricao": "Solos de textura média",
          "condicao": "15% <= argila < 35% AND delta < 50%"
        },
        "tipo3": {
          "nome": "Argilosa",
          "descricao": "Solos de textura argilosa",
          "condicao": "argila >= 35%"
        }
      },
      
      "conversoes": {
        "cmolc_para_mmolc": "1 cmolc/dm³ = 10 mmolc/dm³",
        "k_mg_para_cmolc": "K (mg/dm³) / 391 = K (cmolc/dm³)",
        "porcentagem_para_g_kg": "% * 10 = g/kg ou g/dm³"
      }
    },
    
    "recomendacao_adubacao": {
      "logica_selecao": "Se cultura tem tabela específica E P e K são 'Adequado' ou 'Alto' -> usar tabela específica, senão -> usar tabela mestra",
      
      "tabela_mestra": {
        "descricao": "Adubação em solos com baixa a média fertilidade química (usar quando não há tabela específica ou quando P/K são Baixo/Muito Baixo)",
        "dados": [
          {
            "teor_argila_min": 0,
            "teor_argila_max": 15,
            "nitrogenio": {
              "semeadura_min": 10,
              "semeadura_max": 30,
              "cobertura_min": 20,
              "cobertura_max": 70
            },
            "fosforo": {
              "muito_baixo": 60,
              "baixo": 30,
              "medio": 15,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_menor_4": {
              "baixo": 50,
              "medio": 25,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_maior_igual_4": {
              "baixo": 100,
              "medio": 50,
              "adequado": 0,
              "alto": 0
            }
          },
          {
            "teor_argila_min": 16,
            "teor_argila_max": 35,
            "nitrogenio": {
              "semeadura_min": 10,
              "semeadura_max": 30,
              "cobertura_min": 20,
              "cobertura_max": 70
            },
            "fosforo": {
              "muito_baixo": 100,
              "baixo": 50,
              "medio": 25,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_menor_4": {
              "baixo": 50,
              "medio": 25,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_maior_igual_4": {
              "baixo": 100,
              "medio": 50,
              "adequado": 0,
              "alto": 0
            }
          },
          {
            "teor_argila_min": 36,
            "teor_argila_max": 60,
            "nitrogenio": {
              "semeadura_min": 10,
              "semeadura_max": 30,
              "cobertura_min": 20,
              "cobertura_max": 70
            },
            "fosforo": {
              "muito_baixo": 200,
              "baixo": 100,
              "medio": 50,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_menor_4": {
              "baixo": 50,
              "medio": 25,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_maior_igual_4": {
              "baixo": 100,
              "medio": 50,
              "adequado": 0,
              "alto": 0
            }
          },
          {
            "teor_argila_min": 61,
            "teor_argila_max": None,
            "nitrogenio": {
              "semeadura_min": 10,
              "semeadura_max": 30,
              "cobertura_min": 20,
              "cobertura_max": 70
            },
            "fosforo": {
              "muito_baixo": 280,
              "baixo": 140,
              "medio": 70,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_menor_4": {
              "baixo": 50,
              "medio": 25,
              "adequado": 0,
              "alto": 0
            },
            "potassio_ctc_maior_igual_4": {
              "baixo": 100,
              "medio": 50,
              "adequado": 0,
              "alto": 0
            }
          }
        ]
      },
      
      "tabelas_especificas": {
        "soja": {
          "descricao": "Adubação fosfatada e potássica para soja, em função dos resultados da análise do solo e de diferentes classes de textura, para produtividade de 3,5 t/ha a 4,0 t/ha de grãos",
          "extrator": "Mehlich 1",
          "observacao": "Soja não requer adubação nitrogenada devido à fixação biológica de nitrogênio",
          "dados": [
            {
              "disponibilidade": "Baixa",
              "fosforo": {
                "argilosa": {"min": 0, "max": 5},
                "media": {"min": 0, "max": 8},
                "arenosa": {"min": 0, "max": 10}
              },
              "p2o5_kg_ha": 100,
              "potassio": {"min": 0, "max": 40},
              "k2o_kg_ha": 90
            },
            {
              "disponibilidade": "Média",
              "fosforo": {
                "argilosa": {"min": 6, "max": 10},
                "media": {"min": 9, "max": 15},
                "arenosa": {"min": 11, "max": 18}
              },
              "p2o5_kg_ha": 75,
              "potassio": {"min": 41, "max": 60},
              "k2o_kg_ha": 60
            },
            {
              "disponibilidade": "Alta",
              "fosforo": {
                "argilosa": {"min": 11, "max": 15},
                "media": {"min": 16, "max": 20},
                "arenosa": {"min": 19, "max": 25}
              },
              "p2o5_kg_ha": 50,
              "potassio": {"min": 61, "max": 90},
              "k2o_kg_ha": 30
            },
            {
              "disponibilidade": "Muito Alta",
              "fosforo": {
                "argilosa": {"min": 16},
                "media": {"min": 21},
                "arenosa": {"min": 26}
              },
              "p2o5_kg_ha": 0,
              "potassio": {"min": 91},
              "k2o_kg_ha": 0
            }
          ]
        },
        
        "milho": {
          "descricao": "Adubação para milho sequeiro em solos com níveis de adequado a alto de nutrientes",
          "observacoes": [
            "Para doses superiores a 100 kg ha⁻¹ de N, parcelar metade em V4 a V6 e metade em V8 a V10",
            "20 kg ha⁻¹ de S para expectativa até 8 t ha⁻¹ e 30 kg ha⁻¹ de S para expectativas de 8 a 12 t ha⁻¹"
          ],
          "dados": [
            {
              "expectativa_rendimento": "6,0 t ha⁻¹",
              "nitrogenio": {"semeadura": 20, "cobertura": 40},
              "fosforo": {"adequado": 60, "alto": 30},
              "potassio": {
                "semeadura": {"adequado": 60, "alto": 30},
                "cobertura": 0
              }
            },
            {
              "expectativa_rendimento": "8,0 t ha⁻¹",
              "nitrogenio": {"semeadura": 30, "cobertura": 70},
              "fosforo": {"adequado": 80, "alto": 40},
              "potassio": {
                "semeadura": {"adequado": 60, "alto": 40},
                "cobertura": 30
              }
            },
            {
              "expectativa_rendimento": "10,0 t ha⁻¹",
              "nitrogenio": {"semeadura": 30, "cobertura": 130},
              "fosforo": {"adequado": 100, "alto": 50},
              "potassio": {
                "semeadura": {"adequado": 60, "alto": 50},
                "cobertura": 60
              }
            },
            {
              "expectativa_rendimento": "10,0 t ha⁻¹ (alternativo)",
              "nitrogenio": {"semeadura": 30, "cobertura": 180},
              "fosforo": {"adequado": 120, "alto": 60},
              "potassio": {
                "semeadura": {"adequado": 60, "alto": 60},
                "cobertura": 90
              }
            }
          ]
        },
        
        "trigo": {
          "descricao": "Adubação para trigo sequeiro em solos com níveis de adequado a alto de nutrientes",
          "dados": [
            {
              "expectativa_rendimento": "3,0 t ha⁻¹",
              "nitrogenio": {"semeadura": 20, "cobertura": 10},
              "fosforo": {"adequado": 60, "alto": 30},
              "potassio": {"adequado": 30, "alto": 15}
            },
            {
              "expectativa_rendimento": "4,0 t ha⁻¹",
              "nitrogenio": {"semeadura": 20, "cobertura": 40},
              "fosforo": {"adequado": 70, "alto": 35},
              "potassio": {"adequado": 40, "alto": 20}
            },
            {
              "expectativa_rendimento": "5,0 t ha⁻¹",
              "nitrogenio": {"semeadura": 20, "cobertura": 70},
              "fosforo": {"adequado": 80, "alto": 40},
              "potassio": {"adequado": 50, "alto": 25}
            }
          ],
          "controle_choquamento": {
            "descricao": "O controle de chochamento (esterilidade masculina) é feito pela adição de boro na adubação de semeadura",
            "dose_boro": "0,65 a 1,3 kg ha⁻¹",
            "equivalentes": [
              "5,9 a 11,8 kg ha⁻¹ de bórax",
              "35 a 70 kg ha⁻¹ de FTE BR 12 (1,8% de boro)"
            ]
          }
        }
      },
      
      "enxofre": {
        "descricao": "Recomendação de enxofre (S) para culturas anuais",
        "doses": [
          {"cultura": "Milho", "ate_8t_ha": 20, "8_a_12t_ha": 30},
          {"cultura": "Trigo", "dose": 20},
          {"cultura": "Arroz", "dose": 20},
          {"cultura": "Sorgo", "dose": 20},
          {"cultura": "Milheto", "dose": 20}
        ]
      }
    },
    
    "fontes_fertilizantes": {
      "principais_fertilizantes": {
        "nitrogenados": [
          {"nome": "Ureia", "formula": "45-00-00", "N": 45, "P2O5": 0, "K2O": 0, "S": 0},
          {"nome": "Amônia anidra", "formula": "82-00-00", "N": 82, "P2O5": 0, "K2O": 0, "S": 0},
          {"nome": "Sulfato de amônio", "formula": "20-00-00 + 22% S", "N": 20, "P2O5": 0, "K2O": 0, "S": 22}
        ],
        "fosfatados": [
          {"nome": "MAP", "formula": "10-46-00", "N": 10, "P2O5": 46, "K2O": 0, "S": 0, "descricao": "Fosfato monoamônico"},
          {"nome": "DAP", "formula": "16-38-00", "N": 16, "P2O5": 38, "K2O": 0, "S": 0, "descricao": "Fosfato diamônico"},
          {"nome": "Fosfato natural", "formula": "00-24-00", "N": 0, "P2O5": 24, "K2O": 0, "S": 0},
          {"nome": "Superfosfato simples", "formula": "00-18-00 + 10% S", "N": 0, "P2O5": 18, "K2O": 0, "S": 10},
          {"nome": "Superfosfato triplo", "formula": "00-41-00", "N": 0, "P2O5": 41, "K2O": 0, "S": 0}
        ],
        "potassicos": [
          {"nome": "Cloreto de potássio", "formula": "00-00-60", "N": 0, "P2O5": 0, "K2O": 60, "S": 0}
        ]
      },
      
      "formulas_comerciais": {
        "semeadura": [
          "00-14-14", "00-15-30", "00-20-10", "00-20-20", "00-20-25", "00-20-30", "00-25-20", "00-25-25",
          "00-28-20", "00-30-10", "00-30-15", "02-10-28", "02-15-30", "02-18-28", "02-20-10", "02-20-20",
          "02-20-30", "02-22-10", "02-25-20", "02-25-25", "02-28-18", "02-28-20", "02-30-05", "02-30-10",
          "02-30-15", "03-15-15", "03-15-30", "03-20-15", "03-23-23", "03-25-20", "03-25-25", "04-12-16",
          "04-14-08", "04-16-08", "04-24-08", "04-24-12", "04-30-10", "04-30-15", "05-10-20", "05-15-15",
          "05-15-30", "05-20-10", "05-20-20", "05-20-30", "05-23-23", "05-24-12", "05-25-20", "05-25-25",
          "05-30-10", "05-30-15", "06-24-12", "06-26-16", "06-30-06", "07-11-09", "07-22-22", "07-30-15",
          "08-15-15", "08-15-25", "08-16-12", "08-16-16", "08-16-24", "08-18-28", "08-20-20", "08-20-30",
          "08-26-26", "08-28-16", "08-28-20", "08-28-28", "08-30-30", "09-12-27", "09-13-19", "09-33-12",
          "10-05-20", "10-06-20", "10-10-10", "10-10-20", "10-15-25", "10-16-20", "10-18-20", "10-20-10",
          "10-20-15", "10-20-20", "10-20-30", "10-24-12", "10-25-25", "10-26-25", "10-28-20", "10-30-10",
          "10-30-20"
        ],
        "cobertura": [
          "12-00-12", "12-02-12", "12-06-12", "12-06-18", "12-11-18", "12-14-12", "12-15-12", "12-15-15",
          "12-31-20", "13-13-13", "13-19-19", "14-07-28", "15-00-14", "15-00-15", "15-05-30", "15-06-15",
          "15-08-10", "15-09-20", "16-16-16", "18-00-27", "18-18-18", "19-04-19", "20-00-10", "20-00-15",
          "20-00-20", "20-00-30", "20-05-20", "20-10-10", "20-10-15", "20-10-20", "21-07-14", "22-00-20",
          "22-00-30", "25-00-25", "26-00-25", "30-00-15", "30-00-18", "30-00-20", "30-03-03", "36-00-12"
        ]
      }
    },
    
    "calagem": {
      "parametros": {
        "v2_alvos": {
          "soja": 60,
          "milho": 60,
          "trigo": 70,
          "arroz": 50,
          "sorgo": 50,
          "milheto": 50,
          "cafe": 60,
          "feijao": 70
        }
      },
      "formulas": [
        {
          "nome": "Saturação por bases",
          "descricao": "Método geral para correção da acidez",
          "formula": "NC = [(V2 - V1) * T] / PRNT",
          "onde": {
            "V2": "Saturação por bases desejada (50 a 60%)",
            "V1": "Saturação por bases atual = (100 * SB) / T",
            "T": "CTC a pH 7,0 (cmolc/dm³)",
            "PRNT": "Poder Relativo de Neutralização Total do calcário (%)"
          },
          "condicao": "Usar sempre, selecionar a maior dose entre os métodos"
        },
        {
          "nome": "Neutralização do alumínio",
          "descricao": "Quando a saturação por alumínio (m) é maior que 10%",
          "formula": "NC = Al * 2 * (100 / PRNT)",
          "onde": {
            "Al": "Teor de alumínio trocável (cmolc/dm³)",
            "PRNT": "Poder Relativo de Neutralização Total do calcário (%)"
          },
          "condicao": "Aplicar se m > 10%, onde m = (100 * Al) / (Al + SB)"
        },
        {
          "nome": "Correção de cálcio e magnésio",
          "descricao": "Quando a soma de Ca + Mg é inferior a 2,0 cmolc/dm³",
          "formula": "NC = [(Al * Y) + (X - (Ca + Mg))] * (100 / PRNT)",
          "onde": {
            "Y": "Fator de textura: 1 (arenoso), 2 (médio), 3 (argiloso)",
            "X": "Fator de cultura: 1 (eucalipto), 2 (maioria das culturas), 3 (cafeeiro)",
            "Al": "Teor de alumínio trocável (cmolc/dm³)",
            "Ca": "Teor de cálcio (cmolc/dm³)",
            "Mg": "Teor de magnésio (cmolc/dm³)",
            "PRNT": "Poder Relativo de Neutralização Total do calcário (%)"
          },
          "condicao": "Aplicar se Ca + Mg < 2,0 cmolc/dm³"
        }
      ],
      "observacoes": [
        "Utilizar a maior dose entre os métodos aplicáveis",
        "Aplicar o calcário 3 meses antes do plantio",
        "Incorporar até 20 cm de profundidade",
        "Em solos com teor de argila > 20%, considerar calagem em duas etapas"
      ]
    }
}
