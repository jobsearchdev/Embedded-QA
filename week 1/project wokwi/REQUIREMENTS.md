# Smart Gate Controller — Requirements

## 1. Purpose

The Smart Gate Controller is a simplified embedded controller for an automatic gate.

The system is tested as a **black box**. Testers should verify observable behavior and should not rely on implementation details.

---

## 2. States

The controller supports the following logical states:

- `CLOSED` — gate is fully closed.
- `OPENING` — gate is opening.
- `OPEN` — gate is fully open.
- `CLOSING` — gate is closing.
- `STOPPED` — movement was stopped by the STOP command.
- `ERROR` — unsafe or invalid system condition.

---

## 3. Inputs

### 3.1 User inputs

- `OPEN` button / command
- `CLOSE` button / command
- `STOP` button / command

### 3.2 Position inputs

- `LIMIT_OPEN` — open end-position sensor
- `LIMIT_CLOSE` — closed end-position sensor

### 3.3 Serial commands

The Serial Monitor accepts:

- `O` — OPEN
- `C` — CLOSE
- `S` — STOP
- `R` — RESET ERROR

---

## 4. Outputs

- `OPEN relay`
- `CLOSE relay`
- `OPEN LED`
- `CLOSE LED`
- `ERROR LED`
- `Buzzer`
- Serial diagnostic messages

---

## 5. Functional Requirements

### R1 — Initial state

After startup, the controller shall be in `CLOSED`.

Both relays shall be OFF.

### R2 — Open command

When the controller is in `CLOSED` or `STOPPED` and receives `OPEN`:

- state shall become `OPENING`;
- `OPEN relay` shall turn ON;
- `CLOSE relay` shall remain OFF;
- `OPEN LED` shall turn ON.

### R3 — Open limit

When the controller is in `OPENING` and `LIMIT_OPEN` becomes active:

- `OPEN relay` shall turn OFF;
- state shall become `OPEN`;
- `OPEN LED` shall remain ON;
- `CLOSE relay` shall remain OFF.

### R4 — Close command

When the controller is in `OPEN` or `STOPPED` and receives `CLOSE`:

- state shall become `CLOSING`;
- `CLOSE relay` shall turn ON;
- `OPEN relay` shall remain OFF;
- `CLOSE LED` shall turn ON.

### R5 — Close limit

When the controller is in `CLOSING` and `LIMIT_CLOSE` becomes active:

- `CLOSE relay` shall turn OFF;
- state shall become `CLOSED`;
- both movement relays shall be OFF.

### R6 — STOP

When the controller is moving (`OPENING` or `CLOSING`) and receives `STOP`:

- both relays shall turn OFF immediately;
- state shall become `STOPPED`;
- no movement relay shall remain active.

### R7 — Repeated movement commands

A command that requests the same movement while that movement is already active shall not create an unsafe or contradictory state.

### R8 — Opposite command during movement

If the gate is moving in one direction and the opposite command is received:

- the controller shall not allow both movement relays to be active simultaneously;
- the controller shall transition safely;
- no contradictory relay state is allowed.

### R9 — Relay safety

`OPEN relay` and `CLOSE relay` shall **never be ON simultaneously**.

If an unsafe relay condition occurs, the controller shall enter `ERROR`.

### R10 — Movement timeout

If the gate remains in `OPENING` or `CLOSING` for more than 10 seconds without reaching the corresponding limit:

- movement shall stop;
- both relays shall turn OFF;
- state shall become `ERROR`;
- `ERROR LED` shall turn ON;
- the buzzer shall indicate the error.

### R11 — Both limits active

If `LIMIT_OPEN` and `LIMIT_CLOSE` are active simultaneously:

- the controller shall treat this as an invalid physical condition;
- state shall become `ERROR`;
- both movement relays shall be OFF;
- `ERROR LED` shall turn ON.

### R12 — ERROR state

While in `ERROR`:

- OPEN and CLOSE commands shall not start movement;
- movement relays shall remain OFF.

### R13 — RESET

`RESET` shall clear `ERROR` and transition the controller to `STOPPED`.

RESET outside `ERROR` shall not unexpectedly start movement.

### R14 — Invalid commands

An unsupported serial command shall:

- not start movement;
- not change the gate state;
- produce a diagnostic indication in Serial Monitor.

### R15 — Output indication

The visible outputs shall correspond to the state:

| State | OPEN LED | CLOSE LED | ERROR LED | Movement relay |
|---|---|---|---|---|
| CLOSED | OFF | OFF | OFF | None |
| OPENING | ON | OFF | OFF | OPEN |
| OPEN | ON | OFF | OFF | None |
| CLOSING | OFF | ON | OFF | CLOSE |
| STOPPED | OFF | OFF | OFF | None |
| ERROR | OFF | OFF | ON | None |

### R16 — Single button action

One physical button press shall produce one logical command.

Holding a button shall not generate an uncontrolled stream of repeated movement commands.

---

## 6. QA Task

Test the controller as a black box.

Create and execute at least **15 test scenarios**.

Use several test-design techniques:

- State Transition Testing
- Equivalence Partitioning
- Boundary / Timing Testing
- Negative Testing
- Combination Testing
- Output Verification

For every failed test, create a defect report containing:

- Bug ID
- Requirement
- Preconditions
- Steps to Reproduce
- Expected Result
- Actual Result
- Severity
- Reproducibility
- Evidence

**Do not analyze the source code to find defects.**
