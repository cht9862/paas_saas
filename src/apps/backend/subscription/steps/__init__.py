# -*- coding: utf-8 -*-
from apps.backend.subscription.steps.agent import AgentStep
from apps.backend.subscription.steps.plugin import PluginStep

SUPPORTED_STEPS = {"PLUGIN": PluginStep, "AGENT": AgentStep}


class StepFactory(object):
    @classmethod
    def get_step_manager(cls, subscription_step):
        step_type = subscription_step.type
        try:
            step_cls = SUPPORTED_STEPS[step_type]
        except KeyError:
            raise KeyError("unsupported step type: %s" % step_type)
        return step_cls(subscription_step)
