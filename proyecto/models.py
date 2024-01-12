import datetime
from decimal import ROUND_CEILING, Decimal
import math
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.shortcuts import render


class Ahorros(models.Model):
    num_recibo = models.IntegerField(blank=True, null=True)
    aportes_anteriores = models.FloatField(blank=True, null=True)
    aportes_pendientes = models.FloatField(blank=True, null=True)
    aportes_por_pagar = models.FloatField(blank=True, null=True)
    aportes_recibidos = models.FloatField(blank=True, null=True)
    saldo_aportes_por_pagar = models.FloatField(blank=True, null=True)
    retiro_de_aportes = models.FloatField(blank=True, null=True)
    total_de_aportes = models.FloatField(blank=True, null=True)
    

    class Meta:
        db_table = 'ahorros'
    
    def save(self, *args, **kwargs):
        '''if self.aportes_por_pagar:
            aportes_pendientes = float(self.aportes_pendientes if self.aportes_pendientes else 0)
            
            resultado = aportes_pendientes + self.aportes_por_pagar

            # Redondear hacia arriba con dos dígitos decimales de precisión
            resultado_redondeado = math.ceil(resultado * 100) / 100
            tot_apo = float(resultado_redondeado)
            self.aportes_por_pagar = tot_apo

        super(Ahorros, self).save(*args, **kwargs)'''
        
        # Calcula el total de aportes cuando se actualizan los campos relacionados
        if self.aportes_recibidos is not None and self.aportes_anteriores is not None and self.retiro_de_aportes is not None:
            self.total_de_aportes = self.aportes_recibidos + self.aportes_anteriores - self.retiro_de_aportes
        super(Ahorros, self).save(*args, **kwargs)
        '''if self.retiro_de_aportes >0 and self.total_de_aportes==0:


        super(Ahorros, self).save(*args, **kwargs)'''
    

class BeneficiariosPersonasNaturales(models.Model):
    nombre_completo = models.CharField(max_length=100)
    porcentaje = models.ForeignKey('Porcentajes', models.DO_NOTHING)
    parentesco = models.ForeignKey('Parentescos', models.DO_NOTHING)

    class Meta:
        db_table = 'beneficiarios_personas_naturales'


class Creditos(models.Model):
    solicitud_de_credito = models.FloatField(blank=True, null=True)
    fecha_inicio = models.CharField(max_length=50, null=True)
    fecha_final = models.CharField(max_length=50, null=True)
    valor_credito_solicitado = models.FloatField(blank=True, null=True)
    numero_dias_credito = models.IntegerField(blank=True, null=True)
    plazo_meses = models.IntegerField(blank=True, null=True)
    cuota_credito = models.FloatField(blank=True, null=True)
    valor_cuota_total = models.FloatField(blank=True, null=True)
    credito_actual = models.FloatField(blank=True, null=True)
    abono_credito = models.FloatField(blank=True, null=True)
    saldo_credito = models.FloatField(blank=True, null=True)
    interes_credito = models.FloatField(blank=True, null=True)
    interes_anterior = models.FloatField(blank=True, null=True)
    total_interes_a_pagar = models.FloatField(blank=True, null=True)
    intereses_recibidos = models.FloatField(blank=True, null=True)
    saldo_intereses = models.FloatField(blank=True, null=True)
    nueva_afiliacion = models.FloatField(blank=True, null=True)
    total_recibido = models.FloatField(blank=True, null=True)
    nota = models.CharField(max_length=50,null=True)
    
    class Meta:
        db_table = 'creditos'
    #def set_numero_dias_credito(self, valor):
        #self.numero_dias_credito = valor
    def guardar_total_actualizado(self,a):
        # Sumar 20,000 al total_recibido actual
        self.total_recibido = a
        self.save() 
              
    def save(self, *args, **kwargs):      
        if self.plazo_meses:
            fecha_inicial = self.fecha_inicio if self.fecha_inicio else 0
            fecha_final = self.fecha_final if self.fecha_final else 0

            parts = fecha_inicial.split() 
            dia_i = parts[0][0:2]
            mes_i = parts[0][3:5]
            año_i = parts[0][6:10]
            fecha_update=f"{dia_i}/{mes_i}/{año_i}"
            

            parts2 = fecha_final.split() 
            dia_f = parts2[0][0:2]
            mes_f = parts2[0][3:5]
            año_f = parts2[0][6:10]
            fecha_update2=f"{dia_f}/{mes_f}/{año_f}"
            '''print("dia_i:::::::::::::::::::",dia_f)
            print("mes_i:::::::::::::::::::",mes_f)
            print("dia_i:::::::::::::::::::",año_f)
            print("fecha_update2:::::::::::::::::::",fecha_update2)'''
            
            #_________________
            plazo_meses = self.plazo_meses if self.plazo_meses else 0
            if plazo_meses is None:
                    plazo_mesesa=1
                    self.plazo_meses=1
            else:
                plazo_mesesa=plazo_meses

            if plazo_mesesa >12:
                    anual = plazo_mesesa// 12  # Cociente de la división
                    mensual = plazo_mesesa % 12
                    print("anual:::::::::::::::::::",anual)
                    print("mensual:::::::::::::::::::",mensual)

                    mes_fin=(int(mes_i)+mensual)
                    if mes_fin > 12:
                        me=str(mes_fin-12)
                        año_new=str(int(año_i)+anual)
                    else:
                        me=str(mes_fin)
                        año_new=str(int(año_i)+anual)
            else:
                mes_fin=int(mes_i) + plazo_mesesa
                if mes_fin > 12:
                    me=str(mes_fin-12)
                    año_new=str(int(año_i)+1)
                else:
                    me=str(mes_fin)
                    año_new=str(año_i)

            if float(me) <10 and float(me) > 0:
                fecha_fin=f"{dia_f}/0{me}/{año_new}"  
                self.fecha_final=str(fecha_fin)

            else:
                fecha_fin=f"{dia_f}/{me}/{año_new}"  
                self.fecha_final=str(fecha_fin)
            #numero = 5000000

            # Formatear el número con separadores de miles y un punto decimal
            #formatted_number = "{:,.0f}".format(numero).replace(',', ' ').replace('.', ',')

            # Mostrar el número formateado
            #print(formatted_number)
        
        super(Creditos, self).save(*args, **kwargs)
        
        if self.total_interes_a_pagar:
            interes_credito = float(self.interes_credito if self.interes_credito else 0)
            interes_anterior = float(self.interes_anterior if self.interes_anterior else 0)

            resultado = interes_credito + interes_anterior

            # Redondear hacia arriba con dos dígitos decimales de precisión
            resultado_redondeado = math.ceil(resultado * 100) / 100
            tot_apo = float(resultado_redondeado)
            self.total_interes_a_pagar = tot_apo

        super(Creditos, self).save(*args, **kwargs)


        if self.abono_credito:#is not None
            credito_actual = self.credito_actual if self.credito_actual else 0
            abono_credito = self.abono_credito if self.abono_credito else 0

            tot_apo = float(credito_actual + self.solicitud_de_credito - abono_credito )
            self.saldo_credito = tot_apo    
        super(Creditos, self).save(*args, **kwargs)
        if self.plazo_meses is not None:
            nuevo_valor = self.valor_credito_solicitado if self.valor_credito_solicitado else 0
            nuevo_valor2 = Decimal(nuevo_valor)
            meses2 = Decimal(self.plazo_meses)
            resultado_division = Decimal(nuevo_valor2 / meses2)

            # Verificar si el número no es exacto antes de aplicar el redondeo
            if resultado_division % 100 != 0:
                # Redondeo personalizado a la centena más cercana
                cuota_credito = Decimal((resultado_division // 1000 + 1) * 1000)
            else:
                cuota_credito = resultado_division

            self.cuota_credito = float(cuota_credito)

        super(Creditos, self).save(*args, **kwargs)
    

    


class Departamentos(models.Model):
    nombre = models.CharField(max_length=45)

    class Meta:
        db_table = 'departamentos'


class Discapacidades(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'discapacidades'

class EstadosCiviles(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'estados_civiles'


class Estudios(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'estudios'


class Grupos(models.Model):
    nombre = models.CharField(max_length=45)
    persona_admin = models.ForeignKey('PersonasAdministrativas', models.DO_NOTHING)

    class Meta:
        db_table = 'grupos'


class Municipios(models.Model):
    nombre = models.CharField(max_length=45)
    departamento = models.ForeignKey(Departamentos, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'municipios'


class Ocupaciones(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'ocupaciones'


class Paises(models.Model):
    nombre = models.CharField(max_length=45)

    class Meta:
        db_table = 'paises'


class Parentescos(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'parentescos'


class PersonasAdministrativas(models.Model):
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    genero = models.ForeignKey('TiposGeneros', models.DO_NOTHING)
    tipo_doc = models.ForeignKey('TiposDocumentos', models.DO_NOTHING)
    fecha_expedicion = models.DateField()
    lugar_expedicion = models.ForeignKey(Municipios, models.DO_NOTHING)
    num_documento = models.IntegerField()
    fecha_nacimiento = models.DateField()
    correo_electronico = models.CharField(max_length=140, blank=True, null=True)
    celular1 = models.CharField(max_length=15)
    celular2 = models.CharField(max_length=15, blank=True, null=True)
    discapacidad = models.ForeignKey(Discapacidades, models.DO_NOTHING)
    jefe = models.ForeignKey('PersonasJefe', models.DO_NOTHING)
    
    class Meta:
        db_table = 'personas_administrativas'


class PersonasAhorrosCreditos(models.Model):
    persona = models.ForeignKey('PersonasNaturales', models.DO_NOTHING)
    ahorro = models.ForeignKey(Ahorros, models.DO_NOTHING)
    credito = models.ForeignKey(Creditos, models.DO_NOTHING)
    fecha = models.CharField(max_length=45)
    grupo = models.ForeignKey(Grupos, models.DO_NOTHING,null=True)
    estado= models.CharField(max_length=45, null=True) #quitar null si hay fallas

    class Meta:
        db_table = 'personas_ahorros_creditos'


class PersonasBeneficiarios(models.Model):
    persona_natural = models.ForeignKey('PersonasNaturales', models.DO_NOTHING, blank=True, null=True)
    beneficiario = models.ForeignKey(BeneficiariosPersonasNaturales, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'personas_beneficiarios'


class PersonasJefe(models.Model):
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    genero = models.ForeignKey('TiposGeneros', models.DO_NOTHING)
    tipo_doc = models.ForeignKey('TiposDocumentos', models.DO_NOTHING)
    fecha_expedicion = models.DateField()
    lugar_expedicion = models.ForeignKey(Municipios, models.DO_NOTHING)
    num_documento = models.IntegerField()
    fecha_nacimiento = models.DateField()
    correo_electronico = models.CharField(max_length=140, blank=True, null=True)
    celular1 = models.CharField(max_length=15)
    celular2 = models.CharField(max_length=15, blank=True, null=True)
    discapacidad = models.ForeignKey(Discapacidades, models.DO_NOTHING)
    email_computadora = models.CharField(max_length=140)
    contrasena_computadora = models.CharField(max_length=45)

    class Meta:
        db_table = 'personas_jefe'


class PersonasNaturales(models.Model):
    nombre_1 = models.CharField(max_length=45)
    nombre_2 = models.CharField(max_length=45, blank=True, null=True)
    apellido_1 = models.CharField(max_length=45)
    apellido_2 = models.CharField(max_length=45, blank=True, null=True)
    genero = models.ForeignKey('TiposGeneros', models.DO_NOTHING)
    tipo_doc = models.ForeignKey('TiposDocumentos', models.DO_NOTHING)
    num_documento = models.IntegerField()
    fecha_expedicion = models.DateField()
    lugar_expedicion = models.ForeignKey(Municipios, models.DO_NOTHING)
    estado_civil = models.ForeignKey(EstadosCiviles, models.DO_NOTHING)
    ocupacion = models.ForeignKey(Ocupaciones, models.DO_NOTHING)
    fecha_nacimiento = models.DateField()
    lugar_nacimiento = models.ForeignKey(Municipios, models.DO_NOTHING, related_name='personasnaturales_lugar_nacimiento_set')
    nomenclatura = models.CharField(max_length=45, blank=True, null=True)
    barrio_vereda = models.CharField(max_length=45)
    pais = models.ForeignKey(Paises, models.DO_NOTHING)
    vive_direccion = models.ForeignKey(Municipios, models.DO_NOTHING, related_name='personasnaturales_vive_direccion_set')
    estudios = models.ForeignKey(Estudios, models.DO_NOTHING, blank=True, null=True)
    correo_electronico = models.CharField(max_length=140, blank=True, null=True)
    telefono_fijo = models.IntegerField(max_length=10, blank=True, null=True)
    celular1 = models.CharField(max_length=15)
    celular2 = models.CharField(max_length=15, blank=True, null=True)
    tipo_vivienda = models.ForeignKey('TiposViviendas', models.DO_NOTHING)
    deporte_favorito = models.CharField(max_length=45, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    discapacidad = models.ForeignKey(Discapacidades, models.DO_NOTHING)
    nombre_completo_recom = models.CharField(max_length=100, blank=True, null=True)
    direccion_recom = models.CharField(max_length=45, blank=True, null=True)
    celular_recom = models.CharField(max_length=15, blank=True, null=True)
    nombre_completo_familiar = models.CharField(max_length=45, blank=True, null=True)
    direccion_familiar = models.CharField(max_length=45, blank=True, null=True)
    celular_familiar = models.CharField(max_length=15, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, models.DO_NOTHING)
    email_computadora = models.CharField(max_length=140)
    contrasena_computadora = models.CharField(max_length=45)
    fecha_regis = models.CharField(max_length=45)

    class Meta:
        db_table = 'personas_naturales'


class Porcentajes(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'porcentajes'


class TiposDocumentos(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'tipos_documentos'


class TiposGeneros(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'tipos_generos'


class TiposViviendas(models.Model):
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'tipos_viviendas'
