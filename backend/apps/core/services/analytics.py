from datetime import timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from apps.core.models import AIUsage, CampaignActivity, Conversation, Lead, Prospect


def chart_data():
    end = timezone.localdate()
    days = [end-timedelta(days=n) for n in reversed(range(14))]
    def series(model, aggregate):
        counts = dict(model.objects.filter(created_at__date__gte=days[0]).annotate(day=TruncDate('created_at')).values('day').annotate(value=aggregate).values_list('day','value'))
        return [counts.get(day,0) for day in days]
    stages = dict(Lead.objects.values('stage').annotate(n=Count('pk')).values_list('stage','n'))
    dates = [day.strftime('%d.%m') for day in days]
    campaigns = list(CampaignActivity.objects.values('campaign_id','campaign__name').annotate(n=Count('pk')).order_by('-n')[:10])
    return [
        ('Kunlik mijozlar',dates,series(Prospect,Count('pk'))),
        ('Kunlik suhbatlar',dates,series(Conversation,Count('pk'))),
        ('Savdo natijalari',['Won','Lost'],[stages.get(x,0) for x in ('won','lost')]),
        ('Lid bosqichlari',list(stages),list(stages.values())),
        ('AI chiqish tokenlari',dates,series(AIUsage,Sum('output_tokens'))),
        ('Kampaniya faolligi',[c['campaign__name'] for c in campaigns],[c['n'] for c in campaigns]),
    ]
