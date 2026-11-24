# Boreal Field Services — Follow-Up Questions, Model Answers

*The six rehearsal questions at the end of the Boreal scenario, answered in the defence format: the answer, the reasoning, the rejected alternative. Built 2026-11-20 at Anahita's request.*

---

**1. Why is the capture app an extension and not a fourth agent?**

Because capture is recording, not judgement. An agent reasons over changing inputs and needs its runtime, its models, and its context, all of which need a connection. Capture has to work with no signal at all, behave identically every time, and produce a record an auditor can trust keystroke for keystroke. That is extension work: a custom interface and its own persistence, built side-by-side on BTP under the extension methodology, keeping the core clean. Rejected: a fourth agent, because an agent that cannot reach its runtime is a dead tool exactly where the work happens, and because probabilistic behaviour has no place in the write path for findings, time, and parts.

**2. The pack says stock is "unconfirmed." What exactly should the engineer do differently because of that word?**

She treats the part as a possibility, not a plan. She does not promise the customer a fix time based on it. She physically checks the bin before any strip-down starts. The job is planned on the confirmed source, in this case the neighbouring station's module, and the unconfirmed one is a bonus if it turns out to be real. If she does use it, she records the use on the spot so the sync surfaces it immediately. The word exists so nobody builds a commitment on data the system itself knows is shaky: the pack is stamped with what was known and what was not, and her behaviour follows the stamp.

**3. Two crews claim the same part in a sync conflict on a safety-related job. Who wins, and why is it not automatic?**

Neither crew wins automatically. The conflict goes to a human review queue carrying both records, both timestamps, and both engineers, and a person resolves it. An automatic rule, first sync wins, would reward whoever found signal first, not whoever is right. On a safety-related job the maintenance record is an airworthiness document; a silently wrong resolution corrupts it. The delay of a queue is accepted deliberately: it is cheaper than a wrong record. Both versions stay in the audit trail either way, so the resolution itself can be examined later.

**4. Why not let the tablets connect straight to S/4 and skip Integration Suite entirely?**

Because that is 140 unmonitored doors into the system of record. No single place for authentication, throttling, monitoring, error handling, or version changes; every tablet becomes an integration someone has to maintain; and a lost or compromised device would be talking directly to the core. Integration Suite gives one governed path: managed credentials, API management for the deliberate lookups, events for change, and the store-and-forward pattern for the tablets living in it. The cost is one more layer to run. That layer is what makes the field governable at all, so the cost is the point.

**5. A tablet is lost at a customer site. What can whoever finds it see, and what happens next?**

The finder sees a locked device. The application holds only the signed-in engineer's own jobs, and access runs on personal identity, so without her login there is no way into the data. What happens next: she reports the loss, the device's access is revoked centrally through the identity service, which kills the session everywhere in one action. Any records that existed only on that tablet are treated as unconfirmed, and the affected jobs are re-verified rather than trusted. The audit trail shows what the device held and when it last synced. The design point: because offline authority was bounded, a lost tablet is an operational problem, not a breach of the core.

**6. Where does this design fail? What is the first thing you would add next?**

It fails at the edges of its own assumption. The pack is built before departure, so an engineer dispatched from a station with no coverage and no fresh pack is working from stale context: the design moves the stale-data problem, it does not abolish it. And the human review queue, right as it is, becomes the bottleneck if conflict rates climb, because every conflict waits on a person. The first addition is a feedback loop: monitoring in the AI Agent Hub on conflict rates and unconfirmed-stock frequency, by station and by crew, so the root cause, records not syncing, gets fixed as a behaviour and a process problem, not absorbed forever as a queue. Name the failure before the stakeholder finds it; that is what the format rewards.

---

*Keeper, across all six: every answer names the choice, the reason, and the alternative that was rejected. That shape is the exam.*

**7. Follow-up to question 6: how would you build the feedback loop?**

From events the design already produces. Every sync conflict, every unconfirmed-stock flag, every review-queue resolution is already an event carrying station, crew, part, and timestamps; the audit trail is the raw material, instrumented rather than replaced. The events flow through Integration Suite into Business Data Cloud, where the semantic layer lets rates be cut by station, crew, and part instead of one blunt company-wide count. The watching happens in the AI Agent Hub: conflict rate and unconfirmed rate become health metrics for the agents, with thresholds that alert when a station crosses a line. The loop closes in a standing human rhythm: a monthly operations review, with Signavio Process Intelligence showing where the sync process deviates, decides what changes (connectivity fix, sync prompt, coaching). Rejected: a passive dashboard nobody is alerted by, and a loop that adjusts agent authority by itself. The loop observes and recommends; a human changes the guardrails.
