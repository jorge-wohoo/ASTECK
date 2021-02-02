# -*- coding: utf-8 -*-
import base64
import json
import requests
import pprint
import xml.etree.ElementTree as ET
import string

from odoo import api, exceptions, fields, models, _
from doc._extensions.pyjsparser.parser import null
from psycopg2._json import json
from datetime import datetime

class infile_config_res_company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'
        
    usuariofirma = fields.Char(string='Usuario Firma',store=True, size=150)
    usuariocert = fields.Char(string='Usuario Certificacion',store=True, size=150)
    keyfirma = fields.Char(string='Llave Firma',store=True, size=150)
    keycert = fields.Char(string='Llave de certificacion',store=True, size=150)
    establecimientofe = fields.Float(string='No. de establecimiento',store=True)
    idmaquinafe = fields.Char(string='ID Maquina',store=True, size=150)
   

class infile_product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    
    numero_pieza_fabrica = fields.Char(string='No. Pieza Fabrica',store=True)
    tipo = fields.Selection([
            ('B', 'BIEN'),
            ('S', 'SERVICIO')
            ], string='Tipo de Producto', required=True, store=True, default='B',
        help="Seleccione si es bien o servicio, este valor se usara para certificar la factura electronica.")
  
class infile_account_invoice(models.Model):
    _inherit = 'account.move'
  
    xmlfactura = fields.Text(string='XML de factura', compute='_compute_infile',store=True)
    archivocodificado = fields.Text(string='Archivo codificado', compute='_compute_infile', store=True)
    json_data = fields.Text(string='Data json Firma', compute='_compute_infile',store=True)
    archivofirmado = fields.Text(string='Archivo Firmado Infile', compute='_compute_infile',store=True)
    
    certificacion_json = fields.Text(string='Certificacion JSON', compute='_compute_infile',store=True)
    firmaelectronica = fields.Text(string='uuid', compute='_compute_infile',readonly=True,store=True)
    serie = fields.Text(string='Serie', compute='_compute_infile',store=True)
    numero = fields.Text(string='Numero', compute='_compute_infile',store=True)
    fechacertificacion = fields.Text(string='Fecha de certificacion', compute='_compute_infile',store=True)
    archivocertificado = fields.Text(string='Archivo Certificado Infile', compute='_compute_infile',store=True)

    xmlanulacion = fields.Text(string='Anulacion xml', compute='_compute_infile',store=True)  
    anulacion_json = fields.Text(string='Anulacion JSON', compute='_compute_infile',store=True)  
    archivofirmadoanulado = fields.Text(string='archivo firmado a anular',compute='_compute_infile',store=True)
    xmlfacturaanular = fields.Text(string='xml archivo a anular', compute='_compute_infile',store=True)
    codificado_anular = fields.Text(string='Base64 archivo a anular', compute='_compute_infile',store=True)
    resultadoanulacion = fields.Text(string='resultado_anulacion', compute='_compute_infile',store=True)
    serie_anulacion=  fields.Text(string='Serie Anulacion', compute='_compute_infile',store=True)
    firma_anulacion=fields.Text(string='Firma Anulacion', compute='_compute_infile',store=True)
    numero_anulacion=fields.Text(string='Numero Anulacion', compute='_compute_infile',store=True)
    archivo_anulacion=fields.Text(string='Archivo anulacion', compute='_compute_infile',store=True)
    

    @api.depends('create_date','move_type','amount_tax','state','ref','company_id')
    def _compute_infile(self):
        for record in self:
            if record.move_type == 'out_invoice' and record.state in ('posted', 'cancel') and record.amount_tax is not None and record.create_date is not None:
                xmlstr='<?xml version="1.0"?><dte:GTDocumento xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:dte="http://www.sat.gob.gt/dte/fel/0.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="0.4" xsi:schemaLocation="http://www.sat.gob.gt/dte/fel/0.1.0">'
                xmlstr+='<dte:SAT ClaseDocumento="dte">'
                xmlstr+='<dte:DTE ID="DatosCertificados">'
                xmlstr+='<dte:DatosEmision ID="DatosEmision">'
                xmlstr+='<dte:DatosGenerales CodigoMoneda="' + str(record.currency_id.name) + '"  FechaHoraEmision="'+ str((record.create_date).strftime('%Y-%m-%d')) +"T" + str((record.create_date).strftime('%H:%M:00-06:00')) +'" Tipo="FACT">''</dte:DatosGenerales>'
                xmlstr+='<dte:Emisor AfiliacionIVA="GEN" CodigoEstablecimiento="1" CorreoEmisor="'+ str(record.company_id.email) + '" NITEmisor="'+ str(record.company_id.vat) +'" NombreComercial="'+ str(record.company_id.name) +'" NombreEmisor="'+ str(record.company_id.name) +'">'
                xmlstr+='<dte:DireccionEmisor>'
                xmlstr+='<dte:Direccion>' + str(record.company_id.street) + '</dte:Direccion>'
                xmlstr+='<dte:CodigoPostal>' + str(record.company_id.zip) + '</dte:CodigoPostal>'
                xmlstr+='<dte:Municipio>'+ str(record.company_id.city) + '</dte:Municipio>'
                xmlstr+='<dte:Departamento>'+ str(record.company_id.state_id.name) +'</dte:Departamento>'
                xmlstr+='<dte:Pais>'+ str(record.company_id.country_id.code) +'</dte:Pais></dte:DireccionEmisor>'
                xmlstr+='</dte:Emisor>'
                xmlstr+='<dte:Receptor CorreoReceptor="'+ str(record.partner_id.email) +'" IDReceptor="'+ str(record.partner_id.vat) +'" NombreReceptor="'+ str(record.partner_id.name) +'">'
                xmlstr+='<dte:DireccionReceptor>'
                xmlstr+='<dte:Direccion>Ciudad</dte:Direccion>'
                xmlstr+='<dte:CodigoPostal>' + str(record.partner_id.zip) + '</dte:CodigoPostal>'
                xmlstr+='<dte:Municipio>'+ str(record.partner_id.state_id.name) + '</dte:Municipio>'
                xmlstr+='<dte:Departamento>'+ str(record.partner_id.country_id.name) +'</dte:Departamento>'
                xmlstr+='<dte:Pais>'+ str(record.partner_id.country_id.code) +'</dte:Pais>'
                xmlstr+='</dte:DireccionReceptor>'
                xmlstr+='</dte:Receptor>'
                xmlstr+='<dte:Frases>'
                xmlstr+='<dte:Frase CodigoEscenario="1" TipoFrase="1">''</dte:Frase>'
                xmlstr+='</dte:Frases>'
                xmlstr+='<dte:Items>'
                for lineas in record.invoice_line_ids:    
                    for linea in lineas:                    
                        xmlstr+='<dte:Item BienOServicio="'+ str(linea.product_id.tipo) + '" NumeroLinea="'+ str(linea.id) + '">'
                        xmlstr+='<dte:Cantidad>' + str(linea.quantity) +'</dte:Cantidad>'
                        xmlstr+='<dte:UnidadMedida>UND</dte:UnidadMedida>'
                        xmlstr+='<dte:Descripcion>'+ str(linea.product_id.name) +'</dte:Descripcion>'
                        xmlstr+='<dte:PrecioUnitario>'+ str(round((linea.price_unit),3)) +'</dte:PrecioUnitario>'
                        xmlstr+='<dte:Precio>'+ str(round((linea.price_total),3)) +'</dte:Precio>'
                        xmlstr+='<dte:Descuento>'+ str(round((linea.discount),3)) +'</dte:Descuento>'
                        xmlstr+='<dte:Impuestos>'
                        xmlstr+='<dte:Impuesto>'
                        xmlstr+='<dte:NombreCorto>IVA</dte:NombreCorto>'
                        xmlstr+='<dte:CodigoUnidadGravable>1</dte:CodigoUnidadGravable>'
                        xmlstr+='<dte:MontoGravable>'+ str(round((linea.price_total/1.12),3)) +'</dte:MontoGravable>'
                        xmlstr+='<dte:MontoImpuesto>'+ str(round(((linea.price_total/1.12)*0.12),3)) +'</dte:MontoImpuesto>'
                        xmlstr+='</dte:Impuesto>'
                        xmlstr+='</dte:Impuestos>'
                        xmlstr+='<dte:Total>'+ str(round((linea.price_total),3)) +'</dte:Total>'
                        xmlstr+='</dte:Item>'
                xmlstr+='</dte:Items>'
                xmlstr+='<dte:Totales>' 
                xmlstr+='<dte:TotalImpuestos>'
                xmlstr+='<dte:TotalImpuesto NombreCorto="IVA" TotalMontoImpuesto="'+  str(round(record.amount_tax,3)) +'"></dte:TotalImpuesto>'
                xmlstr+='</dte:TotalImpuestos>'
                xmlstr+='<dte:GranTotal>'+ str(round((record.amount_total),3)) +'</dte:GranTotal>'
                xmlstr+='</dte:Totales>'
                #xmlstr+='<dte:Complementos>'
                #xmlstr+='<dte:Complemento IDComplemento="Cambiaria" NombreComplemento="Cambiaria'+ str(record.id) +'" URIComplemento="http://www.sat.gob.gt/fel/cambiaria.xsd">'
                #xmlstr+='<cfc:AbonosFacturaCambiaria xmlns:cfc="http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0" Version="1" xsi:schemaLocation="http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0">'
                #xmlstr+='<cfc:Abono>'
                #xmlstr+='<cfc:NumeroAbono>'+ str(record.id) +'</cfc:NumeroAbono>'
                #xmlstr+='<cfc:FechaVencimiento>'+ str(record.invoice_date_due) +'</cfc:FechaVencimiento>'
                #xmlstr+='<cfc:MontoAbono>'+ str(round((record.amount_total),3)) +'</cfc:MontoAbono>'
                #xmlstr+='</cfc:Abono>'
                #xmlstr+='</cfc:AbonosFacturaCambiaria>'
                #xmlstr+='</dte:Complemento>'
                #xmlstr+='</dte:Complementos>'
                xmlstr+='</dte:DatosEmision>'
                xmlstr+='</dte:DTE>'
                xmlstr+='<dte:Adenda>'
                xmlstr+='<Codigo_cliente>' + str(record.partner_id.id) + '</Codigo_cliente>'
                xmlstr+='<Observaciones>Factura' + str(record.id) + '</Observaciones>'
                xmlstr+='</dte:Adenda>'
                xmlstr+='</dte:SAT>'
                xmlstr+='</dte:GTDocumento>'
                record.xmlfactura = xmlstr
                if record.xmlfactura !='':
                    xml = str(record.xmlfactura)
                    encodedBytes = base64.b64encode(xml.encode("utf-8"))
                    record.archivocodificado = encodedBytes
                    if record.state in ('posted', 'cancel') and record.company_id.usuariofirma is not None and record.company_id.keyfirma is not None and record.company_id.usuariocert is not None and record.company_id.keycert is not None :
                        data_firma = {"archivo":str(record.archivocodificado),
                                        "llave":str(record.company_id.keyfirma),
                                        "codigo":str(record.id),
                                        "alias":str(record.company_id.usuariofirma),
                                        "es_anulacion":"N"}
                        url_firma = 'https://signer-emisores.feel.com.gt/sign_solicitud_firmas/firma_xml'
                        headers_firma = {'Content-Type': "application/json",'cache-control': "no-cache",}
                        data_firma_json = json.dumps(data_firma)
                        response_firma = requests.post(url_firma, data=data_firma_json, headers=headers_firma)
                        respuesta_firma_json= response_firma.json()
                        record.json_data =respuesta_firma_json
                        if record.json_data !='':
                            record.archivofirmado = respuesta_firma_json["archivo"]
                            url_certificacion = 'https://certificador.feel.com.gt/fel/certificacion/dte'
                            data_certificacion = {
                                "nit_emisor": str(record.company_id.vat), 
                                "correo_copia":str(record.partner_id.email),
                                "xml_dte": str(record.archivofirmado),
                                    }
                            data_certificacion_json = json.dumps(data_certificacion)
                            headers_certificacion = {'Content-type': 'application/json',
                                    'usuario':str(record.company_id.usuariocert),
                                    'llave':str(record.company_id.keycert),
                                        'identificador':str(record.name)}
                            response_certificacion = requests.post(url_certificacion, data = data_certificacion_json, headers = headers_certificacion)
                            certificacion = response_certificacion.json()
                            record.certificacion_json = certificacion
                            record.firmaelectronica = certificacion["uuid"]
                            record.serie = certificacion["serie"]
                            record.numero = certificacion["numero"]
                            record.archivocertificado = certificacion["xml_certificado"]
                            record.fechacertificacion = certificacion["fecha"]
                            record.fechacertificacion = certificacion["fecha"]
                            if record.state=='cancel':
                                xmlstr='<?xml version="1.0"?><dte:GTAnulacionDocumento xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:dte="http://www.sat.gob.gt/dte/fel/0.1.0" xmlns:n1="http://www.altova.com/samplexml/other-namespace" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="0.1" xsi:schemaLocation="http://www.sat.gob.gt/dte/fel/0.1.0">'
                                xmlstr+='<dte:SAT><dte:AnulacionDTE ID="DatosCertificados"><dte:DatosGenerales FechaEmisionDocumentoAnular="'+ fields.Date.from_string(str(record.create_date)).strftime('%Y-%m-%d') +"T" + fields.Date.from_string(str(record.create_date)).strftime('%H:%M:00-06:00') +'" FechaHoraAnulacion="'+ str(record.fechacertificacion)+'" ID="DatosAnulacion" IDReceptor="'+ str(record.partner_id.vat) +'" MotivoAnulacion="Mal ingreso de datos" NITEmisor="'+ str(record.company_id.vat) +'" NumeroDocumentoAAnular="'+ str(record.firmaelectronica) +'"></dte:DatosGenerales></dte:AnulacionDTE></dte:SAT></dte:GTAnulacionDocumento>'
                                record.xmlfacturaanular = xmlstr
                                xml_cancelacion = record.xmlfacturaanular
                                encodedBytes = base64.b64encode(xml_cancelacion.encode("utf-8"))
                                record.codificado_anular = encodedBytes
                                if record.firmaelectronica !='' and record.fechacertificacion !='':
                                   url_cancelacion_signer = 'https://signer-emisores.feel.com.gt/sign_solicitud_firmas/firma_xml'
                                   header_cancelacion_signer = {'Content-Type': "application/json",'cache-control': "no-cache",}
                                   data_cancelacion_signer = {"archivo":str(record.codificado_anular),
                                                                "llave":str(record.company_id.keyfirma),
                                                                "codigo":str(record.id),
                                                                "alias":str(record.company_id.usuariofirma),
                                                                "es_anulacion":"S"}
                                   data_cancelacion_json = json.dumps(data_cancelacion_signer)
                                   response_cancelacion_signer = requests.post(url_cancelacion_signer, data=data_cancelacion_json, headers=header_cancelacion_signer)
                                   respuesta_cancelacion_signer = response_cancelacion_signer.json()
                                   if  record.anulacion_json !='':
                                        record.archivofirmadoanulado = respuesta_cancelacion_signer["archivo"]
                                        record.anulacion_json=respuesta_cancelacion_signer
                                        if record.json_data !='':
                                            if record.firmaelectronica !='' and record.fechacertificacion !='' and record.anulacion_json !='':
                                                url = 'https://certificador.feel.com.gt/fel/anulacion/dte/'
                                                data_anulacion = {
                                                                "nit_emisor": str(record.company_id.vat), 
                                                                "correo_copia":str(record.partner_id.email),
                                                                "xml_dte": str(record.archivofirmadoanulado),
                                                                }
                                                data_json_anulacion = json.dumps(data_anulacion)
                                                header_anulacion = {'Content-type': 'application/json',
                                                    'usuario':str(record.company_id.usuariocert),
                                                    'llave':str(record.company_id.keycert),
                                                    'identificador':str(record.name)}
                                                res_anular = requests.post(url, data=data_json_anulacion, headers=header_anulacion)
                                                anulaciondte = res_anular.json()
                                                record.resultadoanulacion  = anulaciondte
                                                record.firma_anulacion  = anulaciondte["uuid"]
                                                record.numero_anulacion  = anulaciondte["numero"]
                                                record.serie_anulacion  = anulaciondte["serie"]
                                                record.archivo_anulacion  = anulaciondte["xml_certificado"]
                            

                        

                
                
                    
            