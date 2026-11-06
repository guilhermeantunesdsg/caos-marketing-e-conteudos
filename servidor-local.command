#!/bin/bash
# Abre o site no seu computador. Dê dois cliques. Para encerrar, feche a janela.
cd "$(dirname "$0")"
python3 tools/build.py
echo "Site em: http://localhost:8000"
( sleep 1; open "http://localhost:8000" ) &
python3 -m http.server 8000
