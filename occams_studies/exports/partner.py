"""
Partner Linkage
"""

#
# BBB: This needs to be moved into a form.
#


from sqlalchemy.orm import aliased

from .. import _, models
from .plan import ExportPlan
from .codebook import row, types


class PartnerPlan(ExportPlan):

    name = 'PartnerLinkage'

    title = _(u'Partner Linkage')

    has_private = True

    @property
    def is_enabled(self):
        return 'aeh' in self.db_session.bind.url.database

    def codebook(self):
        return iter([
            row('partner_id', self.name, types.NUMBER,
                is_system=True, is_required=True),
            row('partner_pid', self.name, types.STRING,
                title=u'This Partner\'s Patient Entry',
                desc=u'This partner is also a patient; This property references that patient entry'),  # NOQA
            row('index_pid', self.name, types.STRING,
                is_required=True, is_system=True),
            row('site', self.name, types.STRING,
                is_required=True, is_system=True),

            row('report_date', self.name, types.DATE,
                title=u'Date Partner Reported',
                desc=u'The date that the reporting patient reported this partner.',  # NOQA
                is_required=True),

            row('create_date', self.name, types.DATE,
                is_required=True, is_system=True),
            row('create_user', self.name, types.STRING,
                is_required=True, is_system=True),
            row('modify_date', self.name, types.DATE,
                is_required=True, is_system=True),
            row('modify_user', self.name, types.STRING, is_required=True,
                is_system=True)
        ])

    def data(self,
             use_choice_labels=False,
             expand_collections=False,
             ignore_private=True):

        session = self.db_session

        CreateUser = aliased(models.User)
        ModifyUser = aliased(models.User)
        PartnerPatient = aliased(models.Patient)

        query = (
            session.query(
                models.Partner.id.label('partner_id'),
                PartnerPatient.pid.label('partner_pid'),
                models.Patient.pid.label('index_pid'),
                models.Site.name.label('site'),

                models.Partner.report_date,

                models.Partner.create_date,
                CreateUser.key.label('create_user'),
                models.Partner.modify_date,
                ModifyUser.key.label('modify_user'))
            .select_from(models.Partner)
            .join(
                models.Patient,
                models.Partner.patient_id == models.Patient.id)
            .join(models.Patient.site)
            .outerjoin(
                PartnerPatient,
                PartnerPatient.id == models.Partner.enrolled_patient_id)
            .join(CreateUser, models.Partner.create_user_id == CreateUser.id)
            .join(ModifyUser, models.Partner.modify_user_id == ModifyUser.id)
            .order_by(models.Partner.id))
        return query
