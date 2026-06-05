import warnings
from models.transaction import Transaction
from services.transaction_service import insert_transaction, get_report_by_category
from services.category_service import get_all_categories
from ai.clasificadorIA import ClasificadorIA


warnings.filterwarnings("ignore")

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

    # Jalamos todas las categorias que esten guardadas en la base de datos
    categorias = get_all_categories()

    while True:
        # Dibujamos el menu principal en la pantalla
        print("\n================================================")
        print("                MENÚ PRINCIPAL                  ")
        print("================================================")
        print("1. INGRESOS (Transacción / Reporte)")
        print("2. GASTOS   (Transacción / Reporte)")
        print("3. Salir")
        print("================================================")

        opcion = input("Selecciona una opción (1-3): ").strip()

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
                        id_categoria = ia.categorizar_y_mapear(descripcion, categorias)
                        categoria_nombre = next((cat.description for cat in categorias if cat.id_category == id_categoria), "Sin categoría")
                        print(f"→ Categoría detectada: {categoria_nombre}")

                        # Armamos la estructura de la transaccion con los datos que tenemos
                        txn = Transaction(
                            description=descripcion,
                            amount=amount,
                            type_txn="ingreso",
                            id_user=1,  # por ahora el id_user es 1 por defecto
                            id_category=id_categoria
                        )

                


                        # Mandamos a guardar la transaccion a la base de datos
                        insert_transaction(txn)
                        print("[OK] Ingreso guardado con éxito en la base de datos.")

                    except ValueError:
                        print("[Error] Ingresaste un monto inválido. Intenta de nuevo.")
                
                elif sub_opcion == '2':
                    # Llamamos a la funcion para obtener el reporte filtrado solo por ingresos
                    reporte = get_report_by_category("ingreso")
                    print("\n--- REPORTE DE INGRESOS POR CATEGORÍA ---")
                    if not reporte:
                        print("Todavía no tienes ningún ingreso registrado.")
                    else:
                        print(f"{'CATEGORÍA':<25} | {'TOTAL':<15}")
                        print("-" * 43)
                        for categoria, total in reporte:
                            print(f"{categoria:<25} | S/. {total:.2f}")
                        print("-" * 43)
                
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
                        id_categoria = ia.categorizar_y_mapear(descripcion, categorias)
                        print(f"-> Categoría sugerida por la IA (ID): {id_categoria}")

                        # Armamos la estructura del gasto para mandarlo
                        txn = Transaction(
                            description=descripcion,
                            amount=amount,
                            type_txn="gasto",
                            id_user=1,  # por ahora el id_user es 1 por defecto
                            id_category=id_categoria
                        )

                        # Guardamos el gasto en la base de datos
                        insert_transaction(txn)
                        print("[OK] Gasto guardado con éxito en la base de datos.")

                    except ValueError:
                        print("[Error] Ingresaste un monto inválido. Intenta de nuevo.")
                
                elif sub_opcion == '2':
                    # Obtenemos el reporte pero esta vez filtrando solo por gastos
                    reporte = get_report_by_category("gasto")
                    print("\n--- REPORTE DE GASTOS POR CATEGORÍA ---")
                    if not reporte:
                        print("Todavía no tienes ningún gasto registrado.")
                    else:
                        print(f"{'CATEGORÍA':<25} | {'TOTAL':<15}")
                        print("-" * 43)
                        for categoria, total in reporte:
                            print(f"{categoria:<25} | S/. {total:.2f}")
                        print("-" * 43)
                
                elif sub_opcion == '3':
                    # Regresamos al menu principal rompiendo el bucle del submenu
                    break
                else:
                    print("[Alerta] Opción no válida. Elige 1, 2 o 3.")

        elif opcion == '3':
            print("\n¡Gracias por usar la aplicación! Saliendo del sistema...")
            break

        else:
            print("[Alerta] Opción no válida. Elige 1, 2 o 3.")

if __name__ == "__main__":
    main()