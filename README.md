# Kanban QA Automation

A full-stack QA automation project built around a Flask-based Kanban board application. The project demonstrates end-to-end quality assurance practices including API testing, integration testing, Selenium UI testing with the Page Object Model, and documented bug tracking via Allure.

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                  Flask Application              │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │   Auth   │  │  Boards  │  │    Cards     │  │
│  │ Blueprint│  │ Blueprint│  │  Blueprint   │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │         SQLAlchemy ORM (SQLite)         │    │
│  │  Users │ Boards │ BoardMembers │ Cards  │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘

Kanban Columns: Backlog → To Do → In Progress → In Review → Done
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask, SQLAlchemy, SQLite |
| Auth | JWT (PyJWT), Flask sessions |
| API Docs | Flasgger (Swagger UI) |
| Testing | pytest, allure-pytest |
| UI Testing | Selenium 4, ChromeDriver |
| Test Pattern | Page Object Model (POM) |
| Reporting | Allure Framework |

---

## Project Structure

```
Kanban-QA-Automation/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Dev / Testing configs
│   ├── database.py          # SQLAlchemy instance
│   ├── models.py            # User, Board, BoardMember, Card
│   ├── utils.py             # success_response / error_response
│   ├── views.py             # UI routes (Jinja2)
│   ├── auth/                # Auth blueprint (register, login, /me, logout)
│   ├── boards/              # Boards blueprint (CRUD + members)
│   ├── cards/               # Cards blueprint (CRUD + move)
│   ├── templates/           # HTML templates (base, login, register, boards, board_detail)
│   └── static/              # CSS + JS (auth.js, style.css)
├── seed_data/
│   └── seed.py              # 3 users, 2 boards, 11 cards across all columns
├── tests/
│   ├── conftest.py          # API/integration fixtures (function-scoped, in-memory DB)
│   ├── api/
│   │   ├── test_auth_api.py          # 18 tests — register, login, /me, logout
│   │   ├── test_boards_api.py        # 22 tests — CRUD, members
│   │   ├── test_cards_api.py         # 18+ tests — CRUD, move, column validation
│   │   └── test_known_failures.py    # 10 xfail bugs (BUG-001 → BUG-010)
│   ├── integration/
│   │   └── test_end_to_end.py        # 5 full-journey tests
│   └── ui/
│       ├── conftest.py               # UI fixtures (session-scoped server, function-scoped driver)
│       ├── pages/
│       │   ├── base_page.py          # BasePage — data-testid locators, JS click
│       │   ├── login_page.py         # LoginPage POM
│       │   ├── register_page.py      # RegisterPage POM
│       │   ├── boards_page.py        # BoardsPage POM
│       │   └── board_detail_page.py  # BoardDetailPage POM (Kanban columns, cards)
│       ├── test_auth_ui.py           # 11 tests — login, register, logout UI
│       ├── test_boards_ui.py         # 9 tests — create, list, delete, navigate
│       └── test_cards_ui.py          # 10 tests — add, move, delete cards
├── run.py                   # Entry point
├── pytest.ini               # Markers + allure config
├── requirements.txt
└── .gitignore
```

---

## Setup

### Prerequisites
- Python 3.11+
- Google Chrome + matching ChromeDriver on PATH

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the Development Server

```bash
python run.py
# → http://localhost:5000
# → Swagger UI: http://localhost:5000/api/docs
```

Seed data is created automatically on first run.

### Default Users

| Username | Email | Password | Role |
|---|---|---|---|
| adminuser | admin@kanban.com | Admin123! | admin |
| testuser1 | testuser1@kanban.com | Password123! | user |
| testuser2 | testuser2@kanban.com | Password123! | user |

---

## Running Tests

```bash
# All API + integration tests (no browser needed)
pytest tests/api/ tests/integration/ -v

# UI tests only (opens headless Chrome)
pytest tests/ui/ -v

# All tests
pytest -v

# By marker
pytest -m api -v
pytest -m integration -v
pytest -m ui -v

# Single file
pytest tests/api/test_boards_api.py -v

# Single test
pytest tests/api/test_auth_api.py::TestRegister::test_register_success -v

# With Allure report
pytest tests/api/ tests/integration/ -v
allure serve allure-results
```

---

## API Endpoints

### Authentication — `/api/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Register new user |
| POST | `/api/auth/login` | — | Login, returns JWT token |
| GET | `/api/auth/me` | JWT | Get current user profile |
| POST | `/api/auth/logout` | — | Clear session |

### Boards — `/api/boards`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/boards/` | JWT | List my boards |
| POST | `/api/boards/` | JWT | Create board |
| GET | `/api/boards/{id}` | JWT (member) | Get board with all cards grouped by column |
| PATCH | `/api/boards/{id}` | JWT (owner) | Update board name/description |
| DELETE | `/api/boards/{id}` | JWT (owner) | Delete board (cascades cards) |
| POST | `/api/boards/{id}/members` | JWT (owner) | Add member |
| DELETE | `/api/boards/{id}/members/{uid}` | JWT (owner) | Remove member |

### Cards — `/api/boards/{board_id}/cards`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/boards/{id}/cards` | JWT (member) | List cards (filterable by column) |
| POST | `/api/boards/{id}/cards` | JWT (member) | Create card |
| GET | `/api/boards/{id}/cards/{cid}` | JWT (member) | Get card detail |
| PATCH | `/api/boards/{id}/cards/{cid}` | JWT (member) | Update / move card |
| DELETE | `/api/boards/{id}/cards/{cid}` | JWT (member) | Delete card |

### Response Contract

All endpoints return the same envelope:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

---

## Test Coverage

| Layer | Tests | Focus |
|---|---|---|
| API | 58+ | Functional valid/invalid, auth, RBAC |
| Integration | 5 | Full user journeys, cascade deletes, member access |
| UI (Selenium) | 30+ | Login, register, board CRUD, card CRUD, column navigation |
| Known Failures | 10 | Documented bugs as `xfail` |
| **Total** | **~103** | |

---

## 10 Documented Bugs (xfail)

These are intentional limitations documented as `xfail(strict=True)` tests. They appear as **KNOWN FAILURES** in the Allure report — orange, not red.

| Bug ID | Area | Description | Severity |
|---|---|---|---|
| BUG-001 | Boards | Board list response lacks `total_pages` and `page` pagination metadata | Normal |
| BUG-002 | Boards | Board list has no pagination support (`?page` / `?per_page` ignored) | Normal |
| BUG-003 | Boards | No search/filter by board name | Minor |
| BUG-004 | Cards | Cards do not support `due_date` field | Normal |
| BUG-005 | Cards | Cards do not support `priority` field | Normal |
| BUG-006 | Cards | Cards cannot be assigned to a team member (`assignee_id` ignored) | Normal |
| BUG-007 | Cards | Cards do not support tags/labels | Minor |
| BUG-008 | Auth | No minimum username length enforced (single-char usernames accepted) | Minor |
| BUG-009 | Auth | Login endpoint has no rate limiting (brute-force possible) | Normal |
| BUG-010 | Auth | No change password endpoint exists | Normal |

---

## UI Test Design

All UI elements are located via `data-testid` attributes — no XPath, no fragile CSS class selectors.

```python
# BasePage — all page objects inherit this
def find(self, testid: str):
    return self.driver.find_element(By.CSS_SELECTOR, f'[data-testid="{testid}"]')
```

Selenium page objects follow the **Page Object Model**: each page is a class, each action is a method. Tests never call `driver.find_element` directly.

```python
# Example usage in a test
page = BoardsPage(driver, base_url).open()
page.click_new_board()
page.fill_board_name("Sprint 1")
page.submit_board()
assert "Sprint 1" in page.get_board_names()
```

---

## Test Isolation

- **API / integration tests**: function-scoped `app` fixture — fresh in-memory SQLite DB per test, seeded and dropped automatically. Zero state leakage between tests.
- **UI tests**: session-scoped Flask server on port 5002, function-scoped Chrome driver. Shared DB is acceptable for read-heavy UI flows; destructive tests create and clean up their own data.

---

## Allure Report

After running tests, generate and open the Allure report:

```bash
allure serve allure-results
```

The report shows:
- Test results by feature / story
- XFAIL known failures (BUG-001 → BUG-010)
- Attached API request/response bodies
- JWT tokens attached per test

---

## Author

**Ilana Rosenberg** — QA Automation Engineer  
Built as a portfolio project to demonstrate full-stack QA automation skills.
