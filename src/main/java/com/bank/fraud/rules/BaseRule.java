package com.bank.fraud.rules;

import com.bank.fraud.model.FraudRuleConfig;
import com.bank.fraud.repository.FraudRuleConfigRepository;

import java.math.BigDecimal;

public abstract class BaseRule implements FraudRule {

    protected final FraudRuleConfigRepository configRepository;

    public BaseRule(FraudRuleConfigRepository configRepository) {
        this.configRepository = configRepository;
    }

    protected FraudRuleConfig getConfig() {
        return configRepository
                .findByRuleName(ruleName())
                .orElse(null);
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