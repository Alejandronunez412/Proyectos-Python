# wiki-proyecto

Proyecto con archivos: `app.js`, `DAVE_IA.py`, `index.html`.

Instrucciones para respaldar en un repositorio Git remoto:

1. Crea un repo nuevo en GitHub/GitLab (preferiblemente privado) y copia la URL SSH o HTTPS.
2. En el proyecto, añade el remoto y sube los cambios:

```bash
cd /home/alejandro/Proyectos\ Python/wiki-proyecto
# si aún no hay repo:
git init
# configura tu usuario si no está configurado globalmente
git config user.name "Tu Nombre"
git config user.email "tu@correo"
# añade remote (ejemplo https)
git remote add origin https://github.com/usuario/mi-repo.git
# o con SSH:
# git remote add origin git@github.com:usuario/mi-repo.git
# sube la rama principal (main o master según tu preferencia)
git add .
git commit -m "Backup inicial antes de formatear PC"
git branch -M main
git push -u origin main
```

3. Confirma en GitHub/GitLab que los archivos se subieron correctamente.

Si quieres, puedo ejecutar estos pasos aquí y empujar el repo si me das la URL remota y confirmas que deseas subirlo desde este entorno.
