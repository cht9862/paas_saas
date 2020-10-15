# _*_ coding: utf-8 _*_

from rest_framework import serializers

from apps.node_man.constants import PLUGIN_OS_CHOICES
from apps.node_man.models import ProcControl


class ProcessControlInfoSerializer(serializers.ModelSerializer):
    module = serializers.CharField(required=False, max_length=32)
    project = serializers.CharField(required=False, max_length=32)
    plugin_package_id = serializers.IntegerField(required=False)

    install_path = serializers.CharField(required=False)
    log_path = serializers.CharField(required=False)
    data_path = serializers.CharField(required=False)
    pid_path = serializers.CharField(required=False)
    start_cmd = serializers.CharField(required=False, allow_blank=True)
    stop_cmd = serializers.CharField(required=False, allow_blank=True)
    restart_cmd = serializers.CharField(required=False, allow_blank=True)
    reload_cmd = serializers.CharField(required=False, allow_blank=True)

    kill_cmd = serializers.CharField(required=False, allow_blank=True)
    version_cmd = serializers.CharField(required=False, allow_blank=True)
    health_cmd = serializers.CharField(required=False, allow_blank=True)
    debug_cmd = serializers.CharField(required=False, allow_blank=True)

    process_name = serializers.CharField(required=False, max_length=128)
    port_range = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    need_delegate = serializers.BooleanField(default=True)

    os = serializers.ChoiceField(required=False, choices=PLUGIN_OS_CHOICES)

    class Meta:
        model = ProcControl
        fields = (
            "id",
            "module",
            "project",
            "plugin_package_id",
            "install_path",
            "log_path",
            "data_path",
            "pid_path",
            "start_cmd",
            "stop_cmd",
            "restart_cmd",
            "reload_cmd",
            "kill_cmd",
            "version_cmd",
            "health_cmd",
            "debug_cmd",
            "os",
            "process_name",
            "port_range",
            "need_delegate",
        )

    def create(self, validated_data):
        data = {
            "module": validated_data["module"],
            "project": validated_data["project"],
            "os": validated_data["os"],
            "plugin_package_id": validated_data["plugin_package_id"],
        }
        process_info, created = ProcControl.objects.update_or_create(defaults=validated_data, **data)
        return process_info
