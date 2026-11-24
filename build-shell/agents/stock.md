# Stock — Availability & Options Agent (stub)

Joule Studio agent configuration notes. Configured, not coded.

- **Role:** Investigate part availability across stations and present options
  (transfer, expedite, reschedule) with each source labelled verified or
  unverified.
- **Inputs:** Part requirement from the work order; stock picture from governed
  data (BDC) with relationships from the Knowledge Graph; each station's last
  sync time.
- **Tools:** Read stock and station sync status; propose a StockReservation
  (proposal only — execution belongs to the application after human approval).
- **Guardrails:** Every figure it presents carries its verification status and
  last-sync time. It does not hide unverified options; it labels them.
- **Must never:** Turn stale data into confirmed stock. An unverified line
  (e.g. a station not synced in 26 hours) can never be presented, proposed, or
  approved as confirmed availability.
