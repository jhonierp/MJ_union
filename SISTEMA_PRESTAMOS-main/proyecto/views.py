from ast import GeneratorExp
from audioop import maxpp
import datetime
from decimal import ROUND_CEILING, Decimal
import math
from venv import logger
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.db.models import Q

from django.dispatch import Signal
from .forms import PNatuForm
from django.db.models import F, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max

from proyecto.models import (Ahorros, BeneficiariosPersonasNaturales, Creditos, Discapacidades, PersonasBeneficiarios, PersonasNaturales,  Ocupaciones,TiposGeneros,
 Paises,TiposDocumentos, Departamentos, Municipios,
 Estudios,TiposViviendas,Parentescos,Porcentajes,  EstadosCiviles,Grupos,PersonasAdministrativas,PersonasAhorrosCreditos)

# Create your views here.

@login_required
def fun_ahor(request):
    # Recupera los objetos de PersonasNaturales relacionados con sus ahorros
    person_fin = PersonasAhorrosCreditos.objects.select_related('persona', 'ahorro').all()
    
    datos = {
        'person_fin': person_fin,
    }
    
    return render(request, "Tablas/ahorros.html", datos)
@login_required
def fun_credi(request):
    person_fin = PersonasAhorrosCreditos.objects.select_related('persona', 'ahorro').all()
    datos = {
        'person_fin': person_fin,
    }
    return render(request,"Tablas/creditos.html", datos)

@login_required
def fun_prueb_form(request):
    formulario=PNatuForm(request.POST or None) 

    return render(request,"prueb_form.html",{'formulario':formulario} )

@csrf_exempt
@login_required
def fun_tab_main(request):

    #Se convierte la fecha seleccionada en solo mes/año
    fecha_seleccionada = request.GET.get('fecha_sel')
    partes_fecha = fecha_seleccionada.split('-')
    mesYAnioSeleccionado = f"{partes_fecha[1]}/{partes_fecha[0]}" if len(partes_fecha) == 2 else ""
    #La fecha seleccionada en mes/año, ahora se regresa un mes (ej.10/2023, mes_anterior_texto= 09/2023 )
    if len(partes_fecha) == 2 and int(partes_fecha[1]) > 1:
        if int(partes_fecha[1]) < 10:
            partes_fecha[1] = str(int(partes_fecha[1]) - 1)
            mes_anterior_texto = f"0{partes_fecha[1]}/{partes_fecha[0]}"
        else:
            partes_fecha[1] = str(int(partes_fecha[1]) - 1)
            mes_anterior_texto = f"{partes_fecha[1]}/{partes_fecha[0]}"
    
    elif len(partes_fecha) == 2 and int(partes_fecha[1]) == 1:
        partes_fecha[1]=12
        partes_fecha[0] = str(int(partes_fecha[0]) - 1)
        mes_anterior_texto = f"{partes_fecha[1]}/{partes_fecha[0]}"
    else:
        pass
    
    #Se llama el grupo seleccionado
    grupo_select = request.GET.get('grupo_sel')
    #guardamos las personas que cumplan esas 3 condiciones de la tabla PersonasAhorrosCreditos
    personas_activas = PersonasAhorrosCreditos.objects.filter(fecha=mesYAnioSeleccionado, estado='act', grupo_id=grupo_select)

    
    if len(personas_activas) ==0:  # Verifica si el QuerySet está vacío
        personas_activas2 = PersonasAhorrosCreditos.objects.filter(fecha=mes_anterior_texto, estado='act', grupo_id=grupo_select)
        
        if personas_activas2.exists():  # Verifica si personas_activas2 tiene elementos
            #(inicio)
            #aqui SOLO sacamos el valor de APORTES POR PAGAR
            #del mes anterior, para colocar el mismo en el APORTES POR PAGAR
            #del siguiente mes (el cual es vacio)
            for h in personas_activas2:
                id_after_ahorro=0
                id_after_ahorro= h.ahorro_id
            ahorro_after= Ahorros.objects.get(id=id_after_ahorro)
            aportes_por_pagar_after = ahorro_after.aportes_por_pagar
            #(fin)
            ultimos_ids = PersonasAhorrosCreditos.objects.aggregate(
                    Max('id'), Max('ahorro_id'), Max('credito_id')
                )
            nuevo_id_general = int(ultimos_ids['id__max'] + 1 if ultimos_ids['id__max'] else 1)
            nuevo_id_ahorro = int(ultimos_ids['ahorro_id__max'] + 1 if ultimos_ids['ahorro_id__max'] else 1)
            nuevo_id_credito = int(ultimos_ids['credito_id__max'] + 1 if ultimos_ids['credito_id__max'] else 1)
            apo_pag_after =  float(aportes_por_pagar_after)
            for persona in personas_activas2:   
                '''print("____________personas___________________")
                print("fechca_:____",mes_anterior_texto)
                print("fechca_:____",mesYAnioSeleccionado)
                print("nuevo_id_general::: ",nuevo_id_general)
                print("nuevo_id_ahorro::: ",nuevo_id_ahorro)
                print("nuevo_id_credito::: ",nuevo_id_credito)
                print("cant_pa2::: ",len(personas_activas2))'''

                nuevo_ahorro = Ahorros(id=nuevo_id_ahorro)
                nuevo_ahorro.num_recibo=0
                nuevo_ahorro.aportes_anteriores=0
                nuevo_ahorro.aportes_pendientes=0
                nuevo_ahorro.aportes_por_pagar=apo_pag_after
                nuevo_ahorro.aportes_recibidos=0
                nuevo_ahorro.saldo_aportes_por_pagar=0
                nuevo_ahorro.retiro_de_aportes=0
                nuevo_ahorro.total_de_aportes=0
                nuevo_ahorro.save()

                # Crear una nueva instancia de Creditos y asignarle el nuevo ID
                nuevo_credito = Creditos(id=nuevo_id_credito)
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
                nuevo_credito.nueva_afiliacion=0
                nuevo_credito.total_recibido=0
                nuevo_credito.nota="Na"
                nuevo_credito.save()
                nueva_instancia = PersonasAhorrosCreditos(
                    id=nuevo_id_general,
                    persona_id=persona.persona.id,
                    ahorro_id=nuevo_id_ahorro,
                    credito_id=nuevo_id_credito,
                    fecha=mesYAnioSeleccionado,
                    grupo_id=persona.grupo.id,
                    estado="act"
                )
    
                # Guardar la nueva instancia en la base de datos
                nueva_instancia.save()
                nuevo_id_general +=1
                nuevo_id_ahorro +=1
                nuevo_id_credito +=1
                #print(f"Persona ID: {persona.id}, Ahorro ID: {persona.ahorro}, Crédito ID: {persona.credito}, Persona ID: {persona.persona.id}, Estado: {persona.estado}, Grupo ID: {persona.grupo.id}, Fecha: {persona.fecha}")
        else:
            pass
            #for persona in personas_activas:
                #print(f"Persona ID: {persona.id}, Ahorro ID: {persona.ahorro}, Crédito ID: {persona.credito}, Persona ID: {persona.persona.id}, Estado: {persona.estado}, Grupo ID: {persona.grupo.id}, Fecha: {persona.fecha}")
            #print("No hay elementos en personas_activas2")
            #print("mat",mes_anterior_texto)
    else:
        personas_activas=personas_activas
        print("El QuerySet tiene elementos")
    # recorremos las personas que miramos en tabla_main
    for persona_activa in personas_activas:
        '''
        print("___________Persona Actual_____________________")
        print(f"PersonasAhorrosCreditosID:______________, {persona_activa.id}")
        print(f"personaID:______________________________, {persona_activa.persona_id}")
        print(f"AhorrosID:______________________________, {persona_activa.ahorro_id}")
        print(f"CreditosID:_____________________________, {persona_activa.credito_id}")
        print(f"mesYAnioSeleccionado:___________________, {mesYAnioSeleccionado}")
        print(f"credito_actual:_________________________, {persona_activa.credito.credito_actual}")'''
        # todo esto es para valor_cuota_total en la tabla CREDITOS (inicio)
        division = float(persona_activa.credito.valor_credito_solicitado/persona_activa.credito.plazo_meses)
        interes_anterior=persona_activa.credito.interes_anterior 
        if interes_anterior is None:
            interes_anterior_new = float(0)
        else:
            interes_anterior_new = float(interes_anterior)
        suma = float(persona_activa.ahorro.aportes_por_pagar+interes_anterior_new)
        op = float(persona_activa.credito.saldo_credito*2/100/30*persona_activa.credito.numero_dias_credito)
        resul=float(division+suma+op)
        valor_cuota_total = Decimal((resul // 1000 + 1) * 1000)

        persona_activa.credito.valor_cuota_total=valor_cuota_total
        persona_activa.credito.save()
        #(fin)
        
        a=persona_activa.ahorro.aportes_recibidos+persona_activa.credito.abono_credito+persona_activa.credito.intereses_recibidos+ persona_activa.credito.nueva_afiliacion
        persona_activa.credito.total_recibido=float(a)
        persona_activa.credito.save()

        #registros se guardan las personas que tengan un resgitro antiguo, es decir mes anterior (inicio)
        #luego se las recorre y guardamos los valores estaticos (ej.aportes_anteriores tiene el valor de total_de_aportes del anterior mes)
        registros = PersonasAhorrosCreditos.objects.filter(persona_id=persona_activa.persona.id, fecha=mes_anterior_texto)
        for i in registros:
            '''
            print("______Persona Anterior_______")
            print(f"PersonasAhorrosCreditosID:__, {i.id}")
            print(f"personaID:__________________, {i.persona_id}")
            print(f"AhorrosID:__________________, {i.ahorro_id}")
            print(f"CreditosID:_________________, {i.credito_id}")
            print(f"FechaLocal:_________________, {i.fecha}")
            print("credito_actual anterior:_____,", i.credito.credito_actual)'''
            persona_activa.ahorro.aportes_anteriores = i.ahorro.total_de_aportes
            persona_activa.ahorro.aportes_pendientes = i.ahorro.aportes_pendientes
            persona_activa.credito.credito_actual = i.credito.saldo_credito
            persona_activa.credito.total_interes_a_pagar = i.credito.total_interes_a_pagar
            persona_activa.credito.interes_anterior = i.credito.saldo_intereses
            persona_activa.ahorro.aportes_pendientes=i.ahorro.saldo_aportes_por_pagar
            persona_activa.ahorro.save()
            persona_activa.credito.save()
        #(fin)
    #esot son variables que solo se usan para la parte de arriba de la tabla para dar informacion 
    #de cual apartado estamos(inicio)
    grupo_select2 = int(grupo_select)

    lista_personas = PersonasAdministrativas.objects.all()
    lista_grupos = Grupos.objects.all()

    for i in lista_grupos:
        if i.id == grupo_select2:
            id_administrador = i.persona_admin_id
            grupo_l = i.nombre

    for k in lista_personas:
        if k.id == id_administrador:
            name_admin = k.nombres
    #(fin)
    #(inicio)
    #todo esto es para aportes_por_pagar la funcion que tiene, se escoge las personas que se filtraron
    #y se les cambia el valor de esa columna segun lo que escriban 
    input_apo_pag = request.POST.get('input_apo_pag')
    apo_pagar_new = input_apo_pag
    if apo_pagar_new:
        for i in personas_activas:
            apo_pagar_=float(apo_pagar_new)       
            p_id=0
            p_id=i.id
            persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=p_id)
            ahorro = persona_ahorro_credito.ahorro
            #actualiza la aportes_recibidos al modificar aportes_por_pagar
            aportes_recibidos = ahorro.aportes_recibidos if ahorro else None
            if  apo_pagar_ > aportes_recibidos:    
                resta = float(apo_pagar_-aportes_recibidos)
                setattr(ahorro, "aportes_por_pagar", apo_pagar_)
                setattr(ahorro, "saldo_aportes_por_pagar", resta)
                ahorro.save()
            else:
                cero = float(0.0)
                setattr(ahorro, "aportes_por_pagar", apo_pagar_)
                setattr(ahorro, "saldo_aportes_por_pagar", cero)
                ahorro.save()
    else:
        print("vacio xd")
    #(fin)
        
    #(inicio)
    #INTERES_CREDITO
    for zz in personas_activas:
        #print("_________________________")
        p_id=0
        p_id=zz.id
        pp_id=zz.persona_id
        
        PNat = PersonasNaturales.objects.get(id=pp_id)
        persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=p_id)
        PCred_id=persona_ahorro_credito.credito_id
        creditos_us = Creditos.objects.get(id=PCred_id)
        valor2_cred_actu=creditos_us.credito_actual
        valor3_dias=creditos_us.numero_dias_credito
        
        name=PNat.nombre_1
        ocup=PNat.ocupacion.descripcion 
        ocup_id=PNat.ocupacion.id

        #print("persona_ahorro_credito: ", p_id )
        #print("person_id: ", pp_id )
        #print("name: ", name )
        #print("ocupa_id: ",ocup_id )
        #print("ocupacion: ",ocup )
        #print("credito_id: ",PCred_id )
        #print("cred_actu: ",valor2_cred_actu )
        #print("numero_dias_credito: ",valor3_dias )
        
        
        if ocup_id == 1: #estudiante

            resultado = valor2_cred_actu * 1.5 / 100 / 30 * valor3_dias #el primer 30 es de formula y el segundo es porque un mes son 30 dias 
            resultado_redondeado = math.ceil(resultado * 100) / 100
            tot_apo = float(resultado_redondeado)
            #print("tot_apo_est: ",tot_apo)
            setattr(creditos_us, "interes_credito", tot_apo)
            creditos_us.save()

        elif ocup_id == 6: #admin

            resultado = valor2_cred_actu * 1 / 100 / 30 * valor3_dias
            resultado_redondeado = math.ceil(resultado * 100) / 100
            tot_apo = float(resultado_redondeado)
            #print("tot_apo_adm: ",tot_apo)
            setattr(creditos_us, "interes_credito", tot_apo)
            creditos_us.save()
        elif ocup_id == 5: #discapacitado

            resultado = valor2_cred_actu * 0 / 100 / 30 * valor3_dias
            resultado_redondeado = math.ceil(resultado * 100) / 100
            tot_apo = float(resultado_redondeado)
            #print("tot_apo_disca: ",tot_apo)
            setattr(creditos_us, "interes_credito", tot_apo)
            creditos_us.save()
        else: #normal

            resultado = valor2_cred_actu * 2 / 100 / 30 * valor3_dias
            resultado_redondeado = math.ceil(resultado * 100) / 100
            tot_apo = float(resultado_redondeado)
            #print("tot_apo_otro: ",tot_apo)
            setattr(creditos_us, "interes_credito", tot_apo)
            creditos_us.save()

    #(fin)
    datos = {
        'mesYAnioSeleccionado':mesYAnioSeleccionado,
        'name_admin': name_admin,
        'grupo_l': grupo_l,
        'personas_activas':personas_activas,
        'numero_recibido':apo_pagar_new,
        #estos 2 de abajo son diferentes a los 2 de arriba
        'grupo_select':grupo_select,
        'fecha_seleccionada':fecha_seleccionada
    }
    return render(request, "Tablas/tabla_main.html",datos)

@csrf_exempt
def actualizar_campo(request):
    if request.method == 'POST':        
        persona_id = request.POST.get('persona_id')
        campo = request.POST.get('campo')
        rote = request.POST.get('nuevo_valor')
        print("_____________________________________________________")
        print(f"persona id:::::::::::::::::::::: {persona_id}")
        print(f"campo     ::::::::::::::::::::::: {campo}")
        print(f"nuevo_valor::::::::::::::::::::: {rote}")
        
        try:
            if campo == "aportes_recibidos":
                nuevo_valor=float(rote)
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                ahorro = persona_ahorro_credito.ahorro
                aportes_por_pagar = ahorro.aportes_por_pagar if ahorro else None
                
                if  nuevo_valor > aportes_por_pagar:    
                    nuevo_valor=float(rote)
                    cero = 0.0
                    setattr(ahorro, campo, nuevo_valor)
                    setattr(ahorro, "saldo_aportes_por_pagar", cero)
                    ahorro.save()
                else:
                    nuevo_valor=float(rote)
                    valor = float(aportes_por_pagar - nuevo_valor)
                    setattr(ahorro, campo, nuevo_valor)
                    setattr(ahorro, "saldo_aportes_por_pagar", valor)
                    ahorro.save()
            elif campo == "retiro_de_aportes":
                nuevo_valor=float(rote)
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                ahorro = persona_ahorro_credito.ahorro
                aportes_recibidos = ahorro.aportes_recibidos if ahorro else None
                aportes_anteriores = ahorro.aportes_anteriores if ahorro else None                

                tot_apo = float( aportes_recibidos + aportes_anteriores- nuevo_valor)

                setattr(ahorro, campo, nuevo_valor)
                setattr(ahorro, "total_de_aportes", tot_apo)

                ahorro.save()
            elif campo == "valor_credito_solicitado":
                nuevo_valor=float(rote)
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                credito = persona_ahorro_credito.credito
                meses = credito.plazo_meses if credito else None
                if meses is None:
                    nuevo_valor2 = Decimal(nuevo_valor)
                    meses2 = Decimal(1)
                    resultado_division = Decimal(nuevo_valor2 / meses2)

                    meses =1

                    if resultado_division % 100 != 0:
                        # Redondeo personalizado a la centena más cercana
                        cuota_credito = Decimal((resultado_division // 1000 + 1) * 1000)
                    else:
                        cuota_credito = resultado_division
                    
                    setattr(credito, campo, nuevo_valor)
                    setattr(credito, "cuota_credito", cuota_credito)
                    setattr(credito, "plazo_meses", meses)
                    credito.save()
                else:
                    nuevo_valor2 = Decimal(nuevo_valor)
                    meses2 = Decimal(meses)
                    resultado_division = Decimal(nuevo_valor2 / meses2)

                    # Verificar si el número no es exacto antes de aplicar el redondeo
                    if resultado_division % 100 != 0:
                        # Redondeo personalizado a la centena más cercana
                        cuota_credito = Decimal((resultado_division // 1000 + 1) * 1000)
                    else:
                        cuota_credito = resultado_division

                    cuota_credito2 = float(cuota_credito)
                    setattr(credito, campo, nuevo_valor)
                    setattr(credito, "cuota_credito", cuota_credito2)
                    credito.save()
            elif campo == "solicitud_de_credito":
                nuevo_valor=float(rote)
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                credito = persona_ahorro_credito.credito
                credito_actual = credito.credito_actual if credito else None
                abono_credito = credito.abono_credito if credito else None

                if credito_actual == None:
                    nuevo_valor=float(rote)
                    credito_actual =0
                    setattr(credito, "credito_actual", credito_actual)
                    credito.save()
                if abono_credito == None:
                    nuevo_valor=float(rote)
                    abono_credito=0
                    setattr(credito, "abono_credito", abono_credito)
                    credito.save()

                tot_apo = float( credito_actual + abono_credito- nuevo_valor)

                setattr(credito, campo, nuevo_valor)
                setattr(credito, "saldo_credito", tot_apo)
                credito.save()
            elif campo == "fecha_inicio":
                fecha_inicio_get = request.POST.get('fechaInicio')
                fecha_inicio_get_str=str(fecha_inicio_get)
                parts = fecha_inicio_get_str.split() 
                
                dia = parts[0][8:10]
                mes = parts[0][5:7]
                año = parts[0][0:4]
                fecha_update=f"{dia}/{mes}/{año}"

                #___________________________________________________________________________
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                credito = persona_ahorro_credito.credito
                plazo_meses = credito.plazo_meses if credito else None
                if plazo_meses is None:
                    plazo_mesesa=1
                else:
                    plazo_mesesa=plazo_meses
                
                if plazo_mesesa >12:
                    anual = plazo_mesesa// 12  # Cociente de la división
                    mensual = plazo_mesesa % 12

                    me=str((int(mes)+mensual)-12)
                    año_new=str(int(año)+anual)
                else:
                    mes_fin=int(mes) + plazo_mesesa
                    if mes_fin >12:
                        me=str(mes_fin-12)
                        año_new=str(int(año)+1)
                    else:
                        me=str(mes_fin)
                        año_new=str(año)

                fecha_fin=f"{dia}/{me}/{año_new}"      
                    
                setattr(credito, "fecha_final", fecha_fin)
                setattr(credito, "plazo_meses", plazo_mesesa)
                setattr(credito, campo, fecha_update)
                credito.save()
            elif campo == "intereses_recibidos":
                nuevo_valor=float(rote)
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                credito = persona_ahorro_credito.credito
                total_interes_a_pagar = credito.total_interes_a_pagar if credito else None
                saldo_intereses = float( total_interes_a_pagar- nuevo_valor)

                setattr(credito, campo, nuevo_valor)
                setattr(credito, "saldo_intereses", saldo_intereses)
                credito.save()
                
            elif campo == "nota":
                nuevo_valor=rote
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                credito = persona_ahorro_credito.credito
                setattr(credito, campo, nuevo_valor)
                credito.save()
            elif campo == "nueva_afiliacion":
                nuevo_valor=rote
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                credito = persona_ahorro_credito.credito
                setattr(credito, campo, nuevo_valor)
                credito.save()
            
            else:
                nuevo_valor=float(rote)
                persona_ahorro_credito = PersonasAhorrosCreditos.objects.get(id=persona_id)
                ahorro = persona_ahorro_credito.ahorro
                credito = persona_ahorro_credito.credito
                '''
                print("_____________________________________________________")
                print(f"persona id::::::::::::::::::::::::: {persona_id}")
                print(f"ahorro id::::::::::::::::::::::::: {ahorro}")
                print(f"persona_ahorro_credito::::::::::::::::::::::::: {persona_ahorro_credito}")
                print(f"nuevo_valor::::::::::::::::::::::::: {nuevo_valor}")'''
                setattr(ahorro, campo, nuevo_valor)
                setattr(credito, campo, nuevo_valor)
                ahorro.save()
                credito.save()

            #esto se debe confgurar si se entra en ajustes se envie el valor al models de credito
            #credito.set_numero_dias_credito(valor_desde_views)
            #credito.save()
            
            return JsonResponse({'success': True})
        except PersonasAhorrosCreditos.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Persona no encontrada'})
        except Ahorros.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Ahorro no encontrado'})
        except Exception as e:
            print(f"Error al actualizar el campo en Ahorrosaaa: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def fun_tab_edit_admin(request):
    if request.method == 'POST':
        palabra = request.POST.get('keyword')
        lista_personas = PersonasAdministrativas.objects.all()
        lista_grupos = Grupos.objects.all()

        if palabra is not None:
            resultado_busqueda_personas = lista_personas.filter(
                Q(id__icontains=palabra) |
                Q(nombres__icontains=palabra) |
                Q(apellidos__icontains=palabra) |
                Q(num_documento__icontains=palabra)
            )

            datos = {
                'personas': resultado_busqueda_personas,
                'grupos': lista_grupos
            }
            return render(request, "Editar/tabla_edit_admin.html", datos)
        else:
            
            datos = {
                'personas': lista_personas,
                'grupos': lista_grupos
            }
            return render(request, "Editar/tabla_edit_admin.html", datos)
    else:
        persons = PersonasAdministrativas.objects.order_by('id')[:10]
        lista_grupos = Grupos.objects.all()
        datos = {
            'personas': persons,
            'grupos': lista_grupos
        }
        return render(request, "Editar/tabla_edit_admin.html", datos)

@login_required
def fun_tab_edit(request):
    if request.method == 'POST':
        palabra = request.POST.get('keyword')
        lista_personas = PersonasNaturales.objects.all()
        lista_grupos = Grupos.objects.all()  # Obtener todos los grupos

        if palabra is not None:
            resultado_busqueda_personas = lista_personas.filter(
                Q(id__icontains=palabra) |
                Q(nombre_1__icontains=palabra) |
                Q(nombre_2__icontains=palabra) |
                Q(apellido_1__icontains=palabra) |
                Q(apellido_2__icontains=palabra) |
                Q(num_documento__icontains=palabra)
            )
            resultado_busqueda_grupos = lista_grupos.filter(
                Q(nombre__icontains=palabra)  # Agregar aquí los campos de búsqueda para Grupos
            )

            datos = {
                'personas': resultado_busqueda_personas,
                'grupos': resultado_busqueda_grupos
            }
            return render(request, "Editar/tabla_edit.html", datos)
        else:
            datos = {
                'personas': lista_personas,
                'grupos': lista_grupos  # Incluir todos los grupos en datos
            }
            return render(request, "Editar/tabla_edit.html", datos)
    else:
        persons = PersonasNaturales.objects.order_by('id')[:10]
        lista_grupos = Grupos.objects.all()  # Obtener todos los grupos
        datos = {
            'personas': persons,
            'grupos': lista_grupos  # Incluir todos los grupos en datos
        }
        return render(request, "Editar/tabla_edit.html", datos)
    
@login_required
def fun_reg_edit(request,id):
    zz = PersonasNaturales.objects.get(id=id)
    grupos = Grupos.objects.all()
    generos = TiposGeneros.objects.all()
    ocupaciones =  Ocupaciones.objects.all()
    paises =  Paises.objects.all()
    documentos = TiposDocumentos.objects.all()
    departamentos =  Departamentos.objects.all()
    ciudades =  Municipios.objects.all()
    estudios =  Estudios.objects.all()
    viviendas = TiposViviendas.objects.all()
    discapacidades= Discapacidades.objects.all()
    parentescos = Parentescos.objects.all()
    porcentajes = Porcentajes.objects.all()
    estadosc =   EstadosCiviles.objects.all()
    datos = {
        'generos': generos, 'ocupaciones': ocupaciones, 'paises': paises, 
    'documentos': documentos, 'departamentos': departamentos, 'ciudades': ciudades, 'estudios': estudios, 'viviendas': viviendas,
    'discapacidades': discapacidades, 'parentescos': parentescos, 'porcentajes': porcentajes, 'estadosc': estadosc, 'grupos': grupos,
        'zz':zz
    }
        
    return render(request,"Editar/registro_edit.html",datos)

@login_required
def fun_re_adm(request):
    grupos = Grupos.objects.all()
    generos = TiposGeneros.objects.all()
    ocupaciones = Ocupaciones.objects.all()
    paises = Paises.objects.all()
    documentos = TiposDocumentos.objects.all()
    departamentos = Departamentos.objects.all()
    ciudades = Municipios.objects.all()
    estudios = Estudios.objects.all()
    viviendas = TiposViviendas.objects.all()
    discapacidades = Discapacidades.objects.all()
    parentescos = Parentescos.objects.all()
    porcentajes = Porcentajes.objects.all()
    estadosc = EstadosCiviles.objects.all()
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombres = request.POST['nombre_completo']
        apellidos = request.POST['apellidos']
        genero_id = request.POST['genero']
        tipo_doc_id = request.POST['tipo_documento']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        fecha_expedicion = request.POST['fecha_expedicion']
        lugar_expedicion_id = request.POST['ciudad_expedicion']
        num_documento = request.POST['numero_documento']
        discapacidad_id = request.POST['discapacidad']
        correo_electronico = request.POST['email_personal']
        celular1 = request.POST['celular_1']
        celular2 = request.POST['celular_2']
        grupo_id = request.POST['grupo']
        jefe_id = '1'

        # Crear una nueva instancia de PersonasAdministrativas
        administrador = PersonasAdministrativas(
            nombres=nombres,
            apellidos=apellidos,
            genero_id=genero_id,
            tipo_doc_id=tipo_doc_id,
            fecha_nacimiento=fecha_nacimiento,
            fecha_expedicion=fecha_expedicion,
            lugar_expedicion_id=lugar_expedicion_id,
            num_documento=num_documento,
            discapacidad_id=discapacidad_id,
            correo_electronico=correo_electronico,
            celular1=celular1,
            celular2=celular2,
            jefe_id=jefe_id,
        )
        administrador.save()

        # Comprobar si se eligió crear un nuevo grupo
        if grupo_id == 'nuevo':
            nuevo_grupo_nombre = request.POST['nuevo_grupo']
            if nuevo_grupo_nombre:
                # El usuario eligió crear un nuevo grupo y proporcionó un nombre
                nuevo_grupo = Grupos(nombre=nuevo_grupo_nombre, persona_admin=administrador)
                nuevo_grupo.save()
        else:
            # El usuario eligió un grupo existente (o no proporcionó un nombre para uno nuevo)
            grupo = Grupos.objects.get(pk=grupo_id)
            grupo.persona_admin = administrador
            grupo.save()

        return redirect(fun_hom)

    # Si no es una solicitud POST, renderiza el formulario vacío
    return render(request, 'Registros/registro_admin.html', {'generos': generos,
                                                            'ocupaciones': ocupaciones, 'paises': paises,
                                                            'documentos': documentos,
                                                            'departamentos': departamentos, 'ciudades': ciudades,
                                                            'estudios': estudios, 'viviendas': viviendas,
                                                            'discapacidades': discapacidades,
                                                            'parentescos': parentescos, 'porcentajes': porcentajes,
                                                            'estadosc': estadosc, 'grupos': grupos})

@login_required
def fun_hom(request):
    grupos = Grupos.objects.all()
    
    return render(request,"home.html",{'grupos':grupos})
@login_required
def fun_re_us(request):
    generos = TiposGeneros.objects.all()
    ocupaciones = Ocupaciones.objects.all()
    paises = Paises.objects.all()
    documentos = TiposDocumentos.objects.all()
    departamentos = Departamentos.objects.all()
    ciudades = Municipios.objects.all()
    estudios = Estudios.objects.all()
    viviendas = TiposViviendas.objects.all()
    discapacidades = Discapacidades.objects.all()
    parentescos = Parentescos.objects.all()
    porcentajes = Porcentajes.objects.all()
    estadosc = EstadosCiviles.objects.all()
    grupos = Grupos.objects.all()
    person_ac = PersonasAhorrosCreditos.objects.all()

    
    if request.method == 'POST':
        fecha_actual = date.today()
        pase = fecha_actual.strftime("%m/%Y")
        mes_y_anio_actual = str(pase)

        # Obtener datos del formulario
        nombre_1 = request.POST['nombre_1']
        nombre_2 = request.POST['nombre_2']
        apellido_1 = request.POST['apellido_1']
        apellido_2 = request.POST['apellido_2']
        genero_id = request.POST['genero']
        tipo_documento_id = request.POST['tipo_documento']
        num_documento = request.POST['numero_documento']
        fecha_expedicion = request.POST['fecha_expedicion']
        lugar_expedicion_id = request.POST['ciudad_expedicion']  # Asegúrate de obtener la ciudad correcta
        estado_civil_id = request.POST['estado_civil']
        ocupacion_id = request.POST['ocupacion']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        lugar_nacimiento_id = request.POST['ciudad_nacimiento']  # Asegúrate de obtener la ciudad correcta
        nomenclatura = request.POST['nomenclatura']
        barrio_vereda = request.POST['barrio_vereda']
        pais_id = request.POST['pais_direccion']
        vive_direccion_id = request.POST['ciudad_direccion']  # Asegúrate de obtener la ciudad correcta
        estudios_id = request.POST.get('estudios', None)
        correo_electronico = request.POST['correo_electronico']
        telefono_fijo = request.POST.get('telefono_fijo')
        if telefono_fijo == '':
            telefono_fijo = '0'
        celular1 = request.POST['celular1']
        celular2 = request.POST.get('celular2', None)
        tipo_vivienda_id = request.POST['tipo_vivienda']
        deporte_favorito = request.POST.get('deporte_favorito', None)
        edad = request.POST.get('edad', None)
        discapacidad_id = request.POST['discapacidad']
        nombre_completo_recom = request.POST.get('nombre_integrante', None)
        direccion_recom = request.POST.get('direccion_integrante', None)
        celular_recom = request.POST.get('telefono_integrante', None)
        nombre_completo_familiar = request.POST.get('nombre_referencia', None)
        direccion_familiar = request.POST.get('direccion_referencia', None)
        celular_familiar = request.POST.get('telefono_referencia', None)
        # Asegúrate de obtener el valor correcto
        grupo_id = request.POST['grupo']  # Asegúrate de obtener el valor correcto
        
        # Crear una lista para almacenar los beneficiarios
        beneficiarios = []

        # Procesar los datos de los beneficiarios
        for i in range(1, 5):  # Itera sobre los números del 1 al 4
            nombre_beneficiario = request.POST.get('nombre_beneficiario_' + str(i))
            porcentaje_beneficiario_id = request.POST.get('porcentaje_beneficiario_' + str(i))
            parentesco_beneficiario_id = request.POST.get('parentesco_beneficiario_' + str(i))

            # Verificar si se proporcionó información para el beneficiario
            if nombre_beneficiario and porcentaje_beneficiario_id and parentesco_beneficiario_id:
                # Crear el beneficiario con la clave foránea porcentaje_id
                beneficiario = BeneficiariosPersonasNaturales(
                    nombre_completo=nombre_beneficiario,
                    porcentaje_id=porcentaje_beneficiario_id,
                    parentesco_id=parentesco_beneficiario_id
                )
                beneficiario.save()

                # Agregar el beneficiario a la lista
                beneficiarios.append(beneficiario)

        # Guardar la persona natural
        usuario = PersonasNaturales(
            # ... Código para guardar la persona natural ...
            nombre_1=nombre_1,
            nombre_2=nombre_2,
            apellido_1=apellido_1,
            apellido_2=apellido_2,
            genero_id=genero_id,
            tipo_doc_id=tipo_documento_id,
            num_documento=num_documento,
            fecha_expedicion=fecha_expedicion,
            lugar_expedicion_id=lugar_expedicion_id,
            estado_civil_id=estado_civil_id,
            ocupacion_id=ocupacion_id,
            fecha_nacimiento=fecha_nacimiento,
            lugar_nacimiento_id=lugar_nacimiento_id,
            nomenclatura=nomenclatura,
            barrio_vereda=barrio_vereda,
            pais_id=pais_id,
            vive_direccion_id=vive_direccion_id,
            estudios_id=estudios_id,
            correo_electronico=correo_electronico,
            telefono_fijo=telefono_fijo,
            celular1=celular1,
            celular2=celular2,
            tipo_vivienda_id=tipo_vivienda_id,
            deporte_favorito=deporte_favorito,
            edad=edad,
            discapacidad_id=discapacidad_id,
            nombre_completo_recom=nombre_completo_recom,
            direccion_recom=direccion_recom,
            celular_recom=celular_recom,
            nombre_completo_familiar=nombre_completo_familiar,
            direccion_familiar=direccion_familiar,
            celular_familiar=celular_familiar,
            grupo_id=grupo_id,
            fecha_regis=mes_y_anio_actual
        )
        usuario.save()
        
        # Asociar los beneficiarios con la persona natural
        for beneficiario in beneficiarios:
            persona_beneficiario = PersonasBeneficiarios(
                persona_natural=usuario,
                beneficiario=beneficiario
            )
            persona_beneficiario.save()
        messages.success(request, 'Usuario y beneficiarios registrados exitosamente.')
        return redirect(fun_hom)  # Reemplaza 'pagina_de_exito' con la URL de tu elección
    messages.success(request, 'Usuario y beneficiarios registrados exitosamente.')

    return render(request,"Registros/registro_user.html",{'generos':generos,
    'ocupaciones':ocupaciones,'paises':paises,'documentos':documentos,
    'departamentos':departamentos,'ciudades':ciudades,
    'estudios':estudios,'viviendas':viviendas,'discapacidades':discapacidades,
    'parentescos':parentescos,'porcentajes':porcentajes,'estadosc':estadosc,'grupos':grupos})
