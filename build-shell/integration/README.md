# integration/ — Integration & Context Services (stub)

Integration Suite + Business Data Cloud + Knowledge Graph. Notes only; no
flows are built or deployed.

## Integration Suite flows (planned)

- **Tablet sync (API):** tablet → CAP application. Offline records post when
  in coverage; validation and conflict handling happen in `app/`.
- **Stock events (event):** a PartUsage posting emits a stock-changed event so
  stock readers never rely on a pre-sync picture (the phantom-stock lesson).
- **Reservation execution (API):** after human approval, the application posts
  the reservation and transfer to the system of record.
- **S/4HANA reads (API):** work orders, inventory, equipment, contracts/SLAs —
  in this shell, simulated by `../data/` only. No real connection exists.

## Context the agents read

- **Business Data Cloud (BDC):** governed data — the stock picture, station
  sync status, equipment and job data, with consistent definitions. Agents
  read governed data, never raw or stale extracts.
- **Knowledge Graph:** business relationships — which part fits which
  equipment, which stations can serve which sites, part → equipment → contract
  links. Context tells the agents what things mean; BDC tells them the facts.
