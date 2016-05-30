# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.template import loader, RequestContext
from sqlalchemy import or_, and_
from acc.decorators import permission_required, access_focus
from django.shortcuts import render_to_response, render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from Model import ReportPattern, Report, Company
from reports import report_registry
from django.http import Http404, HttpResponse
from reports.definition.report import ReportDefinition
from reports.registry import get_report_builder
from django.conf import settings
from reports.report.field_type import report_field_types
from reports.report.filter_operation import report_filter_operations
from reports.report.aggregation import report_aggregations
from reports.SQLAlchemy_models import *
from Model import JaspreReportTemplate
import json
import base64

from . import jasper_api

JASPER_REPORTS = {
    'sale_tax_report': {'alias': 'sale_tax_report', 'name': 'Sale Tax Report', 'path': 'reports/kiosk_reports/sale_tax_report'},
    'sales_by_kiosk': {'alias': 'sales_by_kiosk', 'name': 'Sales By Kiosk', 'path': 'reports/interactive/Sales/SalesByKiosk'},
    'sale_tax_report_1': {'alias': 'sale_tax_report_1', 'name': 'Sale Tax 1', 'path': 'reports/interactive/SalesTax/SalesTax'},
    'sale_tax_report_2': {'alias': 'sale_tax_report_2', 'name': 'Sale Tax 2', 'path': 'reports/interactive/SalesTax/SalesTax2'}
}


@login_required
def reports(request):
    data = dict()
    if request.user.is_company:
        query = or_(and_(ReportPattern.company_id == request.user.company_id, ReportPattern.is_for_company == 1),
                    and_(ReportPattern.company_id == None, ReportPattern.is_for_company == 1),)
        data['patterns'] = request.db_session.query(ReportPattern).filter(query).order_by(ReportPattern.name)
    elif request.user.is_focus:
        query = or_(ReportPattern.company_id == None, ReportPattern.is_for_company == 0)
        data['patterns'] = request.db_session.query(ReportPattern).filter(query).order_by(ReportPattern.name)
    else:
        raise Http404()

    data['data'] = request.db_session.query(Report).order_by(Report.name).filter_by(company_id=request.user.company_id)
    return render_to_response('reports_reports.html', data, context_instance=RequestContext(request))


@login_required
def jasper_reports(request):
    query = request.db_session.query(JaspreReportTemplate)

    if request.user.is_company:
        query = query.filter(or_(and_(JaspreReportTemplate.company_id == request.user.company_id, JaspreReportTemplate.focus_only == 0),
                                 and_(JaspreReportTemplate.company_id == None, JaspreReportTemplate.focus_only == 0),))
    #data = {'reports': JASPER_REPORTS.values()}
    data = {'reports': query.order_by(JaspreReportTemplate.name)}
    return render_to_response('jasper/jasper_reports.html', data, context_instance=RequestContext(request))


@login_required
def get_jasper_report_params(request):
    alias = request.POST['alias']
    report = get_jasper_report_from_db(request, alias)

    #if alias in JASPER_REPORTS:
    if report:
        #report = JASPER_REPORTS[alias]

        controls = jasper_api.get_report_input_controls(report['path'])
        data = {'controls': controls['inputControl'] if controls else None, 'template': report, 'formats': jasper_api.REPORT_FORMATS.values()}

        template = loader.get_template('jasper/params.html')
        content = template.render(RequestContext(request, data))

        response = {'type': 'success', 'message': '', 'content': content}
    else:
        response = {'type': 'error', 'message': 'Template was not found!'}

    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
def build_jasper_html_report(request):
    data = json.loads(request.POST['data'])
    report = get_jasper_report_from_db(request, data['alias'])

    #if data['alias'] in JASPER_REPORTS:
    if report:
        #report = JASPER_REPORTS[data['alias']]
        del data['alias']
        del data['format']
        del data['csrfmiddlewaretoken']

        if request.user.is_company and 'Company_ID' in data:
            data['Company_ID'] = request.user.company.id

        content = jasper_api.build_report(report['path'], input_controls=data)[0]
        response = {'type': 'success', 'message': '', 'content': content}
    else:
        response = {'type': 'error', 'message': 'Template was not found!'}

    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
def download_jasper_report(request):
    data = dict()
    for val in request.POST:
        data[val] = request.POST[val]

    report = get_jasper_report_from_db(request, data['alias'])

    #if data['alias'] in JASPER_REPORTS:
    if report:
        #report = JASPER_REPORTS[data['alias']]
        fmt = data['format'][1:]
        del data['alias']
        del data['format']
        del data['csrfmiddlewaretoken']

        if request.user.is_company and 'Company_ID' in data:
            data['Company_ID'] = request.user.company.id

        content = jasper_api.build_report(report['path'], output_type=fmt, input_controls=data, save_to_file=True)
        result = HttpResponse(content=content[0], content_type=content[1])
        file_name = '{0}.{1}'.format(report['alias'], fmt)
        result['Content-Encoding'] = 'utf-8'
        result['Content-Disposition'] = 'attachment; filename="'+file_name+'"'

        return result
    else:
        raise Http404()


@login_required
@access_focus
def jasper_templates(request):
    data = dict()
    data['data'] = request.db_session.query(JaspreReportTemplate).order_by(JaspreReportTemplate.name)
    data['companies'] = request.db_session.query(Company).order_by(Company.name)
    return render_to_response('jasper/jasper_templates.html', data, context_instance=RequestContext(request))


@login_required
@access_focus
def jasper_template_edit(request, id):
    j_temp = request.db_session.query(JaspreReportTemplate).filter_by(id=id).first()
    if not j_temp:
        raise Http404()

    data = dict()
    data['is_for'] = -1 if j_temp.focus_only == 1 else -2 if j_temp.company_id is None else j_temp.company_id
    data['j_temp'] = j_temp
    data['companies'] = request.db_session.query(Company).order_by(Company.name)
    return render_to_response('jasper/jasper_template.html', data, context_instance=RequestContext(request))


@login_required
@access_focus
def save_jasper_template(request):
    data = json.loads(request.POST['data'])
    result = {'message': '', 'type': ''}

    try:
        if data['is_for'] == '-1':
            data['focus_only'] = 1
            data['company_id'] = None
        elif data['is_for'] == '-2':
            data['focus_only'] = 0
            data['company_id'] = None
        else:
            data['focus_only'] = '0'
            data['company_id'] = data['is_for']

        del data['is_for']

        if 'id' in data:
            j_temp = request.db_session.query(JaspreReportTemplate).filter_by(id=data['id']).first()
            for k, v in data.iteritems():
                setattr(j_temp, k, v)
        else:
            j_temp = JaspreReportTemplate(**data)

        request.db_session.add(j_temp)
        request.db_session.commit()

        result['type'] = 'success'
        result['message'] = 'Successfully saved!'
        result['redirect_url'] = reverse('reports_views.views.jasper_template_edit', args=(j_temp.id,))
    except Exception as e:
        result['type'] = 'error'
        result['message'] = 'Error occurred during saving: {0}'.format(str(e))

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
@access_focus
def remove_jasper_template(request):
    j_temp_id = request.POST['id']
    result = {'message': 'Jasper template was successfully removed!', 'type': 'success'}
    rep_obj = request.db_session.query(JaspreReportTemplate).filter_by(id=j_temp_id).first()

    if rep_obj is not None:
        request.db_session.delete(rep_obj)
        request.db_session.commit()

    return HttpResponse(json.dumps(result), content_type='application/json')


def get_jasper_report_from_db(request, alias, return_json=True):
    query = request.db_session.query(JaspreReportTemplate).filter(JaspreReportTemplate.alias == alias)
    if request.user.is_company:
        query = query.filter(or_(and_(JaspreReportTemplate.company_id == request.user.company_id, JaspreReportTemplate.focus_only == 0),
                                 and_(JaspreReportTemplate.company_id == None, JaspreReportTemplate.focus_only == 0),))

    res = query.first()
    if return_json and res:
        return {'alias': res.alias, 'name': res.name, 'path': res.path}

    return res


@login_required
@access_focus
def patterns(request):
    data = dict()
    data['patterns'] = report_registry.get_available_reports()
    data['data'] = request.db_session.query(ReportPattern).order_by(ReportPattern.name)
    return render_to_response('reports_patterns.html', data, context_instance=RequestContext(request))


@login_required
@access_focus
def create_report_pattern(request, alias):
    report = report_registry.get_report_by_alias(alias)

    if report is None:
        raise Http404()

    data = {"report": report.get_report_for_template(), 'mode': 'new_pattern',
            'companies': request.db_session.query(Company).order_by(Company.name)}

    return render_to_response('report.html', data, context_instance=RequestContext(request))


@login_required
@access_focus
def edit_report_pattern(request, pattern_id):

    rep_obj = request.db_session.query(ReportPattern).filter_by(id=pattern_id).first()
    if not rep_obj:
        raise Http404()

    report = report_registry.get_report_by_alias(rep_obj.alias)
    pattern = ReportDefinition()
    pattern.from_json(rep_obj.pattern)

    if rep_obj.is_for_company == 1 and rep_obj.company_id is not None:
        is_for_num = rep_obj.company_id
    elif rep_obj.is_for_company == 0:
        is_for_num = -1
    else:
        is_for_num = -2

    pattern_fields = ''
    for field in pattern.fields:
        pattern_fields += build_fields_html(request, field, report, 'edit_pattern')

    template = loader.get_template('report.html')
    response = template.render(RequestContext(request, {"report": report.get_report_for_template(),
                                                        "pattern": pattern,
                                                        "pattern_id": pattern_id,
                                                        "pattern_fields": pattern_fields,
                                                        'mode': 'edit_pattern',
                                                        'companies': request.db_session.query(Company).order_by(Company.name),
                                                        'is_for': is_for_num}))

    return HttpResponse(response)


def build_fields_html(request, field, report, mode):
    data = {}

    if field.alias == '':
        field_template = 'report/helpers/blank_field.html'
        data['tmp_readable_name'] = 'Empty field'
    else:
        field_template = 'report/helpers/not_blank_field.html'
        data['tmp_readable_name'] = report.get_field_by_alias(field.alias).readable_name

    data['tmp_alias'] = field.alias
    data['tmp_header'] = field.header
    data['without_id'] = True
    data['report'] = report
    data['mode'] = mode

    template = loader.get_template(field_template)
    field_info = template.render(RequestContext(request, data))

    sub_field_info = [] if field.sub_fields else None

    for sub_field in field.sub_fields:
        sub_field_info.append(build_fields_html(request, sub_field, report, mode))

    data.clear()

    data['field_info'] = field_info
    data['sub_fields'] = sub_field_info
    template = loader.get_template('report/helpers/field_tree.html')
    response = template.render(RequestContext(request, data))

    return response


@login_required
@access_focus
def save_report_pattern(request):
    input_rep = request.POST['data']
    report = json.loads(input_rep)
    pattern_id = int(report['pattern_id']) if report['pattern_id'] != '' else None

    rep_obj = report_registry.get_report_by_alias(report['alias'])

    result = {'message': '', 'type': ''}

    if rep_obj is None:
        result['type'] = 'error'
        result['message'] = 'There is no any data source with the alias {0}!'.format(report['alias'])
    else:
        rep = ReportDefinition()
        rep.from_json(input_rep)

        validation_result = rep.validate_report(False)
        if len(validation_result) == 0:
            is_available_for = int(report['is_available_for'])
            is_for_focus = is_available_for == -1
            is_for_companies = is_available_for == -2
            company_id = None

            if not (is_for_focus or is_for_companies):
                company_id = is_available_for

            report = rep.to_json(clear_filter_data=True)

            if pattern_id is not None:
                res = request.db_session.query(ReportPattern).filter_by(id=pattern_id).first()

                if res.company_id != request.user.company_id:
                    result['type'] = 'error'
                    result['message'] = 'You do not have rights to edit this tempate'

                res.pattern = report
                res.name = rep.header
                res.company_id = company_id
                res.is_for_company = 0 if is_for_focus else 1
                request.db_session.add(res)
                request.db_session.commit()
            else:
                res = ReportPattern(name=rep.header, alias=rep.alias, user_id=request.user.id,
                                    pattern=report, company_id=company_id, is_for_company=0 if is_for_focus else 1)
                request.db_session.add(res)
                request.db_session.commit()
            result['type'] = 'success'
            result['message'] = 'Report template successfully saved!'
            result['id'] = int(res.id)
        else:
            res_msg = 'An error occurred during report template saving:<br>'

            for msg in validation_result:
                res_msg += '{0}<br>'.format(msg)

            result['type'] = 'error'
            result['message'] = res_msg

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
@access_focus
def remove_report_pattern(request):
    pattern_id = request.POST['id']
    result = {'message': 'Report template was successfully deleted!', 'type': 'success'}
    rep_obj = request.db_session.query(ReportPattern).filter_by(id=pattern_id).first()

    if rep_obj is not None:
        reps_count = request.db_session.query(Report).filter_by(pattern_id=pattern_id).count()
        if rep_obj.company_id != request.user.company_id:
            result['type'] = 'error'
            result['message'] = 'You don''t have rights to remove this report template!'
        elif reps_count != 0:
            result['type'] = 'error'
            result['message'] = 'There are reports were created on the report template!'
        else:
            request.db_session.delete(rep_obj)
            request.db_session.commit()

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
def build_report_pattern(request):
    input_rep = request.POST['data']

    rep = ReportDefinition()
    rep.from_json(input_rep)

    validation_result = rep.validate_report(True)
    result = dict()

    if len(validation_result) == 0:
        try:
            report = report_registry.get_report_by_alias(rep.alias)
            custom_where_clause = ('company_id_seq', request.user.company_id) if request.user.is_company else None
            builder = get_report_builder(report.source_type)(rep, report, custom_where_clause=custom_where_clause)
            html_header = builder.build_html_header()
            report_data = builder.get_report_data()

            template = loader.get_template('report/report_content.html')
            response = template.render(RequestContext(request, {"report_data": report_data, "report_table_header": html_header}))

            result = {"content": response, "type": "success", "message": "Report was successfully generated!"}
        except Exception as e:
            result['type'] = 'error'
            result['message'] = 'There is an exception during report generation: ' + str(e)
    else:
        res_msg = 'There was an errors during report generation:<br>'

        for msg in validation_result:
            res_msg += '{0}<br>'.format(msg)

        result['type'] = 'error'
        result['message'] = res_msg

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
def create_report(request, pattern_id):

    rep_obj = request.db_session.query(ReportPattern).filter_by(id=pattern_id).first()
    if not rep_obj or rep_obj.company_id != request.user.company_id:
        raise Http404()

    report = report_registry.get_report_by_alias(rep_obj.alias)
    pattern = ReportDefinition()
    pattern.from_json(rep_obj.pattern)

    pattern_fields = ''
    for field in pattern.fields:
        pattern_fields += build_fields_html(request, field, report, 'new_report')

    template = loader.get_template('report.html')
    response = template.render(RequestContext(request, {"report": report.get_report_for_template(),
                                                        "pattern": pattern,
                                                        "pattern_id": pattern_id,
                                                        "pattern_fields": pattern_fields,
                                                        'mode': 'new_report'}))

    return HttpResponse(response)


@login_required
def show_report(request, report_id):

    rep_obj = request.db_session.query(Report).filter_by(id=report_id).first()
    if not rep_obj or rep_obj.company_id != request.user.company_id:
        raise Http404()

    report = report_registry.get_report_by_alias(rep_obj.pattern.alias)
    pattern = ReportDefinition()
    pattern.from_json(rep_obj.report)

    template = loader.get_template('report.html')
    response = template.render(RequestContext(request, {"report": report.get_report_for_template(),
                                                        "pattern": pattern,
                                                        "pattern_id": rep_obj.pattern_id,
                                                        "report_id": rep_obj.id,
                                                        'report_html_content': rep_obj.html_content,
                                                        'mode': 'show_report'}))

    return HttpResponse(response)


@login_required
def download_report(request, report_id):
    rep_obj = request.db_session.query(Report).filter_by(id=report_id).first()
    if not rep_obj or rep_obj.company_id != request.user.company_id:
        raise Http404()

    content = base64.b64decode(rep_obj.xls_content)

    result = HttpResponse(content=content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = '{0}.xlsx'.format(rep_obj.name, reversed=True)
    result['Content-Disposition'] = 'attachment; filename="'+file_name+'"'

    return result


@login_required
def save_report(request):
    input_rep = request.POST['data']
    report = json.loads(input_rep)
    pattern_id = int(report['pattern_id'])

    rep_obj = report_registry.get_report_by_alias(report['alias'])

    result = {'message': '', 'type': ''}

    if rep_obj is None:
        result['type'] = 'error'
        result['message'] = 'Report template with ID {0} does not exist!'.format(report['pattern_id'])
    else:
        rep = ReportDefinition()
        rep.from_json(input_rep)
        rep.sub_header = request.user.company.name if request.user.is_company else 'Focus'

        validation_result = rep.validate_report(True)

        if len(validation_result) == 0:
            report = rep.to_json()

            custom_where_clause = ('company_id_seq', request.user.company_id) if request.user.is_company else None
            builder = get_report_builder(rep_obj.source_type)(rep, rep_obj, custom_where_clause=custom_where_clause)
            html_header = builder.build_html_header()
            report_data = builder.get_report_data()
            template = loader.get_template('report/report_content.html')
            html_content = template.render(RequestContext(request, {"report_data": report_data, "report_table_header": html_header}))

            path = builder.generate_report(settings.REPORTS_ROOT)
            with open(path, 'rb') as file:
                content = file.read()

            xls_content = base64.b64encode(content)

            res = Report(name=rep.header, user_id=request.user.id,
                         pattern_id=pattern_id, report=report,
                         xls_content=xls_content, html_content=html_content,
                         company_id=request.user.company_id)
            request.db_session.add(res)
            request.db_session.commit()

            result['type'] = 'success'
            result['message'] = 'Report has been successfully saved!'
            result['id'] = int(res.id)
        else:
            res_msg = 'Errors occurred during report saving:<br>'

            for msg in validation_result:
                res_msg += '{0}<br>'.format(msg)

            result['type'] = 'error'
            result['message'] = res_msg

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
def remove_report(request):
    report_id = request.POST['id']
    result = {'type': 'success', 'message': 'Report has been successfully removed!'}

    rep_obj = request.db_session.query(Report).filter_by(id=report_id).first()

    if rep_obj is not None and rep_obj.company_id != request.user.company_id:
        result = {'type': 'error', 'message': 'You do not have rights to remove this report!'}
    elif rep_obj is not None:
        request.db_session.delete(rep_obj)
        request.db_session.commit()

    return HttpResponse(json.dumps(result), content_type='application/json')


@login_required
@access_focus
def data_sources(request):
    data = request.db_session.query(RepDataSource).order_by(RepDataSource.name)

    template = loader.get_template('data_sources/data_sources.html')
    content = template.render(RequestContext(request, {'data_sources': data}))

    return HttpResponse(content)


@login_required
@access_focus
def data_source_edit(request, alias):
    ds = request.db_session.query(RepDataSource).filter_by(alias=alias).first()
    if not ds:
        raise Http404()

    fields = list(request.db_session.query(RepDataSourceField).filter_by(data_source_id=ds.id).order_by(RepDataSourceField.order_num))
    for field in fields:
        try:
            field.filter = request.db_session.query(RepDataSourceFieldFilter).filter_by(field_id=field.id).first()
            field.operations = [r for r, in request.db_session.query(RepDataSourceFieldFilterOperation.operation).filter_by(filter_id=field.id)]
        except Exception as e:
            field.filter = None
            field.operations = None
        field.aggregations = [r for r, in request.db_session.query(RepDataSourceFieldAggregation.aggregation_type).filter_by(field_id=field.id)]

    data = dict()
    data['ds'] = ds
    data['fields'] = fields
    data['types'] = list(report_field_types.values())
    data['operations'] = list(report_filter_operations.values())
    data['aggregations'] = list(report_aggregations.values())

    template = loader.get_template('data_sources/data_source_edit.html')
    content = template.render(RequestContext(request, data))

    return HttpResponse(content)


@login_required
@access_focus
def data_source_save(request):
    data = json.loads(request.POST['data'])
    fields = data['fields']
    fields_order = data['fields_order']['alias']
    ds = request.db_session.query(RepDataSource).filter_by(alias=data['fields_order']['ds-alias']).first()

    for val in fields:
        field = request.db_session.query(RepDataSourceField).filter_by(data_source_id=ds.id, column_name=val['field_alias']).first()
        field.name = val['name']
        field.allow_display = val['allow_display']
        field.allow_ordering = val['allow_ordering']
        field.allow_grouping = val['allow_grouping']
        field.need_sub_total = val['need_sub_total']
        field.field_type = val['field_type']
        field.order_num = fields_order.index(val['field_alias'])
        request.db_session.add(field)
        request.db_session.commit()

        try:
            filt = request.db_session.query(RepDataSourceFieldFilter).filter_by(field_id=field.id).first()
            request.db_session.query(RepDataSourceFieldFilterOperation).filter_by(filter_id=filt.id).delete()
            request.db_session.commit()
        except Exception as e:
            filt = None

        if val['search_column_name'] == '':
            if filt:
                request.db_session.delete(filt)
                request.db_session.commit()
        else:
            if not filt:
                filt = RepDataSourceFieldFilter(field_id=field.id, source_key_column='key', source_val_column='val', source_type='row_sql')
                request.db_session.add(filt)
                request.db_session.commit()

            filt.column_name = val['search_column_name']
            filt.source = val['search_source']

            s_op = val.get('search_operations', [])
            if not isinstance(s_op, list):
                s_op = [s_op]

            for f_op in s_op:
                try:
                    tmp = RepDataSourceFieldFilterOperation(filter_id=filt.id, operation=f_op)
                    request.db_session.add(tmp)
                except Exception as e:
                    pass

            request.db_session.commit()

        request.db_session.query(RepDataSourceFieldAggregation).filter_by(field_id=field.id).delete()
        request.db_session.commit()

        aggs = val.get('aggregations', [])
        if not isinstance(aggs, list):
            aggs = [aggs]

        for tmp in aggs:
            agg = RepDataSourceFieldAggregation(field_id=field.id, aggregation_type=tmp)
            request.db_session.add(agg)

        request.db_session.commit()

    report_registry.delete_report_by_alias(data['fields_order']['ds-alias'])

    return HttpResponse(json.dumps({"type": "success", "message": "Data source configuration has been successfully saved!"}), content_type='application/json')
