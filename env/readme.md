# Environment definitions

This directory contains the definitions required to reproduce the environment.
Docker reads the contents of these files when building the image.

```text
├── 📁 cmd/             # Executable scripts not provided by apt
│   ├── 📄 ete3
│   └── 📄 trimmomatic
├── 📄 apt.txt          # Apt dependencies
├── 📄 base.yml         # Conda dependencies not available in apt or pip
├── 📄 masurca.yml      # Conda definition for the MaSuRCA assembler
├── 📄 pip.txt          # Pip dependencies
└── 📄 readme.md        # This file
```
