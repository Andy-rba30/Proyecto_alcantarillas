# ¿Puedo borrar el resto de ramas? (2026-10-09)

**Respuesta corta: sí, 23 ramas se pueden borrar sin perder nada.** Todo su
contenido ya está en `main` (0 commits por delante, verificado hoy con el
historial completo). Dos ramas NO se deben borrar todavía, porque tienen un
commit que `main` no tiene.

## Ramas que NO borrar (tienen trabajo sin fusionar)

| Rama | Qué tiene | Qué hacer antes |
|---|---|---|
| `claude/laughing-volta-ubcdsj` | `respuesta_datos_cruces.md` (respuesta sobre datos de cruces de canal, de hoy) | Decidir si se fusiona a `main` o se descarta |
| `claude/charming-ptolemy-rk3y0q` | `estado_ramas_2026-10-09.md` (el informe de esta sesión) | Fusionar a `main` o descartar |

`main` no se borra nunca: es la rama principal.

## Ramas seguras de borrar (23, todas fusionadas en `main`)

```
archivo/expediente-2026-09-21
claude/blissful-wright-trtcxh
claude/bold-hypatia-kici5k
claude/dreamy-turing-wt1yd9
claude/eloquent-pasteur-kwwmop
claude/exciting-bell-zbjgw8
claude/ext-4-deuda-tecnica-szclb3
claude/festive-cray-ft8ibd
claude/festive-euler-wlva7n
claude/funny-franklin-nhh2es
claude/gallant-dirac-3mt6jo
claude/gifted-keller-z060ct
claude/guia-perfil-tesista-xvk30j
claude/indice-formulas-dimensional-i0hffh
claude/inspiring-lamport-1c7ghw
claude/kind-cori-74qchh
claude/magical-cray-x96fow
claude/magical-heisenberg-yv9a9j
claude/modest-hypatia-87ubz8
claude/peaceful-keller-f8kfzj
claude/sweet-ptolemy-mintvw
claude/tkinter-gui-visual-redesign-6p8fwx
claude/zen-euler-6i4q2w
```

Nota sobre `archivo/expediente-2026-09-21`: por el nombre parece una rama
guardada a propósito como «foto» del expediente de ese día. Está fusionada
(0 commits por delante de `main`), así que borrarla no pierde commits, pero si
la quieres conservar como marcador conviene reemplazarla por una etiqueta
(`git tag expediente-2026-09-21 origin/archivo/expediente-2026-09-21`) antes
de borrarla.

## Por qué es seguro

- Un commit no se pierde al borrar una rama si otra rama lo contiene. Las 23
  tienen todos sus commits dentro de `main`.
- Borrar la rama remota no borra nada del historial de `main`.
- Si alguien aún tiene una de esas ramas en su clon local, le seguirá
  existiendo hasta que la borre con `git branch -d`.

## Comando para borrarlas en el remoto (una sola orden)

```bash
git push origin --delete \
  archivo/expediente-2026-09-21 \
  claude/blissful-wright-trtcxh \
  claude/bold-hypatia-kici5k \
  claude/dreamy-turing-wt1yd9 \
  claude/eloquent-pasteur-kwwmop \
  claude/exciting-bell-zbjgw8 \
  claude/ext-4-deuda-tecnica-szclb3 \
  claude/festive-cray-ft8ibd \
  claude/festive-euler-wlva7n \
  claude/funny-franklin-nhh2es \
  claude/gallant-dirac-3mt6jo \
  claude/gifted-keller-z060ct \
  claude/guia-perfil-tesista-xvk30j \
  claude/indice-formulas-dimensional-i0hffh \
  claude/inspiring-lamport-1c7ghw \
  claude/kind-cori-74qchh \
  claude/magical-cray-x96fow \
  claude/magical-heisenberg-yv9a9j \
  claude/modest-hypatia-87ubz8 \
  claude/peaceful-keller-f8kfzj \
  claude/sweet-ptolemy-mintvw \
  claude/tkinter-gui-visual-redesign-6p8fwx \
  claude/zen-euler-6i4q2w
```

También se puede hacer desde GitHub: pestaña **Branches**, filtro «Merged»,
icono de papelera en cada una.

**No borré ninguna.** Borrar ramas remotas es irreversible desde el punto de
vista de la rama (los commits siguen en `main`), así que espero tu
confirmación. Si me dices «borra las 23», lo hago.
