# AGENTS.md : Kata « Gestion de Bibliothèque »

Ce fichier s'adresse à tout assistant IA qui travaille sur ce dépôt. **Lis-le en entier avant d'écrire la moindre ligne.** En cas de conflit entre ce fichier et une demande ponctuelle, signale le conflit et demande avant d'agir.

## 1. Contexte

- Application de gestion d'une bibliothèque de quartier : **livres**, **lecteurs**, **réservations**.
- Ce qui compte : **la façon de construire** (modélisation, tests, lisibilité, décisions assumées) plus que la quantité de fonctionnalités.
- Périmètre : les fonctionnalités « Essentielles » et « Importantes » du cahier des charges, propres et testées. Les fonctionnalités « Bonus » sont hors périmètre sauf demande explicite ; la documentation Swagger/OpenAPI fait exception : elle est demandée dès le début (voir section 6).
- L'auteur doit pouvoir **expliquer et défendre chaque ligne** du code.
- Références : `docs/enonce.md` (cahier des charges), `docs/diagramme_classes.svg` et `docs/diagramme_classes.md` (conception). **Le diagramme fait foi.** Ne t'en écarte pas sans le dire et sans proposer sa mise à jour.

## 2. Façon de travailler avec l'auteur (mode apprentissage)

L'auteur veut **comprendre**, pas recevoir une solution toute faite.

1. **Avant de coder**, annonce en 2 ou 3 lignes ce que tu vas faire et pourquoi.
2. **Petits pas** : un comportement métier à la fois. Pas de gros bloc de code d'un coup.
3. **Explique** toute notion non triviale (en français, avec un exemple court) dès qu'elle apparaît.
4. **Les choix de conception appartiennent à l'auteur.** Présente les options et leurs compromis, recommande si on te le demande, mais **ne tranche pas seul** (voir ci-dessous et section 10).
5. Si l'auteur dit ne pas comprendre, **reformule autrement** (analogie, exemple concret) avant d'avancer.
6. Ne construis jamais le projet entier d'un coup. Avance cycle par cycle.

### Pour chaque nouvelle fonctionnalité : deux approches, puis le choix de l'auteur

Est une « nouvelle fonctionnalité » tout nouveau comportement métier, endpoint ou choix structurant. Les retouches triviales (renommage, faute de frappe, mise à jour de docstring) n'en font pas partie.

1. **Présente au moins deux approches d'implémentation** réellement différentes (pas deux variantes cosmétiques). Pour chacune, de façon **concise** (une dizaine de lignes au total, pas un essai) : le principe, les avantages, les inconvénients ou risques, les couches touchées et l'impact sur les tests.
2. **Attends le choix de l'auteur.** Ne code rien tant qu'il n'a pas choisi. S'il retient une approche hybride ou différente, reformule-la pour confirmer.
3. **Vérifie qu'on est sur la même longueur d'onde avant de coder** : reformule en 2 ou 3 lignes l'approche retenue, les couches concernées et le premier test que tu vas écrire, puis demande confirmation.
4. **Fais comprendre le code généré.** Après chaque cycle, explique le code produit en langage simple (ligne par ligne pour les parties non triviales), puis **vérifie la compréhension** avec **une question courte** à laquelle l'auteur peut répondre (ex. « pourquoi ce paramètre est-il passé en argument ? »). Si la réponse est fausse ou incomplète, reformule autrement avant de continuer. **Ne passe pas au cycle suivant** tant que l'auteur ne confirme pas avoir compris.

## 3. TDD obligatoire

**Aucun code de production n'est écrit sans un test rouge qui le justifie.**

Cycle à respecter, pour chaque comportement, **une fois l'approche choisie par l'auteur** (voir section 2) :

1. **Dire** le comportement visé en une phrase métier (ex. « un lecteur ne peut pas avoir plus de 3 réservations actives »).
2. **Red** : écrire **un seul** test, le lancer, et montrer qu'il **échoue pour la bonne raison** (pas une faute de frappe ou un import manquant).
3. **Green** : écrire le **code minimal** qui fait passer ce test, rien de plus.
4. **Refactor** : nettoyer (nommage, duplication) et mettre les docstrings à jour, en gardant tous les tests verts.
5. **Commit** (voir section 9) : un commit par cycle vert.

Règles associées :

- Ordre des couches : **domaine → services (avec dépôts en mémoire) → infrastructure Django → web**.
- Corriger un bug = **d'abord un test qui l'exhibe**, puis la correction.
- On ne modifie un test existant que si le **comportement attendu a changé**, et on le dit explicitement. Jamais pour « faire passer ».
- Interdits : `skip`, `xfail`, tests commentés, assertions affaiblies pour obtenir du vert.
- **Exécute réellement les tests** et rapporte leur sortie réelle. Ne dis jamais « les tests passent » sans les avoir lancés.

## 4. Architecture

Quatre couches. Les dépendances vont **toujours vers l'intérieur**.

```
web  →  infrastructure  →  application  →  domaine
```

| Couche | Dossier | Contenu | Interdit |
|---|---|---|---|
| Domaine | `src/domaine/` | Entités (`Livre`, `Lecteur`, `Reservation`), énumération `StatutReservation`, erreurs du domaine. Règles métier. | Django, HTTP, base de données, lecture de l'heure système |
| Application | `src/application/` | Services (`ServiceLivre`, `ServiceReservation`, `ServiceLecteur`), interfaces de dépôt, interface `Horloge` | Django, HTTP, ORM |
| Infrastructure | `src/infrastructure/` | Modèles Django, dépôts Django (`DepotXxxDjango`), `HorlogeSysteme`, conversion modèle ↔ entité | Règles métier |
| Web | `src/web/` | Contrôleurs, sérialisation, routes, documentation OpenAPI, traduction erreurs du domaine → codes HTTP | Règles métier, accès direct aux modèles |

Tests : `tests/domaine/`, `tests/application/`, `tests/infrastructure/`, `tests/web/`.

**Qui fait quoi**

- **Entités** : portent leurs données **et** leurs règles (validation métier, transitions d'état). Elles reçoivent l'heure **en paramètre** (`estExpiree(maintenant)`), elles ne la lisent jamais.
- **Services** : orchestrent un cas d'usage, appliquent les règles qui dépassent une entité (ex. quota de 3), **appellent `Horloge.maintenant()`** puis passent l'heure aux entités.
- **Dépôts (interfaces)** : contrats sans code. Les **dépôts Django** les réalisent et convertissent modèle ↔ entité.
- **Modèles Django** : de simples descriptions de tables. Seuls les dépôts Django les voient. Services et dépôts échangent des **entités pures**.
- **Contrôleurs** : valident la **forme** de la requête, appellent **un** service, traduisent les erreurs. Rien d'autre.

**Un test d'architecture est obligatoire** : il échoue si un fichier de `domaine/` ou `application/` importe `django`, ou appelle `datetime.now()`, `date.today()`, `time.time()` ou `timezone.now()`.

## 5. Règles du domaine

- **Pas de champ « disponible » stocké.** La disponibilité d'un livre se **déduit** des réservations actives.
- **RG1** : au plus **une réservation active par livre**, garantie **par la base** (contrainte d'unicité), pas seulement par un test préalable dans le code.
- **RG2** : au plus **3 réservations actives par lecteur**, vérifiée par le service. Cette vérification doit rester correcte en cas de demandes simultanées du même lecteur : y penser, et en parler avant de choisir la stratégie.
- **Cycle de vie** : `RESERVEE → EMPRUNTEE → RETOURNEE`, avec `ANNULEE` ou `EXPIREE` comme autres issues. **Toute transition invalide est refusée** par une erreur explicite levée par l'entité.
- **Expiration** : une réservation non retirée sous **48 h** expire et libère le livre. Testable grâce à `HorlogeFictive.avancer(durée)`.
- **Horloge injectée** partout. `HorlogeSysteme` en production, `HorlogeFictive` dans les tests.
- **Suppression logique** pour `Livre` et `Lecteur` (`dateSuppression`). L'e-mail d'un lecteur est unique parmi les non supprimés.
- **Bug du pseudo-code du cahier des charges** : ne jamais reproduire le schéma « vérifier puis écrire en deux temps ». La correction doit avoir un **test de concurrence** (deux demandes simultanées sur le même livre).

## 6. Bonnes pratiques de code

- **Nommage explicite**, orienté métier. Identifiants en **français sans accent** (`reserver`, `annee_publication`, `duree`), `snake_case` pour fonctions et variables, `PascalCase` pour les classes, comme dans le diagramme.
- **Fonctions courtes**, une seule responsabilité, un seul niveau d'abstraction.
- **Aucune duplication** : factorise dès la deuxième occurrence **identique**, pas avant.
- **Responsabilités séparées** : voir la section 4.
- **Simplicité d'abord** : la solution la plus simple qui fait passer les tests et respecte l'architecture. Pas de motif de conception « au cas où ».
- **Erreurs explicites, jamais silencieuses** : pas de `except: pass`, pas de `return None` pour signaler une erreur, pas de valeur magique.
- **Erreurs du domaine** : une petite hiérarchie d'exceptions (`ErreurDomaine` et ses sous-classes : validation, conflit, introuvable). Le domaine **ne connaît pas HTTP** ; une **seule** fonction côté web les traduit en codes (201, 404, 409, 422…) et en messages exploitables.
- **Commentaires** : seulement pour le « pourquoi », jamais pour répéter le code. Pas de code mort, pas de `TODO` orphelin.
- **Annotations de type** sur le code public.

### Docstrings en français

Les docstrings expliquent **ce que fait** le code, **pourquoi**, et **ce qui peut mal se passer**. Elles sont écrites **en français**, claires et nettes.

- **Début de chaque module** (dans `src/`) : une docstring en tête de fichier. Première ligne = rôle du module ; puis, si utile, 1 à 3 lignes sur sa place dans l'architecture (couche, collaborateurs). Dans `tests/`, une seule ligne suffit.
- **Chaque classe** : sa responsabilité, ses invariants ou règles importantes, et ses collaborateurs si ce n'est pas évident.
- **Chaque fonction ou méthode publique** dont le comportement ne se lit pas entièrement dans le nom : ce qu'elle fait, ses paramètres (`Args`), ce qu'elle retourne (`Returns`), les erreurs qu'elle lève (`Raises`) et la règle de gestion concernée (RG1, RG2…). Les fonctions privées triviales et les tests n'ont pas besoin de docstring : le nom du test décrit déjà le comportement.
- **Format** : style Google (sections `Args:`, `Returns:`, `Raises:`). Première ligne = résumé court à l'indicatif, puis une ligne vide, puis les détails.
- **Ce n'est pas un commentaire** : la docstring documente le contrat, elle ne décrit pas l'implémentation et ne paraphrase pas le code. Elle est **mise à jour avec le code**, dans le même cycle TDD (étape Refactor).

### Documentation de l'API (Swagger / OpenAPI)

- La documentation **Swagger/OpenAPI est configurée dès le début** du projet, **avant le premier endpoint** : elle fait partie du squelette du dépôt.
- Un test du squelette vérifie que le **schéma OpenAPI se génère sans erreur**.
- **Chaque endpoint est documenté dès sa création** : description, paramètres, corps de requête, réponses avec leurs **codes HTTP** (succès et erreurs) et format des messages d'erreur.
- L'interface Swagger est accessible une fois l'application lancée avec `docker compose` ; son URL est indiquée dans le `README.md`.
- Un endpoint ajouté ou modifié **sans mise à jour de la documentation** n'est pas terminé.

## 7. Tests : ce qu'on attend

- **Le nom du test décrit le comportement métier** : `test_un_lecteur_ne_peut_pas_avoir_plus_de_trois_reservations_actives`.
- Structure **Given / When / Then** (ou Arrange / Act / Assert), lisible sans commentaires.
- **Tests de domaine et de services** : rapides, **sans base de données**, avec des dépôts en mémoire (faux simples écrits à la main) et `HorlogeFictive`.
- **Ne jamais mocker le domaine** (entités, services). On teste le comportement, pas l'implémentation.
- **Tests d'infrastructure** : sur une vraie base, pour les dépôts Django, la conversion modèle ↔ entité et les contraintes (RG1, unicité de l'e-mail).
- **Test de concurrence** pour le bug : il doit **échouer sans la correction** et **passer avec**. Il exige une base qui supporte de vraies transactions concurrentes.
- **Tests web** : codes HTTP et messages d'erreur de chaque cas (201, 404, 409, 422).
- Un test = une raison d'échouer.

## 8. Docker

- L'application **et** les tests se lancent via `docker compose` depuis un dépôt fraîchement cloné, sans installation locale.
- Les commandes courantes (lancer, tester, migrer) sont documentées dans le `README.md`.
- Aucun secret ni mot de passe en dur : variables d'environnement, avec un `.env.example` versionné.

## 9. Git

- **Un commit = un cycle TDD vert** (le test et le code qui le fait passer, ensemble).
- Messages en français, au format **Conventional Commits** : `feat(domaine): refuser l'emprunt d'une réservation annulée`, `test(application): couvrir le quota de trois réservations`, `refactor(...)`, `docs(...)`, `chore(...)`.
- **Jamais** de commit fourre-tout, de message `wip` / `fix` / `test`, ni de code non testé.
- Ne réécris pas l'historique publié. Ne modifie pas une migration déjà commitée : crées-en une nouvelle.
- L'historique doit se lire comme le récit du développement : chaque commit raconte une étape.

### Nommage des branches

Les branches suivent le même découpage que les Conventional Commits : `<scope>/<description-en-kebab-case>`.

| Scope | Exemples de branches |
|---|---|
| `domaine` | `domaine/statut-et-erreurs`, `domaine/entite-livre` |
| `application` | `application/horloge-et-depots`, `application/service-reservation` |
| `infrastructure` | `infrastructure/modeles-et-migrations`, `infrastructure/depots-django` |
| `web` | `web/endpoints-livres`, `web/traduction-erreurs` |
| `chore` | `chore/configuration-docker` |
| `docs` | `docs/readme` |

- Une branche = un cycle de développement.
- On merge sur `main` uniquement quand tous les tests sont verts et la définition de « terminé » (section 12) est satisfaite.
- On ne travaille jamais directement sur `main`.

## 10. Décisions ouvertes : à ne pas trancher seul

Ne choisis pas à la place de l'auteur. Pose la question, présente les options et les compromis.

- **Base de données** (doit permettre une unicité conditionnelle pour RG1, ou prévoir un contournement)
- **Expiration** : job planifié ou vérification à l'opération (impact sur RG1)
- **Définition d'« active »** : `RESERVEE` seule, ou `RESERVEE` + `EMPRUNTEE`
- **Transitions permises** pour `annuler` et `expirer`
- **Code HTTP du dépassement de quota** : 409 ou 422
- **Unicité de l'e-mail** parmi les non supprimés
- **Outil de génération Swagger/OpenAPI**

## 11. À ne jamais faire

- Écrire du **code de production avant un test rouge**.
- Ajouter des fonctionnalités, outils ou dépendances qui ne sont **pas demandés** (sur-ingénierie).
- Laisser un module, une classe ou une méthode publique **sans docstring**, ou écrire une docstring **en anglais** ou qui se contente de répéter le code.
- Ajouter ou modifier un endpoint **sans mettre à jour la documentation Swagger**.
- Mettre une **règle métier** dans un contrôleur, un modèle Django ou un dépôt.
- **Importer Django** dans `domaine/` ou `application/`.
- Lire l'heure **hors** de `Horloge` (`datetime.now()`, `timezone.now()`, etc.).
- **Stocker** un booléen « disponible ».
- Faire « vérifier puis écrire » sans **contrainte en base ou transaction**.
- **Avaler** une exception, ou renvoyer un code HTTP sans message exploitable.
- **Mocker** le domaine, ou tester l'implémentation plutôt que le comportement.
- Utiliser des noms vagues (`data`, `tmp`, `manager`, `helper`, `utils`) ou des fonctions de plus de ~15 lignes sans raison.
- **Inventer** une bibliothèque, une fonction ou une option : si tu n'es pas sûr, dis-le et vérifie dans la documentation.
- Ajouter une **dépendance** sans l'annoncer et la justifier.
- **Affirmer** qu'un test passe, qu'un fichier existe ou qu'une commande marche sans l'avoir exécutée.
- Modifier des fichiers **hors du périmètre** de la tâche en cours.
- Livrer du code que l'auteur **ne comprend pas** : si c'est le cas, on s'arrête et on explique.
- Implémenter une nouvelle fonctionnalité **sans avoir présenté au moins deux approches** et obtenu le **choix de l'auteur**.
- Enchaîner sur le cycle suivant **sans avoir vérifié la compréhension** du code qui vient d'être généré.

## 12. Définition de « terminé » pour un comportement

- [ ] Le test a été vu **rouge**, puis **vert**.
- [ ] Tous les tests existants restent verts.
- [ ] Le test d'architecture passe.
- [ ] Le nommage est clair, pas de duplication, pas de code mort.
- [ ] Les docstrings (module, classes, méthodes publiques) sont à jour et en français.
- [ ] Si un endpoint a été touché, la documentation Swagger est à jour.
- [ ] Le commit est petit, cohérent, avec un message clair.
- [ ] L'approche a été **choisie par l'auteur** parmi au moins deux propositions.
- [ ] L'auteur peut **expliquer le code** sans le relire, et la compréhension a été vérifiée.
- [ ] Si une décision a été prise, elle est notée pour le `README.md` (section « décisions et compromis »).
