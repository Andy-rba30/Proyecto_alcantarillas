"""Corre la CLI de la app (python cli.py ...) desde /home/user/val_web y deja
el comando exacto en <dir>/comandos.txt y la salida en <dir>/salida/<nombre>.txt.
Uso: python correr.py <dir_caso> <nombre> -- <args de cli.py ...>
Las declaraciones se pueden pasar con @archivo (una por linea: CLAVE=VALOR)."""
import subprocess, sys, shlex, os, datetime
caso, nombre = sys.argv[1], sys.argv[2]
args = sys.argv[sys.argv.index('--') + 1:]
final = []
for a in args:
    if a.startswith('@decl:'):
        for l in open(a[6:]):
            l = l.strip()
            if l and not l.startswith('#'):
                final += ['--declarar', l]
    else:
        final.append(a)
cmd = ['python', 'cli.py'] + final
env = dict(os.environ, NORMAS_DIR='/home/user/andy-rba30/normas')
os.makedirs(f'{caso}/salida', exist_ok=True)
r = subprocess.run(cmd, cwd='/home/user/val_web', env=env, capture_output=True, text=True)
with open(f'{caso}/salida/{nombre}.txt', 'w') as f:
    f.write(r.stdout); f.write(r.stderr)
with open(f'{caso}/comandos.txt', 'a') as f:
    f.write(f'# {datetime.datetime.now().isoformat(timespec="seconds")} [{nombre}] rc={r.returncode}\n')
    f.write('cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas ' + ' '.join(shlex.quote(c) for c in cmd) + '\n\n')
print(f'[{nombre}] rc={r.returncode}')
import contextlib
with contextlib.suppress(BrokenPipeError):
    print('\n'.join((r.stdout + r.stderr).splitlines()[-12:]))
