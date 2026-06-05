# 📚 Sistema de Control Escolar

## 📖 Descripción del proyecto
El **Sistema de Control Escolar** es una aplicación desarrollada en **Python** con el framework **Flet** y una base de datos **MySQL**. Su propósito es facilitar la gestión académica de los alumnos, permitiendo registrar usuarios, iniciar sesión de manera segura, capturar calificaciones, consultar el historial académico y visualizar el perfil del estudiante.  

La interfaz gráfica es sencilla e intuitiva, con navegación mediante una barra inferior que conecta las secciones principales: Inicio, Dashboard, Calificaciones, Perfil e Historial.

---

## 🎯 Objetivos
- Implementar un sistema escolar básico que centralice la información de los alumnos.  
- Permitir el **registro seguro** de usuarios con contraseñas encriptadas.  
- Facilitar el **registro y consulta de calificaciones** por materia y semestre.  
- Mostrar el **promedio general** y el historial académico acumulado.  
- Ofrecer un **perfil de alumno** con datos personales y académicos.  
- Proporcionar una interfaz amigable y fácil de usar para estudiantes y administradores.

---

## ▶️ Pasos para ejecutar el proyecto

1. **Clonar el repositorio** 
   git clone https://github.com/tuusuario/control-escolar.git
   cd control-escolar

2. **Crear entorno virtual e instalar dependencias**
   python -m venv venv
   venv\Scripts\activate   # En Windows
   pip install -r requirements.txt

3. **Configurar la base de datos MySQL**  
   - Crear la base de datos `control_escolar`.  
   - Ejecutar los scripts SQL para crear las tablas: `usuarios`, `materias`, `calificaciones` y `historial`.  
   - Ajustar los parámetros de conexión en `main.py` (usuario, contraseña, host).

4. **Ejecutar la aplicación**  
   python main.py

5. **Flujo de uso**  
   - Registrar un nuevo alumno.  
   - Iniciar sesión con usuario y contraseña.  
   - Acceder al Dashboard para ver materias y promedios.  
   - Registrar calificaciones en la sección correspondiente.  
   - Consultar el historial académico acumulado.  
   - Revisar el perfil del alumno con sus datos básicos.