# Copyright (c) Istituto Nazionale di Fisica Nucleare (INFN). 2020-2021
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import current_app as app, Blueprint, render_template
from app import forms, models, db
from sqlalchemy.exc import IntegrityError
from flask_login import login_required
from app.utils.decorators import *

group_bp = Blueprint('group_bp', __name__,
                           template_folder='templates',
                           static_folder='static')


@group_bp.route("/create", methods=["GET", "POST"])
@roles_required('Admin')
def create():

    form = forms.GroupForm()

    if form.validate_on_submit():
        # save to db
        try:
            new_group = models.Group()

            form.populate_obj(new_group)
            db.session.add(new_group)
            db.session.commit()
            flash('You have successfully saved the new group!', 'success')
        except IntegrityError as e:
            app.logger.error("IntegrityError saving new group {}: {}".format(form.name.data, str(e)))
            flash("Error saving the group: {} already exists".format(form.name.data), 'warning')
        except Exception as e:
            app.logger.error("Error saving new group {}: {}".format(form.name.data, str(e)))
            flash("Error saving the group {}: {}".format(form.name.data, str(e)), 'warning')

        return redirect(url_for('group_bp.list'))

    return render_template('groupform.html', title="Create group", form=form)


@group_bp.route('/list', methods=["GET"])
@login_required
def list():
    user = current_user

    if user.is_admin():
        groups = models.Group.query.all()
    else:
        groups = user.groups

    return render_template('groups.html', title='Groups', groups=groups)


@group_bp.route('/edit/<name>', methods=['GET', 'POST'])
@roles_required('Admin')
def edit(name=None):

    group = models.Group.query.filter(models.Group.name == name).first()

    form = forms.GroupForm(obj=group)

    if form.validate_on_submit():
        # save to db
        try:
            form.populate_obj(group)
            db.session.add(group)
            db.session.commit()
            flash('You have successfully updated the Group information!', 'success')
        except Exception as e:
            flash("Error updating the Group {}: {}".format(group.name, str(e)), 'warning')

        return redirect(url_for('group_bp.list'))

    # disable fields that cannot be changed
    form.name.render_kw = {'disabled': 'disabled'}

    return render_template('groupform.html', title='Update Group Information', form=form)



@group_bp.route('/view', methods=["GET"])
@login_required
def view():
    name = request.args.get('name', None)
    if name:
        group = models.Group.query.filter(models.Group.name == name).first()

        return render_template('groupdetails.html', title="Group details", group=group, slas=group.slas)
    else:
        return "not found"


@group_bp.route('/delete', methods=["GET"])
@roles_required('Admin')
def delete():
    name = request.args.get('name', None)

    try:
        group = models.Group.query.filter(models.Group.name == name).first()
        db.session.delete(group)
        db.session.commit()

        flash('You have successfully deleted the Group {}'.format(group.name), 'success')

    except IntegrityError as e:
        app.logger.error("IntegrityError deleting group {}: {}".format(name, str(e)))
        flash("Error deleting group {}: Check if there are existing slas".format(name), 'warning')
    except Exception as e:
        app.logger.error("Error deleting group {}: {}".format(name, str(e)))
        flash("Error deleting group {}: {}".format(name, str(e)), 'warning')

    return redirect(url_for('group_bp.list'))
