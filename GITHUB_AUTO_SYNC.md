# Auto-Sync Automático - Matuzalen AGI AGI

## Configuración de GitHub

El proyecto Matuzalen AGI AGI está configurado para mantenerse actualizado automáticamente en GitHub.

### Repositorio
- **URL**: https://github.com/JoniCore-X/Matuzalen AGI-AGI
- **Rama principal**: main
- **Estado**: Público

### Script de Auto-Sync

**Archivo**: `auto-sync.bat`

Este script automatiza el proceso de sincronización con GitHub:

```batch
@echo off
cd /d "C:\Users\jonie\OneDrive\Desktop\Matuzalen-AGI"
git add .
git commit -m "Auto-sync: Actualización automática"
git push origin main
```

### Uso del Script

**Manual**:
```batch
cd C:\Users\jonie\OneDrive\Desktop\Matuzalen-AGI
auto-sync.bat
```

**Automático (Programador de Tareas de Windows)**:
1. Abrir Programador de Tareas
2. Crear tarea básica
3. Desencadenador: Cada 30 minutos
4. Acción: Ejecutar `auto-sync.bat`

### Comandos Git Manuales

**Ver estado**:
```bash
cd C:\Users\jonie\OneDrive\Desktop\Matuzalen-AGI
git status
```

**Agregar cambios**:
```bash
git add .
```

**Crear commit**:
```bash
git commit -m "Descripción del cambio"
```

**Push a GitHub**:
```bash
git push origin main
```

**Pull desde GitHub**:
```bash
git pull origin main
```

### Flujo de Trabajo Recomendado

1. **Antes de trabajar**:
   ```bash
   git pull origin main
   ```

2. **Durante el trabajo**:
   - Trabajar normalmente en el proyecto
   - El script auto-sync se ejecuta periódicamente

3. **Después de cambios importantes**:
   ```bash
   git add .
   git commit -m "Descripción del cambio importante"
   git push origin main
   ```

### Configuración de Auto-Sync Automático

**Opción 1: Programador de Tareas de Windows**
1. Win + R → `taskschd.msc`
2. Crear tarea básica
3. Nombre: "Matuzalen AGI Auto-Sync"
4. Desencadenador: Cada 30 minutos
5. Acción: Iniciar programa
   - Programa: `cmd.exe`
   - Argumentos: `/c "C:\Users\jonie\OneDrive\Desktop\Matuzalen-AGI\auto-sync.bat"`

**Opción 2: Script PowerShell**
```powershell
# auto-sync.ps1
$path = "C:\Users\jonie\OneDrive\Desktop\Matuzalen-AGI"
Set-Location $path
git add .
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git push origin main
}
```

### Verificación de Sincronización

**Verificar último commit**:
```bash
git log -1 --oneline
```

**Verificar commits remotos**:
```bash
git log origin/main -1 --oneline
```

**Comparar local vs remoto**:
```bash
git diff main origin/main
```

### Respaldo de Seguridad

El repositorio en GitHub funciona como:
- **Respaldo automático**: Todo el código está respaldado
- **Historial completo**: Todos los commits están guardados
- **Colaboración**: Permite colaboración futura
- **Disponibilidad**: Accesible desde cualquier lugar

### Archivos Excluidos (.gitignore)

El `.gitignore` excluye:
- Archivos temporales y caché
- Entornos virtuales
- Archivos de configuración local (.env)
- Archivos de IDE
- Archivos de logs
- Modelos grandes (.pkl, .h5, etc.)
- Archivos de datos

### Estado Actual

✅ **Repositoritorio Git**: Inicializado
✅ **GitHub**: Configurado (https://github.com/JoniCore-X/Matuzalen AGI-AGI)
✅ **Commit inicial**: Realizado (141 archivos, 17,187 líneas)
✅ **Push inicial**: Completado
✅ **Script auto-sync**: Creado
✅ **.gitignore**: Configurado

### Próximos Pasos

1. **Configurar auto-sync automático**: Usar Programador de Tareas
2. **Configurar webhook**: Para sincronización en tiempo real (opcional)
3. **Configurar GitHub Actions**: Para CI/CD (opcional)
4. **Configurar branches**: Para desarrollo y producción (opcional)

### Recuperación en Caso de Pérdida

Si pierdes el código local:

```bash
# Clonar desde GitHub
git clone https://github.com/JoniCore-X/Matuzalen AGI-AGI.git

# Restaurar entorno virtual
cd Matuzalen AGI-AGI/cognitive-core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Notas Importantes

- **Frecuencia recomendada**: Auto-sync cada 30 minutos
- **Commit manual**: Para cambios importantes, hacer commit manual con mensaje descriptivo
- **Conflicto**: Si hay conflictos, resolverlos manualmente antes de push
- **Seguridad**: El token de GitHub está configurado y funcionando

### Contacto

- **GitHub**: https://github.com/JoniCore-X/Matuzalen AGI-AGI
- **Issues**: https://github.com/JoniCore-X/Matuzalen AGI-AGI/issues

El proyecto está ahora respaldado y sincronizado automáticamente con GitHub.
