import warnings
from models.transaction import Transaction
from services.transaction_service import insert_transaction
from services.category_service import get_all_categories
from ai.clasificadorIA import ClasificadorIA


warnings.filterwarnings("ignore")

def main():
    print("="*50)
    print(" ASISTENTE INTELIGENTE DE FINANZAS PERSONALES ")
    print("="*50)

    try:
        ia = ClasificadorIA()
    except Exception as e:
        print(f"\n[Error Crítico] No se pudo cargar la IA: {e}")
        return

    # Cargar categorías desde BD
    categorias = get_all_categories()

    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Registrar transacción")
        print("2. Ver reporte por categoría")
        print("3. Salir")

        opcion = input("Selecciona una opción (1-3): ")

        if opcion == '1':
            try:
                descripcion = input("\nDescripción: ")
                amount = float(input("Monto: S/. "))
                tipo = input("Tipo (ingreso/gasto): ").lower()
 
                if tipo not in ['ingreso', 'gasto']:
                    print("[Error] Tipo inválido")
                    continue

                # IA clasifica
                id_categoria = ia.categorizar_y_mapear(descripcion, categorias)

                print(f"→ Categoría detectada (ID): {id_categoria}")

                # Crear objeto Transaction
                txn = Transaction(
                    description=descripcion,
                    amount=amount,
                    type_txn=tipo,
                    id_user=1,  # usuario fijo por ahora
                    id_category=id_categoria
                )

                # Guardar en BD
                insert_transaction(txn)

                print("✅ Transacción guardada correctamente")

            except ValueError:
                print("[Error] Monto inválido")

        elif opcion == '2':
            from services.transaction_service import get_report_by_category

            reporte = get_report_by_category()

            if not reporte:
                print("No hay datos aún")
            else:
                print("\nCATEGORÍA | TOTAL")
                print("-"*30)
                for categoria, total in reporte:
                    print(f"{categoria:<20} S/. {total:.2f}")

        elif opcion == '3':
            print("Saliendo...")
            break

        else:
            print("Opción inválida. Por favor, selecciona 1, 2 o 3.")

if __name__ == "__main__":
    main()