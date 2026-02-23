import pytest
from unittest.mock import patch, ANY

from docker_explorer_tui.app import (
    DockerExplorerApp,
    ContainerListScreen,
    _calc_cpu,
    _calc_mem,
)


class TestCalculations:
    def test_cpu_calculation(self) -> None:
        stats = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 20000, "percpu_usage": [5000, 15000]},
                "system_cpu_usage": 100000,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 0},
                "system_cpu_usage": 0,
            },
        }
        assert _calc_cpu(stats) == 35.0  # (20k/100k)*2 cpus *100

    def test_mem_calculation(self) -> None:
        stats = {"memory_stats": {"usage": 256 * 1024**2, "limit": 1024 * 1024**2}}
        assert _calc_mem(stats) == 25.0

    def test_cpu_zero_delta(self) -> None:
        stats = {
            "cpu_stats": {"cpu_usage": {"total_usage": 0}, "system_cpu_usage": 0},
            "precpu_stats": {"cpu_usage": {"total_usage": 0}, "system_cpu_usage": 0},
        }
        assert _calc_cpu(stats) == 0.0

    def test_mem_unlimited(self) -> None:
        stats = {"memory_stats": {"usage": 100, "limit": 0}}
        assert _calc_mem(stats) == 0.0


class TestAppIntegration:
    @pytest.mark.asyncio
    @patch("docker_explorer_tui.docker.from_env")
    async def test_docker_connect_fail(self, mock_from_env: Mock) -> None:
        mock_from_env.side_effect = Exception("No daemon")
        app = DockerExplorerApp()
        with pytest.raises(SystemExit):
            await app.run_async()

    @pytest.mark.asyncio
    @patch("docker_explorer_tui.docker.from_env")
    async def test_screen_mount_refresh(self, mock_from_env, mock_client) -> None:
        mock_from_env.return_value = mock_client
        app = DockerExplorerApp()
        await app.run_async(initial=False)
        screen = ContainerListScreen(mock_client)
        await screen.on_mount()
        mock_client.containers.list.assert_called_once()

    def test_action_start_success(self, mock_client, mock_container) -> None:
        screen = ContainerDetailScreen(mock_container, mock_client)
        screen.action_start()
        mock_container.start.assert_called_once()

    def test_action_remove_confirm(self, mock_client, mock_container) -> None:
        screen = ContainerDetailScreen(mock_container, mock_client)
        with patch.object(screen.app, "confirm", return_value=True):
            screen.action_remove()
        mock_container.remove.assert_called_once_with(force=True)

    def test_action_remove_deny(self, mock_client, mock_container) -> None:
        screen = ContainerDetailScreen(mock_container, mock_client)
        with patch.object(screen.app, "confirm", return_value=False):
            screen.action_remove()
        mock_container.remove.assert_not_called()