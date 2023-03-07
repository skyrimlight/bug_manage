from untils.bootstrap import BootStrapModelForm
from web.models import ProjectInvite


class InviteModelForm(BootStrapModelForm):
    class Meta:
        model = ProjectInvite
        fields = ['period', 'count']
