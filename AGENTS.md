# Working on Kasoma

This repository currently contains the product and engineering specification baseline. Consult [README.md](README.md) for the documentation entry points and current implementation status.

Before implementing application code, read and follow:

- [Source of truth and authority order](Kasoma_MVP_Engineering_Specification_Pack/00_README_Source_of_Truth.md)
- [Coding LLM operating contract](Kasoma_MVP_Engineering_Specification_Pack/12_Coding_LLM_Operating_Contract.md), including its required read order and comprehension report
- [Repository bootstrap and environment contract](Kasoma_MVP_Engineering_Specification_Pack/15_Repository_Bootstrap_and_Environment.md)

Preserve the fixed MVP scope and implement only the assigned slice. Do not treat requirements for future infrastructure as evidence that infrastructure already exists. Document actual setup and validation commands as they are implemented.

Never commit credentials, production exports, real learner data, restricted source material or generated build artifacts. Local startup and ordinary tests must not call paid or external model providers.
