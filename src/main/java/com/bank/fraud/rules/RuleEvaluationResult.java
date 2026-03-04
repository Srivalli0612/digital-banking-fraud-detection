package com.bank.fraud.rules;

import java.math.BigDecimal;

public class RuleEvaluationResult {

    private BigDecimal normalizedScore;
    private String triggeredRules;

    public RuleEvaluationResult(BigDecimal normalizedScore,
                                String triggeredRules) {
        this.normalizedScore = normalizedScore;
        this.triggeredRules = triggeredRules;
    }

    public BigDecimal getNormalizedScore() {
        return normalizedScore;
    }

    public String getTriggeredRules() {
        return triggeredRules;
    }
}