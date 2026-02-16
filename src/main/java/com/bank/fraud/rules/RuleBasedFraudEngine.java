package com.bank.fraud.rules;

import org.springframework.stereotype.Component;

import com.bank.fraud.model.FraudResult;
import com.bank.fraud.model.Transaction;
import com.bank.fraud.service.FraudDetectionEngine;

@Component
public class RuleBasedFraudEngine implements FraudDetectionEngine {
 
	private final RuleEngine ruleEngine;

    public RuleBasedFraudEngine(RuleEngine ruleEngine) {
        this.ruleEngine = ruleEngine;
    }

    @Override
    public boolean isFraud(Transaction transaction) {

    	return ruleEngine.evaluate(transaction).getFraudDetected();
    }

    public FraudResult evaluate(Transaction transaction) {
        return ruleEngine.evaluate(transaction);
    }
}
