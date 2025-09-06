# RPPanel

Cog base para un panel de utilidades de rol con comandos de prefijo y slash.

## Comandos

Prefijo:
- `[p]rppanel ping`

Slash (tras sincronizar):
- `/rppanel ping`

La respuesta slash es efímera (solo visible para quien la usa); puedes cambiarlo en el código quitando `ephemeral=True`.

## Instalación

1. Añade el repo si no está:
   `[p]repo add joanjuan-cogs https://github.com/JoanJuan10/joanjuan-cogs`
2. Instala:
   `[p]cog install joanjuan-cogs rppanel`
3. Carga:
   `[p]load rppanel`
4. Sincroniza slash (global):
   `[p]slash sync`  (puede tardar hasta 1h en global; para un servidor rápido usa abajo)
   
   Para un solo servidor (en el servidor objetivo):
   `[p]slash sync guild`
5. Prueba:
   - Prefijo: `[p]rppanel ping`
   - Slash: `/rppanel ping` (puede requerir refrescar Discord con Ctrl+R)

## Notas
- No guarda datos persistentes.
- Al recargar el cog se eliminan los comandos para evitar duplicados.
- Si cambias estructura de slash, ejecuta de nuevo `[p]slash sync guild`.
