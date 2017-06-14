# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
from openerp.exceptions import Warning
import time
import datetime
import dateutil
from datetime import date, timedelta, datetime
from dateutil import parser


# Clase heredada Producto
class product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    precio_venta_produccion = fields.Float (string = 'Precio de Compra por produccion (Parqueo - Papel)')

# Clase Linea de Compra
class linea_compra(models.Model):
    _name = "linea_compra"
    _description = "Linea de Compra"
    sub_total = fields.Integer(string='Sub Total', compute='_action_calcular_sub_total' , readonly=True)
    orden_compra_id = fields.Many2one(comodel_name='orden_compra', string='Orden de Compra', delegate=True)
    product_id = fields.Many2one(comodel_name='product.product', string='Producto', delegate=True)
    cantidad = fields.Float('Cantidad', required=True, default=1)
    precio = fields.Float('Precio Unidad', required=True)
    fecha = fields.Date(string='Fecha')
    _defaults = {
    'fecha': fields.Date.today(), 
    }

# Colocar el precio del producto
    @api.onchange('product_id')
    def _action_configurar_precio(self):
      self.precio = self.product_id.precio_venta_produccion

# Calcular Total
    @api.one
    @api.depends('cantidad')
    def _action_calcular_sub_total(self):  
        self.sub_total = self.cantidad * self.precio

# Orden Compra Diaria
class orden_compra(models.Model):
    _name = "orden_compra"
    _description = "Orden Compra Diaria"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    name = fields.Char(string='Name', default=lambda self: self._action_aceite())
    empleado_id= fields.Many2one(comodel_name='hr.employee', string='Proveedor', delegate=True, required=True)
    linea_compra_ids = fields.One2many(comodel_name='linea_compra',inverse_name='orden_compra_id', string="Lineas de Compra")
    total = fields.Float(compute='_action_calcular_total',string='Total', readonly=True)
    notas = fields.Text('Observaciones')
    fecha_pedido = fields.Datetime(string="Fecha Pedido", readonly=True)
    produccion_semanal_id = fields.Many2one(comodel_name='produccion_semanal', string='Produccion Semanal', delegate=True)
    saldo_prestamo = fields.Float(string='Saldo Prestamos')
    monto_prestamo = fields.Float(string='Total Prestamo')
    abono_prestamo = fields.Float(string='Abono Prestamo')
    prod_lunes = fields.Float(compute='_action_production_diaria', store=True, string='Lunes')
    prod_martes = fields.Float(compute='_action_production_diaria', store=True, string='Martes')
    prod_miercoles = fields.Float(compute='_action_production_diaria', store=True, string='Miercoles')
    prod_jueves = fields.Float(compute='_action_production_diaria', store=True, string='Jueves')
    prod_viernes = fields.Float(compute='_action_production_diaria', store=True, string='Viernes')
    _defaults = { 
    'fecha_pedido' : fields.Datetime.now()
    }

# Calcular Total
    @api.one
    @api.depends('linea_compra_ids')
    def _action_calcular_total(self):  
      for i in self.linea_compra_ids:
        self.total += i.sub_total

# Genera consecutivo en orden de compra
    @api.model
    def _action_aceite(self):
        return str(self.env['ir.sequence'].next_by_code('orden_compra_diaria'))
 
    @api.one
    @api.depends('linea_compra_ids')
    def _action_production_diaria(self):
        # Obtiene la lista de todas las fechas
        lista_fechas = []
        for i in self.linea_compra_ids:
            if i.fecha not in lista_fechas:
                lista_fechas.append(i.fecha)

        # Calcula la produccion del Lunes
        if len(lista_fechas) >= 1:
            prod_diaria = 0
            for i in self.linea_compra_ids:
                if i.fecha == str(sorted(lista_fechas)[0]) and i.sub_total > 0 :
                    print "----------> " + str(i.product_id.name)
                    prod_diaria += i.sub_total 
            self.prod_lunes = prod_diaria

        # Calcula la produccion del Martes
        if len(lista_fechas) >= 2:
            prod_diaria = 0
            for i in self.linea_compra_ids:
                if i.fecha == str(sorted(lista_fechas)[1]) and i.sub_total > 0 :
                    prod_diaria += i.sub_total 
            self.prod_martes = prod_diaria

        # Calcula la produccion del Miercoles
        if len(lista_fechas) >= 3:
            prod_diaria = 0
            for i in self.linea_compra_ids:
                if i.fecha == str(sorted(lista_fechas)[2]) and i.sub_total > 0 :
                    prod_diaria += i.sub_total 
            self.prod_miercoles = prod_diaria

        # Calcula la produccion del Jueves
        if len(lista_fechas) >= 4:
            prod_diaria = 0
            for i in self.linea_compra_ids:
                if i.fecha == str(sorted(lista_fechas)[3]) and i.sub_total > 0 :
                    prod_diaria += i.sub_total 
            self.prod_jueves = prod_diaria

        # Calcula la produccion del Viernes
        if len(lista_fechas) >= 5:
            prod_diaria = 0
            for i in self.linea_compra_ids:
                if i.fecha == str(sorted(lista_fechas)[4]) and i.sub_total > 0 :
                    prod_diaria += i.sub_total 
            self.prod_viernes = prod_diaria

# Clase Produccion semanal
class produccion_semanal(models.Model):
    _name = "produccion_semanal"
    _description = "Produccion Semanal"
    state = fields.Selection ([('new','Nuevo'), ('progress', 'En Proceso'), ('closed','Cerrado')], string='state', readonly=True)
    name = fields.Char(compute='_action_name', string='Nombre', readonly=True)
    fecha_inicio = fields.Date(string='Fecha Inicio', required=True)
    fecha_final = fields.Date(string='Fecha Final',  required=True)
    orden_compra_ids = fields.One2many(comodel_name='orden_compra',inverse_name='produccion_semanal_id', string="Proveedores")
    notas= fields.Text(string='Notas')
    hr_department_id = fields.Many2one(comodel_name='hr.department', string='Departamento', delegate=True, required=True)
    total_planilla = fields.Float(compute='_calcular_planillas', store=True, string="Total")
    _defaults = { 
    'fecha_inicio': fields.Date.today(),
    'state': 'new'
    }

#  Asigna el nombre produccion semanal
    @api.one
    def _action_name(self):
        self.name = "Planilla " + str(self.fecha_inicio) + " al " + str(self.fecha_final)

# Generar lista de proveedores   
    @api.one
    def action_generar_lista(self):
        res= self.env['hr.employee'].search([('active', '=', 'True')])
        for employee in res:
                if employee.department_id.name == str(self.hr_department_id.name) : 
                    self.orden_compra_ids.create({'empleado_id': str(employee.id),'produccion_semanal_id': str(self.id) })
        self.state= 'progress' 

# Cerrar Planilla y procesar abonos al prestamo
    @api.one
    def action_estado_planilla(self):
        lista_prestamos= self.env['empleado.allowance'].search([('state', '=', 'new')])
        # Notas para incluir en el detalle del abono
        notas = 'Orden de compa del: ' + str(self.fecha_inicio) + ' al ' + str(self.fecha_final)
        # Valida si la factura del proveedor tiene un rebajo de prestamo
        for orden_compra in self.orden_compra_ids :
            for linea in orden_compra.linea_compra_ids:
                if linea.product_id.name == 'Prestamo' and linea.sub_total < 0: 
                    monto_abono = -linea.sub_total
                    # Busca al prooveedor en la lista de prestamos abiertos
                    for prestamo in lista_prestamos :
                        if orden_compra.empleado_id == prestamo.res_employee_id :
                    # Valida si tiene el salario suficiente para abonar al prestamo
                            if orden_compra.total > 0 :
                                # Valida si todavia hay saldo en el prestamo antes de hacer el abono
                                if prestamo.saldo >= monto_abono :
                                # Crea el abono al prestamos
                                    prestamo.abono_ids.create({'libro_id': str(prestamo.id), 'monto': float(monto_abono), 'notas': str(notas) })
                                    orden_compra.abono_prestamo = float(monto_abono)
                                else :
                                    raise Warning ("El Colaborador: " + str(orden_compra.empleado_id.name) + " El abono al prestamo excede su saldo.")  
                            else :
                                raise Warning ("El Colaborador: " + str(orden_compra.empleado_id.name) + " No tiene salario sufuciente para aplicar un abono al prestamo")

        # Estado de los prestamos para mostrar en el reporte de planilla
        for orden_compra in self.orden_compra_ids:
            for prestamo in lista_prestamos :
                if orden_compra.empleado_id == prestamo.res_employee_id :
                    orden_compra.saldo_prestamo = prestamo.saldo
                    orden_compra.monto_prestamo = prestamo.total_amortizable


        self.state = 'closed'  

# Metodo: Calculo de Planillas
    @api.one
    @api.depends('orden_compra_ids.total')
    def _calcular_planillas(self):
            total_planilla = 0 
            for orden_compra in self.orden_compra_ids:
                self.total_planilla += float(orden_compra.total)
