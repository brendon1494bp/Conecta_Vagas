# 🎨 Diretrizes de Identidade Visual e UI/UX
> **Sistema de Troca de Vagas Escolares — Rede Pública de Ensino do DF**  
> *Guia de estilo, acessibilidade e componentes de interface para desenvolvimento.*

---

## 📌 Visão Geral do Design
O sistema foi projetado para ser **extremamente simples, minimalista, moderno e acessível**. Como o público-alvo principal são pais e responsáveis por alunos da rede pública (acessando via dispositivos móveis), toda a interface prioriza **legibilidade, facilidade de toque (touch) e clareza nas ações**.

---

## 🎨 Paleta de Cores & Papéis na Interface

| Cor | Código HEX | Código RGB | Aplicação / Papel UI |
| :--- | :---: | :---: | :--- |
| 🟢 **Verde Profundo** | `#006B4F` | `0, 107, 79` | **Apoio, Confiança e Sucesso:** Header/topo do sistema, telas de *Match* confirmado, selos de validação institucional e botões de ação finalizada. |
| 🟡 **Dourado** | `#D9A51A` | `217, 165, 26` | **Destaque / Ação Principal (CTA):** Botões primários (ex: *"Cadastrar Troca"*), avisos importantes e focos de atenção visual. |
| 🔵 **Azul** | `#008FC4` | `0, 143, 196` | **Conexão e Interação:** Botão do Chat, balões de conversa, links informativos, ícones de navegação e indicadores de fluxo. |
| ⚫ **Preto** | `#050505` | `5, 5, 5` | **Tipografia Primária:** Textos do corpo, títulos de formulários e ícones estruturais. Alto contraste garantido. |
| ⚪ **Off-white** | `#FDFCF8` | `253, 252, 248` | **Fundo Geral (Background):** Substitui o branco puro (`#FFFFFF`), reduzindo a fadiga visual e trazendo elegância e acolhimento. |

---

## 🔤 Tipografia (Fontes)

Para garantir carregamento rápido em redes móveis e leitura fluida:

- **Família da Fonte:** Usar fontes de sistema (System Font Stack) ou **Inter** / **Roboto** (Google Fonts).
  ```css
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;