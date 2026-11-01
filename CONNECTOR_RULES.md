# Connector rules

These are not suggestions. They are conditions attached to every API key, and a
key that breaks them is revoked. Each one exists for a reason, and the reason is
written next to it — a connector that understands why tends to get the details
right.

## 1. Delete the data when the connection ends

When a status comes back as `no_data`, or a field disappears from `data`, remove
what you stored. Do not keep the last known value.

*Why:* the person disconnected, or stopped sharing that field. A stale value in
a record looks current to whoever reads it next, and is worse than an empty
field.

## 2. Never show "not connected" as "below threshold"

`no_data` is neutral. Render it as grey, blank, "not connected" — never as red,
never as a failure.

*Why:* if disconnecting turns a row red, disconnecting is no longer free: it
becomes a penalty, and consent under penalty is not consent.

## 3. Never try to deduce or store the score

No history of outcomes over time, no time series, no changing the threshold to
narrow down the number.

*Why:* the whole design rests on the number never leaving Hurank. Reconstructing
it defeats the person's control over their own data.

## 4. Ask only for what you need, and never require the optional

Request only the fields your process uses. Do not make access to your service
conditional on fields you declared optional.

*Why:* optional means the person can say no. If saying no costs them something,
it was never optional.

## 5. Sync incrementally

Call `GET /v1/status` with `since`, typically once a day. Use
`POST /v1/status/batch` only to recover after an outage.

*Why:* outcomes change only when people receive votes, which is slow. Reading
more often brings nothing new, and every key is limited to 60 requests per minute.

## 6. The decision is yours, never Hurank's

If an outcome feeds an automated decision that affects the person (a shortlist,
an approval), a human in your organization must be able to review it.

*Why:* Hurank is a measuring instrument, not a gatekeeper. Under the GDPR
(art. 22), significant automated decisions need human oversight — and that
responsibility sits with the organization making the decision.
