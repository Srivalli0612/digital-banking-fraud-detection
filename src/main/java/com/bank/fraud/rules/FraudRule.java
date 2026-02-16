package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;

public interface FraudRule {

    boolean evaluate(Transaction transaction);

    String ruleName();

    double riskScore();
}
