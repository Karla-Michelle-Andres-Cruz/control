import flet as ft
import mysql.connector
import bcrypt

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
def conectar_bd():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",       # Ajusta según tu configuración
            password="",       # Ajusta según tu configuración
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
async def main(page: ft.Page):
    page.title = "Sistema de Control Escolar"
    page.window_width = 500
    page.window_height = 650

    usuario_actual = {"id": None, "nombre": ""}

        # --- Drawer (Menú lateral) ---
    nav_drawer = ft.NavigationDrawer(
        controls=[
            ft.NavigationDrawerDestination(icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationDrawerDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationDrawerDestination(icon=ft.Icons.SCHOOL, label="Calificaciones"),
            ft.NavigationDrawerDestination(icon=ft.Icons.PERSON, label="Perfil"),
            ft.NavigationDrawerDestination(icon=ft.Icons.HISTORY, label="Historial Académico"),
            ft.NavigationDrawerDestination(icon=ft.Icons.LOGOUT, label="Cerrar Sesión"),
        ],
        on_change=lambda e: (
            page.push_route("/" if e.control.selected_index == 0 else
                            "/dashboard" if e.control.selected_index == 1 else
                            "/calificaciones" if e.control.selected_index == 2 else
                            "/perfil" if e.control.selected_index == 3 else
                            "/historial" if e.control.selected_index == 4 else
                            "/")
        )
    )

    page.navigation_drawer = nav_drawer

    # --- VISTAS ---
    # Login
    txt_usuario = ft.TextField(label="Usuario", width=300)
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)

    async def login_click(e):
        if not txt_usuario.value or not txt_password.value:
            txt_usuario.error_text = "Campo obligatorio" if not txt_usuario.value else None
            txt_password.error_text = "Campo obligatorio" if not txt_password.value else None
            await page.update_async()
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
                usuario_actual["id"] = usuario["id_usuario"]
                usuario_actual["nombre"] = usuario["nombre_usuario"]
                await page.push_route("/dashboard")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Usuario o contraseña incorrectos"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                await page.update_async()


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
                        ft.TextButton("¿No tienes cuenta? Regístrate aquí", on_click=lambda _: page.push_route("/registro"))
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

        async def registro_click(e):
            registrar_usuario(
                txt_usuario_reg.value,
                txt_password_reg.value,
                txt_nombre.value,
                txt_curp.value,
                txt_matricula.value,
                txt_correo.value,
                txt_celular.value,
                dropdown_especialidad.value
            )
            page.snack_bar = ft.SnackBar(ft.Text("Usuario registrado correctamente"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            await page.push_route("/")


        return ft.View(
            route="/registro",
            controls=[
                ft.AppBar(title=ft.Text("Registro de Alumno"), bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
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
                            ft.TextButton("¿Ya tienes cuenta? Inicia sesión aquí", on_click=lambda _: page.push_route("/"))
                        ]
                    )
                )
            ]
        )

    # Dashboard
    def vista_dashboard():
        dropdown_semestre = ft.Dropdown(
            label="Selecciona el Semestre",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 7)],
            width=200
        )
        lista_materias = ft.Column()
        lbl_promedio_general = ft.Text("Promedio General del Semestre: --", size=16, weight=ft.FontWeight.BOLD)

        # Función para cargar materias y calificaciones desde BD
        def cargar_datos(e):
            lista_materias.controls.clear()
            semestre = dropdown_semestre.value
            if not semestre:
                lbl_promedio_general.value = "Selecciona un semestre"
                page.update()
                return

            db = conectar_bd()
            if db:
                cursor = db.cursor(dictionary=True)
                query = """SELECT m.nombre_materia, c.unidad1, c.unidad2, c.unidad3, c.promedio
                            FROM materias m
                            JOIN calificaciones c ON m.id_materia = c.id_materia
                            WHERE m.id_usuario = %s AND m.semestre = %s"""
                cursor.execute(query, (usuario_actual["id"], semestre))
                resultados = cursor.fetchall()
                cursor.close()
                db.close()

                if resultados:
                    suma = 0
                    for r in resultados:
                        estado = "Aprobado ✅" if r["promedio"] >= 6 else "Reprobado ❌"
                        lista_materias.controls.append(
                            ft.Card(
                                content=ft.Container(
                                    padding=10,
                                    content=ft.Column([
                                        ft.Text(f"Materia: {r['nombre_materia']}", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Unidad 1: {r['unidad1']} | Unidad 2: {r['unidad2']} | Unidad 3: {r['unidad3']}"),
                                        ft.Text(f"Promedio: {r['promedio']:.2f} - {estado}")
                                    ])
                                )
                            )
                        )
                        suma += r["promedio"]
                    promedio_general = suma / len(resultados)
                    lbl_promedio_general.value = f"Promedio General del Semestre: {promedio_general:.2f}"
                else:
                    lbl_promedio_general.value = "No hay materias registradas en este semestre"

            page.update()

        dropdown_semestre.on_change = cargar_datos

        return ft.View(
            route="/dashboard",
            controls=[
                ft.AppBar(title=ft.Text(f"Panel de {usuario_actual['nombre']}"),
                            bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE,
                            leading=ft.IconButton(ft.Icons.MENU, on_click=lambda _: setattr(nav_drawer, "open", True))),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Mi Historial Académico", size=22, weight=ft.FontWeight.BOLD),
                            dropdown_semestre,
                            lbl_promedio_general,
                            lista_materias
                        ]
                    )
                )
            ]
        )


    # Calificaciones
    def vista_calificaciones(id_usuario):
        txt_materia = ft.TextField(label="Nombre de la Materia", width=300)
        txt_u1 = ft.TextField(label="Unidad 1", width=100)
        txt_u2 = ft.TextField(label="Unidad 2", width=100)
        txt_u3 = ft.TextField(label="Unidad 3", width=100)
        lbl_promedio = ft.Text("Promedio: --", size=16, weight=ft.FontWeight.BOLD)

        def calcular_promedio(e):
            try:
                u1, u2, u3 = float(txt_u1.value), float(txt_u2.value), float(txt_u3.value)
                if not (0 <= u1 <= 10 and 0 <= u2 <= 10 and 0 <= u3 <= 10):
                    lbl_promedio.value = "Error: valores fuera de rango (0-10)"
                else:
                    promedio = (u1 + u2 + u3) / 3
                    lbl_promedio.value = f"Promedio: {promedio:.2f}"
            except ValueError:
                lbl_promedio.value = "Error: ingresa solo números"
            page.update()

        def guardar_calificacion(e):
            try:
                u1, u2, u3 = float(txt_u1.value), float(txt_u2.value), float(txt_u3.value)
                # Registrar la materia en BD
                registrar_materia(txt_materia.value, 1, id_usuario)  # ejemplo: semestre 1
                db = conectar_bd()
                cursor = db.cursor()
                cursor.execute("SELECT LAST_INSERT_ID()")
                id_materia = cursor.fetchone()[0]
                cursor.close()
                db.close()

                # Registrar calificaciones ligadas a la materia
                registrar_calificaciones(id_materia, u1, u2, u3)

                page.snack_bar = ft.SnackBar(ft.Text("Calificación guardada correctamente"), bgcolor=ft.Colors.GREEN)
                page.snack_bar.open = True
                page.update()
            except Exception as err:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {err}"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                page.update()

        return ft.View(
            route="/calificaciones",
            controls=[
                ft.AppBar(
                    title=ft.Text("Registro de Calificaciones"),
                    bgcolor=ft.Colors.ORANGE,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(ft.Icons.MENU, on_click=lambda _: setattr(nav_drawer, "open", True))
                ),
                ft.Column(
                    controls=[
                        txt_materia,
                        ft.Row([txt_u1, txt_u2, txt_u3]),
                        lbl_promedio,
                        ft.Row([
                            ft.Button("Calcular Promedio", on_click=calcular_promedio, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                            ft.Button("Guardar", on_click=guardar_calificacion, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
                        ])
                    ]
                )
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
                query = """SELECT semestre, promedio_semestre
                            FROM historial
                            WHERE id_usuario = %s
                            ORDER BY semestre"""
                cursor.execute(query, (id_usuario,))
                resultados = cursor.fetchall()
                cursor.close()
                db.close()

                if resultados:
                    suma = 0
                    for r in resultados:
                        lista_historial.controls.append(
                            ft.Card(
                                content=ft.Container(
                                    padding=10,
                                    content=ft.Column([
                                        ft.Text(f"Semestre {r['semestre']}", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Promedio: {r['promedio_semestre']:.2f}")
                                    ])
                                )
                            )
                        )
                        suma += r["promedio_semestre"]
                    promedio_general = suma / len(resultados)
                    lbl_promedio_general.value = f"Promedio General Acumulado: {promedio_general:.2f}"
                else:
                    lbl_promedio_general.value = "No hay historial registrado"

            page.update()

        # Cargar historial al entrar a la vista
        cargar_historial()

        return ft.View(
            route="/historial",
            controls=[
                ft.AppBar(title=ft.Text("Historial Académico"),
                            bgcolor=ft.Colors.PURPLE, color=ft.Colors.WHITE,
                            leading=ft.IconButton(ft.Icons.MENU, on_click=lambda _: setattr(nav_drawer, "open", True))),
                ft.Column(
                    controls=[
                        lbl_promedio_general,
                        lista_historial
                    ]
                )
            ]
        )

    # Vista Perfil del Alumno
    def vista_perfil(usuario_actual):
        return ft.View(
            route="/perfil",
            controls=[
                ft.AppBar(
                    title=ft.Text("Perfil del Alumno"),
                    bgcolor=ft.Colors.BLUE_700,
                    color=ft.Colors.WHITE,
                    leading=ft.IconButton(ft.Icons.MENU, on_click=lambda _: setattr(nav_drawer, "open", True))
                ),
                ft.Column(
                    controls=[
                        ft.CircleAvatar(radius=40, foreground_image_url="https://via.placeholder.com/150"),
                        ft.Text(f"Nombre: {usuario_actual['nombre']}", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Matrícula: {usuario_actual['Matrícula']}"),
                        ft.Text(f"Especialidad: {usuario_actual['Especialidad']}"),
                        ft.Text(f"Correo: {usuario_actual['correo']}"),
                        ft.Text(f"Teléfono: {usuario_actual['celular']}"),
                    ]
                )
            ]
        )



    # --- NAVEGACIÓN ENTRE VISTAS ---
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(vista_login)
        elif page.route == "/registro":
            page.views.append(vista_registro())
        elif page.route == "/dashboard":
            page.views.append(vista_dashboard())
        elif page.route == "/calificaciones":
            page.views.append(vista_calificaciones(usuario_actual["id"] or 0))
        elif page.route == "/perfil":
            page.views.append(vista_perfil(usuario_actual))
        elif page.route == "/historial":
            page.views.append(vista_historial(usuario_actual["id"]))

        page.update()

    page.on_route_change = route_change
    route_change(None)


ft.run(main)
