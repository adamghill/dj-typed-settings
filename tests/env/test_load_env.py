import os

from dj_typed_settings.env import load_env


def test_load_env_upward_search(tmp_path, monkeypatch):
    # Setup:
    # project/
    #   manage.py
    #   .env (target)
    #   app/
    #     (CWD here)

    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "manage.py").touch()
    (project_dir / ".env").write_text("UPWARD_VAR=found\n")

    app_dir = project_dir / "app"
    app_dir.mkdir()

    monkeypatch.chdir(app_dir)

    if "UPWARD_VAR" in os.environ:
        del os.environ["UPWARD_VAR"]

    load_env()
    assert os.environ["UPWARD_VAR"] == "found"


def test_load_env_stops_at_manage_py(tmp_path, monkeypatch):
    # Setup:
    # project/
    #   .env (should NOT be found)
    #   subproject/
    #     manage.py
    #     app/
    #       (CWD here)

    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / ".env").write_text("DANGEROUS_VAR=wrong\n")

    subproject_dir = project_dir / "subproject"
    subproject_dir.mkdir()
    (subproject_dir / "manage.py").touch()

    app_dir = subproject_dir / "app"
    app_dir.mkdir()

    monkeypatch.chdir(app_dir)

    if "DANGEROUS_VAR" in os.environ:
        del os.environ["DANGEROUS_VAR"]

    load_env()
    assert "DANGEROUS_VAR" not in os.environ
