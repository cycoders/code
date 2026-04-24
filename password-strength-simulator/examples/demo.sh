#!/bin/bash
set -e

python -m password_strength_simulator "password" --algo md5 --hardware rtx4090
python -m password_strength_simulator "P@ssw0rd123" --algo bcrypt --cost 12 --hardware cpu-i9
python -m password_strength_simulator batch passwords.txt --algo argon2 --cost 3 --hardware rtx4090
python -m password_strength_simulator chart --algo sha1 --hardware 100-gpu-cluster --charset-size 62 --min-length 8 --max-length 14
python -m password_strength_simulator benchmark --algo bcrypt --cost 10 --duration 1