import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from scaffold_writing_setup import scaffold_setup
from writing_config import validate_catalog, validate_profile


def test_initial_setup_has_two_long_form_assets_and_no_primary(tmp_path):
    result = scaffold_setup(tmp_path, mode="initial")
    assert result.profile_path == tmp_path / "config/writing/writing-profile.yaml"
    assert result.catalog_path == tmp_path / "config/writing/writing-asset-catalog.yaml"
    assert result.primary_long_form_asset_type is None
    assert {"default-blog", "default-newsletter"} <= set(result.asset_type_ids)
    profile = yaml.safe_load(result.profile_path.read_text())
    catalog = yaml.safe_load(result.catalog_path.read_text())
    assert validate_profile(tmp_path, profile) == []
    assert validate_catalog(tmp_path, catalog) == []
    candidates = yaml.safe_load((tmp_path / "config/writing/exemplar-candidates.yaml").read_text())
    assert candidates["approved"] is False


def test_incremental_mode_preserves_existing_approved_configuration(tmp_path):
    first = scaffold_setup(tmp_path)
    first.profile_path.write_text("approved: true\n")
    second = scaffold_setup(tmp_path, mode="incremental")
    assert first.profile_path in second.preserved_paths
    assert first.profile_path.read_text() == "approved: true\n"
