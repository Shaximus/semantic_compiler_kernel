# Relative Clause / Coordinated Verb Extraction Report V2.1.3

Verifies extraction of relative-clause subjects, coordinated verbs, and pronoun antecedents.

| input | relationships |
|---|---|
| The company has an immune system that detects threats and remembers them. | immune system--detects-->threats; immune system--remembers-->threats |
| A firewall is a membrane which filters packets. | membrane--filters-->packets |
| The nervous system routes signals to the brain. | nervous system--routes-->signals |
| The brain's memory consolidates during sleep. | none |
| A supply chain delivers materials like a circulatory system delivers oxygen. | supply chain--delivers-->materials; circulatory system--delivers-->oxygen; supply chain--is_structurally_like-->circulatory system |