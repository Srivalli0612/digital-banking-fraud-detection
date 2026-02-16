package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;

public class ForeignLocationRule implements FraudRule {

	@Override
	public boolean evaluate(Transaction transaction) {
	    return transaction.getLocation() != null &&
	           !transaction.getLocation().equalsIgnoreCase("INDIA") &&
	           transaction.getAmount() > 5000;
	}


    @Override
    public String ruleName() {
        return "FOREIGN_LOCATION_RULE";
    }

    @Override
    public double riskScore() {
        return 0.7;
    }
}
