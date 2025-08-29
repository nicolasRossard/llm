<!-- image -->

## AU CŒUR DES MODÈLES CONVERSATIONNELS : LES RÉSEAUX DE NEURONES

## Réseau de neurones, késako ?

Un réseau de neurones est un modèle reposant sur des hypothèses statistiques et des règles, qui s'entraîne à partir de grands volumes de données.  
Cet entraînement tend à imiter celui d'un cerveau : les données fournies en entrée traversent plusieurs couches de « neurones » avant de fournir un résultat.  

Chaque neurone contient des paramètres, c'est-à-dire des nombres qui permettent, via des calculs simples, de détecter des motifs récurrents (ou *patterns*) dans les données d'entrée.  
Un algorithme, dit de **rétropropagation de l'erreur**, indique ensuite au réseau si le résultat est juste afin qu'il puisse ajuster les paramètres dans les neurones (cf. Figure 1).  

Cette opération d'inférence puis de rétropropagation est effectuée de très grands nombres de fois sur de très nombreux exemples, afin d'obtenir de solides performances sur des nouvelles données.  
En ce sens, le modèle s'entraîne à avoir raison aussi souvent que possible au regard de la distribution statistique des données d'entrée.

---

The image is a screenshot of a webpage. The page is titled *"Chaque fois deux carauses"* and is written in French.  
The main content of the page is divided into two sections.

### Section 1:
- **Title**: "Chaque fois deux carauses"
- **Content**:  
  - The first section is titled "Chaque fois deux carauses" and is written in French.  
  - It contains a list of four carauses, each with a unique number.  
  - The carauses are numbered 1 through 4.  

### Section 2:
- **Title**: "Motif abstract"
- **Content**:  
  - The second section is titled "Motif abstract" and is written in French.  
  - It contains a list of four carauses, each with a unique number.  
  - The carauses are numbered 5 through 10.  

<!-- image -->

### Sortie attendue

**Figure 1** : Représentation simplifiée de l'entraînement d'un réseau de neurones classifieur.  

Chaque couche détecte des motifs récurrents (ou *patterns*) à partir de la couche précédente. Plus les couches sont situées profondément au sein du réseau, plus elles traitent des motifs abstraits.  

Les neurones se spécialisent par eux-mêmes : on ne précise jamais que, pour différencier une voiture d'un chat, la présence de roues est un indice.  
C'est cette spécialisation **sans supervision humaine** qui rend les réseaux de neurones difficilement interprétables.  

La structure d'un réseau de neurones est appelée **architecture**. Elle permet de reconstruire un réseau identique, en indiquant :
- le nombre de couches,  
- le nombre de neurones dans chaque couche,  
- et le type de ces neurones.  

Dans la Figure 1, l'architecture consiste en :
- une première couche de trois neurones,  
- plusieurs couches non détaillées,  
- une avant-dernière couche avec deux neurones,  
- et enfin une couche de résultat avec un seul neurone.  

Cependant, imiter l'architecture d'un modèle ne permet pas toujours d'obtenir des résultats comparables.

---

<!-- image -->

- En Europe, le collectif **BigScience**, composé de plusieurs centaines de chercheurs, a entraîné le LLM **BLOOM** sur le supercalculateur Jean-Zay de Paris-Saclay.  
Ce modèle est entraîné à réaliser les mêmes tâches que GPT dans **46 langues naturelles** (y compris des langues régionales ou en danger) et **13 langages de programmation**.  

Les ensembles de données utilisés pour l'entraînement sont tous disponibles en open-source, tout comme le modèle entraîné via HuggingFace.  
Le modèle comprend **175 milliards de paramètres**, soit autant que GPT-3.

---

### Table 1 : Exemples de LLM à l'état de l'art et des politiques d'ouverture associées

| Modèle                                 | Année       | Nb. maximal de paramètres (en mds) | Architecture publique | Modèle entraîné ouvert | Données ouvertes | Conversationnel (RLHF) | Accessible aux utilisateurs (UI ou API) |
|----------------------------------------|-------------|------------------------------------|-----------------------|------------------------|------------------|-------------------------|-----------------------------------------|
| BigScience BLOOM                       | 2022        | 175                                | ✓                     | ✓                      | ✓                | ✗                       | ✓                                       |
| Google GLaM/PaLM                       | 2021 / 2022 | 1200 / 540                         | ✓                     | ✗                      | ✗                | ✗                       | ✓ (API payante)                         |
| Google LaMDA/Bard                      | 2022        | 137 / ?                            | ✓ / ✗                 | ✗                      | ✗                | ✓                       | ✓ (UK/US)                               |
| Meta OPT                               | 2022        | 175                                | ✓                     | ✓                      | ✓                | ✗                       | ✗                                       |
| Meta BlenderBot3                       | 2022        | 175                                | ✓                     | ✓                      | ✓                | ✓                       | ✓ (US)                                  |
| Meta LLaMA                             | 2023        | 65                                 | ✓                     | ✓                      | ✓                | ✗                       | ✗                                       |
| OpenAI GPT-3                           | 2020        | 175                                | ✓                     | ✗                      | ✓ (1re version)  | ✗                       | ✓ (option payante)                      |
| OpenAI GPT-3.5 (InstructGPT / ChatGPT) | 2022        | 175 / ?                            | ✓ / ✗                 | ✗                      | ✗                | ✓                       | ✓ (option payante)                      |
| OpenAI GPT-4                           | 2023        | ?                                  | ✗                     | ✗                      | ✗                | ✓                       | ✓ (API et UI payantes)                  |

---

## LLM CONVERSATIONNELS : UN CHANGEMENT DE PARADIGME POUR LES MOTEURS DE RECHERCHE

Les LLM ont déjà métamorphosé les pratiques dans de nombreux domaines. Leur évolution conversationnelle transformera à son tour certains usages.  
Le marché des moteurs de recherche apparaît comme l'un des premiers secteurs impactés par ces développements.  

La tâche d'un moteur de recherche consiste le plus souvent à **ordonner des résultats externes par pertinence** vis-à-vis d'une requête fournie par un utilisateur.  

À l'origine, les moteurs de recherche étaient d'autant plus efficaces que l'utilisateur connaissait leur fonctionnement.  
De nos jours, les acteurs du marché ont développé des outils en mesure de s'adapter à tous les types d'utilisateurs.

---

📄 Référence : [BigScience BLOOM - Arxiv](https://arxiv.org/pdf/2211.05100.pdf)
