```mermaid
graph TD
    %% Nó Central
    Design((Design))

    %% Macroáreas
    Comunicacao((Design de<br>Comunicação))
    Produto((Design de<br>Produto / Industrial))
    Moda((Design de<br>Moda))
    Espaco((Design de<br>Espaço / Interiores))

    %% Conexões Centrais
    Design --- Comunicacao
    Design --- Produto
    Design --- Moda
    Design --- Espaco

    %% Subvertentes - Comunicação
    Comunicacao --- Branding[Branding / Identidade Visual]
    Comunicacao --- Editorial[Design Editorial & Informação]
    Comunicacao --- Sinaletica[Sinalética / Wayfinding]
    Comunicacao --- Digital[Design Digital & Redes Sociais]
    Comunicacao --- EmbalagemCom[Design de Embalagem]

    %% Subvertentes - Produto
    Produto --- Eletronicos[Bens de Consumo & Eletrónicos]
    Produto --- Mobiliario[Mobiliário & Luminárias]
    Produto --- Medico[Equipamento Médico & Hospitalar]
    Produto --- Mobilidade[Automóvel & Transportes]
    Produto --- Brinquedos[Brinquedos & Jogos]

    %% Subvertentes - Moda
    Moda --- Luxo[Alta-Costura & Prêt-à-Porter]
    Moda --- Massa[Fast Fashion & Mercado de Massa]
    Moda --- Acessorios[Acessórios & Calçado]
    Moda --- Textil[Design Têxtil & Estamparia]
    Moda --- Sustentavel[Eco-Design & Moda Sustentável]

    %% Subvertentes - Espaço
    Espaco --- Residencial[Espaços Residenciais]
    Espaco --- Comercial[Design Comercial / Retail]
    Espaco --- Corporativo[Espaços Corporativos]
    Espaco --- Ceno[Cenografia & Efémeros]
    Espaco --- Museu[Design Expositivo & Museografia]

    %% Estilização (Tons de Verde)
    style Design fill:#76B82A,stroke:#558B1D,stroke-width:2px,color:#fff
    style Comunicacao fill:#76B82A,stroke:#558B1D,stroke-width:2px,color:#fff
    style Produto fill:#76B82A,stroke:#558B1D,stroke-width:2px,color:#fff
    style Moda fill:#76B82A,stroke:#558B1D,stroke-width:2px,color:#fff
    style Espaco fill:#76B82A,stroke:#558B1D,stroke-width:2px,color:#fff
    
    classDef subNode fill:#fff,stroke:#76B82A,stroke-width:1px,color:#333;
    class Branding,Editorial,Sinaletica,Digital,EmbalagemCom,Eletronicos,Mobiliario,Medico,Mobilidade,Brinquedos,Luxo,Massa,Acessorios,Textil,Sustentavel,Residencial,Comercial,Corporativo,Ceno,Museu subNode;
