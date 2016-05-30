# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from Model import SysObject, Group, SysFunction
from acc.decorators import permission_required
from django.core.urlresolvers import reverse

__author__ = 'D.Ivanets'


@permission_required('perms_moderate_groups')
def add_group(request):
    errors = []
    prefix = "perm_"
    sys_objects = request.db_session.query(SysObject).all()
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        if request.db_session.query(Group).filter_by(company=request.user.company).filter_by(name=group_name).first():
            errors.append(
                {'field': 'Group name', 'message': 'Group with such name already exists.'})
        if not errors:
            group = Group()
            group.name = group_name
            group.company = request.user.company
            for function in request.db_session.query(SysFunction).all():
                if prefix + str(function.id) in request.POST:
                    group.permissions.append(function)
            request.db_session.add(group)
            request.db_session.commit()

            return HttpResponseRedirect('/acc/permission/groups_list/')

    return render_to_response('permission_add_group.html',
                              {'operation': 'add',
                               'errors': errors,
                               'sys_objects': sys_objects,
                               'prefix': prefix},
                              context_instance=RequestContext(request))


@permission_required('perms_moderate_groups')
def edit_group(request, group_id):
    errors = []
    prefix = "perm_"
    sys_objects = request.db_session.query(SysObject).all()
    group = request.db_session.query(Group).filter_by(
        company=request.user.company).filter_by(id=group_id).first()
    if not group:
        raise Http404
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        if request.db_session.query(Group).filter_by(company=request.user.company).filter_by(name=group_name)\
                .filter(Group.id != group.id).first():
            errors.append(
                {'field': 'Group name', 'message': 'Group with such name already exists.'})
        if not errors:
            group.name = group_name
            functions = []
            for function in request.db_session.query(SysFunction).all():
                if prefix + str(function.id) in request.POST:
                    functions.append(function)
            group.permissions = functions
            request.db_session.commit()

            return HttpResponseRedirect('/acc/permission/groups_list/')

    return render_to_response('permission_add_group.html',
                              {'operation': 'edit',
                               'errors': errors,
                               'sys_objects': sys_objects,
                               'prefix': prefix,
                               'group': group},
                              context_instance=RequestContext(request))
