import pytest
from dagster_dbt import (
    dbt_cli_compile,
    dbt_cli_docs_generate,
    dbt_cli_run,
    dbt_cli_run_operation,
    dbt_cli_seed,
    dbt_cli_snapshot,
    dbt_cli_snapshot_freshness,
    dbt_cli_test,
)
from dagster_dbt.errors import DagsterDbtCliFatalRuntimeError

from dagster import configured, execute_solid


class TestDbtCliSolids:
    def test_dbt_cli_with_unset_env_var_in_profile(
        self, dbt_seed, test_project_dir, dbt_config_dir, monkeypatch
    ):  # pylint: disable=unused-argument

        monkeypatch.delenv("POSTGRES_TEST_DB_DBT_HOST")
        test_solid = configured(dbt_cli_run, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )
        with pytest.raises(DagsterDbtCliFatalRuntimeError) as exc:
            execute_solid(test_solid)

        failure: DagsterDbtCliFatalRuntimeError = exc.value
        expected_str = "Env var required but not provided:"
        assert (
            expected_str in str(failure.metadata_entries[0].entry_data.data)
            or expected_str in failure.metadata_entries[1].entry_data.text
        )

    def test_dbt_cli_run(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_run, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )

        result = execute_solid(test_solid)
        assert result.success

        # Test asset materializations
        asset_materializations = [
            event
            for event in result.step_events
            if event.event_type_value == "ASSET_MATERIALIZATION"
        ]
        assert len(asset_materializations) == 4
        table_materializations = [
            materialization
            for materialization in asset_materializations
            if materialization.asset_key.path[0] == "model"
        ]
        assert len(table_materializations) == 4

    def test_dbt_cli_run_with_extra_config(
        self, dbt_seed, test_project_dir, dbt_config_dir, dbt_target_dir, monkeypatch
    ):  # pylint: disable=unused-argument

        # Specify dbt target path
        monkeypatch.setenv("DBT_TARGET_PATH", dbt_target_dir)

        test_solid = configured(dbt_cli_run, name="test_solid")(
            {
                "project-dir": test_project_dir,
                "profiles-dir": dbt_config_dir,
                "threads": 1,
                "models": ["least_caloric"],
                "target-path": dbt_target_dir,
                "fail-fast": True,
            }
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_test(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_test, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_test_with_extra_confg(
        self, dbt_seed, test_project_dir, dbt_config_dir, dbt_target_dir, monkeypatch
    ):  # pylint: disable=unused-argument

        # Specify dbt target path
        monkeypatch.setenv("DBT_TARGET_PATH", dbt_target_dir)

        test_solid = configured(dbt_cli_test, name="test_solid")(
            {
                "project-dir": test_project_dir,
                "profiles-dir": dbt_config_dir,
                "target-path": dbt_target_dir,
            }
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_snapshot(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_snapshot, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_snapshot_with_extra_config(
        self,
        dbt_seed,
        test_project_dir,
        dbt_config_dir,
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_snapshot, name="test_solid")(
            {
                "project-dir": test_project_dir,
                "profiles-dir": dbt_config_dir,
                "threads": 1,
                "select": ["sort_by_calories+"],
                "exclude": ["least_caloric"],
            },
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_run_operation(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_run_operation, name="test_solid")(
            {
                "project-dir": test_project_dir,
                "profiles-dir": dbt_config_dir,
                "macro": "log_macro",
                "args": {"msg": "<<test succeded!>>"},
            }
        )

        result = execute_solid(test_solid)
        assert result.success
        assert any(
            "Log macro: <<test succeded!>>" in log.get("message", log.get("msg", []))
            for log in result.output_value("dbt_cli_output").logs
        )

    def test_dbt_cli_snapshot_freshness(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        """This command will is a no-op without more arguments, but this test shows that it can invoked successfully."""
        test_solid = configured(dbt_cli_snapshot_freshness, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_compile(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_compile, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_docs_generate(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_docs_generate, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )

        result = execute_solid(test_solid)
        assert result.success

    def test_dbt_cli_seed(
        self, dbt_seed, test_project_dir, dbt_config_dir
    ):  # pylint: disable=unused-argument
        test_solid = configured(dbt_cli_seed, name="test_solid")(
            {"project-dir": test_project_dir, "profiles-dir": dbt_config_dir}
        )

        result = execute_solid(test_solid)
        assert result.success
