import { phaseFlipMetrics } from "./model.mjs";

const slider = document.querySelector("#probability");
const probabilityLabel = document.querySelector("#probability-label");
const successLabel = document.querySelector("#selected-success");
const fidelityLabel = document.querySelector("#fidelity");
const coherenceLabel = document.querySelector("#coherence");
const matrix = document.querySelector("#density-matrix");

function format(value) {
  return Number(value).toFixed(3);
}

function render() {
  const probability = Number(slider.value);
  const basis = document.querySelector("input[name=basis]:checked").value;
  const model = phaseFlipMetrics(probability);
  const selectedSuccess = basis === "Z" ? model.zBasisSuccess : model.xBasisSuccess;

  probabilityLabel.textContent = format(probability);
  successLabel.textContent = `${basis}-basis correlated success: ${format(selectedSuccess)}`;
  fidelityLabel.textContent = format(model.fidelity);
  coherenceLabel.textContent = format(model.coherence);
  matrix.replaceChildren(
    ...model.densityMatrix.flatMap((row) => row.map((value) => {
      const cell = document.createElement("span");
      cell.textContent = format(value);
      return cell;
    })),
  );
}

slider.addEventListener("input", render);
document.querySelectorAll("input[name=basis]").forEach((input) => input.addEventListener("change", render));
render();
