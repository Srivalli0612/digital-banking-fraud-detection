package com.bank.fraud.rules;

import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.repository.TransactionRepository;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Component;

@Component
public class RuleEngine {

	private static final double FRAUD_THRESHOLD = 0.7;
    private final List<FraudRule> rules;
    TransactionRepository transactionRepository;
    
     // 🔹 Constructor for Spring
    public RuleEngine(List<FraudRule> rules) {
    	this.rules = rules;
    }

     // 🔹 Constructor for Simulator (Manual)
    public RuleEngine() {
        this.rules = new ArrayList<>();
        this.rules.add(new HighAmountRule());
        this.rules.add(new ForeignLocationRule());
        this.rules.add(new SuspiciousMerchantRule());
        this.rules.add(new OddHoursRule());
        // Add simulation rapid rule
        this.rules.add(new com.bank.fraud.simulator
                .RapidMultipleTransactionsSimulationRule());
    }
   
    public FraudResult evaluate(Transaction transaction) {

        FraudResult result = new FraudResult();
        result.setTransaction(transaction);

        double totalRisk = 0.0;
        StringBuilder triggeredRules = new StringBuilder();

        for (FraudRule rule : rules) {
            if (rule.evaluate(transaction)) {
                totalRisk += rule.riskScore();
                triggeredRules.append(rule.ruleName()).append(" | ");
            }
        }

        result.setRiskScore(totalRisk);
        
     // Always store triggered rules if any rule fired
        if (triggeredRules.length() > 0) {
            result.setRuleTriggered(triggeredRules.toString());
        }

        if (totalRisk >= FRAUD_THRESHOLD) {
            result.setFraudDetected(true);
//            result.setRuleTriggered(triggeredRules.toString());
        } else {
            result.setFraudDetected(false);
        }

        return result;
    }

}
