# Password Manager

A simple Python-based password manager with **Argon2id** encryption, password generation, a command-line interface, and a graphical user interface.

---

## Getting Started

This project uses [**uv**](https://astral.sh/blog/uv/) for fast dependency management and environment setup.

### Clone the Repository

```bash
git clone https://github.com/TheL0L/password_manager.git
cd password_manager
```

### Set Up the Environment

To create the virtual environment and install all project dependencies:

```bash
uv sync
```

---

## Running Tests

You can run all the test suites using `uv`:

```bash
uv run pytest
```

---

## Running the Application

You can run either the CLI or GUI version of the app using `uv`. Two macros are available for convenience:

```bash
uv run pm-cli
```

```bash
uv run pm-gui
```

Or, if you prefer using the scripts directly:

```bash
uv run ./src/password_manager/main_cli
```

```bash
uv run ./src/password_manager/main_gui
```

---

## Requirements

- Python 3.13+
- [`uv`](https://github.com/astral-sh/uv)

