package com.bank.fraud.rules;

import java.math.BigDecimal;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.RiskLevel;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudDetectionEngine;

@Component
public class RuleBasedFraudEngine implements FraudDetectionEngine {

    // ✅ Add Logger
    private static final Logger log =
            LoggerFactory.getLogger(RuleBasedFraudEngine.class);

    private final List<FraudRule> rules;

    private static final BigDecimal MAX_SCORE = BigDecimal.ONE;

    public RuleBasedFraudEngine(List<FraudRule> rules) {
        this.rules = rules;
    }

    @Override
    public boolean isFraud(Transaction transaction) {
        return evaluate(transaction).getFraudDetected();
    }

    public FraudResult evaluate(Transaction transaction) {

        BigDecimal totalRisk = BigDecimal.ZERO;
        StringBuilder triggeredRules = new StringBuilder();

        for (FraudRule rule : rules) {
            
            // ✅ Log which rule is being evaluated
            log.info("Evaluating rule: {}", rule.ruleName());

            BigDecimal ruleScore = rule.evaluate(transaction);

            if (ruleScore.compareTo(BigDecimal.ZERO) > 0) {
                
                // ✅ Log when a rule is triggered (warn level is good for highlighting risk)
                log.warn("Rule triggered: {}", rule.ruleName());

                totalRisk = totalRisk.add(ruleScore);
                triggeredRules.append(rule.ruleName()).append(", ");
            }
        }

        // Normalize risk (cap at 1.0)
        BigDecimal normalizedRisk =
                totalRisk.compareTo(MAX_SCORE) > 0
                        ? MAX_SCORE
                        : totalRisk;
                        
        // ✅ Log the final normalized score
        log.info("Final normalized risk score: {}", normalizedRisk);

        RiskLevel level = calculateRiskLevel(normalizedRisk);

        boolean fraudDetected =
                level == RiskLevel.HIGH_RISK ||
                level == RiskLevel.CRITICAL_RISK;

        FraudResult result = new FraudResult();
        result.setFraudDetected(fraudDetected);
        result.setRiskScore(normalizedRisk);
        result.setRuleTriggered(triggeredRules.toString());
        result.setRiskLevel(level);

        return result;
    }

    private RiskLevel calculateRiskLevel(BigDecimal score) {

        if (score.compareTo(new BigDecimal("0.3")) < 0)
            return RiskLevel.LOW_RISK;

        else if (score.compareTo(new BigDecimal("0.6")) < 0)
            return RiskLevel.MEDIUM_RISK;

        else if (score.compareTo(new BigDecimal("0.8")) < 0)
            return RiskLevel.HIGH_RISK;

        else
            return RiskLevel.CRITICAL_RISK;
    }
}