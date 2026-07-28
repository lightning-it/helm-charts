#!/usr/bin/env bash
set -euo pipefail

found=0
for chart in charts/*; do
  if [ ! -f "$chart/Chart.yaml" ]; then
    continue
  fi
  found=1
  echo "Validating $chart"
  helm lint "$chart"
  helm template lit-quality "$chart" >/dev/null
done

if [ "$found" -ne 1 ]; then
  echo "ERROR: no product charts found under charts/." >&2
  exit 1
fi
