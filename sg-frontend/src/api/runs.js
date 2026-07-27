import { apiFetch } from "./client";

export function createRun(payload) {
  return apiFetch("/runs/", {
    // mode:"no-cors",
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listRuns() {
  return apiFetch("/runs/");
}

export function getRun(id) {
  return apiFetch(`/runs/${id}/`);
}