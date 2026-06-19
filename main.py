import warnings
from models.transaction import Transaction
from models.category import Category
from services.transaction_service import insert_transaction, get_report_by_category, get_financial_summary
from services.category_service import get_all_categories, get_subcategories_by_parent, create_category
from ai.clasificadorIA import ClasificadorIA
from services.user_service import login, create_user, get_user_by_username
from models.user import User

def iniciar_sesion():
    while True:
        print("\n================================================")
        print("                 ACCESO AL SISTEMA              ")
        print("================================================")
        print("1. Iniciar Sesión")
        print("2. Registrarse")
        print("3. Salir")
        print("================================================")
        
        opc = input("Selecciona una opción (1-3): ").strip()
        
        if opc == '1':
            print("\n--- INICIAR SESIÓN ---")
            username = input("Usuario: ").strip()
            password = input("Contraseña: ").strip()
            
            if not username or not password:
                print("[Alerta] El usuario y contraseña no pueden estar vacíos.")
                continue
                
            user = login(username, password)
            if user:
                print(f"\n[OK] Acceso concedido. ¡Bienvenido, {user[1]}!")
                return user  # Retorna tuple (id_user, username)
            else:
                print("[Error] Usuario o contraseña incorrectos.")
                
        elif opc == '2':
            print("\n--- REGISTRO DE NUEVO USUARIO ---")
            username = input("Nuevo Usuario: ").strip()
            password = input("Nueva Contraseña: ").strip()
            
            if not username or not password:
                print("[Alerta] El usuario y contraseña no pueden estar vacíos.")
                continue
                
            # Verificar si ya existe
            existing = get_user_by_username(username)
            if existing:
                print("[Error] El nombre de usuario ya está registrado.")
                continue
                
            new_user = User(username=username, password=password)
            try:
                new_id = create_user(new_user)
                print(f"[OK] Usuario registrado con éxito. ID asignado: {new_id}")
                print("Por favor, inicia sesión con tus credenciales.")
            except Exception as e:
                print(f"[Error] No se pudo crear el usuario: {e}")
                
        elif opc == '3':
            print("\nSaliendo del sistema...")
            return None
        else:
            print("[Alerta] Opción no válida. Elige 1, 2 o 3.")


warnings.filterwarnings("ignore")

def gestionar_subcategoria(parent_id, descripcion, ia):
    subcategorias = get_subcategories_by_parent(parent_id)
    if not subcategorias:
        return None
    
    id_subcategoria, subcat_nombre = ia.categorizar_y_mapear_subcategoria(descripcion, subcategorias)
    if id_subcategoria:
        print(f"-> Subcategoría sugerida por la IA: {subcat_nombre} (ID: {id_subcategoria})")
    return id_subcategoria

def main():
    print("="*50)
    print(" ASISTENTE INTELIGENTE DE FINANZAS PERSONALES ")
    print("="*50)

    try:
        # Cargamos el clasificador con inteligencia artificial para que organice todo
        ia = ClasificadorIA()
    except Exception as e:
        print(f"\n[Error] No se pudo iniciar el modelo de IA: {e}")
        return

    # Flujo de login/registro
    user_session = iniciar_sesion()
    if not user_session:
        return
        
    current_user_id, current_username = user_session

    while True:
        # Dibujamos el menu principal en la pantalla
        print("\n================================================")
        print("                MENÚ PRINCIPAL                  ")
        print("================================================")
        print("1. INGRESOS (Transacción / Reporte)")
        print("2. GASTOS   (Transacción / Reporte)")
        print("3. VER DASHBOARD FINANCIERO")
        print("4. Salir")
        print("================================================")

        opcion = input("Selecciona una opción (1-4): ").strip()

        if opcion == '1':
            while True:
                # Submenu para controlar todo lo que son ingresos de dinero
                print("\n------------------------------------------------")
                print("                MENÚ INGRESOS                   ")
                print("------------------------------------------------")
                print("1. Registrar Transacción")
                print("2. Ver Reporte por Categoría")
                print("3. Volver al Menú Principal")
                print("------------------------------------------------")
                
                sub_opcion = input("Selecciona una opción (1-3): ").strip()
                
                if sub_opcion == '1':
                    try:
                        print("\n--- NUEVO INGRESO ---")
                        descripcion = input("Descripción: ").strip()
                        if not descripcion:
                            print("[Alerta] La descripción no puede quedar en blanco.")
                            continue
                        
                        amount = float(input("Monto: S/. "))
                        if amount <= 0:
                            print("[Alerta] El monto ingresado debe ser mayor que cero.")
                            continue


                        # Le pedimos a la IA que decida la categoria mas adecuada segun el texto
                        id_categoria, cat_nombre = ia.categorizar_y_mapear(descripcion, 'ingreso')
                        print(f"-> Categoría sugerida por la IA: {cat_nombre} (ID: {id_categoria})")

                        # Gestionamos la subcategoría
                        id_subcategoria = gestionar_subcategoria(id_categoria, descripcion, ia)

                        # Si la IA sugiere subcategoría, guardamos ese ID en la transacción; de lo contrario, la principal.
                        id_final = id_subcategoria if id_subcategoria else id_categoria

                        # Armamos la estructura de la transaccion con los datos que tenemos
                        txn = Transaction(
                            description=descripcion,
                            amount=amount,
                            type_txn="ingreso",
                            id_user=current_user_id,
                            id_category=id_final
                        )

                


                        # Mandamos a guardar la transaccion a la base de datos
                        insert_transaction(txn)
                        print("[OK] Ingreso guardado con éxito en la base de datos.")

                    except ValueError:
                        print("[Error] Ingresaste un monto inválido. Intenta de nuevo.")
                
                elif sub_opcion == '2':
                    # Llamamos a la funcion para obtener el reporte filtrado solo por ingresos
                    reporte = get_report_by_category(current_user_id, "ingreso")
                    print("\n--- REPORTE DE INGRESOS POR CATEGORÍA ---")
                    if not reporte:
                        print("Todavía no tienes ningún ingreso registrado.")
                    else:
                        print(f"{'CATEGORÍA':<20} | {'SUBCATEGORÍA':<20} | {'TOTAL':<15}")
                        print("-" * 62)
                        for categoria, subcategoria, total in reporte:
                            print(f"{categoria:<20} | {subcategoria:<20} | S/. {total:.2f}")
                        print("-" * 62)
                
                elif sub_opcion == '3':
                    # Salimos del bucle interno para volver al menu principal
                    break
                else:
                    print("[Alerta] Opción no válida. Elige 1, 2 o 3.")

        elif opcion == '2':
            while True:
                # Submenu para controlar los gastos o egresos
                print("\n------------------------------------------------")
                print("                 MENÚ GASTOS                    ")
                print("------------------------------------------------")
                print("1. Registrar Transacción")
                print("2. Ver Reporte por Categoría")
                print("3. Volver al Menú Principal")
                print("------------------------------------------------")
                
                sub_opcion = input("Selecciona una opción (1-3): ").strip()
                
                if sub_opcion == '1':
                    try:
                        print("\n--- NUEVO GASTO ---")
                        descripcion = input("Descripción: ").strip()
                        if not descripcion:
                            print("[Alerta] La descripción no puede quedar en blanco.")
                            continue
                        
                        amount = float(input("Monto: S/. "))
                        if amount <= 0:
                            print("[Alerta] El monto ingresado debe ser mayor que cero.")
                            continue

                        # La IA analiza la descripcion para asociarle una categoria
                        id_categoria, cat_nombre = ia.categorizar_y_mapear(descripcion, 'gasto')
                        print(f"-> Categoría sugerida por la IA: {cat_nombre} (ID: {id_categoria})")

                        # Gestionamos la subcategoría
                        id_subcategoria = gestionar_subcategoria(id_categoria, descripcion, ia)

                        # Si la IA sugiere subcategoría, guardamos ese ID en la transacción; de lo contrario, la principal.
                        id_final = id_subcategoria if id_subcategoria else id_categoria

                        # Armamos la estructura del gasto para mandarlo
                        txn = Transaction(
                            description=descripcion,
                            amount=amount,
                            type_txn="gasto",
                            id_user=current_user_id,
                            id_category=id_final
                        )

                        # Guardamos el gasto en la base de datos
                        insert_transaction(txn)
                        print("[OK] Gasto guardado con éxito en la base de datos.")

                    except ValueError:
                        print("[Error] Ingresaste un monto inválido. Intenta de nuevo.")
                
                elif sub_opcion == '2':
                    # Obtenemos el reporte pero esta vez filtrando solo por gastos
                    reporte = get_report_by_category(current_user_id, "gasto")
                    print("\n--- REPORTE DE GASTOS POR CATEGORÍA ---")
                    if not reporte:
                        print("Todavía no tienes ningún gasto registrado.")
                    else:
                        print(f"{'CATEGORÍA':<20} | {'SUBCATEGORÍA':<20} | {'TOTAL':<15}")
                        print("-" * 62)
                        for categoria, subcategoria, total in reporte:
                            print(f"{categoria:<20} | {subcategoria:<20} | S/. {total:.2f}")
                        print("-" * 62)
                
                elif sub_opcion == '3':
                    # Regresamos al menu principal rompiendo el bucle del submenu
                    break
                else:
                    print("[Alerta] Opción no válida. Elige 1, 2 o 3.")

        elif opcion == '3':
            try:
                summary = get_financial_summary(current_user_id)
                
                total_inc = summary["total_income"]
                total_exp = summary["total_expense"]
                net_bal = summary["net_balance"]
                
                print("\n================================================")
                print("               DASHBOARD FINANCIERO             ")
                print("================================================")
                print(f"  (+) Total Ingresos:   S/. {total_inc:,.2f}")
                print(f"  (-) Total Gastos:     S/. {total_exp:,.2f}")
                print("  ----------------------------------------------")
                if net_bal >= 0:
                    print(f"  (=) Balance Neto:     S/. {net_bal:,.2f} (Ahorro)")
                else:
                    print(f"  (=) Balance Neto:     S/. {net_bal:,.2f} (Deficit [!])")
                
                # Dynamic indicators
                if total_inc > 0:
                    pct_spent = (total_exp / total_inc) * 100
                    print(f"  Porcentaje Gastado:   {pct_spent:.1f}%")
                    
                    # Visual representation bar
                    bar_length = 20
                    filled = min(bar_length, int((pct_spent / 100) * bar_length))
                    bar = "#" * filled + "." * (bar_length - filled)
                    print(f"  Ratio Gasto/Ingreso:  [{bar}]")
                else:
                    if total_exp > 0:
                        print("  Ratio Gasto/Ingreso:  [[!] Sin ingresos registrados]")
                    else:
                        print("  Ratio Gasto/Ingreso:  [Sin transacciones]")
                print("================================================")
                input("\nPresiona Enter para volver al Menú Principal...")
            except Exception as e:
                print(f"[Error] No se pudo cargar el dashboard: {e}")

        elif opcion == '4':
            print("\n¡Gracias por usar la aplicación! Saliendo del sistema...")
            break

        else:
            print("[Alerta] Opción no válida. Elige 1, 2, 3 o 4.")

if __name__ == "__main__":
    main()