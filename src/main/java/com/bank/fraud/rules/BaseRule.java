package com.bank.fraud.rules;

import com.bank.fraud.model.FraudRuleConfig;
import com.bank.fraud.service.FraudRuleConfigService;

import java.math.BigDecimal;

public abstract class BaseRule implements FraudRule {

    protected final FraudRuleConfigService configService;

    public BaseRule(FraudRuleConfigService configService) {
        this.configService = configService;
    }

    protected FraudRuleConfig getConfig() {
        return configService.getByRuleName(ruleName());
    }

    protected boolean isActive() {
        FraudRuleConfig config = getConfig();
        return config != null && Boolean.TRUE.equals(config.getActive());
    }

    protected BigDecimal getThreshold() {
        FraudRuleConfig config = getConfig();
        return config != null && config.getThresholdValue() != null
                ? config.getThresholdValue()
                : BigDecimal.ZERO;
    }

    @Override
    public BigDecimal riskScore() {
        FraudRuleConfig config = getConfig();
        return config != null && config.getWeight() != null
                ? config.getWeight()
                : BigDecimal.ZERO;
    }
}