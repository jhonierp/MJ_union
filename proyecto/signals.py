from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_save   
from .models import PersonasNaturales, PersonasAhorrosCreditos, Creditos,Ahorros


@receiver(post_save, sender=PersonasNaturales)
def crear_ahorros_y_creditos(sender, instance, created, **kwargs):
    
    if created:
        
        # Obtener los últimos IDs utilizados en las tablas Ahorros y Creditos
        ultimo_id_ahorros = Ahorros.objects.latest('id').id if Ahorros.objects.exists() else 0
        ultimo_id_creditos = Creditos.objects.latest('id').id if Creditos.objects.exists() else 0

        # Incrementar los valores de los IDs para las nuevas instancias
        nuevo_id_ahorros = ultimo_id_ahorros + 1
        nuevo_id_creditos = ultimo_id_creditos + 1

        # Crear una nueva instancia de Ahorros y asignarle el nuevo ID
        nuevo_ahorro = Ahorros(id=nuevo_id_ahorros)
        nuevo_ahorro.num_recibo=0
        nuevo_ahorro.aportes_anteriores=0
        nuevo_ahorro.aportes_pendientes=0
        nuevo_ahorro.aportes_por_pagar=20000
        nuevo_ahorro.aportes_recibidos=0
        nuevo_ahorro.saldo_aportes_por_pagar=0
        nuevo_ahorro.retiro_de_aportes=0
        nuevo_ahorro.total_de_aportes=0
        nuevo_ahorro.save()

        # Crear una nueva instancia de Creditos y asignarle el nuevo ID
        nuevo_credito = Creditos(id=nuevo_id_creditos)
        nuevo_credito.solicitud_de_credito=0
        nuevo_credito.fecha_inicio="01/01/2023"
        nuevo_credito.fecha_final="01/02/2023"
        nuevo_credito.valor_credito_solicitado=0
        nuevo_credito.numero_dias_credito=30
        nuevo_credito.plazo_meses=1
        nuevo_credito.cuota_credito=0
        nuevo_credito.valor_cuota_total=0
        nuevo_credito.credito_actual=0
        nuevo_credito.abono_credito=0
        nuevo_credito.saldo_credito=0
        nuevo_credito.interes_credito=0
        nuevo_credito.interes_anterior=0
        nuevo_credito.total_interes_a_pagar=0
        nuevo_credito.intereses_recibidos=0
        nuevo_credito.saldo_intereses=0
        nuevo_credito.nueva_afiliacion=35000
        nuevo_credito.total_recibido=0
        nuevo_credito.nota="Na"
        nuevo_credito.save()

        # Crear una nueva instancia de PersonasAhorrosCreditos con los IDs de Ahorros y Creditos
        nueva_relacion = PersonasAhorrosCreditos(
            persona_id=instance.id,
            ahorro_id=nuevo_id_ahorros,
            credito_id=nuevo_id_creditos,
            fecha=instance.fecha_regis,
            grupo_id=instance.grupo_id,
            estado="act"
        )
        nueva_relacion.save()   

