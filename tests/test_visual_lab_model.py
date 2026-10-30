import json
import subprocess

import numpy as np

from src.phase_error_blind_spot import metrics


def test_javascript_visual_lab_model_matches_python_on_a_probability_grid():
    probabilities = [0.0, 0.25, 0.5, 0.75, 1.0]
    expression = (
        "import { phaseFlipMetrics } from './docs/model.mjs'; "
        f"console.log(JSON.stringify({json.dumps(probabilities)}.map(phaseFlipMetrics)));"
    )
    result = subprocess.run(
        ["node", "--input-type=module", "--eval", expression],
        check=True,
        capture_output=True,
        text=True,
    )
    browser_rows = json.loads(result.stdout)

    for probability, browser in zip(probabilities, browser_rows):
        python = metrics(probability)
        np.testing.assert_allclose(browser["zBasisSuccess"], python["success_probability"], atol=1e-12)
        np.testing.assert_allclose(browser["xBasisSuccess"], python["x_basis_success_probability"], atol=1e-12)
        np.testing.assert_allclose(browser["fidelity"], python["fidelity"], atol=1e-12)
        np.testing.assert_allclose(browser["coherence"], python["coherence_real"], atol=1e-12)
        np.testing.assert_allclose(browser["coherenceMagnitude"], python["coherence_magnitude"], atol=1e-12)
