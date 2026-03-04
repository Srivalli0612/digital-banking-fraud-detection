package com.bank.fraud.rules;

import com.bank.fraud.model.AlertPriority;
import com.bank.fraud.model.RiskLevel;
import com.bank.fraud.model.Transaction;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;

@Component
public class RuleEngine {

    private final List<FraudRule> rules;

    public RuleEngine(List<FraudRule> rules) {
        this.rules = rules;
    }

    public RuleEvaluationResult evaluate(Transaction transaction) {

        BigDecimal totalScore = BigDecimal.ZERO;
        BigDecimal maxPossibleScore = BigDecimal.ZERO;

        List<String> triggeredRules = new ArrayList<>();

        for (FraudRule rule : rules) {

            // Skip inactive rules safely
            if (rule instanceof BaseRule baseRule) {
                if (!baseRule.isActive()) {
                    continue;
                }
            }

            BigDecimal ruleWeight = rule.riskScore();

            // Add only active rule weight
            maxPossibleScore = maxPossibleScore.add(ruleWeight);

            BigDecimal ruleScore = rule.evaluate(transaction);

            if (ruleScore.compareTo(BigDecimal.ZERO) > 0) {
                totalScore = totalScore.add(ruleScore);
                triggeredRules.add(rule.ruleName());
            }
        }

        BigDecimal normalizedScore = BigDecimal.ZERO;

        if (maxPossibleScore.compareTo(BigDecimal.ZERO) > 0) {
            normalizedScore = totalScore
                    .divide(maxPossibleScore, 4, RoundingMode.HALF_UP);
        }
        
      
        return new RuleEvaluationResult(
                normalizedScore,
                String.join(", ", triggeredRules)
        );
    }
       
}