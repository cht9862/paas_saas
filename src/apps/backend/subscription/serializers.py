# -*- coding: utf-8 -*-


from rest_framework import serializers

from apps.exceptions import ValidationError
from apps.backend.constants import TargetNodeType


class GatewaySerializer(serializers.Serializer):
    bk_username = serializers.CharField()
    bk_app_code = serializers.CharField()


class CreateSubscriptionSerializer(GatewaySerializer):
    class ScopeSerializer(serializers.Serializer):
        bk_biz_id = serializers.IntegerField(required=False, default=None)
        object_type = serializers.ChoiceField(choices=["HOST", "SERVICE"])
        node_type = serializers.ChoiceField(
            choices=[
                TargetNodeType.INSTANCE,
                TargetNodeType.TOPO,
                TargetNodeType.SET_TEMPLATE,
                TargetNodeType.SERVICE_TEMPLATE,
            ]
        )
        need_register = serializers.BooleanField(required=False, default=False)
        nodes = serializers.ListField()

    class StepSerializer(serializers.Serializer):
        id = serializers.CharField()
        type = serializers.CharField()
        config = serializers.DictField()
        params = serializers.DictField()

    class TargetHostSerializer(serializers.Serializer):
        bk_host_id = serializers.CharField(required=False, label="目标机器主机ID")
        ip = serializers.CharField(required=False, label="目标机器IP")
        bk_cloud_id = serializers.CharField(required=False, label="目标机器云区域ID")
        bk_supplier_id = serializers.CharField(default="0", label="目标机器开发商ID")

        def validate(self, attrs):
            # bk_host_id 和 (ip, bk_cloud_id) 必须有一组
            if attrs.get("bk_host_id"):
                return attrs

            if attrs.get("ip") and attrs.get("bk_cloud_id"):
                return attrs

            raise ValidationError("目前机器必须要有 bk_host_id 或者 (ip + bk_cloud_id)")

    name = serializers.CharField(required=False)
    scope = ScopeSerializer(many=False)
    steps = serializers.ListField(child=StepSerializer(), min_length=1)
    target_hosts = TargetHostSerializer(many=True, label="下发的目标机器列表", required=False, allow_empty=False)
    run_immediately = serializers.BooleanField(required=False, default=False)
    is_main = serializers.BooleanField(required=False, default=False)


class GetSubscriptionSerializer(GatewaySerializer):
    subscription_id_list = serializers.ListField(child=serializers.IntegerField())


class UpdateSubscriptionSerializer(GatewaySerializer):
    class ScopeSerializer(serializers.Serializer):
        node_type = serializers.ChoiceField(
            choices=[
                TargetNodeType.INSTANCE,
                TargetNodeType.TOPO,
                TargetNodeType.SET_TEMPLATE,
                TargetNodeType.SERVICE_TEMPLATE,
            ]
        )
        nodes = serializers.ListField()
        bk_biz_id = serializers.IntegerField(required=False, default=None)

    class StepSerializer(serializers.Serializer):
        id = serializers.CharField()
        params = serializers.DictField()

    subscription_id = serializers.IntegerField()
    name = serializers.CharField(required=False)
    scope = ScopeSerializer()
    steps = serializers.ListField(child=StepSerializer())
    run_immediately = serializers.BooleanField(required=False, default=False)


class DeleteSubscriptionSerializer(GatewaySerializer):
    subscription_id = serializers.IntegerField()


class SwitchSubscriptionSerializer(GatewaySerializer):
    subscription_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=["enable", "disable"])


class RunSubscriptionSerializer(GatewaySerializer):
    class ScopeSerializer(serializers.Serializer):
        node_type = serializers.ChoiceField(
            choices=[
                TargetNodeType.INSTANCE,
                TargetNodeType.TOPO,
                TargetNodeType.SET_TEMPLATE,
                TargetNodeType.SERVICE_TEMPLATE,
            ]
        )
        nodes = serializers.ListField()

    subscription_id = serializers.IntegerField()
    scope = ScopeSerializer(required=False)
    actions = serializers.DictField(child=serializers.CharField(), required=False)


class RevokeSubscriptionSerializer(GatewaySerializer):
    subscription_id = serializers.IntegerField()
    instance_id_list = serializers.ListField(required=False)


class RetrySubscriptionSerializer(GatewaySerializer):
    subscription_id = serializers.IntegerField()
    instance_id_list = serializers.ListField(required=False)
    actions = serializers.DictField(child=serializers.CharField(), required=False)


class TaskResultSerializer(GatewaySerializer):
    subscription_id = serializers.IntegerField()
    task_id_list = serializers.ListField(child=serializers.IntegerField(), required=False)
    need_detail = serializers.BooleanField(default=False)


class TaskResultDetailSerializer(GatewaySerializer):
    subscription_id = serializers.IntegerField()
    task_id = serializers.IntegerField(required=False)
    instance_id = serializers.CharField()


class InstanceHostStatusSerializer(GatewaySerializer):
    subscription_id_list = serializers.ListField(child=serializers.IntegerField())
    show_task_detail = serializers.BooleanField(default=False)
    need_detail = serializers.BooleanField(default=False)


class RetryNodeSerializer(GatewaySerializer):
    subscription_id = serializers.IntegerField()
    instance_id = serializers.CharField()


class CMDBSubscriptionSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    action = serializers.CharField()
    obj_type = serializers.CharField()
    data = serializers.ListField()


class FetchCommandsSerializer(serializers.Serializer):
    bk_host_id = serializers.IntegerField()
    host_install_pipeline_id = serializers.CharField()
    is_uninstall = serializers.BooleanField()
    batch_install = serializers.BooleanField()
