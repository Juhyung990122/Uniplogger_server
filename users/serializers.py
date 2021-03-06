from rest_auth.serializers import PasswordResetSerializer
from rest_framework import serializers

from planets.models import Planet
from quests.models import Quest
from quests.serializers import QuestSerializer
from users.models import CustomUser,Feed,QuestList
from rest_auth.registration.serializers import RegisterSerializer


class PlanetSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planet
        fields = '__all__'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','registeredDate', 'email', 'nickname', 'level', 'rank', 'state', 'planet', 'weekly_stats', 'monthly_stats','agree_push', 'registration_token']
    
    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def rank_save(self,user_info):
        rank_list = []
        #feed_count 갯수 기준으로 역순정렬
        for user in user_info:
            feed_count = len(Feed.objects.filter(uid=user.id))
            rank_list.append([feed_count,user.id])
        rank_list = sorted(rank_list, key = lambda x : -x[0])
        user_idx = 0
        for rank in range(1,len(rank_list)+1):
            if rank_list[user_idx][0] == 0:
                rank_list[user_idx][0] = -1
            else:
                rank_list[user_idx][0] = rank
            user_idx+=1

        for i in rank_list:
            user = CustomUser.objects.get(id = i[1])
            if i[0] == -1:
                user.rank = 100
            else:
                total = CustomUser.objects.all().count()
                user.rank = int((i[0] / total) * 100)
            user.save()
    
    def level_save(self,user_info):
        if user_info.experience >= 5:
            user_info.level += user_info.experience // 5
            user_info.experience = user_info.experience % 5
            user_info.save()

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.planet:
            response['planet'] = PlanetSimpleSerializer(instance.planet).data
        else:
            # planet 참여하지 않은 경우 null return
            response['planet'] = None
        return response

class UserjoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['weekly_stats','monthly_stats','level','rank']

# 챌린지(행성)에서만 보여줄 user 정보(planet_score) 추가한 serializer 따로 정의
class PlayerSerializer(serializers.ModelSerializer):
    planet_score = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'nickname', 'planet_score']

    def get_planet_score(self, instance):
        return instance.get_feed_cnt(instance.planet) * 1000 \
               + instance.get_distance(instance.planet) * 100 \
               + instance.get_time(instance.planet) // 60


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = '__all__'
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = UserjoinSerializer(instance.uid).data
        return response
    

class QuestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestList
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['qid'] = QuestSerializer(instance.qid).data
        return response


class QuestListDetailSerializer(serializers.ModelSerializer):
    more_quest = serializers.SerializerMethodField()

    class Meta:
        model = QuestList
        fields = ['id', 'uid', 'qid', 'state', 'more_quest']

    def get_more_quest(self, instance):
        queryset = QuestList.objects.filter(uid=self.context["user_id"], state="TODO").exclude(id=instance.id)
        result = []
        if instance.qid.category == "T":
            # training 이니까 다음 단계 퀘스트 2개 보여주기 (quest.category=="T" & questlist.uid==me & questlist.state=="todo")
            # queryset = queryset.filter(qid__category="T")
            cur = instance.qid.step
            if cur < 10:
                result.append(Quest.objects.get(step=cur+1))
            if cur < 9:
                result.append(Quest.objects.get(step=cur+2))
        elif instance.qid.category == "R":
            # 목표달성형이니까 랜덤으로 퀘스트 2개 보여주기 (quest.category=="R" & questlist.state=="todo")
            queryset = queryset.filter(qid__category="R").order_by('?')
            qcnt = queryset.count()
            if qcnt > 0:
                result.append(Quest.objects.get(id=queryset[0].qid_id))
            if qcnt > 1:
                result.append(Quest.objects.get(id=queryset[1].qid_id))
        return QuestSerializer(result, many=True).data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['qid'] = QuestSerializer(instance.qid).data
        return response


class RegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(required=False, write_only=True)
    registration_token = serializers.CharField(required=False, write_only=True)
    def get_cleaned_data(self):
        users = CustomUser.objects.all()
        return {
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'nickname': self.validated_data.get('nickname', ''),
            'registration_token': self.validated_data.get('registration_token','')
        }

    def validate_nickname(self, nickname):
        return nickname

    def save(self, request):
        users = CustomUser.objects.all()
        for user in users:
            if user.nickname == self.validated_data.get('nickname', ''):
                raise serializers.ValidationError({'msgType':'error','message':'duplicate nickname'})
        res = super(RegisterSerializer, self).save(request)
        res.nickname = self.validated_data.get('nickname', '')
        res.registration_token = self.validated_data.get('registration_token','')
        res.save()
        return res


class CustomPasswordResetSerializer(PasswordResetSerializer):

    # uniplogger://resetPassword?uid=&token=
    def get_email_options(self):
        return {
            'subject_template_name': 'registration/password_reset_subject.txt',
            'html_email_template_name': 'registration/password_reset_message.html',
            # 'email_template_name': 'pw_reset_email.html',
            'extra_email_context': {
                'frontend_url': 'uniplogger://resetPassword'
            }
        }
