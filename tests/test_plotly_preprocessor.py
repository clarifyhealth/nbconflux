import base64
import nbformat
import pytest
from unittest.mock import patch, MagicMock
from nbconvert.preprocessors import TagRemovePreprocessor

from nbconflux.plotly_preprocessor import PlotlyStaticPreprocessor

PLOTLY_HTML = (
    "<div id='p'></div>"
    "<script>Plotly.newPlot('p', [{'type': 'bar', 'x': [1], 'y': [1]}], {}, {})</script>"
)

FAKE_PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20


def _make_cell(*outputs):
    cell = nbformat.v4.new_code_cell()
    cell.outputs = list(outputs)
    return cell


def _make_nb(*cells):
    nb = nbformat.v4.new_notebook()
    nb.cells = list(cells)
    return nb


def _run(nb):
    """Run preprocessor with mocked figure rendering (no kaleido needed)."""
    pp = PlotlyStaticPreprocessor()

    def fake_write_image(path, format):
        with open(path, "wb") as f:
            f.write(FAKE_PNG)

    with patch("nbconflux.plotly_preprocessor.go.Figure") as mock_fig_cls, \
         patch("nbconflux.plotly_preprocessor.os.remove"):
        mock_fig = MagicMock()
        mock_fig.layout.width = 800
        mock_fig.write_image.side_effect = fake_write_image
        mock_fig_cls.return_value = mock_fig

        return pp.preprocess(nb, {})


# --- filtering tests (no rendering needed) ---

def test_plotly_json_only_output_is_skipped():
    """Outputs with only application/vnd.plotly.v1+json should be dropped."""
    cell = _make_cell(
        nbformat.v4.new_output(
            output_type="display_data",
            data={"application/vnd.plotly.v1+json": {"data": [], "layout": {}}},
        )
    )
    pp = PlotlyStaticPreprocessor()
    result_nb, _ = pp.preprocess(_make_nb(cell), {})
    assert result_nb.cells[0].outputs == []


def test_non_plotly_image_is_preserved():
    """Regular image/png outputs (e.g. matplotlib) must not be removed."""
    png_b64 = base64.b64encode(FAKE_PNG).decode()
    cell = _make_cell(
        nbformat.v4.new_output(
            output_type="display_data",
            data={"image/png": png_b64},
        )
    )
    pp = PlotlyStaticPreprocessor()
    result_nb, _ = pp.preprocess(_make_nb(cell), {})
    assert len(result_nb.cells[0].outputs) == 1
    assert "image/png" in result_nb.cells[0].outputs[0].data


def test_non_plotly_html_is_preserved():
    """HTML outputs that don't contain Plotly.newPlot should pass through."""
    cell = _make_cell(
        nbformat.v4.new_output(
            output_type="display_data",
            data={"text/html": "<table><tr><td>hello</td></tr></table>"},
        )
    )
    pp = PlotlyStaticPreprocessor()
    result_nb, _ = pp.preprocess(_make_nb(cell), {})
    assert len(result_nb.cells[0].outputs) == 1
    assert "text/html" in result_nb.cells[0].outputs[0].data


# --- deduplication test (rendering mocked) ---

def test_plotly_html_with_json_fallback_produces_single_png():
    """A Plotly HTML output + a separate vnd.plotly.v1+json fallback should yield exactly one PNG."""
    cell = _make_cell(
        nbformat.v4.new_output(
            output_type="display_data",
            data={"text/html": PLOTLY_HTML},
        ),
        nbformat.v4.new_output(
            output_type="display_data",
            data={"application/vnd.plotly.v1+json": {"data": [], "layout": {}}},
        ),
    )
    result_nb, resources = _run(_make_nb(cell))
    outputs = result_nb.cells[0].outputs
    assert len(outputs) == 1, f"Expected 1 output, got {len(outputs)}"
    assert "image/png" in outputs[0].data
    assert base64.b64decode(outputs[0].data["image/png"]) == FAKE_PNG


def test_plotly_html_converted_to_png():
    """A Plotly HTML output should be replaced by a PNG display_data output."""
    cell = _make_cell(
        nbformat.v4.new_output(
            output_type="display_data",
            data={"text/html": PLOTLY_HTML},
        )
    )
    result_nb, resources = _run(_make_nb(cell))
    outputs = result_nb.cells[0].outputs
    assert len(outputs) == 1
    assert outputs[0].output_type == "display_data"
    assert "image/png" in outputs[0].data
    # PNG should also be stored in resources for attachment upload
    assert any(k.startswith("plotly_static_") for k in resources.get("outputs", {}))


# --- parameters tag tests ---

def test_parameters_cell_removed():
    """Cells tagged 'parameters' should be stripped from the notebook."""
    cell = nbformat.v4.new_code_cell(
        source='release_yr_mnth = "202603"\ndata_sources = ["iguana_v3"]'
    )
    cell.metadata["tags"] = ["parameters"]

    nb = _make_nb(cell)
    pp = TagRemovePreprocessor(remove_cell_tags={"parameters"})
    result_nb, _ = pp.preprocess(nb, {})

    assert result_nb.cells == []


def test_parameters_cell_content_not_in_output():
    """Parameter variable names must not appear alongside normal cell output."""
    params_cell = nbformat.v4.new_code_cell(
        source='release_yr_mnth = "202603"\ndata_sources = ["iguana_v3"]'
    )
    params_cell.metadata["tags"] = ["parameters"]

    normal_cell = nbformat.v4.new_code_cell(source='print("hello")')
    normal_cell.outputs = [
        nbformat.v4.new_output(output_type="stream", name="stdout", text="hello\n")
    ]

    nb = _make_nb(params_cell, normal_cell)
    pp = TagRemovePreprocessor(remove_cell_tags={"parameters"})
    result_nb, _ = pp.preprocess(nb, {})

    assert len(result_nb.cells) == 1
    assert result_nb.cells[0].source == 'print("hello")'
