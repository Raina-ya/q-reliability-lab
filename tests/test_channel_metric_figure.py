from PIL import Image

from src.channel_metric_matrix import channel_metric_matrix, write_heatmap


def test_channel_metric_heatmap_is_generated_from_the_matrix_rows(tmp_path):
    output = tmp_path / "channel_metric_sensitivity_matrix.png"
    write_heatmap(channel_metric_matrix(), output)

    with Image.open(output) as image:
        assert image.size[0] > image.size[1] > 0
