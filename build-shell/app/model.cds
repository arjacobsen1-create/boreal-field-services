// Boreal Field Services — CAP data-model STUB (not a working CAP project)
// Entities are notes in CDS style. Rules are comments, not implementation.

namespace boreal.fieldservice;

entity WorkOrder {
  key ID          : UUID;
  equipment       : String;   // e.g. 'Ground Power Unit GPU-114'
  station         : String;   // home station / site code
  engineer        : String;   // e.g. 'Dana'
  status          : String;   // captured | confirmed | inProgress | completed
  dueBy           : Timestamp; // e.g. medevac flight deadline
  capturedOffline : Boolean;  // true when recorded without coverage
}

entity PartUsage {
  key ID        : UUID;
  workOrder     : Association to WorkOrder;
  part          : String;     // e.g. 'Voltage Regulator Module'
  quantity      : Integer;
  consumedAt    : Timestamp;  // when the part was actually used
  syncedAt      : Timestamp;  // when the tablet record reached the app
  sourceTablet  : String;
}

entity StockReservation {
  key ID         : UUID;
  workOrder      : Association to WorkOrder;
  part           : String;
  fromStation    : String;
  stockStatus    : String;    // verified | unverified  (see governance/gates.yaml)
  approvedBy     : String;    // human approver — required, never an agent
  status         : String;    // proposed | approved | refused | executed
}

// SYNC / VALIDATION / CONFLICT RULES (comments only):
// 1. A tablet record is "captured, not confirmed" until it syncs and validates.
// 2. On sync, validate: work order open, part correct for the equipment,
//    engineer authorised for the station.
// 3. Conflict: if a PartUsage sync post-dates a stock read, stock figures shown
//    before that sync are stale — re-read before any reservation is proposed.
//    (This is the phantom-stock case: home station showed 1, reality was 0.)
// 4. Reservations may only be *proposed* by agents; approval is a human action
//    recorded in approvedBy. Execution posts to the system of record.
