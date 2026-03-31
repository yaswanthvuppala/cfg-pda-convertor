# CFG ↔ PDA Converter

A web-based tool to convert between **Context-Free Grammars (CFG)** and **Pushdown Automata (PDA)** instantly, built with Flask and a modern dark-themed UI.

> **Live Demo:** Deployed on [Render](https://render.com) (or run locally)

---

## ✨ Features

- **CFG → PDA Conversion** — Input a context-free grammar and generate the equivalent pushdown automaton using the standard leftmost-derivation construction.
- **PDA → CFG Conversion** — Input a pushdown automaton and reconstruct the equivalent CFG using the triple-variable construction.
- **Interactive UI** — Dynamically add/remove production rules and transitions with a sleek, animated dark-mode interface.
- **Instant Results** — Conversion results are displayed in organized tables with color-coded badges for states, alphabets, and symbols.
- **Responsive Design** — Works on desktop and mobile screens.

---

## 🛠️ Tech Stack

| Layer     | Technology             |
|-----------|------------------------|
| Backend   | Python, Flask          |
| Frontend  | HTML, CSS, JavaScript  |
| Fonts     | Google Fonts (Inter)   |
| Deploy    | Gunicorn, Render       |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yaswanthvuppala/cfg-pda-convertor.git
cd cfg-pda-convertor

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 📖 Usage

### CFG → PDA

1. Select the **CFG → PDA** tab.
2. Enter variables (e.g. `S, A, B`), terminals (e.g. `a, b`), and the start variable.
3. Add production rules — use `|` for alternatives and `ε` for epsilon.
4. Click **⚡ Convert to PDA**.

**Example Input:**

| Field       | Value                    |
|-------------|--------------------------|
| Variables   | `S, A, B, T, U`         |
| Terminals   | `a, b`                  |
| Start       | `S`                     |
| Productions | `S → AT \| BU \| AA \| BB` |
|             | `T → AS`                |
|             | `U → BS`                |
|             | `A → a`                 |
|             | `B → b`                 |

### PDA → CFG

1. Select the **PDA → CFG** tab.
2. Enter states, input/stack alphabets, start state, initial stack symbol, and (optionally) accept states.
3. Add transitions — use `ε` for epsilon input/push.
4. Click **⚡ Convert to CFG**.

---

## 📁 Project Structure

```
cfg-pda-convertor/
├── app.py              # Flask backend — routes, conversion logic, data structures
├── requirements.txt    # Python dependencies (flask, gunicorn)
├── T1.py               # Standalone CYK parser for CFG string validation
├── T2.py               # Standalone CLI version of the CFG ↔ PDA converter
├── templates/
│   └── index.html      # Frontend — forms, tabs, result rendering
└── static/
    └── style.css       # Dark-themed stylesheet with animations
```

---

## ⚙️ Algorithms

### CFG → PDA (Leftmost Derivation Construction)

Given a CFG `G = (V, Σ, P, S)`, the equivalent PDA is constructed as:

- **States:** `{q_start, q_loop, q_accept}`
- **Transitions:**
  1. `δ(q_start, ε, Z₀) = (q_loop, SZ₀)` — push start variable
  2. For each production `A → α`: `δ(q_loop, ε, A) = (q_loop, α)` — expand non-terminal
  3. For each terminal `a`: `δ(q_loop, a, a) = (q_loop, ε)` — match terminal
  4. `δ(q_loop, ε, Z₀) = (q_accept, ε)` — accept on empty stack

### PDA → CFG (Triple-Variable Construction)

Given a PDA with states `Q`, create variables `[p, A, q]` for all `p, q ∈ Q` and `A ∈ Γ`:

- **Start:** `S → [q₀, Z₀, q]` for every `q ∈ Q`
- For each transition `δ(p, a, A) = (r, B₁B₂…Bₖ)`:
  - `[p, A, qₖ] → a [r, B₁, q₁] [q₁, B₂, q₂] … [qₖ₋₁, Bₖ, qₖ]` for all combinations of `q₁, …, qₖ ∈ Q`
- For each transition `δ(p, a, A) = (r, ε)`:
  - `[p, A, r] → a`

---

## 📝 API Endpoints

| Method | Endpoint              | Description                |
|--------|-----------------------|----------------------------|
| GET    | `/`                   | Serves the main UI         |
| POST   | `/convert/cfg-to-pda` | Converts a CFG to a PDA    |
| POST   | `/convert/pda-to-cfg` | Converts a PDA to a CFG    |

### Request/Response Format

All POST endpoints accept and return JSON. Example CFG → PDA request:

```json
{
  "variables": "S, A, B",
  "terminals": "a, b",
  "start": "S",
  "productions": [
    { "lhs": "S", "rhs": "aSb | ε" }
  ]
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
