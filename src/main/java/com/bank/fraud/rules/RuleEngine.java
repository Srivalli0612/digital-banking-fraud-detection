package com.bank.fraud.rules;

import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.model.AlertPriority;
import com.bank.fraud.model.FraudRuleConfig;
import com.bank.fraud.repository.FraudRuleConfigRepository;

import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;

@Component
public class RuleEngine {

    private final List<FraudRule> rules;
    private final FraudRuleConfigRepository configRepository;

    public RuleEngine(List<FraudRule> rules,
                      FraudRuleConfigRepository configRepository) {
        this.rules = rules;
        this.configRepository = configRepository;
    }

    public FraudResult evaluate(Transaction transaction) {

        BigDecimal totalScore = BigDecimal.ZERO;
        BigDecimal maxPossibleScore = BigDecimal.ZERO;

        List<String> triggeredRules = new ArrayList<>();

        for (FraudRule rule : rules) {

            BigDecimal ruleWeight = rule.riskScore();
            maxPossibleScore = maxPossibleScore.add(ruleWeight);

            BigDecimal ruleScore = rule.evaluate(transaction);

            if (ruleScore.compareTo(BigDecimal.ZERO) > 0) {
                totalScore = totalScore.add(ruleScore);
                triggeredRules.add(rule.ruleName());
            }
        }

        BigDecimal normalizedScore = BigDecimal.ZERO;

        if (maxPossibleScore.compareTo(BigDecimal.ZERO) > 0) {
            normalizedScore = totalScore.divide(
                    maxPossibleScore,
                    4,
                    RoundingMode.HALF_UP
            );
        }

        BigDecimal fraudThreshold = getFraudThreshold();

        boolean isFraud =
                normalizedScore.compareTo(fraudThreshold) >= 0;
      
       
        FraudResult result = new FraudResult();
        result.setTransaction(transaction);
        result.setRiskScore(normalizedScore);
        result.setFraudDetected(isFraud);
        result.setRuleTriggered(String.join(", ", triggeredRules));
        result.setPriority(calculatePriority(normalizedScore));

        return result;
    }

    private BigDecimal getFraudThreshold() {

        FraudRuleConfig config = configRepository
                .findByRuleName("GLOBAL_FRAUD_THRESHOLD")
                .orElse(null);

        return config != null
                ? config.getThresholdValue()
                : new BigDecimal("0.2000");
    }

    private AlertPriority calculatePriority(BigDecimal score) {

        if (score.compareTo(new BigDecimal("0.85")) >= 0) {
            return AlertPriority.CRITICAL;
        } else if (score.compareTo(new BigDecimal("0.70")) >= 0) {
            return AlertPriority.HIGH;
        } else if (score.compareTo(new BigDecimal("0.50")) >= 0) {
            return AlertPriority.MEDIUM;
        } else {
            return AlertPriority.LOW;
        }
    }
}