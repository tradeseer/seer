# About the report

This report shares Seer's trading activity for August 17–21, 2026. Proprietary features, signal-selection logic, and model architecture have been withheld to protect the strategy's IP. The shared record includes timestamped decisions, trade execution logic, risk management, and modeled transaction costs.

## Files

- [`data/seer-anonymized.json`](../data/seer-anonymized.json): the original supplied export, byte-for-byte unchanged.
- [`index.html`](../index.html): readable performance summary, equity curve, daily results, stock results, and all 147 closed trades.
- [`replay.html`](../replay.html): the full week of decisions and trades, with the supplied price candles, source references, and a running capital total.
- [`data/SHA256SUMS`](../data/SHA256SUMS): checksum for the raw file.

## Reading the numbers

All amounts are USD. Timestamps are shown in America/New_York (Eastern Time).

The replay's Cash total is $10,000 plus cumulative closed-trade net P&L, including the export's modeled transaction costs. It updates when a trade closes. It is not the uninvested buying-power balance during an open position. The report's equity chart uses the export's equity marks, which also include open-position changes.

Win rate is winning trades divided by all closed trades. Profit factor is total winning-trade P&L divided by the absolute total losing-trade P&L. The reported 13.51% drawdown comes from the observed equity curve; it is distinct from the closed-trade cash drawdown.

## Replay and sources

Play runs all 147 trades in order. At 1×, the complete week takes eight minutes; the speed control, day navigation, and timeline let you explore the record. Playback time is compressed, while the displayed event timestamps come from the export.

Charts show only price candles included in the JSON. Missing intervals remain empty. News links are supporting context; their inclusion does not by itself establish why a trade was taken. Trade rationale and source relationships are available under “Reason & sources.”

The raw file retains its original metadata, price-reference fields, and execution assumptions. The presentation does not alter these fields or reconstruct withheld features.

## Run locally

Open `index.html` in a browser. Both views work without a server, account connection, or external JavaScript dependencies.

To rebuild the report and replay from the raw file, run `python3 scripts/build.py`. To verify the raw file, run `cd data && shasum -a 256 -c SHA256SUMS`.

## Assets

The Seer wordmark belongs to Seer. Geist is bundled under the [SIL Open Font License](../assets/geist-OFL.txt). No open-source license for the report, data, or proprietary strategy is assigned by this release.
