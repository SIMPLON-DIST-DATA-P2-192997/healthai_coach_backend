"""Exemple de référence : mocker un appel HTTP externe dans un test pytest.

Objectif pédagogique pour l'équipe ETL — ne jamais appeler une vraie API
(ExerciseDB, Kaggle...) dans un test unitaire : c'est lent, ça dépend du
réseau en CI, et le contenu réel peut changer sous nos pieds.

`fetch_exercises_page` ci-dessous est une fonction de démonstration, pas
le vrai client ETL. L'idée à retenir est de structurer les appels HTTP en
fonctions (plutôt qu'en code de niveau module, comme actuellement dans
etl/extract/extract.py) pour pouvoir les mocker facilement : on remplace
`requests.get` par un faux objet le temps du test, avec `monkeypatch`
(fixture pytest core) + `unittest.mock.Mock` pour construire la fausse
réponse.

Pagination réelle de l'API ExerciseDB : `after=<exerciseId>`, pas
`nextCursor` (cf. l'OpenAPI spec sur /swagger, qui fait foi).

Alternative à ce patron : la librairie `responses` (mock par URL/méthode)
ou `vcrpy`/`pytest-recording` (rejoue une vraie réponse enregistrée une
fois) — utiles si on veut éviter d'écrire le payload de test à la main.
Pas nécessaire ici, `unittest.mock` seul suffit pour ce cas.
"""
from unittest.mock import Mock

import pytest
import requests

EXERCISEDB_URL = "https://oss.exercisedb.dev/api/v1/exercises"


def fetch_exercises_page(after: str | None = None, limit: int = 25) -> dict:
    """Récupère une page d'exercices depuis ExerciseDB."""
    params = {"limit": limit}
    if after:
        params["after"] = after
    response = requests.get(EXERCISEDB_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


FAKE_PAGE = {
    "data": [
        {"exerciseId": "0001", "name": "3/4 sit-up", "bodyParts": ["waist"]},
        {"exerciseId": "0002", "name": "45 degree side bend", "bodyParts": ["waist"]},
    ],
    "meta": {"hasNextPage": True},
}


def _fake_get(expected_params, response_json, status_ok=True):
    """Construit un faux `requests.get` : mêmes paramètres attendus, réponse figée."""

    def fake_get(url, params=None, timeout=None):
        assert params == expected_params
        mock_response = Mock()
        mock_response.json.return_value = response_json
        if status_ok:
            mock_response.raise_for_status.return_value = None
        else:
            mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        return mock_response

    return fake_get


def test_fetch_exercises_page_parses_response(monkeypatch):
    monkeypatch.setattr(requests, "get", _fake_get({"limit": 25}, FAKE_PAGE))

    result = fetch_exercises_page(limit=25)

    assert result == FAKE_PAGE


def test_fetch_exercises_page_sends_after_param_for_pagination(monkeypatch):
    monkeypatch.setattr(
        requests, "get", _fake_get({"limit": 25, "after": "0002"}, FAKE_PAGE)
    )

    fetch_exercises_page(after="0002", limit=25)
    # Si `after` n'était pas transmis (ou sous le mauvais nom, ex.
    # `nextCursor`), l'assertion dans _fake_get aurait échoué avant même
    # d'arriver ici.


def test_fetch_exercises_page_raises_on_http_error(monkeypatch):
    monkeypatch.setattr(
        requests, "get", _fake_get({"limit": 25}, {}, status_ok=False)
    )

    with pytest.raises(requests.HTTPError):
        fetch_exercises_page(limit=25)
