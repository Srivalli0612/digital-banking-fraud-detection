package com.bank.fraud.rules;

import com.bank.fraud.model.Transaction;
import java.math.BigDecimal;

public interface FraudRule {

    BigDecimal evaluate(Transaction transaction);

    String ruleName();

    BigDecimal riskScore();
}