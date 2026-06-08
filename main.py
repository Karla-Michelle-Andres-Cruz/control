import flet as ft
import mysql.connector
import bcrypt
import re

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
def conectar_bd():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="control_escolar"
        )
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

# --- FUNCIONES DE BD ---
def registrar_usuario(nombre_usuario, contrasenia, nombre_completo, curp, matricula, correo, celular, id_especialidad):
    db = conectar_bd()
    if db:
        cursor = db.cursor()
        hashed = bcrypt.hashpw(contrasenia.encode('utf-8'), bcrypt.gensalt())
        query = """INSERT INTO usuarios 
                    (nombre_usuario, contrasenia, nombre_completo, curp, matricula, correo_institucional, celular, id_especialidad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (nombre_usuario, hashed.decode('utf-8'), nombre_completo, curp, matricula, correo, celular, id_especialidad)
        cursor.execute(query, valores)
        db.commit()
        cursor.close()
        db.close()

def registrar_materia(nombre_materia, semestre, id_usuario):
    db = conectar_bd()
    if db:
        cursor = db.cursor()
        query = "INSERT INTO materias (nombre_materia, semestre, id_usuario) VALUES (%s, %s, %s)"
        valores = (nombre_materia, semestre, id_usuario)
        cursor.execute(query, valores)
        db.commit()
        cursor.close()
        db.close()

def registrar_calificaciones(id_materia, u1, u2, u3):
    promedio = (u1 + u2 + u3) / 3
    db = conectar_bd()
    if db:
        cursor = db.cursor()
        query = """INSERT INTO calificaciones (id_materia, unidad1, unidad2, unidad3, promedio)
                    VALUES (%s, %s, %s, %s, %s)"""
        valores = (id_materia, u1, u2, u3, promedio)
        cursor.execute(query, valores)
        db.commit()
        cursor.close()
        db.close()




# --- APLICACIÓN PRINCIPAL ---
def main(page: ft.Page):
    page.title = "Sistema de Control Escolar"
    page.window_width = 500
    page.window_height = 650

    usuario_actual = {"id": None, "nombre": ""}

    def mostrar_snackbar(mensaje, color=ft.Colors.BLUE):
        page.show_dialog(ft.SnackBar(ft.Text(mensaje), bgcolor=color))
        page.show_dialog( ft.SnackBar(ft.Text(mensaje), bgcolor=color))
        page.update()

    # --- Barra de navegación inferior ---
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.BOOK, label="Materias"),
            ft.NavigationBarDestination(icon=ft.Icons.SCHOOL, label="Calificaciones"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Perfil"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY, label="Historial"),
        ],
        on_change=lambda e: page.go(
            "/dashboard" if e.control.selected_index == 0 else
            "/calificaciones" if e.control.selected_index == 1 else
            "/perfil" if e.control.selected_index == 2 else
            "/historial"
        )
    )

    # --- Vistas ---
    # Login
    txt_usuario = ft.TextField(label="Usuario", width=300)
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)

    def login_click(e):
        if not txt_usuario.value or not txt_password.value:
            txt_usuario.error_text = "Campo obligatorio" if not txt_usuario.value else None
            txt_password.error_text = "Campo obligatorio" if not txt_password.value else None
            page.update()
            return

        db = conectar_bd()
        if db:
            cursor = db.cursor(dictionary=True)
            query = "SELECT * FROM usuarios WHERE nombre_usuario = %s"
            cursor.execute(query, (txt_usuario.value,))
            usuario = cursor.fetchone()
            cursor.close()
            db.close()

            if usuario and bcrypt.checkpw(txt_password.value.encode('utf-8'),
                                        usuario["contrasenia"].encode('utf-8')):
            # Guardar todos los datos necesarios en usuario_actual
                usuario_actual["id"] = usuario["id_usuario"]
                usuario_actual["nombre"] = usuario["nombre_usuario"]
                usuario_actual["matricula"] = usuario["matricula"]
                usuario_actual["especialidad"] = usuario["id_especialidad"]
                usuario_actual["correo"] = usuario["correo_institucional"]
                usuario_actual["telefono"] = usuario["celular"]

                page.go("/dashboard")
            else:
                page.show_dialog(ft.SnackBar(ft.Text("Usuario o contraseña incorrectos"), bgcolor=ft.Colors.RED))
                page.update()


    vista_login = ft.View(
        route="/",
        controls=[
            ft.AppBar(title=ft.Text("Iniciar Sesión"), bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Bienvenido al Control Escolar", size=20, weight=ft.FontWeight.BOLD),
                        txt_usuario,
                        txt_password,
                        ft.Button("Ingresar", on_click=login_click, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                        ft.TextButton("¿No tienes cuenta? Regístrate aquí", on_click=lambda e: page.go("/registro"))
                    ]
                )
            )
        ]
    )

    # Registro
    def vista_registro():
        txt_nombre = ft.TextField(label="Nombre completo")
        txt_curp = ft.TextField(label="CURP")
        txt_matricula = ft.TextField(label="Matrícula")
        txt_correo = ft.TextField(label="Correo")
        txt_celular = ft.TextField(label="Celular")
        txt_usuario_reg = ft.TextField(label="Usuario")
        txt_password_reg = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)
        dropdown_especialidad = ft.Dropdown(
            label="Especialidad", 
            options=[
                ft.dropdown.Option("1", "Ingeniería en Sistemas"),
                ft.dropdown.Option("2", "Técnico en Electrónica"),
                ft.dropdown.Option("3", "Administración"),
                ft.dropdown.Option("4", "Contaduría")
            ]
        )

        def registro_click(e):
            valido = True
            mensaje_error = ""

    # Validar nombre
            if not txt_nombre.value.strip():
                txt_nombre.error_text = "Nombre obligatorio"
                mensaje_error = "El nombre es obligatorio"
                valido = False
            else:
                txt_nombre.error_text = None

    # Validar CURP
            curp_regex = r"^[A-Z0-9]{18}$"
            if not re.match(curp_regex, txt_curp.value.upper()):
                txt_curp.error_text = "CURP inválida"
                mensaje_error = "La CURP debe tener 18 caracteres en formato oficial"
                valido = False
            else:
                txt_curp.error_text = None

    # Validar matrícula
            if not txt_matricula.value.isdigit() or len(txt_matricula.value) < 14:
                txt_matricula.error_text = "Matrícula inválida"
                mensaje_error = "La matrícula debe tener al menos 14 números"
                valido = False
            else:
                txt_matricula.error_text = None

    # Validar correo
            correo_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.match(correo_regex, txt_correo.value):
                txt_correo.error_text = "Correo inválido"
                mensaje_error = "El correo debe tener formato usuario@dominio.com"
                valido = False
            else:
                txt_correo.error_text = None

    # Validar teléfono
            if not txt_celular.value.isdigit() or len(txt_celular.value) >= 10:
                txt_celular.error_text = "Teléfono inválido"
                mensaje_error = "El teléfono debe tener al menos 10 números"
                valido = False
            else:
                txt_celular.error_text = None

    # Validar usuario
            if not txt_usuario_reg.value.strip():
                txt_usuario_reg.error_text = "Usuario obligatorio"
                mensaje_error = "El usuario es obligatorio"
                valido = False
            else:
                txt_usuario_reg.error_text = None

    # Validar contraseña
            if not txt_password_reg.value.strip():
                txt_password_reg.error_text = "Contraseña obligatoria"
                mensaje_error = "La contraseña es obligatoria"
                valido = False
            else:
                txt_password_reg.error_text = None

            page.update()

            if not valido:
        # Mostrar SnackBar con el mensaje de error general
                page.show_dialog(ft.SnackBar(ft.Text(mensaje_error), bgcolor=ft.Colors.RED))
                page.update()
                return

    # Validar que todos los campos estén llenos
            if not all([
                txt_usuario_reg.value,
                txt_password_reg.value,
                txt_nombre.value,
                txt_curp.value,
                txt_matricula.value,
                txt_correo.value,
                txt_celular.value,
                dropdown_especialidad.value
            ]):
                mostrar_snackbar("Por favor llena todos los campos antes de continuar", ft.Colors.RED)
                page.update()
                return

            registrar_usuario(
                txt_usuario_reg.value,
                txt_password_reg.value,
                txt_nombre.value,
                txt_curp.value.upper(),
                txt_matricula.value,
                txt_correo.value,
                txt_celular.value,
                dropdown_especialidad.value
            )
            page.show_dialog(ft.SnackBar(ft.Text("Usuario registrado correctamente"), bgcolor=ft.Colors.GREEN))
            page.update()
            page.go("/")


        return ft.View(
            route="/registro",
            controls=[
                ft.AppBar(title=ft.Text("Registro de Alumno"), bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            txt_nombre, txt_curp, txt_matricula, txt_correo, txt_celular,
                            dropdown_especialidad, txt_usuario_reg, txt_password_reg,
                            ft.ElevatedButton("Registrar", on_click=registro_click, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                            ft.TextButton("¿Ya tienes cuenta? Inicia sesión aquí", on_click=lambda e: page.go("/")),
                        ]
                    )
                )
            ]
        )

    def vista_dashboard(id_usuario):
        txt_materia = ft.TextField(label="Nombre de la Materia", width=300)
        dropdown_semestre = ft.Dropdown(
            label="Semestre",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 7)],
            width=200
        )
        lbl_mensaje = ft.Text("", size=16)

        def guardar_materia(e):
            if not txt_materia.value.strip() or not dropdown_semestre.value:
                mostrar_snackbar("❌ Debes ingresar nombre y semestre", ft.Colors.RED)
                return

            registrar_materia(txt_materia.value, int(dropdown_semestre.value), usuario_actual["id"])
            mostrar_snackbar("✅ Materia registrada correctamente", ft.Colors.GREEN)


        return ft.View(
            route="/dashboard",
            controls=[
                ft.AppBar(title=ft.Text("Dashboard"), bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Alta de Materias", size=20, weight=ft.FontWeight.BOLD),
                            txt_materia,
                            dropdown_semestre,
                            ft.ElevatedButton("Guardar Materia", on_click=guardar_materia, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                            lbl_mensaje
                        ]
                    )
                ),
                nav_bar
            ]
        )


    # Calificaciones
    def vista_calificaciones(id_usuario):
        dropdown_materia = ft.Dropdown(label="Materia", width=300)
        txt_u1 = ft.TextField(label="Unidad 1", width=100)
        txt_u2 = ft.TextField(label="Unidad 2", width=100)
        txt_u3 = ft.TextField(label="Unidad 3", width=100)
        lbl_promedio = ft.Text("Promedio: --", size=16, weight=ft.FontWeight.BOLD)

    # Cargar materias desde BD
        def cargar_materias():
            db = conectar_bd()
            if db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT id_materia, nombre_materia FROM materias WHERE id_usuario = %s", (id_usuario,))
                resultados = cursor.fetchall()
                cursor.close()
                db.close()

                dropdown_materia.options = [ft.dropdown.Option(str(r["id_materia"]), r["nombre_materia"]) for r in resultados]
            page.update()

        cargar_materias()

        def calcular_promedio(e):
            try:
                valores = []
                if txt_u1.value.strip():
                    valores.append(float(txt_u1.value))
                if txt_u2.value.strip():
                    valores.append(float(txt_u2.value))
                if txt_u3.value.strip():
                    valores.append(float(txt_u3.value))

                if len(valores) == 0:
                    lbl_promedio.value = "❌ Ingresa al menos una calificación"
                else:
                    promedio = sum(valores) / len(valores)
                    if len(valores) == 1:
                        lbl_promedio.value = f"Unidad 1: {valores[0]:.2f}"
                    elif len(valores) == 2:
                        lbl_promedio.value = f"Promedio U1-U2: {promedio:.2f}"
                    else:
                        lbl_promedio.value = f"Promedio U1-U3: {promedio:.2f}"
            except:
                lbl_promedio.value = "❌ Error en los valores"
            page.update()


        def guardar_calificacion(e):
            try:
                id_materia = int(dropdown_materia.value)
                u1, u2, u3 = float(txt_u1.value), float(txt_u2.value), float(txt_u3.value)
                registrar_calificaciones(id_materia, u1, u2, u3)
                mostrar_snackbar("✅ Calificación guardada correctamente", ft.Colors.GREEN)
            except Exception as err:
                mostrar_snackbar(f"❌ Error: {err}", ft.Colors.RED)

        return ft.View(
            route="/calificaciones",
            controls=[
                ft.AppBar(title=ft.Text("Registro de Calificaciones"), bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            dropdown_materia,
                            ft.Row([txt_u1, txt_u2, txt_u3]),
                            lbl_promedio,
                            ft.Row([
                                ft.Button("Calcular Promedio", on_click=calcular_promedio, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                            ft.Button("Guardar", on_click=guardar_calificacion, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
                            ])
                        ]
                    )
                ),
                nav_bar
            ]
        )



    # Vista Historial Académico Completo
    def vista_historial(id_usuario):
        lista_historial = ft.Column()
        lbl_promedio_general = ft.Text("Promedio General Acumulado: --", size=16, weight=ft.FontWeight.BOLD)

        def cargar_historial():
            lista_historial.controls.clear()
            db = conectar_bd()
            if db:
                cursor = db.cursor(dictionary=True)
                # Traer materias y calificaciones por semestre
                query = """
                    SELECT m.semestre, m.nombre_materia, c.promedio
                    FROM materias m
                    JOIN calificaciones c ON m.id_materia = c.id_materia
                    WHERE m.id_usuario = %s
                    ORDER BY m.semestre
                """
                cursor.execute(query, (id_usuario,))
                resultados = cursor.fetchall()
                cursor.close()
                db.close()

                if resultados:
                    suma = 0
                    count = 0
                    semestre_actual = None
                    bloque_semestre = ft.Column()

                    for r in resultados:
                        # Si cambia el semestre, agregamos un bloque nuevo
                        if semestre_actual != r["semestre"]:
                            if semestre_actual is not None:
                                lista_historial.controls.append(
                                    ft.Card(
                                        content=ft.Container(
                                            padding=10,
                                            content=ft.Column([
                                                ft.Text(f"Semestre {semestre_actual}", weight=ft.FontWeight.BOLD),
                                                bloque_semestre
                                            ])
                                        )
                                    )
                                )
                            semestre_actual = r["semestre"]
                            bloque_semestre = ft.Column()

                        bloque_semestre.controls.append(
                            ft.Text(f"{r['nombre_materia']}: {r['promedio']:.2f}")
                        )
                        suma += r["promedio"]
                        count += 1

                    # Último semestre
                    lista_historial.controls.append(
                        ft.Card(
                            content=ft.Container(
                                padding=10,
                                content=ft.Column([
                                    ft.Text(f"Semestre {semestre_actual}", weight=ft.FontWeight.BOLD),
                                    bloque_semestre
                                ])
                            )
                        )
                    )

                    promedio_general = suma / count
                    lbl_promedio_general.value = f"Promedio General Acumulado: {promedio_general:.2f}"
                else:
                    lbl_promedio_general.value = "No hay calificaciones registradas"

            page.update()

        cargar_historial()

        return ft.View(
            route="/historial",
            controls=[
                ft.AppBar(title=ft.Text("Historial Académico"), bgcolor=ft.Colors.PURPLE, color=ft.Colors.WHITE),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            lbl_promedio_general,
                            lista_historial
                        ]
                    )
                ),
                nav_bar
            ]
        )


    # Vista Perfil del Alumno
    def vista_perfil(usuario_actual):
        return ft.View(
            route="/perfil",
            controls=[
                ft.AppBar(title=ft.Text("Perfil del Alumno"), bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(f"Nombre: {usuario_actual.get('nombre', '--')}", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Matrícula: {usuario_actual.get('matricula', '--')}"),
                            ft.Text(f"Especialidad: {usuario_actual.get('especialidad', '--')}"),
                            ft.Text(f"Correo: {usuario_actual.get('correo', '--')}"),
                            ft.Text(f"Teléfono: {usuario_actual.get('telefono', '--')}"),
                        ]
                    )
                ),
                nav_bar
            ]
        )


    # --- NAVEGACIÓN ENTRE VISTAS ---
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(vista_login)
        elif page.route == "/registro":
            page.views.append(vista_registro())
        elif page.route == "/calificaciones":
            page.views.append(vista_calificaciones(usuario_actual["id"] or 0))
        elif page.route == "/perfil":
            page.views.append(vista_perfil(usuario_actual))
        elif page.route == "/historial":
            page.views.append(vista_historial(usuario_actual["id"]))
        elif page.route == "/dashboard":
            page.views.append(vista_dashboard(usuario_actual))

        page.update()

    page.on_route_change = route_change
    route_change(None)

ft.run(main)
