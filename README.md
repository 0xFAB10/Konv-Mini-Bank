# Konv Mini Bank

Este projeto é uma simulação de um sistema bancário básico, implementado em Python. Ele oferece funcionalidades essenciais de um mini-banco, como gerenciamento de contas de clientes, depósitos, saques e extratos. O foco principal é demonstrar conceitos de manipulação de dados, persistência de informações em arquivos e validação de entradas.

## Funcionalidades

*   **Criação de Contas:** Permite o cadastro de novos clientes via CPF.
*   **Depósito:** Adiciona fundos à conta de um cliente.
*   **Saque:** Permite a retirada de fundos, com validação de saldo e disponibilidade de cédulas.
*   **Extrato:** Exibe o histórico de transações de uma conta.
*   **Validação de CPF:** Implementa a lógica de validação de CPF, incluindo o cálculo do dígito verificador.
*   **Formatação de Valores:** Funções para padronizar a exibição de valores monetários.

## Tecnologias Utilizadas

*   **Python 3**
*   **Manipulação de Arquivos:** Utilização de arquivos `.bin` e diretórios para simular a persistência de dados de clientes e cédulas de caixa.

## Conceitos Abordados

*   Programação Orientada a Objetos (se aplicável, ou estruturada).
*   Validação de dados e tratamento de erros.
*   Persistência de dados em sistemas de arquivos.
*   Lógica de negócios para operações bancárias.

## Limitações

Este projeto utiliza um sistema de persistência de dados baseado em arquivos simples para fins didáticos. Em um ambiente de produção, seria essencial a integração com um banco de dados relacional (ex: PostgreSQL, MySQL) para garantir escalabilidade, segurança e integridade dos dados.
