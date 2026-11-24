# Boreal Field Services — A Field-Service Scenario Across All Three Pillars

*Anahita's second study scenario for SAP Business AI Platform Architecture (C_BAIPA_2610), built 2026-11-19. Modelled on the shape of the one real predecessor-exam (P_BTPA) scenario a candidate described publicly — field-service engineers who must get and update data in S/4 systems while at customer sites — but the company, people, and numbers are original, fictional, and synthetic, created for learning. Companion to the TrueNorth AeroWorks scenario, not a replacement for it.*

---

## 1. The Company

Boreal Field Services maintains ground support equipment — ground power units, de-icing rigs, tugs, belt loaders — for airports across the north, many of them remote.

- About 140 field engineers covering 22 stations
- Roughly 6,500 service jobs a year, most of them at the customer's site, not in a workshop
- Connectivity ranges from hangar Wi-Fi to satellite links to nothing at all for hours at a time
- Systems landscape: SAP S/4HANA (cloud) for work orders, inventory, service contracts, and billing; engineers work on tablets; parts stock is held in small stores at each station

The company's reputation rests on one promise: **the equipment is running before the aircraft needs it.** In the north, a dead ground power unit is not an inconvenience. It can be the difference between a flight leaving and a community waiting, and some of those flights are medevac.

## 2. The Problem Everything Hangs On

A January morning, minus 30. A ground power unit at a remote station fails its start check, and a medevac flight is due through that station in five hours.

- The fault code points to a failed voltage regulator module
- S/4HANA shows one module at Dana's own station store, and one at the neighbouring station, 90 km away by winter road
- The module at her own station is not actually there: another crew consumed it yesterday on a different job, and their tablet has not synced since
- Dana does not know any of that yet. She knows the flight is coming.

One failed start check has just become an information problem, a logistics problem, and a trust problem at the same time. This is the event the design is built for.

## 3. The Cast

**The agents**

- **Scout** — the engineer's field companion. Before a job, it assembles the job pack: the work order, the equipment's service history, the relevant manual sections, the parts picture. On site, it captures findings, time, and parts used, online or offline, and syncs when a connection exists.
- **Stock** — a parts agent. It watches stock across all 22 station stores, sees reservations and priorities, and arranges transfers between stations when a part has to move.
- **Dispatch** — a planning agent. It assigns and re-sequences field jobs around engineer location, certifications, weather and road conditions, and parts arrivals.

**The systems**

- SAP S/4HANA: work orders, inventory, contracts, billing — the system of record
- The engineers' tablets: where the work is actually captured
- External feeds: weather, road conditions, flight schedules
- SAP Integration Suite: the connective tissue, including the store-and-forward path the tablets sync through
- SAP Business Data Cloud: the shared data foundation (see Pillar Two)
- The AI Agent Hub: the registry and control point for every agent (see Pillar Three)

---

## Pillar One — BUILD

*How the field system is built and connected, so an engineer at a remote site and the core system are working on the same job instead of two versions of it.*

**Building the pieces.** Scout's job-pack and reasoning skills are built in Joule Studio over the platform runtime: assemble the pack, summarise the history, flag the parts risk. But the on-device capture — findings, photos, time, parts consumed, customer sign-off, all of it usable with no connection — is not an agent. It is a side-by-side extension: a field application on BTP with its own local persistence on the tablet, because capture has to be deterministic and available at minus 30 with no signal. That split is deliberate, and it is the extension methodology in action: identify the requirement, name the extension task (custom UI, business logic, consume API, consume event, persistence), then map to technology. The core is never touched, so S/4 stays clean and upgrade-safe.

**Connecting them.** Integration Suite is the single governed path between the field and the core:

- APIs serve deliberate lookups when the engineer is online: give me this equipment's open work orders, this part's stock picture
- Events carry what changed: a work order reassigned, a part consumed, a job completed — published once, delivered to whoever cares, whenever they reconnect
- The tablet sync is store-and-forward through Integration Suite, never a private wire from a device straight into S/4: queued changes travel one managed doorway, with identity attached, in order, monitored

**Why not just sync directly?** Because 140 tablets each holding their own connection into the core is 140 unmonitored doors. One governed path means the company can secure it, watch it, and change what sits behind it without touching every device.

**What Build alone does not give you.** At the end of this pillar, Dana has a job pack, a capture app that works offline, and a sync path home. Nothing so far guarantees the pack told her the truth. A confident pack built on stale stock is worse than no pack, because she will drive past the neighbouring station on the strength of it. That is the second pillar.

---

## Pillar Two — CONTEXTUALIZE & REASON

*How the agents get grounded business context, so a part shown as "available" means available for this job, and the nearest engineer means the right engineer. Told in two acts: first the failure, then the fix.*

### Act 1 — The failure (agents built, context missing)

Run the January event with the Build pillar only:

1. **Scout builds the pack from a stale picture.** S/4 shows the module in Dana's station store, because yesterday's consumption is still sitting unsynced on another crew's tablet. The pack says: part on site, no transfer needed. Dana plans around a part that does not exist.
2. **Stock robs a medevac commitment.** Stock sees the neighbouring station's module as free stock and reserves it for a routine job that afternoon. Nothing in its view says that module is the designated backup for the medevac contract at that station, the one piece of equipment that must never be caught without it.
3. **Dispatch sends the nearest engineer, not the right one.** The closest engineer to a second callout is 20 minutes away. He is not certified on that equipment class. The certified engineer is 50 minutes away and never gets considered, because distance is the only fact Dispatch can see.

None of these are stupid agents. Each did exactly what it was asked, with the information it was given. The information was fragmented and stripped of meaning: stock visible as quantities but not as *commitments*, engineers visible as dots on a map but not as *certifications*, a part visible as a bin balance but not as *the backup a contract depends on*.

### Act 2 — The fix (one shared meaning for the data)

**Business Data Cloud provides the foundation.** The data products from S/4HANA — work orders, inventory, contracts — plus the field-captured records are brought together under a common semantic layer: a *part*, a *reservation*, an *engineer*, and a *commitment* mean the same thing everywhere. A module in a bin is no longer just a quantity; it carries what it is reserved for and what breaking that reservation would put at risk.

**The knowledge graph holds the relationships.** On top of that shared meaning, the graph connects the entities the decisions actually depend on:

- This module fits these ground power unit variants, and no other part substitutes for it
- This module is the designated backup under this station's medevac-support contract
- This engineer is certified on this equipment class; that one is not, however close he is
- This station's stock, this crew's unsynced records, this job's priority class

**Now run January again.** Scout's pack is honest about uncertainty: the home-station module shows as *unconfirmed*, because a crew working that store has records outstanding, so the pack plans the transfer from the neighbouring station as the primary path. Stock, asked for that module, sees the medevac reservation, and instead sources the routine job from a third station with genuine free stock, flagging the one-hour delay to a human rather than silently breaking a commitment. Dispatch assigns the certified engineer and says why. The agents did not get smarter. They got *context*, and context is what turns a stock balance into a decision you can defend.

**The design call to be able to defend:** context does not live inside the agent or on the tablet. It lives in the platform — the shared semantic layer and the graph — so Scout, Stock, and Dispatch all reason over the same grounded facts, and the offline pack is stamped with what was known, and what was not, at the moment it was built.

---

## Pillar Three — GOVERN

*How the company stays in control of a system whose most important actions happen offline, on devices it cannot watch, in weather it cannot control. The cautionary tale is the same shape as RestockBot: authority handed out broadly, damage done before a human ever sees it. Boreal is designed so that story cannot repeat.*

**Every agent is registered.** Scout, Stock, and Dispatch each have an entry in the AI Agent Hub: what the agent is, which business unit it serves, which role it acts as, and who its human owner is. The field application is registered too, as the extension it is, with its own owner. There is no such thing as a tool in the field that nobody owns.

**Identity travels with the device, and it is personal.** The tablet acts as the signed-in engineer, not as "a tablet." Scout sees Dana's jobs, Dana's customers, Dana's certifications — not the whole company's book. If a tablet is shared at a station, the identity switches with the login, and the audit trail follows the person, not the hardware.

**Offline authority is bounded, on purpose.** Working offline, an engineer can record findings, time, and parts consumed against her own work orders. She cannot write off stock, change a work order's commercial terms, or close a job above a set value. Those wait for connection and, where the value demands it, a supervisor's approval. The sync does not ask "was this allowed to happen offline" after the fact; the boundaries are in the application before she leaves the hangar.

**Sync conflicts go to a human, with the evidence attached.** When two records claim the same part, the system does not silently pick a winner. The conflict lands in a review queue showing both records, both timestamps, and both engineers, and a human resolves it. Yesterday's unsynced consumption is exactly how Dana's phantom module happened; the design treats that as a governed event, not an error to hide.

**Every decision leaves a trail.** What the pack said and when it was built, what was known and what was unconfirmed, what the engineer recorded and when it synced, who approved what. When a customer asks why the flight waited, or an auditor asks why that part moved, the answer exists.

**The human decides.** The line the whole design holds: the agents prepare, recommend, and execute inside their guardrails; a human owns every commitment that matters — and in the field, the engineer on site is that human for the job in front of her, inside boundaries set before she left.

---

## How It Works — the January Event, End to End

*The underneath, in sequence. Each step names which pillar is doing the work.*

1. **Something happens in the real world.** The ground power unit fails its start check at the remote station, and the failure is booked as a work order in S/4HANA. That booking is the trigger.
2. **The event travels on governed rails (Build).** The work-order event comes out through Integration Suite. Dispatch and Stock wake on it; there is no group chat, no phone tree, no one watching a dashboard at 6 a.m.
3. **Dispatch assigns the right engineer (Contextualize & Reason).** Not the nearest dot on the map: the certified engineer, with the medevac flight's arrival in view, and the reason for the choice attached.
4. **Scout builds an honest pack (Build, Contextualize & Reason).** Work order, service history, manual sections, and a parts picture that distinguishes *confirmed* from *unconfirmed* stock, because a crew's records are outstanding at Dana's station. The pack plans the neighbouring station's module as the primary source.
5. **Stock protects the commitment (Contextualize & Reason, Govern).** Asked to move that module, Stock checks what it is reserved for. It is free to move — the medevac backup at the *destination* station is a different unit — but Stock flags the transfer for human confirmation anyway, because the part is contract-designated. A supervisor confirms in one tap.
6. **Dana works offline (Build).** At the unit, out of coverage, she records the diagnosis, swaps the module when it arrives by the winter road run, captures the customer's sign-off on the tablet. Everything is stored locally, inside her offline authority: no commercial terms touched, nothing written off.
7. **The sync lands cleanly (Build, Govern).** Back in coverage, her records travel the one governed path into S/4: work order updated, module consumption posted against the transfer, time and sign-off attached. Yesterday's other crew syncs too, and the phantom stock record resolves in the review queue instead of corrupting the bin.
8. **Everything leaves a trail (Govern).** The pack's timestamped honesty, the transfer approval, the offline records, the conflict resolution: when the airline asks why the medevac flight's ground power was ready with 40 minutes to spare, the answer exists.

In one sentence: **events wake the agents, context tells them what things mean, guardrails decide what they are allowed to do, and a human owns the commitments** — and in the field, all four have to survive a dead signal at minus 30.

---

## The Five Design Calls (the exam spine)

These are the decisions an architect has to defend out loud on this scenario, each with the rejected alternative:

1. **Agent or extension?** Agents for dispatch, stock reasoning, and the job pack, because the work is judgement across changing inputs. A side-by-side extension for the offline capture application, because capture must be deterministic, available without a connection, and keep the core clean. Rejected: building the whole field tool as an agent (an agent that cannot reason when the signal dies is the wrong tool at minus 30), and rejected: customising S/4, which buys convenience with upgrade paralysis.
2. **Where does context come from?** From the platform: Business Data Cloud's shared semantic layer and the knowledge graph — reservations, certifications, contract designations. Rejected: letting each agent and each tablet read raw S/4 extracts, which is Act 1: a phantom part, a robbed medevac backup, the wrong engineer.
3. **Which integration pattern?** Integration Suite as the single governed path: APIs for deliberate lookups, events for change, store-and-forward sync for the tablets. Rejected: direct device-to-core connections, 140 unmonitored doors into the system of record.
4. **How are the agents and devices governed?** Agents registered in the AI Agent Hub with named owners; personal identity on every device; offline authority bounded in the application itself; sync conflicts resolved by humans with evidence attached. Rejected: broad device access and silent conflict resolution, which is how phantom stock becomes a grounded aircraft.
5. **How is value proven?** In business numbers, not agent counts: first-time-fix rate, equipment downtime hours against flight schedules, return trips to station avoided, inventory record accuracy across the 22 stores. Measured before and after, on the same definitions.

## Likely Follow-Up Questions (for rehearsal later)

- Why is the capture app an extension and not a fourth agent?
- The pack says stock is "unconfirmed." What exactly should the engineer do differently because of that word?
- Two crews claim the same part in a sync conflict on a safety-related job. Who wins, and why is it not automatic?
- Why not let the tablets connect straight to S/4 and skip Integration Suite entirely?
- A tablet is lost at a customer site. What can whoever finds it see, and what happens next?
- Where does this design fail? What is the first thing you would add next?

---

*Companion to the TrueNorth AeroWorks scenario. Built 2026-11-19 at Anahita's request, shaped on the field-service scenario described by a P_BTPA candidate, with the emphasis TrueNorth underweights: mobile and offline working, integration patterns back to the core, and identity on devices in the field.*
