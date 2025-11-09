# Projects Portfolio Index

This directory curates end-to-end applications developed alongside the CyberBionic Systematics Python program. Each subfolder contains a production-style project complete with its own documentation, infrastructure scripts, and testing utilities. Use this index to locate the solution that best matches the domain or technology stack you are interested in.

## Directory At A Glance

| Project | Domain & Scope | Core Stack | Status |
| --- | --- | --- | --- |
| `🌌 CosmicFinance_project` | Personal finance platform with budgeting, analytics, and JWT-secured APIs | Django, DRF, PostgreSQL, Bootstrap, Chart.js, Docker | Stable feature set, ready for demo deployments |
| `aigolos_project` | AI voice assistant orchestrating ASR → LLM → TTS workflows with web UI and REST APIs | Django, DRF, Ollama, faster-whisper, Piper TTS, Docker | Production-ready base, extensible via plug-in AI services |
| `balck_jack_project` | PyGame sandbox for blackjack mechanics and UI/UX experiments | Python, PyGame | Prototype; focused on gameplay loop validation |
| `blackjack_v_0.1_project` | Web-enabled blackjack application with tests and packaging | Flask, HTML/CSS, PyTest | MVP; suitable for incremental feature development |
| `booking_CRM_project` | Full-stack CRM prototype for booking workflows (multi-app Django suite) | Django, DRF, React/JSX, Celery, Redis (planned) | Under active development; modular service architecture |
| `law_crm_project` | Domain-specific CRM tailored to legal practices | Django, DRF, PostgreSQL | Feature-complete core; awaiting UX refinements |
| `Law_Firm_CRM_System_v1_project` | Successor CRM iteration with expanded automation & reporting | Django, Celery, REST integrations | Iterative build; targets enterprise deployment readiness |

> **Note:** Some project names retain their original spelling (e.g., `balck_jack_project`) to preserve commit history and tooling compatibility.

## How To Explore
- **Read local docs** – Most projects provide a dedicated `README.md` plus supplementary guides (`HOW_TO_RUN.md`, `TESTING_SETUP.md`, etc.).
- **Use per-project environments** – Activate the `requirements.txt` or `pyproject.toml` listed within each folder to avoid dependency clashes.
- **Check infrastructure tooling** – Dockerfiles, compose stacks, and automation scripts live alongside the application code for reproducible setups.

## Contribution Workflow
1. Pick a project and review its roadmap or open issues (where available).
2. Create a feature branch scoped to that project, following its contribution guidelines.
3. Run the project’s test suite locally; many repos standardize on `pytest` or Django’s test runner.
4. Open a pull request against the corresponding project folder in this monorepo, referencing any relevant documentation updates.

## Support & Feedback
Questions, bug reports, or feature ideas? Open an issue in the root repository and prefix the title with the project name (for example, `[CosmicFinance] Improve analytics performance`). This keeps discussions organized while maintaining a single tracking location.
