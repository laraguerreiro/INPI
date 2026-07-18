```mermaid
graph LR
    %% ==========================================
    %% PILAR CENTRAL E FUNDAMENTOS
    %% ==========================================
    Design(((DESIGN))) === Pilares{Pilares Comuns}
    Pilares -.-> P1[Praticidade]
    Pilares -.-> P2[Viabilidade]
    Pilares -.-> P3[Desejabilidade]

    %% ==========================================
    %% ÁREA 1: GRÁFICO E COMUNICAÇÃO (Preto/Borgonha)
    %% ==========================================
    Design === Area1(Design Gráfico e de Comunicação)
    subgraph ComVis[Comunicação Visual]
        Area1 --- Branding[Identidade Visual / Branding]
        Area1 --- Editorial[Design Editorial]
        Area1 --- Tipografia[Tipografia]
    end

    %% ==========================================
    %% ÁREA 2: DIGITAL E INTERAÇÃO (Cinza-Azulado)
    %% ==========================================
    Design === Area2(Design Digital e de Interação)
    subgraph IntExp[Interfaces e Experiência]
        Area2 --- UX[UX Design]
        Area2 --- UI[UI Design]
        Area2 --- Games[Design de Jogos]
    end

    %% ==========================================
    %% ÁREA 3: PRODUTO E ESPAÇO (Magenta/Roxo)
    %% ==========================================
    Design === Area3(Design de Produto e Espaço)
    subgraph Mundo3D[Mundo Tridimensional]
        Area3 --- Industrial[Design Industrial]
        Area3 --- Interiores[Design de Interiores]
        Area3 --- Moda[Design de Moda]
    end

    %% ==========================================
    %% ÁREA 4: ESTRATÉGICO E SERVIÇOS (Castanho/Terra)
    %% ==========================================
    Design === Area4(Design Estratégico e de Serviços)
    subgraph ProcEst[Processos e Estratégia]
        Area4 --- Servicos[Design de Serviços]
        Area4 --- Thinking[Design Thinking]
    end

    %% ==========================================
    %% RELAÇÕES E PONTES (INTERSECÇÕES)
    %% ==========================================
    Branding -.-> UI
    Industrial -- "Embalagem" --- Area1
    Area1 -- "Sinalética / Wayfinding" --- Interiores
    Area4 -- "Retail Design" --- Interiores
    
    %% ==========================================
    %% ESTILIZAÇÃO AVANÇADA (PADRÃO PREMIUM ESCURO)
    %% ==========================================
    
    %% Nó Principal e Pilares
    style Design fill:#5c6b73,stroke:#2f3e46,stroke-width:3px,color:#fff;
    style Pilares fill:#2f3e46,stroke:#5c6b73,stroke-dasharray: 5 5,color:#fff;
    style P1 fill:#4a5568,stroke:#718096,color:#fff;
    style P2 fill:#4a5568,stroke:#718096,color:#fff;
    style P3 fill:#4a5568,stroke:#718096,color:#fff;

    %% Subgraph 1: Comunicação Visual (Preto / Borgonha)
    style Area1 fill:#1a0f0f,stroke:#000,stroke-width:2px,color:#fff;
    style Branding fill:#2b1a1a,stroke:#1a0f0f,color:#fff;
    style Editorial fill:#2b1a1a,stroke:#1a0f0f,color:#fff;
    style Tipografia fill:#2b1a1a,stroke:#1a0f0f,color:#fff;
    style ComVis fill:#110808,stroke:#2b1a1a,color:#fff;

    %% Subgraph 2: Digital (Cinza-Azulado / Petróleo)
    style Area2 fill:#283d3b,stroke:#192c2b,stroke-width:2px,color:#fff;
    style UX fill:#3d5a57,stroke:#283d3b,color:#fff;
    style UI fill:#3d5a57,stroke:#283d3b,color:#fff;
    style Games fill:#3d5a57,stroke:#283d3b,color:#fff;
    style IntExp fill:#142220,stroke:#283d3b,color:#fff;

    %% Subgraph 3: Mundo Tridimensional (Magenta / Roxo)
    style Area3 fill:#4a154b,stroke:#300a3a,stroke-width:2px,color:#fff;
    style Industrial fill:#6b114d,stroke:#4a154b,color:#fff;
    style Interiores fill:#6b114d,stroke:#4a154b,color:#fff;
    style Moda fill:#6b114d,stroke:#4a154b,color:#fff;
    style Mundo3D fill:#290b2a,stroke:#4a154b,color:#fff;

    %% Subgraph 4: Estratégia (Tons de Castanho / Terra)
    style Area4 fill:#582f0e,stroke:#3f1d0b,stroke-width:2px,color:#fff;
    style Servicos fill:#7f4f24,stroke:#582f0e,color:#fff;
    style Thinking fill:#7f4f24,stroke:#582f0e,color:#fff;
    style ProcEst fill:#331a07,stroke:#582f0e,color:#fff;

    %% Links Gerais
    linkStyle default stroke:#718096,stroke-width:2px;
    linkStyle 0,4,8,12,16 stroke:#adb5bd,stroke-width:4px;
