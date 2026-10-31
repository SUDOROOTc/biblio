"""Test d'architecture du projet Biblio.

Vérifie que les couches domaine et application restent pures :
- pas d'import django
- pas d'appel à datetime.now(), date.today(), time.time() ou timezone.now()
"""

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COUCHES_PURES = [PROJECT_ROOT / "src" / "domaine", PROJECT_ROOT / "src" / "application"]


def _verifier_fichier(chemin: Path) -> list[str]:
    erreurs = []
    contenu = chemin.read_text(encoding="utf-8")
    arbre = ast.parse(contenu, filename=str(chemin))

    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            for alias in noeud.names:
                if alias.name.split(".")[0] == "django":
                    erreurs.append(f"{chemin}: import interdit '{alias.name}'")
        elif isinstance(noeud, ast.ImportFrom):
            if noeud.module and noeud.module.split(".")[0] == "django":
                erreurs.append(f"{chemin}: import interdit depuis '{noeud.module}'")
        elif isinstance(noeud, ast.Call):
            if isinstance(noeud.func, ast.Attribute):
                nom = noeud.func.attr
                if nom in {"now", "today", "time"}:
                    erreurs.append(f"{chemin}: appel interdit '{nom}()'")
            elif isinstance(noeud.func, ast.Name):
                nom = noeud.func.id
                if nom in {"now", "today", "time"}:
                    erreurs.append(f"{chemin}: appel interdit '{nom}()'")

    return erreurs


@pytest.mark.parametrize("couche", COUCHES_PURES)
def test_couches_domaine_et_application_restent_pures(couche):
    erreurs = []
    for fichier in couche.rglob("*.py"):
        if fichier.name == "__init__.py":
            continue
        erreurs.extend(_verifier_fichier(fichier))
    assert not erreurs, "\n".join(erreurs)
