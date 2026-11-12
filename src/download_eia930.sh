#!/usr/bin/env bash
# Resumable download of EIA-930 six-month BALANCE files (public domain, US EIA).
# Usage: bash src/download_eia930.sh   (run from paper_A)
set -u
OUT="data/raw/eia930"
mkdir -p "$OUT"
BASE="https://www.eia.gov/electricity/gridmonitor/sixMonthFiles"
files=("EIA930_BALANCE_2018_Jul_Dec.csv")
for y in 2019 2020 2021 2022 2023 2024 2025; do
  files+=("EIA930_BALANCE_${y}_Jan_Jun.csv" "EIA930_BALANCE_${y}_Jul_Dec.csv")
done
files+=("EIA930_BALANCE_2026_Jan_Jun.csv")
for f in "${files[@]}"; do
  remote=$(curl -sI -A "Mozilla/5.0" "$BASE/$f" | tr -d '\r' | awk 'tolower($1)=="content-length:"{print $2}')
  for attempt in 1 2 3 4 5 6; do
    local_size=$( [ -f "$OUT/$f" ] && stat -c %s "$OUT/$f" || echo 0 )
    if [ -n "$remote" ] && [ "$local_size" = "$remote" ]; then break; fi
    curl -s -L -A "Mozilla/5.0" -C - --retry 5 --retry-delay 10 --max-time 900 -o "$OUT/$f" "$BASE/$f"
    sleep 2
  done
  local_size=$( [ -f "$OUT/$f" ] && stat -c %s "$OUT/$f" || echo 0 )
  echo "$(date '+%F %T') $f local=$local_size remote=$remote"
done
(cd "$OUT" && sha256sum EIA930_BALANCE_*.csv > SHA256SUMS.txt)
echo "DONE"
