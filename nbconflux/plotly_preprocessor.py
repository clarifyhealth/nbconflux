import re
import ast
import uuid
import base64
import plotly.graph_objects as go
import plotly.io as pio
from nbconvert.preprocessors import Preprocessor
from nbformat.v4 import new_output


class PlotlyStaticPreprocessor(Preprocessor):
    """
    Converts interactive Plotly JS outputs into static PNG images for nbconvert.
    """

    NEWPLOT_PATTERN = re.compile(
        r"Plotly\.newPlot\s*\(\s*"
        r"(?P<id>'[^']+'|\"[^\"]+\")\s*,\s*"
        r"(?P<data>\[[\s\S]*?\])\s*,\s*"
        r"(?P<layout>\{[\s\S]*?\})"
        r"(?:\s*,\s*(?P<config>\{[\s\S]*?\}))?"
        r"\s*\)",
        flags=re.MULTILINE,
    )

    @staticmethod
    def _fix_js(js: str) -> str:
        """Convert JS syntax to valid Python syntax."""
        return (
            js.replace("null", "None")
               .replace("true", "True")
               .replace("false", "False")
        )

    def extract_plotly_json(self, html: str):
        """Parse Plotly.newPlot(...) content from HTML."""
        match = self.NEWPLOT_PATTERN.search(html)
        if not match:
            return None
        fix = self._fix_js
        try:
            data = ast.literal_eval(fix(match.group("data")))
            layout = ast.literal_eval(fix(match.group("layout")))
            cfg_str = match.group("config")
            config = ast.literal_eval(fix(cfg_str)) if cfg_str else {}
            return {"data": data, "layout": layout, "config": config}
        except Exception as e:
            print(f"Plotly JSON parse failed: {e}")
            return None

    @staticmethod
    def normalize_heatmapgl(fig_json: dict):
        """Convert heatmapgl to heatmap for static PNG rendering."""
        for trace in fig_json.get("data", ()):
            if trace.get("type") == "heatmapgl":
                trace["type"] = "heatmap"

        layout = fig_json.get("layout", {})
        template = layout.get("template", {})

        data_template = template.get("data")
        if isinstance(data_template, dict):
            template["data"] = {
                ("heatmap" if k == "heatmapgl" else k): v
                for k, v in data_template.items()
            }

        layout["template"] = template
        fig_json["layout"] = layout


    def preprocess(self, nb, resources):
        """Main nbconvert hook. Replaces Plotly JS with static PNG output."""
        resources = resources or {}
        outputs_store = resources.setdefault("outputs", {})

        for cell in nb.cells:
            if cell.cell_type != "code":
                continue

            new_outputs = []
            for out in cell.get("outputs", []):

                html = out.get("data", {}).get("text/html")
                if not html:
                    new_outputs.append(out)
                    continue

                fig_json = self.extract_plotly_json(html)
                if not fig_json:
                    new_outputs.append(out)
                    continue

                self.normalize_heatmapgl(fig_json)
                try:
                    fig = go.Figure(
                        data=fig_json["data"],
                        layout=fig_json.get("layout", {})
                    )
                    png_bytes = pio.to_image(fig, format="png")
                except Exception as e:
                    print(f"Plotly to PNG conversion failed: {e}")
                    new_outputs.append(out)
                    continue

                fname = f"plotly_static_{uuid.uuid4().hex}.png"
                outputs_store[fname] = png_bytes
                png_b64 = base64.b64encode(png_bytes).decode()

                new_outputs.append(
                    new_output(
                        output_type="display_data",
                        data={"image/png": png_b64},
                        metadata={
                            "image/png": {
                                "width": fig.layout.width or 700
                            }
                        },
                    )
                )
            cell["outputs"] = new_outputs

        return nb, resources