# FOTA Server and Database Manager

This folder contains the server-side desktop component described by the project documentation. It provides a PyQt5 interface and integration with Firebase for firmware-update data and related information.

## Technologies documented

- Python 3.6 or newer in the original project notes
- PyQt5 for the desktop UI
- Pyrebase for Firebase integration
- PyCryptodome for AES encryption

The original dependency notes list these packages but do not pin exact versions. Use a compatible Python environment and record a tested lock file before relying on reproducible installations.

## Setup

Create and activate a virtual environment:

    python -m venv .venv

On Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

On Linux or Raspberry Pi OS:

    source .venv/bin/activate

Install the documented dependencies:

    python -m pip install PyQt5 pyrebase pycryptodome

The repository snapshot does not expose a complete pinned requirements file or a verified application entry point for this folder. Inspect the Python files and Firebase initialization before selecting the command used to launch the GUI.

## Security

- Keep Firebase service-account credentials and private API keys outside Git.
- Load encryption keys from a secure local configuration or a secrets manager.
- Use authenticated encryption (for example, AES-GCM) for new data formats where compatibility permits; legacy encrypted records may require a controlled migration.
- Add integrity/signature verification to firmware images and verify signatures on the device before flashing.
- Avoid logging credentials, tokens, plaintext firmware, or sensitive user information.

See the [root FOTA overview](../README.md) for the complete system architecture.
