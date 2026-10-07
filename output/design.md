# Dashboard design

## Direction

The dashboard is a calm operations desk rather than a generic admin table. It uses a deep navy rail, warm brass crest, paper-white cards, and restrained blue accents: a modern heraldic reading of the Campus Customs shop. Playfair Display gives the desk a sense of place while DM Sans and DM Mono keep statuses, tool names, and operational data quick to scan.

## Layout

- A narrow left rail provides a persistent home for Desk, Stock, Cash, and a visible “Safe mode” reminder.
- The top bar establishes the current operating context and live connection state.
- Three summary cards show open requests, checking balance, and connected agent roles before the operator reads any ticket.
- The main workspace keeps the queue on the left and the selected ticket’s command center on the right. This makes choosing a ticket and acting on it a single visual movement.
- The activity transcript sits below the selected ticket so the operator can watch the team without losing the request details.

## Agent readability

Each agent has a distinct color and icon: Boss is brass and crowned, Inventory is green and stocked, Accounting is blue and ledger-like, Facilities is purple and architectural, and Customer Service is rose and message-oriented. Events show the role, action type, natural-language detail, and MCP tool name separately. That distinction helps a human tell the difference between an agent’s reasoning, a delegation, and a database lookup.

## Resolution and cash

Open tickets carry an amber status and attention icon; resolved tickets turn green with a check badge. The run button disables while the team is working, and the activity count makes new evidence visible. The approval button is deliberately green but separate from the agent run: agents can prepare a payment, while only a human click can change cash. The checking balance is always visible in the summary row and refreshes after approval, making the financial effect concrete.

## Small details that make it pleasant

The brass crest, “captain” greeting, live desk indicator, generous whitespace, gentle lift on ticket hover, and compact event avatars make the screen feel like a place with a crew and a ritual—not a wall of logs. Refreshing is available as a quiet icon action, while polling keeps the live transcript current without making the user manage a connection. Responsive breakpoints collapse the desk into a useful single-column flow on smaller screens.
